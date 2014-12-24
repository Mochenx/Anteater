# encoding=utf-8

import unittest
from Roles.Role import Role, RoleCreatorWithLogger
from Roles.Logger import Logger
from six import with_metaclass

__author__ = 'mochenx'


class UselessSubclassOfRole(with_metaclass(RoleCreatorWithLogger, Role, Logger)):
    index = 0

    def __init__(self, **kwargs):
        super(UselessSubclassOfRole, self).__init__(**kwargs)
        self.index = UselessSubclassOfRole.index
        UselessSubclassOfRole.index += 1

    def get_index(self):
        return self.index

    @classmethod
    def create(cls):
        return UselessSubclassOfRole()


class Grandfather(with_metaclass(RoleCreatorWithLogger, Role, Logger)):

    @classmethod
    def create(cls):
        return Grandfather()


class GrandMother(with_metaclass(RoleCreatorWithLogger, Role, Logger)):

    @classmethod
    def create(cls):
        return GrandMother()


class Father(Grandfather):

    def __init__(self, **kwargs):
        super(Father, self).__init__(**kwargs)

    @classmethod
    def create(cls):
        return Father()


class Son(Father):
    new_property_cnt = 0

    def __init__(self, **kwargs):
        super(Son, self).__init__(**kwargs)

    @classmethod
    def create(cls):
        if cls.new_property('age'):
            cls.new_property_cnt += 1
        if cls.new_property('score'):
            cls.new_property_cnt += 1
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

    def test_new_property(self):
        duts = [Role.get('Son') for _ in range(10)]
        dut = duts[0]
        self.assertTrue(hasattr(dut, 'age'))
        self.assertTrue(hasattr(dut, 'score'))
        self.assertIsNone(dut.age)
        self.assertIsNone(dut.score)
        dut.age = 10
        dut.score = 99
        self.assertEqual(dut.age, 10)
        self.assertEqual(dut.score, 99)
        self.assertEqual(dut._age, 10)
        self.assertEqual(dut._score, 99)
        print('Age: {0}, Score: {1}'.format(dut.age, dut.score))
        dut._age = 11
        dut._score = 98
        self.assertEqual(dut.age, 11)
        self.assertEqual(dut.score, 98)
        print('Age: {0}, Score: {1}'.format(dut.age, dut.score))
        self.assertEqual(dut.new_property_cnt, 2)
        print('new_property in class<Son> has been called {0} times'.format(dut.new_property_cnt))



