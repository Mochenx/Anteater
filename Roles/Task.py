# encoding=utf-8

from datetime import datetime

from six import with_metaclass, text_type
from Roles.Role import RoleCreatorWithLogger, Role, Logger
from Roles.Driver import LoginAgain
from Roles.Session import Session
from Roles.Launcher import Launcher
import random
import time

__author__ = 'mochenx'


class Task(with_metaclass(RoleCreatorWithLogger, Role, Logger)):
    pass

"""
"""


class WaitToTimeTask(Task):
    """{'Task': ['WaitToTimeTask', {
                    'name' : 'some values',
                    'timer': ['WaitingTimer', {'set_book_date': some value}],
                    'driver': ['Driver', {'drivername': some value, 'password': some value}],
                    'booker': ['Booker', {'time_periods': some value, 'lesson_type': some value}]
                }
            ]
        }
        {
            # To Driver
            'drivername': '',
            'password': '',
            # To Timer
            'set_book_date': '',
            # To Booker
            'time_periods': '',
            'lesson_type': '',
        }
    """
    def __init__(self, **kwargs):
        super(WaitToTimeTask, self).__init__(**kwargs)
        # self.session = Role.get('Session')
        self.session = Session()
        self.cars = None
        self.max_thread_number = 10
        self.launcher = Launcher(max_thread_number=self.max_thread_number)

    @classmethod
    def create(cls):
        cls.new_property('timer')
        cls.new_property('driver')
        cls.new_property('booker')
        return WaitToTimeTask()

    def load_properties(self, **kwargs):
        if 'timer' in kwargs and 'driver' in kwargs and 'booker' in kwargs and 'name' in kwargs:
            self.log_path = self.log_file_name = kwargs['name']
            self.timer = self.role_create(kwargs['timer'])
            self.driver = self.role_create(kwargs['driver'])
            self.booker = self.role_create(kwargs['booker'])
        elif self.session is None:
            raise ValueError('Properties timer, driver and booker are needed for class WaitToTimeTask')

    def role_create(self, role_parameters):
        role_name = role_parameters[0]
        loaded_prop = role_parameters[1]
        role = Role.get(role_name)
        role.logger = self.logger
        role.log_path = self.log_path
        role.load_properties(session=self.session, **loaded_prop)
        return role

    def run(self):
        book_date = self.timer.run()
        if not self.driver_login(book_date):
            return False

        self.debug(msg="Login done at {0}".format(datetime.now()), by='WaitToTimeTask.run')

        if not self.get_cars(book_date):
            return False

        if not self.book_cars(book_date):
            return False

    def driver_login(self, date):
        retry_cnt = 10
        while retry_cnt > 0:
            try:
                self.driver.login()
                self.debug(msg="Login done operation has done at {0}".format(datetime.now()),
                           by='WaitToTimeTask.login')
                try:
                    # We try to get car information is to make sure it has logged in successfully
                    self.cars = self.booker.get_cars(date)
                    break
                except Exception as e:
                    self.debug(msg=u"Raise LoginAgain for the reason that "
                                   u"something wrong in get_cars at time: {0}".format(datetime.now()),
                               by=u'WaitToTimeTask.login')
                    self.debug(msg=text_type(e), by=u'WaitToTimeTask.login')
                    raise LoginAgain()
            except LoginAgain:
                if retry_cnt == 0:
                    return False
                retry_cnt -= 1
                time.sleep(random.randrange(100, 150)/100)
                continue

        return True

    def get_cars(self, book_date):
        """ Launch bookings simultaneously here """
        retry_cnt = 20
        while retry_cnt > 0:
            try:
                self.cars = self.booker.get_cars(book_date)
                return True
            except Exception as e:
                self.debug(msg=u"Exception occurs when getting CARS, try to get again", by='WaitToTimeTask.run')
                self.debug(msg=text_type(e), by='WaitToTimeTask.run')
                if retry_cnt == 0:
                    return False
                retry_cnt -= 1
                time.sleep(random.randrange(25, 100)/100)
                continue

    def book_cars(self, book_date):
        """ Launch bookings simultaneously here """
        retry_cnt = 20
        while retry_cnt > 0:
            try:
                self.burst_booking()
                if self.booker.get_booking_status(book_date):
                    return True
            except Exception as e:
                self.debug(msg=u"Exception occurs when BOOKING, try to get again", by='WaitToTimeTask.run')
                self.debug(msg=text_type(e), by='WaitToTimeTask.run')
                if retry_cnt == 0:
                    return False
                retry_cnt -= 1
                time.sleep(random.randrange(50, 100)/100)
                continue

    def burst_booking(self):
        """ Randomly choose some cars, then call Launcher's run method to book them simultaneously  """
        worker_num = self.max_thread_number + 5
        if len(self.cars) <= worker_num:
            workers = self.cars
        else:
            workers = [random.choice(self.cars) for _ in range(worker_num)]
        self.launcher.load_workers(workers)
        self.launcher.run()

    def __str__(self):
        task_description = 'WaitToTimeTask:\n'
        task_description += str(self.timer) + '\n'
        task_description += str(self.driver) + '\n'
        task_description += str(self.booker)
        return task_description
