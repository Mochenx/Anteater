# encoding=utf-8

import requests
from six import text_type
from requests.exceptions import Timeout, RequestException, ConnectionError, HTTPError, ReadTimeout
from requests.adapters import HTTPAdapter
import traceback
from datetime import datetime

from Roles.Logger import Logger

__author__ = 'mochenx'

# The URL of document for requests
# http://docs.python-requests.org/en/latest/


class URLsForHJ(object):
    connect = 'http://haijia.bjxueche.net'
    login_url = 'http://haijia.bjxueche.net/'
    net_text_url = r'http://haijia.bjxueche.net/Login.aspx/GetNetText'
    get_cars = 'http://haijia.bjxueche.net/Han/ServiceBooking.asmx/GetCars?'
    book_car = 'http://haijia.bjxueche.net/Han/ServiceBooking.asmx/BookingCar?'
    booking_rslt_url = 'http://haijia.bjxueche.net/NetBooking.aspx'


class Session(Logger):
    def __init__(self):
        super(Session, self).__init__()
        self._session = requests.Session()
        self._timeout_parameters = {'connect': 6, 'open_url_n_read': 3, 'post_with_response': 3}
        self._urls = {'connect': URLsForHJ.connect}

    @property
    def urls(self):
        return self._urls

    @property
    def timeout_parameters(self):
        return self._timeout_parameters

    def set_max_retry(self, for_url, max_retries):
        self._session.mount(for_url, HTTPAdapter(max_retries=max_retries))

    def connect(self):
        """
        At first, it needs to access the following page to get a cookie, for the reason the website will NOT send me
        CAPTCHA if no cookie is established.
        """

        self.debug(msg=u'Starting to connect URL:{0} at time {1}' .format(self.urls['connect'], datetime.now()),
                   by='Connect URL')
        try:
            resp = self._session.get(self.urls['connect'], timeout=self.timeout_parameters['connect'])
        except (Timeout, RequestException, ConnectionError, ReadTimeout, HTTPError) as e:
            self.debug(msg=text_type(e), by='Connect URL')
            self.debug(msg=u','.join(line.strip() for line in traceback.format_stack()), by='Connect URL')
            raise e
        self.debug(msg=u'Successfully to connect URL:{0} at time {1}' .format(self.urls['connect'], datetime.now()),
                   by='Connect URL')

        return resp

    def open_url_n_read(self, url, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout_parameters['open_url_n_read']
        try:
            self.debug(msg=u'Opening {0} at time {1}'.format(url, datetime.now()), by='Open URL')
            resp = self._session.get(url, **kwargs)
            resp_body = resp.content
        except (Timeout, RequestException, ConnectionError, ReadTimeout, HTTPError) as e:
            self.debug(msg=u'Failed to open URL:{0} at time {1}' .format(url, datetime.now()),
                       by='Open URL')
            self.debug(msg=text_type(e), by='Open URL')
            self.debug(msg=u','.join(line.strip() for line in traceback.format_stack()), by='Open URL')
            raise e
        return resp, resp_body

    def post_with_response(self, url, data, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout_parameters['post_with_response']
        try:
            self.debug(msg=u'Opening {0} at time {1}'.format(url, datetime.now()), by='Post')
            resp = self._session.post(url, data, **kwargs)
            resp_body = resp.content
            self.debug(msg=u'Status {0} at time {1}'.format(resp.status_code, datetime.now()), by='Post')
        except (Timeout, RequestException, ConnectionError, ReadTimeout, HTTPError) as e:
            self.debug(msg=text_type(e), by='Post')
            self.debug(msg=u','.join(line.strip() for line in traceback.format_stack()), by='Post')
            raise e
        return resp, resp_body
