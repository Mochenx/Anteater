# encoding=utf-8

import unittest
import json
import pytz
from Roles.Role import Role
from datetime import datetime

# The followings are essential to UTTask, for the reason that no class registering occurs when they're not imported
from Roles.Task import WaitToTimeTask
from Roles.Timer import WaitingTimer
from Roles.Booker import Booker
from Roles.Driver import LoginAgain


class UTTask(unittest.TestCase):
    def setUp(self):
        self.dut = Role.get('WaitToTimeTask')


    def test_creation_n_properties_of_booker(self):
        task_descripton = {
            'timer': ['WaitingTimer', {'set_book_date': 'Jan 01 2017'}],
            'driver': ['Driver', {'drivername': 'mm', 'password': '112233'}],
            'booker': ['Booker', {'time_periods': 'Morning', 'lesson_type': '2'}]
        }
        self.dut.load_properties(**task_descripton)
        print(self.dut)
        self.assertEquals('mm', self.dut.driver.drivername)
        self.assertEquals('112233', self.dut.driver.password)
        self.assertEquals('Morning', self.dut.booker.time_periods)
        self.assertEquals('2', self.dut.booker.lesson_type)

    def test_driver_login(self):
        task_descripton = {
            'timer': ['WaitingTimer', {}],
            'driver': ['Driver', {'drivername': 'mm', 'password': '112233'}],
            'booker': ['Booker', {'time_periods': 'Morning', 'lesson_type': '2'}]
        }
        # utdriver_login.txt should contain the following format:
        # username
        # password
        with open('Private files/utdriver_login.txt', 'r') as f:
            s_file = f.read()
            s_lst = s_file.split('\n')
        task_descripton['driver'][1]['drivername'], task_descripton['driver'][1]['password'] = (s_lst[0], s_lst[1])
        self.dut.load_properties(**task_descripton)
        print(self.dut)

        book_date, _1, _2 = self.dut.timer.calc_date()
        # Step 1, Fail to get cars
        def get_cars():
            self.dut.booker.get_cars(book_date)
        self.assertRaises(Exception, get_cars)
        # Step 2, login successfully
        self.assertTrue(self.dut._driver_login(book_date.strftime('%Y%m%d')))
