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


class UTTask(unittest.TestCase):
    def setUp(self):
        self.dut = Role.get('WaitToTimeTask')


    def test_creation_n_properties_of_booker(self):
        task_descripton = {
            'timer': ['WaitingTimer', {'set_book_date': WaitingTimer.localize_date('Jan 01 2017')}],
            'driver': ['Driver', {'drivername': 'mm', 'password': '112233'}],
            'booker': ['Booker', {'time_periods': 'Morning', 'lesson_type': '2'}]
        }
        self.dut.load_properties(**task_descripton)
        print(self.dut)
        self.assertEquals('mm', self.dut.driver.drivername)
        self.assertEquals('112233', self.dut.driver.password)
        self.assertEquals('Morning', self.dut.booker.time_periods)
        self.assertEquals('2', self.dut.booker.lesson_type)
