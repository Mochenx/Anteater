# encoding=utf-8

import unittest
import httpretty
import socket
from requests.exceptions import ConnectionError
import time
from datetime import datetime, timedelta

from Roles.Role import Role
from Roles.Session import Session, URLsForHJ
from Roles.Timer import WaitingTimer, BookNowTimer

__author__ = 'mochenx'


class UTWaitingTimer(unittest.TestCase):
    def setUp(self):
        URLsForHJ.connect = 'http://haijia.bjxueche.net'
        self.session = Session()
        self.session.set_max_retry(for_url='http://haijia.bjxueche.net/', max_retries=10)
        self.dut = Role.get('WaitingTimer')
        self.dut.load_properties(session=self.session)

    @httpretty.activate
    def test_get_server_time(self):

        httpretty.register_uri(httpretty.GET, 'http://haijia.bjxueche.net/',
                               body='Mock, Post succeed',
                               forcing_headers={'date': 'Fri, 26 Dec 2014 14:59:41 GMT'})
        loc_time = self.dut.get_server_time()
        self.assertEqual('2014-12-26 22:59:41+08:00', str(loc_time))

    @httpretty.activate
    def test_get_server_time_2(self):
        httpretty.register_uri(httpretty.GET, "http://haijia.bjxueche.net/",
                               Date='Mon, 15 Dec 2014 16:58:19 GMT')
        loc_time = self.dut.get_server_time()
        self.assertEqual(loc_time.day, 16)
        self.assertEqual(loc_time.hour, 0)
        self.assertEqual(loc_time.minute, 58)
        httpretty.register_uri(httpretty.GET, "http://haijia.bjxueche.net/",
                               Date='Mon, 15 Dec 2014 17:08:20 GMT')
        loc_time = self.dut.get_server_time()
        self.assertEqual(loc_time.day, 16)
        self.assertEqual(loc_time.hour, 1)
        self.assertEqual(loc_time.minute, 8)

    @httpretty.activate
    def test_get_server_time_with_retry(self):
        self.retry_cnt = 0

        def _retry(request, uri, headers):
            if self.retry_cnt == 9:
                print('Round:{0}, Response'.format(self.retry_cnt))
                return 200, headers, 'Mock, Connection succeed'
            else:
                print('Round:{0}, Timeout'.format(self.retry_cnt))
                self.retry_cnt += 1
                raise socket.timeout()
        httpretty.register_uri(httpretty.GET, 'http://haijia.bjxueche.net/',
                               body=_retry,
                               forcing_headers={'date': 'Fri, 26 Dec 2014 14:59:41 GMT'})

        loc_time = self.dut.get_server_time()
        self.assertEqual('2014-12-26 22:59:41+08:00', str(loc_time))
        self.assertEqual(self.retry_cnt, 9)

    def test_localize_date(self):
        fmt01 = self.dut.localize_date('Jan 01 2017')
        fmt02 = self.dut.localize_date('2017-01-01')
        fmt03 = self.dut.localize_date('20170101')
        self.assertEquals(fmt01, fmt02)
        self.assertEquals(fmt02, fmt03)

    def test_get_server_time_timeout_after_retry(self):
        URLsForHJ.connect = 'http://haijia.bjxueche.net:81'
        self.session.set_max_retry(for_url='http://haijia.bjxueche.net:81/', max_retries=5)

        def _test():
            self.dut.get_server_time()
        start_time = time.time()
        self.assertRaises(ConnectionError, _test)
        delta = time.time() - start_time
        print('Return after {0} seconds because of timeout '.format(delta))
        self.assertGreaterEqual(delta, 20*5)

    def offset_n_minutes(self, current_time, func_get_offset_minute):
        self.dut.debut_hour = current_time.hour + func_get_offset_minute(current_time.minute)//60
        self.dut.debut_minute = func_get_offset_minute(current_time.minute) % 60

    def test_get_book_time_today(self):
        """
            Don't set book date, DUT set it 7 days later automatically, and gives the wake-up time as 3 minutes later
        """
        loc_time = datetime.now()
        self.offset_n_minutes(loc_time, func_get_offset_minute=lambda e: e + 3)
        book_time = self.dut.get_debut_time(loc_time)
        self.assertEqual(book_time.day, loc_time.day)
        self.assertEqual(book_time.hour, self.dut.debut_hour)
        self.assertEqual(book_time.minute, self.dut.debut_minute)

    def test_get_book_time_today_set(self):
        """
            Set book date to 7 days later , and DUT gives the wake-up time as 3 minutes later
        """
        seven_days = timedelta(days=7)
        loc_time = datetime.now()
        self.offset_n_minutes(loc_time, func_get_offset_minute=lambda e: e + 3)
        self.dut.set_book_date = loc_time + seven_days
        book_time = self.dut.get_debut_time(loc_time)
        self.assertEqual(book_time.day, loc_time.day)
        self.assertEqual(book_time.hour, self.dut.debut_hour)
        self.assertEqual(book_time.minute, self.dut.debut_minute)

    def test_get_book_time_later_equal_tomorrow_set(self):
        """
            Set book date to 8 and 9 days later , and DUT gives the wake-up time as 3 minutes later at some day
        """
        for i in range(2):
            print('Round {0}'.format(i))
            eight_days = timedelta(days=8+i)
            loc_time = datetime.now()
            self.offset_n_minutes(loc_time, func_get_offset_minute=lambda e: e + 3)
            self.dut.set_book_date = loc_time + eight_days
            book_time = self.dut.get_debut_time(loc_time)
            wake_up_date = loc_time + timedelta(days=1+i)
            self.assertEqual(book_time.day, wake_up_date.day)
            self.assertEqual(book_time.hour, self.dut.debut_hour)
            self.assertEqual(book_time.minute, self.dut.debut_minute)

    def test_get_book_time_tomorrow(self):
        """
            Don't set book date, DUT set it 8 days later automatically,
            and gives the wake-up time at tomorrow
        """
        loc_time = datetime.now()
        self.offset_n_minutes(loc_time, func_get_offset_minute=lambda e: e - 3)
        book_time = self.dut.get_debut_time(loc_time)
        print('Wake up at {0}'.format(str(book_time)))
        wake_up_date = loc_time + timedelta(days=1)
        self.assertEqual(book_time.day, wake_up_date.day)
        self.assertEqual(book_time.hour, self.dut.debut_hour)
        self.assertEqual(book_time.minute, self.dut.debut_minute)

    def test_get_book_time_tomorrow_set(self):
        """
            Set book date to 1~8 days later , and DUT gives the wake-up time as tomorrow
        """
        for i in range(8):
            _7_8_days = timedelta(days=1+i)
            loc_time = datetime.now()
            self.offset_n_minutes(loc_time, func_get_offset_minute=lambda e: e - 3)
            self.dut.set_book_date = loc_time + _7_8_days
            print('Round {0}: want {1} in {2}'.format(i, str(self.dut.set_book_date), str(_7_8_days)))
            book_time = self.dut.get_debut_time(loc_time)
            print('Wake up at {0}'.format(str(book_time)))
            wake_up_date = loc_time + timedelta(days=1)
            self.assertEqual(book_time.day, wake_up_date.day)
            self.assertEqual(book_time.hour, self.dut.debut_hour)
            self.assertEqual(book_time.minute, self.dut.debut_minute)

    def test_get_book_time_later_than_tomorrow_set(self):
        """
            Set book date to 9~11 days later , and DUT gives the wake-up time as tomorrow
        """
        for i in range(3):
            _7_8_days = timedelta(days=9+i)
            loc_time = datetime.now()
            self.offset_n_minutes(loc_time, func_get_offset_minute=lambda e: e - 3)
            self.dut.set_book_date = loc_time + _7_8_days
            print('Round {0}: want {1} in {2}'.format(i, str(self.dut.set_book_date), str(_7_8_days)))
            book_time = self.dut.get_debut_time(loc_time)
            print('Wake up at {0}'.format(str(book_time)))
            wake_up_date = loc_time + timedelta(days=2+i)
            self.assertEqual(book_time.day, wake_up_date.day)
            self.assertEqual(book_time.hour, self.dut.debut_hour)
            self.assertEqual(book_time.minute, self.dut.debut_minute)

    def test_get_sleep_span_0(self):
        loc_time = self.dut.get_server_time()
        book_time = loc_time.replace(second=(loc_time.second + 30) % 60,
                                     minute=loc_time.minute + (loc_time.second + 30) // 60)

        self.assertEqual(0, self.dut.get_sleep_span(book_time, loc_time))

    def test_get_sleep_span_50s_tc0(self):
        loc_time = self.dut.get_server_time()
        book_time = loc_time.replace(minute=(loc_time.minute + 1) % 60,
                                     hour=loc_time.hour + (loc_time.minute + 1) // 60)

        self.assertLessEqual(self.dut.get_sleep_span(book_time, loc_time), 50)

    def test_get_sleep_span_50s_tc1(self):
        loc_time = self.dut.get_server_time()
        book_time = loc_time.replace(minute=(loc_time.minute + 3) % 60,
                                     hour=loc_time.hour + (loc_time.minute + 3) // 60)

        self.assertEqual(50, self.dut.get_sleep_span(book_time, loc_time))

    def test_get_sleep_span_10m_tc0(self):
        loc_time = self.dut.get_server_time()
        book_time = loc_time.replace(minute=(loc_time.minute + 10) % 60,
                                     hour=loc_time.hour + (loc_time.minute + 10) // 60)

        self.assertEqual(50, self.dut.get_sleep_span(book_time, loc_time))

    def test_get_sleep_span_10m_tc1(self):
        loc_time = self.dut.get_server_time()
        book_time = loc_time.replace(minute=(loc_time.minute + 15) % 60,
                                     hour=loc_time.hour + (loc_time.minute + 15) // 60)

        self.assertEqual(600, self.dut.get_sleep_span(book_time, loc_time))

    def test_get_sleep_span_10m_tc2(self):
        loc_time = self.dut.get_server_time()
        book_time = loc_time.replace(minute=(loc_time.minute + 11) % 60,
                                     hour=loc_time.hour + (loc_time.minute + 11) // 60)

        self.assertEqual(50, self.dut.get_sleep_span(book_time, loc_time))

    def test_get_book_date_auto(self):
        _7_days = timedelta(days=7)
        loc_time = datetime.now()
        book_date = self.dut.get_book_date(loc_time)
        expt_date = loc_time + _7_days
        self.assertEqual(expt_date.year, book_date.year)
        self.assertEqual(expt_date.month, book_date.month)
        self.assertEqual(expt_date.day, book_date.day)

    def test_get_book_date_set(self):
        _9_days = timedelta(days=9)
        loc_time = datetime.now()
        self.offset_n_minutes(loc_time, func_get_offset_minute=lambda e: e - 3)
        expt_date = loc_time + _9_days
        self.dut.set_book_date = expt_date
        book_date = self.dut.get_book_date(loc_time)
        self.assertEqual(expt_date.year, book_date.year)
        self.assertEqual(expt_date.month, book_date.month)
        self.assertEqual(expt_date.day, book_date.day)

    def to_test_run_common(self, func_get_book_minute, delay=None):
        server_time = self.dut.get_server_time()
        self.offset_n_minutes(server_time, func_get_book_minute)

        if delay is not None:
            time.sleep(delay)
        self.dut.run()
        return self.dut, server_time

    def test_run_tc0(self):
        dut, server_time = self.to_test_run_common(lambda e: e + 1)
        wait_end_time = dut.get_server_time()
        self.assertTrue(wait_end_time - server_time < timedelta(seconds=50))

    def test_run_tc1(self):
        dut, server_time = self.to_test_run_common(lambda e: e + 1, delay=10)
        wait_end_time = dut.get_server_time()
        self.assertTrue(wait_end_time - server_time < timedelta(seconds=50))

    def test_run_tc2(self):
        dut, server_time = self.to_test_run_common(lambda e: e + 3)
        wait_end_time = dut.get_server_time()
        self.assertTrue(wait_end_time - server_time > timedelta(seconds=100))

    def test_run_tc3(self):
        dut, server_time = self.to_test_run_common(lambda e: e + 4)
        wait_end_time = dut.get_server_time()
        self.assertGreaterEqual(wait_end_time - server_time, timedelta(minutes=2))

    def test_book_now_0(self):
        dut_book_now = BookNowTimer()
        dut_book_now.load_properties(session=self.session, set_book_date='Jan 1 2020')
        loc_time = dut_book_now.get_server_time()
        book_time = dut_book_now.run()
        wait_end_time = dut_book_now.get_server_time()

        self.assertLess(wait_end_time - loc_time, timedelta(seconds=1))
