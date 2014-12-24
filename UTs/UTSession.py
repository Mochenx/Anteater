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
    def _do_success(self, do_func, fake_body='Mock, Connection succeed', func_get_expt=None):
        httpretty.register_uri(httpretty.GET, 'http://haijia.bjxueche.net/',
                               body=fake_body)
        httpretty.register_uri(httpretty.POST, 'http://haijia.bjxueche.net/',
                               body=fake_body)
        body = do_func()
        if isinstance(fake_body, str):
            self.assertEqual(body, fake_body)
        elif callable(func_get_expt):
            self.assertEqual(body, func_get_expt())
        else:
            self.assertTrue(False)

    def _do_failed(self, do_func):
        self.assertRaises(ConnectionError, do_func)

    @httpretty.activate
    def _do_with_retry(self, do_func, func_check_request=None):
        self.retry_cnt = 0

        def _retry(request, uri, headers):
            if func_check_request is not None and callable(func_check_request):
                func_check_request(request)
                print('Checking Request:{0}, Pass'.format(request.body))
            if self.retry_cnt == 5:
                print('Round:{0}, Response'.format(self.retry_cnt))
                return 200, headers, 'Mock, Connection succeed'
            else:
                print('Round:{0}, Timeout'.format(self.retry_cnt))
                self.retry_cnt += 1
                raise socket.timeout()

        httpretty.register_uri(httpretty.GET, 'http://haijia.bjxueche.net/', body=_retry)
        httpretty.register_uri(httpretty.POST, 'http://haijia.bjxueche.net/', body=_retry)
        self.dut.set_max_retry(for_url='http://haijia.bjxueche.net/', max_retries=6)
        body = do_func()
        self.assertEqual(body, 'Mock, Connection succeed')
        self.assertEqual(self.retry_cnt, 5)

    @httpretty.activate
    def _do_retried_but_failed(self, do_func, func_check_request=None):
        self.retry_cnt = 0

        def _retry(request, uri, headers):
            if func_check_request is not None and callable(func_check_request):
                func_check_request(request)
                print('Checking Request:{0}, Pass'.format(request.body))
            print('Round:{0}, Timeout'.format(self.retry_cnt))
            self.retry_cnt += 1
            raise socket.timeout()

        httpretty.register_uri(httpretty.GET, 'http://haijia.bjxueche.net/', body=_retry)
        httpretty.register_uri(httpretty.POST, 'http://haijia.bjxueche.net/', body=_retry)
        self.dut.set_max_retry(for_url='http://haijia.bjxueche.net/', max_retries=10)
        self.assertRaises(ConnectionError, do_func)
        self.assertEqual(self.retry_cnt, 11)

    def _do_timeout_failed(self, do_func, expt_time):
        start_time = time.time()
        self.assertRaises(Timeout, do_func)
        delta = time.time() - start_time
        print('Return after {0} seconds because of timeout '.format(delta))
        self.assertLessEqual(delta, expt_time)

    def _do_multi_timeout_failed(self, do_func, expt_time):
        start_time = time.time()
        self.assertRaises(ConnectionError, do_func)
        delta = time.time() - start_time
        print('Return after {0} seconds because of timeout '.format(delta))
        self.assertLessEqual(delta, expt_time)

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

    def test_connect_timeout_failed(self):
        self.dut.urls['connect'] = 'http://haijia.bjxueche.net:81/'
        self.dut.timeout_parameters['connect'] = 3
        self._do_timeout_failed(self.dut.connect, self.dut.timeout_parameters['connect']+1)

    def test_connect_multi_timeout_failed(self):
        self.dut.urls['connect'] = 'http://haijia.bjxueche.net:81/'
        self.dut.timeout_parameters['connect'] = 2
        self.dut.set_max_retry(for_url=self.dut.urls['connect'], max_retries=5)
        self._do_multi_timeout_failed(self.dut.connect, (self.dut.timeout_parameters['connect']+0.5)*5)

    def test_open_url_n_read_success(self):
        def _test():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.net/')
            return body
        self._do_success(_test)

    def test_open_url_n_read_failed(self):
        def _test():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.ne/')
            return body
        self._do_failed(_test)

    def test_open_url_n_read_with_retry(self):
        def _test():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.net/')
            return body
        self._do_with_retry(_test)

    def test_open_url_n_read_retry_but_failed(self):
        def _test():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.net/')
            return body
        self._do_retried_but_failed(_test)

    def test_open_url_n_read_timeout_failed(self):
        self.dut.timeout_parameters['open_url_n_read'] = 6

        def _test():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.net:81/')
            return body

        def _test_with_timeout_args():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.net:81/', timeout=7)
            return body
        self._do_timeout_failed(_test, self.dut.timeout_parameters['open_url_n_read']+1)
        self._do_timeout_failed(_test_with_timeout_args, 8)


    def test_open_url_n_read_multi_timeout_failed(self):
        self.dut.timeout_parameters['open_url_n_read'] = 2
        def _test():
            resp, body = self.dut.open_url_n_read('http://haijia.bjxueche.net:81/')
            return body
        self.dut.set_max_retry(for_url='http://haijia.bjxueche.net:81/', max_retries=5)
        self._do_multi_timeout_failed(_test, (self.dut.timeout_parameters['open_url_n_read']+0.5)*5)

    def test_post_with_response_success(self):
        def _post_with_response():
            resp, body = self.dut.post_with_response('http://haijia.bjxueche.net/', data='Posted Data')
            print(body)
            return body

        def chk_post_data(request, uri, headers):
            self.assertEqual(request.body, 'Posted Data')
            return 200, headers, 'Mock, Post succeed'

        self._do_success(_post_with_response, fake_body=chk_post_data, func_get_expt=lambda: 'Mock, Post succeed')

    def test_post_with_response_fail(self):
        def _post_with_response():
            resp, body = self.dut.post_with_response('http://haijia.bjxueche.ne/', data='Posted Data')
            print(body)
            return body
        self._do_failed(_post_with_response)

    def test_post_with_response_with_retry(self):
        def _test():
            resp, body = self.dut.post_with_response('http://haijia.bjxueche.net/', data='Posted Data')
            return body
        self._do_with_retry(_test, func_check_request=lambda r: self.assertEqual(r.body, 'Posted Data'))

    def test_post_with_response_retry_but_failed(self):
        def _test():
            resp, body = self.dut.post_with_response('http://haijia.bjxueche.net/', data='Posted Data')
            return body
        self._do_retried_but_failed(_test, func_check_request=lambda r: self.assertEqual(r.body, 'Posted Data'))

    def test_post_with_response_timeout_failed(self):
        self.dut.timeout_parameters['post_with_response'] = 3

        def _test():
            print('Calling Test function')
            resp, body = self.dut.post_with_response('http://haijia.bjxueche.net:81/', data='Posted Data')
            return body

        def _test_with_timeout_args():
            print('Calling Test function with timeout argument')
            resp, body = self.dut.post_with_response('http://haijia.bjxueche.net:81/', data='Posted Data', timeout=7)
            return body
        self._do_timeout_failed(_test, self.dut.timeout_parameters['post_with_response']+1)
        self._do_timeout_failed(_test_with_timeout_args, 8)

    def test_post_with_response_multi_timeout_failed(self):
        self.dut.timeout_parameters['post_with_response'] = 2

        def _test():
            print('Calling Test function')
            resp, body = self.dut.post_with_response('http://haijia.bjxueche.net:81/', data='Posted Data')
            return body

        def _test_with_timeout_args():
            print('Calling Test function with timeout argument')
            resp, body = self.dut.post_with_response('http://haijia.bjxueche.net:81/', data='Posted Data', timeout=3)
            return body
        self.dut.set_max_retry(for_url='http://haijia.bjxueche.net:81/', max_retries=5)
        self._do_multi_timeout_failed(_test, (self.dut.timeout_parameters['post_with_response']+0.5)*5)
        self._do_multi_timeout_failed(_test_with_timeout_args, (3+0.8)*5)
