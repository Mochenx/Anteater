# encoding=utf-8

import unittest
import httpretty
import socket
from requests.exceptions import ConnectionError
import time

from Roles.Role import Role
from Roles.Session import Session
from Roles.Timer import WaitingTimer

__author__ = 'mochenx'


class UTWaitingTimer(unittest.TestCase):
    def setUp(self):
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

    def test_get_server_time_timeout_after_retry(self):
        self.dut.home_page_url = 'http://haijia.bjxueche.net:81/'
        self.session.set_max_retry(for_url='http://haijia.bjxueche.net:81/', max_retries=5)

        def _test():
            self.dut.get_server_time()
        start_time = time.time()
        self.assertRaises(ConnectionError, _test)
        delta = time.time() - start_time
        print('Return after {0} seconds because of timeout '.format(delta))
        self.assertGreaterEqual(delta, 20*5)

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
