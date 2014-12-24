# encoding=utf-8

import unittest
from Roles.Role import Role, RoleCreatorWithLogger
from Roles.Logger import Logger

__author__ = 'mochenx'


class UselessSubclassOfRole(object):
    __metaclass__ = RoleCreatorWithLogger
    index = 0

    def __init__(self):
        super(UselessSubclassOfRole, self).__init__()
        self.index = UselessSubclassOfRole.index
        UselessSubclassOfRole.index += 1

    def get_index(self):
        return self.index

    @classmethod
    def create(cls):
        return UselessSubclassOfRole()


class Grandfather(object):
    __metaclass__ = RoleCreatorWithLogger

    @classmethod
    def create(cls):
        return Grandfather()


class GrandMother(object):
    __metaclass__ = RoleCreatorWithLogger

    @classmethod
    def create(cls):
        return GrandMother()


class Father(Grandfather):

    def __init__(self):
        super(Father, self).__init__()

    @classmethod
    def create(cls):
        return Father()


class Son(Father):
    @classmethod
    def create(cls):
        return Son()


class UTRole(unittest.TestCase):
    def check_subclass_of_role(self, inst, klass):
        print('Checking all attributes of {0} and its instances to ensure '
              'subclassing is done correctly'.format(klass.__name__))
        self.assertTrue(isinstance(inst, klass))
        self.assertTrue(issubclass(klass, Role))
        self.assertTrue(issubclass(klass, Logger))
        self.assertTrue(hasattr(inst, 'debug'))
        self.assertTrue(hasattr(inst, 'logger'))
        self.assertTrue(hasattr(inst, 'set_logger'))

    def test_register(self):
        useless_role = Role.get('UselessSubclassOfRole')
        role0 = Role.get('Grandfather')
        role1 = Role.get('GrandMother')
        role00 = Role.get('Father')
        role000 = Role.get('Son')

        self.check_subclass_of_role(useless_role, UselessSubclassOfRole)
        self.check_subclass_of_role(role0, Grandfather)
        self.check_subclass_of_role(role1, GrandMother)
        self.check_subclass_of_role(role00, Father)
        self.check_subclass_of_role(role000, Son)

    def test_get(self):
        duts = [Role.get('UselessSubclassOfRole') for _ in range(5)]
        for i, dut in enumerate(duts):
            print('Checking the {0} DUT whose index is {1}'.format(i, dut.get_index()))
            self.assertEqual(i, dut.get_index())

