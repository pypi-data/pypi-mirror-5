from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPUnprocessableEntity
from sapyens.helpers import get_by_id, raise_not_found
from wtforms.ext import csrf
import wtforms.widgets
import wtforms
import wtforms as w
import wtforms.validators as v
from sqlalchemy.orm import scoped_session, sessionmaker, class_mapper, ColumnProperty, RelationshipProperty
import sqlalchemy.types
import logging


log = logging.getLogger(__name__)


class SecureForm (csrf.SecureForm):
	def generate_csrf_token (self, request):
		return request.session.get_csrf_token()

	def validate_csrf_token (self, field):
		if field.current_token != field.data:
			raise HTTPUnprocessableEntity()


_default_sqla_t = sqlalchemy.types.String
sqla_t_to_field = {
	_default_sqla_t:          (w.StringField, []),
	sqlalchemy.types.Boolean: (w.BooleanField, []),
	sqlalchemy.types.Integer: (w.IntegerField, []),
}

def _coltype_to_field (coltype):
	for sqla_t, v in sqla_t_to_field.items():
		if isinstance(coltype, sqla_t):
			return v
	return sqla_t_to_field[_default_sqla_t]

def make_form (model_class, field_config = None, form_base_class = SecureForm):
	field_config = field_config or {}

	class Form (form_base_class):
		pass

	for prop in class_mapper(model_class).iterate_properties:
		name = prop.key

		if not (name in field_config and not field_config[name]):
			if isinstance(prop, ColumnProperty):
				if len(prop.columns) > 1:
					log.warning("prop '%s' has > 1 columns, skipping" % prop)
				else:
					[column] = prop.columns
					if not column.primary_key:
						field_class, validators = _coltype_to_field(column.type)
						
						vs = field_config[name].get('validators', validators) if name in field_config else validators
						is_readonly = field_config[name].get('readonly', False) if name in field_config else False
						widget = False if is_readonly else None
						field_args = field_config[name].get('field_args', {}) if name in field_config else {}

						title = name.capitalize().replace('_', ' ')

						field = field_class(title, vs, widget = widget, **field_args)
						setattr(Form, name, field)
			elif isinstance(prop, RelationshipProperty):
				#https://groups.google.com/forum/#!msg/sqlalchemy/wb2M_oYkQdY/CZhuu45g40UJ
				#http://stackoverflow.com/questions/3805712/what-type-is-on-the-other-end-of-relation-in-sqlalchemy-without-creating-objects
				#https://groups.google.com/forum/?fromgroups=#!topic/sqlalchemy/z5fS-3Rwkfs
				pass
	
	return Form


def make_relation_field (model, *args, **kwargs):
	class ItemWidget (unicode):
		def all_objects (self):
			return model.query.all()

		def object_title (self, obj):
			object_title_attr = kwargs.get('object_title_attr')
			if object_title_attr:
				return getattr(obj, object_title_attr)
			else:
				return getattr(obj, 'title', unicode(obj))

	class RelationField (wtforms.IntegerField):
		widget = wtforms.widgets.HiddenInput()

		def process_formdata (self, valuelist):
			[id] = valuelist
			self.data = model.query.get(id)

	return wtforms.FieldList(RelationField(), *args, widget = ItemWidget('sapyens.crud:templates/relation.mako'))

class CrudView (object):
	renderer = None
	route_name = None
	route_path = None

	def __init__ (self, model_class, form_class):
		self._model = model_class
		self._form_class = form_class

	def include_to_config (self, config):
		raise NotImplementedError()

	def _produce_extra_form_args (self, form_class, request):
		if issubclass(form_class, csrf.SecureForm):
			return {'csrf_context': request}
		else:
			return {}

class SubmitView (CrudView):
	redirect_route = None
	db_session = None
	list_route = None
	page_title = None

	def _fetch_model (self, request):
		raise NotImplementedError()

	def _produce_form_input (self, request):
		return request.POST

	def _on_after_saved (self, request, model):
		pass

	def _on_before_populate (self, request, model, form):
		pass

	def _make_redirect_url (self, request, model_id): #TODO merge model and pass
		return request.route_url(self.redirect_route, id = model_id)

	def __call__ (self, request):
		model = self._fetch_model(request)

		form = self._form_class(self._produce_form_input(request),
			**self._produce_extra_form_args(self._form_class, request))

		def form_page_with_errors ():
			return {
				'model': model,
				'form': form,
				'submit_path': request.current_route_path(),
				'list_route': self.list_route,
				'page_title': self._page_title(model),
			}

		if form.validate():
			#TODO delete old csrf token?

			# remove readonly fields
			for field in form:
				if field.widget is False:
					del form[field.short_name]

			if self._on_before_populate(request, model, form) is False:
				return form_page_with_errors()
			else:
				return self._populate_and_return(form, model, request)
		else:
			return form_page_with_errors()

	def _populate_and_return (self, form, model, request):
		form.populate_obj(model)

		self.db_session.add(model)
		self.db_session.flush()
		model_id = model.id
		#TODO merge

		self._on_after_saved(request, model)

		request.session.flash(u"Successfully saved")

		return HTTPFound(location = self._make_redirect_url(request, model_id))

	def _page_title (self, model):
		raise NotImplementedError()

class CreateView (SubmitView):
	def _fetch_model (self, _request):
		return self._model()

	def include_to_config (self, config):
		config.add_route(self.route_name, self.route_path)
		config.add_view(self, route_name = self.route_name, renderer = self.renderer, request_method = 'POST', permission = self.permission)

		config.add_view(lambda req: HTTPFound(
			location = self._make_GET_redirect_route(req)
		), route_name = self.route_name, request_method = 'GET', permission = self.permission)

	def _make_GET_redirect_route (self, request): #TODO shit
		return req.route_url(self.redirect_route)

	def _page_title (self, _model):
		return self.page_title or (u"create %s" % unicode(self._model.__name__)) #TODO copypaste

class UpdateView (CreateView):
	def _fetch_model (self, request):
		return get_by_id(self._model, int(request.matchdict['id'])) or raise_not_found()

	def _page_title (self, model):
		return (self.page_title or (u"edit %s #{id}" % unicode(self._model.__name__))).format(id = model.id) #TODO copypaste

class EditView (CrudView):
	submit_path_route = None
	list_route = None
	page_title = None

	def __call__ (self, request):
		model = get_by_id(self._model, int(request.matchdict['id'])) or raise_not_found()
		return {
			'model': model,
			'form': self._form_class(obj = model, **self._produce_extra_form_args(self._form_class, request)),
			'submit_path': request.route_path(self.submit_path_route, id = model.id),
			'list_route': self.list_route,
			'page_title': (self.page_title or (u"edit %s #{id}" % unicode(self._model.__name__))).format(id = model.id)
		}

	def include_to_config (self, config):
		config.add_route(self.route_name, self.route_path)
		config.add_view(self, route_name = self.route_name, renderer = self.renderer, permission = self.permission)

class NewView (EditView):
	def __call__ (self, request):
		return {
			'model': self._model(),
			'form': self._form_class(**self._produce_extra_form_args(self._form_class, request)),
			'submit_path': request.route_path(self.submit_path_route),
			'list_route': self.list_route,
			'page_title': self.page_title or (u"create %s" % unicode(self._model.__name__))
		}

class ListView (CrudView):
	edit_route = None
	new_route = None
	delete_route = None
	page_title = None

	def get_obj_title (self, obj):
		for name in ('title', 'name', 'email'):
			value = getattr(obj, name, None)
			if value:
				return value
		return repr(obj)

	edit_title = get_obj_title

	def __call__ (self, request):
		models = self._model.query.order_by(self._model.id.desc()).all()
		return {
			'models': models,
			'edit_route': self.edit_route,
			'edit_title': self.edit_title,
			'new_route': self.new_route,
			'delete_route': self.delete_route,
			'page_title': self.page_title or (u"%s list" % unicode(self._model.__name__))
		}

	def include_to_config (self, config):
		config.add_route(self.route_name, self.route_path)
		config.add_view(self, route_name = self.route_name, renderer = self.renderer, permission = self.permission)

class DeleteView (CrudView):
	redirect_route = None

	def __call__ (self, request):
		#TODO csrf
		self._model.query.filter_by(id = request.matchdict['id']).delete()
		return HTTPFound(location = request.route_url(self.redirect_route))

	def include_to_config (self, config):
		config.add_route(self.route_name, self.route_path)
		config.add_view(self, route_name = self.route_name, permission = self.permission)

class Crud (object):
	show_in_admin_index = False
	_registered_cruds = []

	model = None
	form = None
	title = None

	new = None
	edit = None
	create = None
	update = None
	list = None
	delete = None

	@classmethod
	def include_to_config (cls, config):
		if cls.show_in_admin_index:
			cls._registered_cruds.append(cls)

		for view_class in (cls.new, cls.edit, cls.create, cls.update, cls.list, cls.delete):
			if view_class:
				view_class(cls.model, cls.form).include_to_config(config)

	@classmethod
	def get_title (cls):
		return cls.title or cls.__name__

class AdminCrud (Crud):
	show_in_admin_index = True

class IndexView (object):
	def __call__ (self, request):
		return {'cruds': Crud._registered_cruds}

def make_view_classes (pathname, db_session_, permission_ = 'admin',
		new = NewView, edit = True, create = True, update = True, list_ = True, delete = True,
		list_route_ = None):
	classes = []

	class CommonParams (object):
		renderer = 'sapyens.crud:templates/admin/edit.mako'
		permission = permission_

	list_route_ = list_route_ or '%s.list' % pathname
	delete_route_ = '%s.delete' % pathname

	if new:
		class New (CommonParams, new):
			route_name = '%s.new' % pathname
			route_path = '/%s/new' % pathname
			submit_path_route = '%s.create' % pathname
			list_route = list_route_
		classes.append(New)

	if edit:
		class Edit (CommonParams, EditView):
			route_name = '%s.edit' % pathname
			route_path = '/%s/edit/{id:\d+}' % pathname
			submit_path_route = '%s.update' % pathname
			list_route = list_route_
		classes.append(Edit)

	if create:
		class Create (CommonParams, CreateView):
			route_name = '%s.create' % pathname
			route_path = '/%s/create' % pathname
			redirect_route = Edit.route_name #TODO !
			list_route = list_route_
			db_session = db_session_
			def _make_GET_redirect_route (self, request):
				return request.route_url(New.route_name)
		classes.append(Create)

	if update:
		class Update (CommonParams, UpdateView):
			route_name = '%s.update' % pathname
			route_path = '/%s/update/{id:\d+}' % pathname
			redirect_route = '%s.edit' % pathname
			list_route = list_route_
			db_session = db_session_
			def _make_GET_redirect_route (self, request):
				return request.route_url(Edit.route_name, id = request.matchdict['id'])
		classes.append(Update)

	if list_:
		class List (CommonParams, ListView):
			renderer = 'sapyens.crud:templates/admin/list.mako'
			route_name = list_route_
			edit_route = Edit.route_name #TODO !
			route_path = '/%s/list' % pathname
			db_session = db_session_
			new_route = New.route_name
			delete_route = delete_route_
		classes.append(List)

	if delete:
		class Delete (CommonParams, DeleteView):
			route_name = delete_route_
			route_path = '/%s/delete/{id:\d+}' % pathname
			redirect_route = list_route_
		classes.append(Delete)

	return classes
