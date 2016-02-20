# encoding=utf-8

import unittest
import json
import pytz
from Roles.Role import Role
from datetime import datetime, timedelta

# The followings are essential to UTTask, for the reason that no class registering occurs when they're not imported
from Roles.Task import WaitToTimeTask
from Roles.Timer import WaitingTimer
from Roles.Booker import Booker
from Roles.Driver import LoginAgain


class UTTask(unittest.TestCase):
    def setUp(self):
        self.dut = Role.get('WaitToTimeTask')
        self.dut.HJ_book_time = {'hour': 7, 'minute': 35, 'second': 0, 'microsecond': 0}


    def test_creation_n_properties_of_booker(self):
        task_descripton = {
            'name': 'creation_n_properties_of_booker', 'retry_times': '3',
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
        self.assertEquals(3, self.dut.retry_times)

    def test_driver_login(self):
        task_descripton = {
            'name': 'driver_login',
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
        self.assertTrue(self.dut.driver_login(book_date.strftime('%Y%m%d')))

    def test_t_minus(self):
        task_descripton = {
            'name': 't_minus', 'retry_times': '3',
            'timer': ['WaitingTimer', {'set_book_date': 'Jan 01 2017'}],
            'driver': ['Driver', {'drivername': 'mm', 'password': '112233'}],
            'booker': ['Booker', {'time_periods': 'Morning', 'lesson_type': '2'}]
        }
        self.dut.load_properties(**task_descripton)

        loc_time = self.dut.timer.get_server_time()
        book_time = loc_time + timedelta(minutes=1)
        book_time = book_time.replace(second=1, microsecond=0)
        print(loc_time)
        print(book_time)
        self.dut.HJ_book_time['hour'] = book_time.hour
        self.dut.HJ_book_time['minute'] = book_time.minute
        before = datetime.now()
        self.dut.t_minus()
        after = datetime.now()
        time_t_minus = after - before
        print(time_t_minus.seconds)
        self.assertLessEqual(time_t_minus.seconds, 61)
        self.assertGreaterEqual(time_t_minus.seconds, 1)
