# encoding=utf-8

from six import with_metaclass
from datetime import datetime, timedelta
import time
import pytz
import re

from Roles.Role import RoleCreatorWithLogger, Role, Logger

__author__ = 'mochenx'


class Timer(with_metaclass(RoleCreatorWithLogger, Role, Logger)):
    def run(self):
        raise NotImplementedError('Method run must be implemented in sub class of Timer')


class WaitingTimer(Timer):

    def __init__(self, **kwargs):
        super(Timer, self).__init__(**kwargs)
        self.book_hour = 7
        self.book_minute = 34
        self.home_page_url = 'http://haijia.bjxueche.net/'

    @classmethod
    def create(cls):
        # cls.new_property('book_date')
        cls.new_property('session')
        return WaitingTimer()

    def load_properties(self, **kwargs):
        if 'session' in kwargs:
            self.session = kwargs['session']
        else:
            raise ValueError('Property session are needed for class Driver')

    def run(self):
        while True:
            loc_time = self.get_server_time()
            book_time = self.get_book_time(loc_time)

            sleep_span = self.get_sleep_span(book_time, loc_time)

            the_day_of_do_booking = ((loc_time.day + self.days_in_future) if self.user_set_book_date is None
                                     else self.user_set_book_date.day)
            book_date = book_time.replace(day=the_day_of_do_booking)
            print("To book car on {1}, wake up on {0}".format(book_time.strftime('%d %b %X'),
                                                              book_date.strftime('%d %b %X')))
            self.debug(msg="To book car on {1}, wake up on {0}".format(book_time.strftime('%d %b %X'),
                                                                       book_date.strftime('%d %b %X')),
                       by='wait_to_book_time')
            if sleep_span == 0:
                return book_date.strftime('%Y%m%d')
            time.sleep(sleep_span)
            self.debug(msg="Wake up & check time again", by='wait_to_book_time')
            print("Wake up & check time again at {0}".format(book_time.strftime('%d %b %X')))

    def get_server_time(self):
        resp, _ = self.session.open_url_n_read(url=self.home_page_url, timeout=20)
        time_from_http_server = self.get_date_from_http_header(resp.headers)
        self.debug(msg=time_from_http_server, by='get_server_time')
        server_time = datetime.strptime(time_from_http_server, '%a, %d %b %Y %X %Z')
        return self.convert_to_local_tz(server_time)

    def get_book_time(self, loc_time):
        if ((loc_time.hour == self.book_hour and loc_time.minute > self.book_minute) or
                    loc_time.hour >= self.book_hour + 1):
            if self.user_set_book_date is not None and self.user_set_book_date.day - self.days_in_future > (loc_time.day + 1):
                book_day = self.user_set_book_date.day - self.days_in_future
            else:
                book_day = loc_time.day + 1
        else:
            if self.user_set_book_date is not None and self.user_set_book_date.day - self.days_in_future > loc_time.day:
                book_day = self.user_set_book_date.day - self.days_in_future
            else:
                book_day = loc_time.day
        book_time = loc_time.replace(day=book_day, hour=self.book_hour, minute=self.book_minute,
                                     second=0, microsecond=0)
        return book_time

    def get_sleep_span(self, book_time, loc_time):
        if book_time - loc_time <= timedelta(minutes=1):
            print("Now it's {0}, Let's start to work".format(book_time.strftime('%Y %m %d %X')))
            self.debug(msg="Now it's {0}, Let's start to work".format(book_time.strftime('%Y %m %d %X')),
                       by='wait_to_book_time')
            sleep_span = 0
        elif book_time - loc_time > timedelta(minutes=11):
            print("Sleep 10 minutes")
            self.debug(msg="Sleep 10 minutes", by='wait_to_book_time')
            sleep_span = 60*10
        else:
            print("Sleep 50 seconds")
            self.debug(msg="Sleep 50 seconds", by='wait_to_book_time')
            sleep_span = 50
        return sleep_span

    @staticmethod
    def get_date_from_http_header(headers):
        """
            A function of scanning all items in a header and finding the response time
        """
        the_date = None
        the_date = headers['Date']
        # for header in headers:
        #     mrslt = re.search(r'date\s*:\s*(.*)', header, re.IGNORECASE)
        #     if mrslt:
        #         the_date = mrslt.group(1)
        #         break
        the_date = re.sub(r'\s*[\r\n]', '', the_date)
        return the_date

    def convert_to_local_tz(self, server_time):
        """
            Convert time from GMT to local time zone, at here, Asia/Shanghai
        """
        tz_gmt = pytz.timezone('GMT')
        tz_beijing = pytz.timezone('Asia/Shanghai')
        server_time = server_time.replace(tzinfo=tz_gmt)
        loc_time = server_time.astimezone(tz_beijing)
        self.debug(msg=loc_time.strftime('%d %b %X'), by='get_server_time')
        return loc_time

