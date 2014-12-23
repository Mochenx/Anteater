# encoding=utf-8

import unittest
import httpretty
import socket
import time
from Roles.Session import Session, URLsForHJ
from requests.exceptions import Timeout, RequestException, ConnectionError, HTTPError

__author__ = 'mochenx'


class UTSession(unittest.TestCase):
    def setUp(self):
        self.dut = Session()
        self.dut.log_file_name = 'UTSession'


    @httpretty.activate
    def _do_success(self, do_func):
        httpretty.register_uri(httpretty.GET, 'http://haijia.bjxueche.net/',
                               body='Mock, Connection succeed')
        body = do_func()
        self.assertEqual(body, 'Mock, Connection succeed')

    def _do_failed(self, do_func):
        self.assertRaises(ConnectionError, do_func)

    @httpretty.activate
    def _do_with_retry(self, do_func):
        self.retry_cnt = 0

        def _retry(request, uri, headers):
            if self.retry_cnt == 5:
                return 200, headers, 'Mock, Connection succeed'
            else:
                self.retry_cnt += 1
                raise socket.timeout()

        httpretty.register_uri(httpretty.GET, 'http://haijia.bjxueche.net/', body=_retry)
        self.dut.set_max_retry(for_url='http://haijia.bjxueche.net/', max_retries=6)
        body = do_func()
        self.assertEqual(body, 'Mock, Connection succeed')
        self.assertEqual(self.retry_cnt, 5)

    @httpretty.activate
    def _do_retried_but_failed(self, do_func):
        self.retry_cnt = 0

        def _retry(request, uri, headers):
            self.retry_cnt += 1
            raise socket.timeout()

        httpretty.register_uri(httpretty.GET, 'http://haijia.bjxueche.net/', body=_retry)
        self.dut.set_max_retry(for_url='http://haijia.bjxueche.net/', max_retries=10)
        self.assertRaises(ConnectionError, do_func)
        self.assertEqual(self.retry_cnt, 11)

    def test_connect_success(self):
        def _connect():
            resp = self.dut.connect()
            print(resp.content)
            return resp.content
        self._do_success(_connect)

    def test_connect_connection_failed(self):
        self.dut.urls['connect'] = 'http://haijia.bjxueche.ne/'
        self._do_failed(self.dut.connect)

    def test_connect_with_retry(self):
        def _test_connect():
            resp = self.dut.connect()
            print(resp.content)
            return resp.content
        self._do_with_retry(_test_connect)

    def test_connect_retried_but_failed(self):
        self._do_retried_but_failed(self.dut.connect)

    def _do_timeout_failed(self, do_func, expt_time):
        start_time = time.time()
        self.assertRaises(Timeout, do_func)
        delta = time.time() - start_time
        print('Return after {0} seconds because of timeout '.format(delta))
        self.assertLessEqual(delta, expt_time)

    def test_connect_timeout_failed(self):
        self.dut.urls['connect'] = 'http://www.facebook.com/'
        self.dut.timeout_parameters['connect'] = 3
        self._do_timeout_failed(self.dut.connect, self.dut.timeout_parameters['connect']+1)

    def _do_multi_timeout_failed(self, do_func, expt_time):
        start_time = time.time()
        self.assertRaises(ConnectionError, do_func)
        delta = time.time() - start_time
        print('Return after {0} seconds because of timeout '.format(delta))
        self.assertLessEqual(delta, expt_time)

    def test_connect_multi_timeout_failed(self):
        self.dut.urls['connect'] = 'http://www.facebook.com/'
        self.dut.timeout_parameters['connect'] = 2
        self.dut.set_max_retry(for_url=self.dut.urls['connect'], max_retries=5)
        self._do_multi_timeout_failed(self.dut.connect, (self.dut.timeout_parameters['connect']+0.5)*5)

    def test_open_url_n_read_success(self):
        def _test():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.net/')
            return body
        self._do_success(_test)

    def test_open_url_n_read_connection_failed(self):
        def _test():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.ne/')
            return body
        self._do_failed(_test)

    def test_open_url_n_read_timeout_failed(self):
        self.dut.timeout_parameters['open_url_n_read'] = 6

        def _test():
            resp, body = self.dut.open_url_n_read('http://www.facebook.com/')
            return body
        self._do_timeout_failed(_test, self.dut.timeout_parameters['open_url_n_read']+1)

    def test_open_url_n_read_multi_timeout_failed(self):
        self.dut.timeout_parameters['open_url_n_read'] = 2
        def _test():
            resp, body = self.dut.open_url_n_read('http://www.facebook.com/')
            return body
        self.dut.set_max_retry(for_url='http://www.facebook.com/', max_retries=5)
        self._do_multi_timeout_failed(_test, (self.dut.timeout_parameters['open_url_n_read']+0.5)*5)

    def test_open_url_n_read_retry_but_failed(self):
        def _test():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.net/')
            return body
        self._do_retried_but_failed(_test)

    def test_open_url_n_read_with_retry(self):
        def _test():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.net/')
            return body
        self._do_with_retry(_test)
