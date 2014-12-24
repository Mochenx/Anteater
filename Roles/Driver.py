# encoding=utf-8

from Roles.Role import RoleCreatorWithLogger

__author__ = 'mochenx'


class Driver(object):
    __metaclass__ = RoleCreatorWithLogger

    def __init__(self, **kwargs):
        super(Driver, self).__init__(**kwargs)

    @classmethod
    def create(cls):
        cls.new_property('drivername')
        cls.new_property('password')
        cls.new_property('session')
        return Driver()

    def load_properties(self, **kwargs):
        if 'drivername' in kwargs and 'password' in kwargs and 'session' in kwargs:
            self.drivername = kwargs['drivername']
            self.password = kwargs['password']
            self.session = kwargs['session']
        else:
            raise ValueError('Properties drivername, password and session are needed for class Driver')
