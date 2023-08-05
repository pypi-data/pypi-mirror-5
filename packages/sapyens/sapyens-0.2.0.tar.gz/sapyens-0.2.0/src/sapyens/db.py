import logging
from contextlib import contextmanager
import collections
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection
from sqlalchemy.orm import scoped_session, sessionmaker, class_mapper
#NOTE conditional zope.sqlalchemy import in make_classes() below
#NOTE pyramid.httpexceptions.HTTPNotFound import in notfound_tween_factory() below


@contextmanager
def engine_log_level (level):
	db_logger = logging.getLogger('sqlalchemy.engine')
	old_level = db_logger.level

	db_logger.level = level
	try:
		yield
	finally:
		db_logger.level = old_level


class NotFound (Exception):
	pass

Base = declarative_base(cls = DeferredReflection)

class Reflected (Base):
	__abstract__ = True

	def __repr__ (self):
		return u"<{module}.{class_name} #{id}>".format(
			module = self.__class__.__module__,
			class_name = self.__class__.__name__,
			id = self.id,
		)

	@classmethod
	def try_get (cls, id = None, **kwargs):
		if id:
			kwargs['id'] = id
			
		obj = cls.query.filter_by(**kwargs).first()
		if obj:
			return obj
		else:
			raise NotFound()

	def set (self, **fields):
		for name, value in fields.items():
			setattr(self, name, value)
		return self


def notfound_tween_factory (handler, _registry):
	from pyramid.httpexceptions import HTTPNotFound

	def tween (request):
		try:
			response = handler(request)
		except NotFound:
			raise HTTPNotFound()

		return response
	return tween


def make_classes (use_zope_ext = True):
	if use_zope_ext:
		from zope.sqlalchemy import ZopeTransactionExtension

	DBSession = scoped_session(sessionmaker(
		extension = ZopeTransactionExtension() if use_zope_ext else None
	))

	class QueryPropertyMixin (object):
		query = DBSession.query_property()

	class ScopedSessionMixin (object):
		def add (self):
			DBSession.add(self)
			return self

		def delete (self):
			DBSession.delete(self)
			return self

		def flush (self):
			DBSession.flush()
			return self

		def commit (self):
			DBSession.commit()
			return self

	return collections.namedtuple('Classes', ('DBSession', 'QueryPropertyMixin', 'ScopedSessionMixin'))(
		DBSession, QueryPropertyMixin, ScopedSessionMixin
	)

def init (engine, DBSession, Reflected, on_before_reflect = None, import_before_reflect = None, enable_setattr_check = False):
	Reflected.metadata.bind = engine

	DBSession.configure(bind = engine)

	if import_before_reflect:
		__import__(import_before_reflect)

	if on_before_reflect:
		on_before_reflect()

	with engine_log_level(logging.WARN):
		# if you for example use some table as relationship secondary parameter and the table is not
		# reflected yet, you will get an error, so reflect in advance:
		Reflected.metadata.reflect()
		
		Reflected.prepare(engine)

	if enable_setattr_check:
		init_setattr_check(Reflected)


class SetattrCheckError (Exception):
	pass

def init_setattr_check (Reflected):
	def __setattr__ (self, name, value):
		skip_check = getattr(Reflected, '__skip_setattr_check', False)
		if name != '_sa_instance_state' and not skip_check:
			is_name_ok = any(name == prop.key for prop in class_mapper(self.__class__).iterate_properties)
			if not is_name_ok:
				raise SetattrCheckError("Attempt to set a property that is not registered with "
					"the mapper (did you make a typo?): %s" % name)
		super(Reflected, self).__setattr__(name, value)
	Reflected.__setattr__ = __setattr__

	orig_new = Reflected.__new__
	def __new__ (cls, *args, **kwargs):
		orig_init = cls.__init__
		def __init__ (self, *args, **kwargs):
			Reflected.__skip_setattr_check = True
			orig_init(self, *args, **kwargs)
			del Reflected.__skip_setattr_check
		cls.__init__ = __init__

		obj = orig_new(cls, *args, **kwargs)
		cls.__init__ = orig_init

		return obj
	Reflected.__new__ = staticmethod(__new__)