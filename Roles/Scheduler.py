# encoding=utf-8

from six import with_metaclass
from Roles.Role import RoleCreatorWithLogger, Role, Logger
import json
import sqlite3

__author__ = 'mochenx'


class Scheduler(with_metaclass(RoleCreatorWithLogger, Role, Logger)):
    """
        A class to read task description(YAML format) and save it in Sqlite DB.

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

        Table in DB
        Schedule-Date text, Description text(JSON format)
    """

    name_converter = {'when': 'timer', 'who': 'driver', 'what': 'booker'}

    def __init__(self, **kwargs):
        super(Scheduler, self).__init__(**kwargs)

    def read_tasks(self):
        task_descriptions = self.load_yaml()
        self.convert_names(task_descriptions)

    def load_yaml(self, file_name):
        pass

    def convert_names(self, task_descriptions):
        assert isinstance(task_descriptions, list)
        for task in task_descriptions:
            properties = task[-1]
            for key in properties.keys():
                if key in self.name_converter.keys():
                    properties[self.name_converter[key]] = properties[key]
                    del properties[key]

    def analyze_tasks(self, task_descriptions):
        for description in task_descriptions:
            name, properties = description[0], description[-1]
            task = Role.get(name)
            task.load_properties(properties)
            task.timer.schedule_date
