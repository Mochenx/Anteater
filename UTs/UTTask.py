# encoding=utf-8

import unittest
import json
import pytz
from Roles.Role import Role
from datetime import datetime
from Roles.Task import WaitToTimeTask
from Roles.Timer import WaitingTimer
from Roles.Booker import Booker


class UTTask(unittest.TestCase):
    def setUp(self):
        self.dut = Role.get('WaitToTimeTask')

    def set_book_date(self, naive_date):
        tz_beijing = pytz.timezone('Asia/Shanghai')
        return tz_beijing.localize(naive_date)

    def test_creation_n_properties_of_booker(self):
        task_descripton = {
            'timer': ['WaitingTimer', {'set_book_date': self.set_book_date(datetime.strptime('20160222', '%Y%m%d'))}],
            'driver': ['Driver', {'drivername': 'mm', 'password': '840430'}],
            'booker': ['Booker', {'time_periods': 'Morning', 'lesson_type': '2'}]
        }
        self.dut.load_properties(**task_descripton)
        print(self.dut)
