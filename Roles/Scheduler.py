# encoding=utf-8

from six import with_metaclass
from Roles.Role import RoleCreatorWithLogger, Role, Logger

__author__ = 'mochenx'


class Scheduler(with_metaclass(RoleCreatorWithLogger, Role, Logger)):
    """
        A class to convert task description(YAML format) to list of task callings.

        YAML
        - - WaitToTimeTask
          - name : some values
            when:
            - WaitingTimer
            - lesson_date: some value
            who:
            - Driver
            - drivername: some value
              password: some value
            what:
            - Booker
            - time_periods: some value
              lesson_type: some value
        - - WaitToTimeTask
          - name : some values
            timer:
            - WaitingTimer
            ......

        JSON
        [
            ['WaitToTimeTask', {
                'name' : 'some values',
                'timer': ['WaitingTimer', {'lesson_date': some value}],
                'driver': ['Driver', {'drivername': some value, 'password': some value}],
                'booker': ['Booker', {'time_periods': some value, 'lesson_type': some value}]
            }],
            ['WaitToTimeTask', {
                'name' : 'some values',
                'timer': ['WaitingTimer', ...
                ......
        ]
    """
    def __init__(self, **kwargs):
        super(Scheduler, self).__init__(**kwargs)
