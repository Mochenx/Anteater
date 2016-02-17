# encoding=utf-8

from datetime import datetime

from six import with_metaclass
from Roles.Role import RoleCreatorWithLogger, Role, Logger
from Roles.Driver import LoginAgain
from Roles.Session import Session

__author__ = 'mochenx'


class Task(with_metaclass(RoleCreatorWithLogger, Role, Logger)):
    pass

"""
"""


class WaitToTimeTask(Task):
    """{'Task': ['WaitToTimeTask', {
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

    @classmethod
    def create(cls):
        cls.new_property('timer')
        cls.new_property('driver')
        cls.new_property('booker')
        return WaitToTimeTask()

    def load_properties(self, **kwargs):
        if 'timer' in kwargs and 'driver' in kwargs and 'booker' in kwargs:
            self.timer = self.role_create(kwargs['timer'])
            self.driver = self.role_create(kwargs['driver'])
            self.booker = self.role_create(kwargs['booker'])
        elif self.session is None:
            raise ValueError('Properties timer, driver and booker are needed for class WaitToTimeTask')

    def role_create(self, role_parameters):
        role_name = role_parameters[0]
        loaded_prop = role_parameters[1]
        role = Role.get(role_name)
        role.load_properties(session=self.session, **loaded_prop)
        return role

    def run(self):
        book_date = self.timer.run()
        self._driver_login(book_date)

        self.debug(msg="Login done at {0}".format(datetime.now()), by='WaitToTimeTask.run')
        print("Login done at {0}".format(datetime.now()))
        try_cnt = 0
        while True:
            try:
                # Launch bookings simultaneously here
                self.cars = self.booker.get_cars(book_date)
                try_cnt += 1
                if try_cnt == 50:
                    return
                elif try_cnt > 0 and try_cnt % 10 == 0 and self.booker.get_booking_status(book_date):
                    return
            except LoginAgain:
                print("Exception occurs, try to login again")
                self.debug(msg="Exception occurs, try to login again", by='WaitToTimeTask.run')
                self._driver_login()
                print("Login done")
                self.debug(msg="Login done", by='WaitToTimeTask.run')
                continue

    def _driver_login(self, date):
        while True:
            try:
                self.driver.login()
                self.debug(msg="Login done operation has done at {0}".format(datetime.now()),
                           by='WaitToTimeTask.login')
                try:
                    # We try to get car information is to make sure it has logged in successfully
                    self.cars = self.booker.get_cars(date)
                except Exception as e:
                    self.debug(msg="Raise LoginAgain for the reason that "
                                   "something wrong in get_cars at time: {0}".format(datetime.now()),
                               by='WaitToTimeTask.login')
                    raise LoginAgain()
                break
            except LoginAgain:
                continue
        return True

    def __str__(self):
        task_description = 'WaitToTimeTask:\n'
        task_description += str(self.timer) + '\n'
        task_description += str(self.driver) + '\n'
        task_description += str(self.booker)
        return task_description
