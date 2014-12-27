# encoding=utf-8

from six import with_metaclass
from datetime import datetime, timedelta
import time
import pytz
import re

from requests.exceptions import ConnectionError, Timeout

from Roles.Role import RoleCreatorWithLogger, Role, Logger

__author__ = 'mochenx'


class Timer(with_metaclass(RoleCreatorWithLogger, Role, Logger)):
    def run(self):
        raise NotImplementedError('Method run must be implemented in sub class of Timer')


class WaitingTimer(Timer):

    def __init__(self, **kwargs):
        super(Timer, self).__init__(**kwargs)
        self.home_page_url = 'http://haijia.bjxueche.net/'
        self.debut_hour, self.debut_minute = 7, 34  # 7:34 AM
        self.days_in_advance = 7  #of days

    @classmethod
    def create(cls):
        cls.new_property('session')
        cls.new_property('set_book_date')
        return WaitingTimer()

    def load_properties(self, **kwargs):
        if 'session' in kwargs:
            self.session = kwargs['session']
        elif self.session is None:
            raise ValueError('Property session are needed for class Driver')
        if 'set_book_date' in kwargs:
            self.set_book_date = kwargs['set_book_date']

    def run(self):
        while True:
            try:
                loc_time = self.get_server_time()
            except (ConnectionError, Timeout) as e:
                self.debug(msg="{0}".format(str(e)), by='WaitingTimer.run')
                continue
            book_time = self.get_book_time(loc_time)

            sleep_span = self.get_sleep_span(book_time, loc_time)
            book_date = self.get_book_date(loc_time, book_time)

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
        """
        """
        now_is_later_than_debute = lambda: ((loc_time.hour == self.debut_hour and loc_time.minute > self.debut_minute) or
                                            loc_time.hour >= self.debut_hour + 1)
        user_wants_later_than = lambda day: (self.set_book_date is not None and
                                             self.set_book_date - timedelta(days=self.days_in_advance) > day)
        today = loc_time
        tomorrow = loc_time + timedelta(days=1)
        some_days_later = today
        if self.set_book_date is not None:
            some_days_later = self.set_book_date - timedelta(self.days_in_advance)

        if now_is_later_than_debute() and user_wants_later_than(tomorrow):
            book_day = some_days_later
        elif now_is_later_than_debute():
            book_day = tomorrow
        elif user_wants_later_than(today):
            book_day = some_days_later
        else:
            book_day = today
        book_time = loc_time.replace(year=book_day.year, month=book_day.month, day=book_day.day,
                                     hour=self.debut_hour, minute=self.debut_minute,
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

    def get_book_date(self, loc_time, book_time):
        the_day_of_do_booking = ((loc_time + timedelta(self.days_in_advance)) if self.set_book_date is None
                                 else self.set_book_date)
        book_date = book_time.replace(year=the_day_of_do_booking.year,
                                      month=the_day_of_do_booking.month,
                                      day=the_day_of_do_booking.day)
        return book_date

    @staticmethod
    def get_date_from_http_header(headers):
        """
            A function of scanning all items in a header and finding the response time
        """
        the_date = headers['Date']
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

