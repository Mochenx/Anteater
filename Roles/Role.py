# encoding=utf-8

from Roles.Logger import Logger

__author__ = 'mochenx'


class Role(object):
    registered_cls = {}

    @classmethod
    def new_property(cls, property_name):
        if hasattr(cls, property_name):
            return False
        inner_name = '_' + property_name

        def _getter(obj):
            if not hasattr(obj, inner_name):
                setattr(obj, inner_name, None)
            return getattr(obj, inner_name)

        def _setter(obj, val):
            if not hasattr(obj, inner_name):
                setattr(obj, inner_name, None)
            setattr(obj, inner_name, val)

        setattr(cls, property_name, property(fget=_getter, fset=_setter))
        return True

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)

    @classmethod
    def get(cls, name):
        klass = cls.registered_cls[name]
        return klass.create()

    @classmethod
    def register_self(cls, klass):
        if not issubclass(klass, Role):
            raise TypeError('Registered class should be a subclass of Role, instead of {0}'.format(type(klass)))
        cls.registered_cls[klass.__name__] = klass

    def create(self):
        raise NotImplementedError('Method "create" must be overrided in subclass of Role')


class RoleCreatorWithLogger(type):
    """
        The Meta-class for creating subclass of Role, we can customize subclass dynamically.
    """
    def __new__(mcs, name, bases, class_dict):
        result = type.__new__(mcs, name, bases, dict(class_dict))
        result.register_self(result)
        return result
