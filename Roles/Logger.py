# encoding=utf-8

import logging

__author__ = 'mochenx'


class Logger(object):
    def __init__(self):
        self._logger = None
        self.log_file_name = 'DefaultLogger'

    def set_logger(self, name):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        file_handler = logging.FileHandler(name + '.log', mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('::%(name)s - %(source)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        # add the handlers to logger
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    @property
    def logger(self):
        if self._logger is None:
            self.set_logger(self.log_file_name)
        return self._logger

    @logger.setter
    def logger(self, val):
        self._logger = val

    def debug(self, msg, by):
        self.logger.debug(msg, extra={'source': by})
