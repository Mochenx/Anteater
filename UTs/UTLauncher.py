# encoding=utf-8

import unittest
from Roles.Launcher import Launcher
from time import sleep
from datetime import datetime, timedelta


__author__ = 'mochenx'


class UTLauncher(unittest.TestCase):
    def setUp(self):
        self.dut = Launcher(10)

    def do_test_work_done(self, worker_number, last_sec):
        def worker(**kwargs):
            work_done = kwargs['work_done']
            sleep(6)
            print('work ends')
            work_done()

        working_span = timedelta(seconds=last_sec)
        self.dut.load_workers([worker for _ in range(worker_number)])
        start_time = datetime.now()
        self.dut.run()
        end_time = datetime.now()
        obsv_span = end_time - start_time
        self.assertLess(working_span, obsv_span)
        print('----- Test done after {0} seconds -----'.format(obsv_span))

    def test_work_done(self):
        """ One worker, ends after 5 seconds """
        self.do_test_work_done(1, 5)

    def test_work_done_2_workers(self):
        """ Two workers, ends after 5 seconds """
        self.do_test_work_done(2, 5)

    def test_work_done_10_workers(self):
        """ 10 workers, ends after 6 seconds """
        self.do_test_work_done(10, 6)

    def test_work_done_13_workers(self):
        """ 13 workers, ends after 12 seconds. 12 = 6 * (13 % 10) """
        self.do_test_work_done(13, 12)

    def test_work_done_more_workers(self):
        """ 10 workers, ends after 18 seconds. 18 = 6 * (22 % 10) """
        self.do_test_work_done(22, 18)

    def test_work_done_mul_times(self):
        """ One worker, ends after 5 seconds in each round, 9 rounds totally """
        for _ in range(9):
            self.dut = Launcher(10)
            self.do_test_work_done(1, 5)
