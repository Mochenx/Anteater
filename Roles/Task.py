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
    HJ_book_time = {'hour': 7, 'minute': 35, 'second': 0, 'microsecond': 0}

    def __init__(self, **kwargs):
        super(WaitToTimeTask, self).__init__(**kwargs)
        # self.session = Role.get('Session')
        self.session = Session()
        self.cars = None
        self.max_thread_number = 10
        self.launcher = None
        self.retry_times = 20

    @classmethod
    def create(cls):
        cls.new_property('timer')
        cls.new_property('driver')
        cls.new_property('booker')
        return WaitToTimeTask()

    def load_properties(self, **kwargs):
        if 'timer' in kwargs and 'driver' in kwargs and 'booker' in kwargs and 'name' in kwargs:
            self.log_path = self.log_file_name = kwargs['name']
            self.session.logger = self.logger

            self.timer = self.role_create(kwargs['timer'])
            self.driver = self.role_create(kwargs['driver'])
            self.booker = self.role_create(kwargs['booker'])
        elif self.session is None:
            raise ValueError('Properties timer, driver and booker are needed for class WaitToTimeTask')

        if 'retry_times' in kwargs:
            self.retry_times = kwargs['retry_times'] if isinstance(kwargs['retry_times'], int) else \
                int(kwargs['retry_times'])

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

        self.t_minus()

        if not self.book_cars(book_date):
            return False

    def driver_login(self, date):
        retry_cnt = 30
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
                time.sleep(random.randrange(200, 500)/100)
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

    def t_minus(self):
        loc_time = self.timer.get_server_time()
        book_time = loc_time.replace(**self.HJ_book_time)
        if book_time < loc_time:
            return
        t_minus = book_time - loc_time
        t_minus = t_minus.seconds + 1  # 1 more second
        self.debug(msg=u"T-Minus: {0} at {1}".format(t_minus, datetime.now()), by='WaitToTimeTask.t_minus')
        time.sleep(t_minus)
        self.debug(msg=u"T-Minus: Go at {0}".format(datetime.now()), by='WaitToTimeTask.t_minus')

    def book_cars(self, book_date):
        """ Launch bookings simultaneously here """
        retry_cnt = self.retry_times
        while retry_cnt > 0:
            try:
                self.burst_booking()
                if self.booker.get_booking_status(book_date):
                    self.debug(msg=u"Success to book cars", by='WaitToTimeTask.run')
                    return True
            except Exception as e:
                self.debug(msg=u"Exception occurs when BOOKING, try to get again", by='WaitToTimeTask.run')
                self.debug(msg=text_type(e), by='WaitToTimeTask.run')

            if retry_cnt == 0:
                self.debug(msg=u"Quit to book cars", by='WaitToTimeTask.run')
                return False
            retry_cnt -= 1
            time.sleep(random.randrange(300, 700)/100)
            self.debug(msg=u"Retry to book again, {0} times left".format(retry_cnt), by='WaitToTimeTask.run')
            continue

    def burst_booking(self):
        """ Randomly choose some cars, then call Launcher's run method to book them simultaneously  """
        self.launcher = Launcher(max_thread_number=self.max_thread_number)

        worker_num = self.max_thread_number + 5
        if len(self.cars) <= worker_num:
            workers = self.cars
        else:
            cars_after_rand = self.cars
            random.shuffle(cars_after_rand)
            workers = cars_after_rand[: worker_num]
        self.debug(msg=u"Start to book {0} cars simultaneously".format(len(workers)),
                   by='WaitToTimeTask.run')
        self.launcher.load_workers(workers)
        self.launcher.run()

    def __str__(self):
        task_description = 'WaitToTimeTask:\n'
        task_description += str(self.timer) + '\n'
        task_description += str(self.driver) + '\n'
        task_description += str(self.booker)
        return task_description
