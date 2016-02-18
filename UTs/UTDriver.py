# encoding=utf-8

import unittest
import httpretty

from Roles.Driver import LoginForm, Driver, LoginAgain, LoginFail
from Roles.Role import Role
from Roles.Session import Session
from Roles.CAPTCHARecognizer import CAPTCHAError

__author__ = 'mochenx'


class UTDriver(unittest.TestCase):
    def setUp(self):
        self.shared_session = Session()
        self.driver = Role.get('Driver')
        self.driver.log_path = 'log_utdriver'

    def test_creation_n_properties_of_driver(self):
        self.driver = Role.get('Driver')
        self.assertTrue(hasattr(self.driver, 'drivername'))
        self.assertTrue(hasattr(self.driver, 'password'))
        self.assertTrue(hasattr(self.driver, 'session'))
        self.assertEqual(self.driver.drivername, None)
        self.assertEqual(self.driver.password, None)
        self.assertEqual(self.driver.session, None)
        self.driver.drivername = 'John Doe'
        self.assertEqual(self.driver.drivername, 'John Doe')
        print(self.driver.drivername)
        print(self.driver.password)
        print(self.driver.session)

    def test_load_properties_success(self):
        self.driver.load_properties(drivername='John Smith', password='888888', session=self.shared_session)
        self.assertEqual(self.driver.drivername, 'John Smith')
        self.assertEqual(self.driver.password, '888888')
        self.assertIs(self.driver.session, self.shared_session)

    def test_load_properties_fail(self):

        def _no_drivername():
            self.driver.load_properties(password='888888', session=self.shared_session)

        def _no_password():
            self.driver.load_properties(drivername='John Smith', session=self.shared_session)

        def _no_session():
            self.driver.load_properties(drivername='John Smith', password='888888')

        self.assertRaises(ValueError, _no_drivername)
        self.assertRaises(ValueError, _no_password)
        self.assertRaises(ValueError, _no_session)

    def test_get_login_form(self):
        self.shared_session.set_max_retry(for_url='http://haijia.bjxueche.net/', max_retries=5)
        self.driver.load_properties(drivername='John Smith', password='888888', session=self.shared_session)
        login_form = self.driver._get_login_form()

        self.assertTrue('txtUserName' in login_form)
        self.assertTrue('txtPassword' in login_form)
        self.assertTrue('txtIMGCode' in login_form)
        self.assertEqual(login_form['txtUserName'], 'John Smith')
        self.assertEqual(login_form['txtPassword'], '8'*6)
        self.assertEqual(login_form['txtIMGCode'], None)

    def test_login_again(self):
        def monkey_patch_get_login_form():
            raise TypeError('monkey_patch_get_login_form')
        setattr(self.driver, '_get_login_form', monkey_patch_get_login_form)
        self.assertRaises(LoginAgain, self.driver.login)

    def test_login_retry(self):
        self.retry_cnt = 0
        expect_retry_num = 11
        Driver.login_repeat_times = expect_retry_num

        def monkey_patch_get_net_text():
            self.retry_cnt += 1

        def monkey_patch_get_login_form():
            raise CAPTCHAError('monkey_patch_get_login_form')

        setattr(self.driver, '_get_login_form', monkey_patch_get_login_form)
        setattr(self.driver, '_get_net_text', monkey_patch_get_net_text)
        self.assertRaises(LoginFail, self.driver.login)
        self.assertEquals(expect_retry_num, self.retry_cnt)

    def test_login(self):
        self.shared_session.set_max_retry(for_url='http://haijia.bjxueche.net/', max_retries=5)
        # utdriver_login.txt should contain the following format:
        # username
        # password
        with open('Private files/utdriver_login.txt', 'r') as f:
            s_file = f.read()
            s_lst = s_file.split('\n')
        print(s_lst)
        self.driver.load_properties(drivername=s_lst[0], password=s_lst[1], session=self.shared_session)
        self.assertTrue(self.driver.login())

