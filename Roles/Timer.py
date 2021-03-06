# encoding=utf-8

from six import with_metaclass
from datetime import datetime, timedelta
import time
import pytz
import re

from requests.exceptions import ConnectionError, Timeout

from Roles.Role import RoleCreatorWithLogger, Role, Logger
from Roles.Session import URLsForHJ

__author__ = 'mochenx'


class Timer(with_metaclass(RoleCreatorWithLogger, Role, Logger)):
    supported_date_formats = ['%Y%m%d', '%Y-%m-%d', '%b %d %Y']
    return_date_format = '%Y%m%d'

    @staticmethod
    def localize_date(date_str):
        fmt_success = False
        for fmt in Timer.supported_date_formats:
            try:
                naive_date = datetime.strptime(date_str, fmt)
                fmt_success = True
            except ValueError:
                continue
        if not fmt_success:
            raise ValueError('{0} is not a supported format'.format(date_str))
        tz_beijing = pytz.timezone('Asia/Shanghai')
        return tz_beijing.localize(naive_date)

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

    def get_server_time(self):
        resp, _ = self.session.open_url_n_read(url=URLsForHJ.connect, timeout=20)
        time_from_http_server = self.get_date_from_http_header(resp.headers)
        self.debug(msg=time_from_http_server, by='get_server_time')
        server_time = datetime.strptime(time_from_http_server, '%a, %d %b %Y %X %Z')
        return self.convert_to_local_tz(server_time)

    def run(self):
        raise NotImplementedError('Method run must be implemented in sub class of Timer')

    @property
    def schedule_date(self):
        raise NotImplementedError('Method schedule_date must be implemented in sub class of Timer')


class BookNowTimer(Timer):
    """ A Timer which return immediately """

    @classmethod
    def create(cls):
        cls.new_property('session')
        cls.new_property('lesson_date')
        return BookNowTimer()

    def load_properties(self, **kwargs):
        if 'session' in kwargs:
            self.session = kwargs['session']
        elif self.session is None:
            raise ValueError('Property session are needed for class Timer')
        if 'lesson_date' in kwargs:
            self.lesson_date = self.localize_date(kwargs['lesson_date'])
        else:
            raise KeyError('Not Found Setting: lesson_date')

    def run(self):
        loc_time = self.get_server_time()
        book_date = self.get_book_date(loc_time)
        return book_date.strftime('%Y%m%d')

    def get_book_date(self, debut_time):
        the_day_of_do_booking = self.lesson_date
        book_date = debut_time.replace(year=the_day_of_do_booking.year,
                                       month=the_day_of_do_booking.month,
                                       day=the_day_of_do_booking.day)
        return book_date

    @property
    def schedule_date(self):
        loc_time = self.get_server_time()
        return loc_time.strftime(self.return_date_format)


class WaitingTimer(Timer):
    """ A Timer which sleeps for days and wake up at calculated date & time """

    debut_hour, debut_minute = 7, 34  # 7:34 AM
    days_in_advance = 7  #of days

    @classmethod
    def create(cls):
        cls.new_property('session')
        cls.new_property('lesson_date')
        return WaitingTimer()

    def load_properties(self, **kwargs):
        if 'session' in kwargs:
            self.session = kwargs['session']
        elif self.session is None:
            raise ValueError('Property session are needed for class Timer')
        if 'lesson_date' in kwargs:
            # TODO: How to deal with the raised exception
            self.lesson_date = self.localize_date(kwargs['lesson_date'])

    def run(self):
        while True:
            try:
                book_date, debut_time, loc_time = self.calc_date()
            except (ConnectionError, Timeout) as e:
                self.debug(msg="{0}".format(str(e)), by='WaitingTimer.run')
                continue
            sleep_span = self.get_sleep_span(debut_time, loc_time)

            self.debug(msg="To book car on {1}, wake up on {0}".format(debut_time.strftime('%d %b %X'),
                                                                       book_date.strftime('%d %b %X')),
                       by='wait_to_book_time')
            if sleep_span == 0:
                return book_date.strftime('%Y%m%d')
            time.sleep(sleep_span)
            self.debug(msg="Wake up & check time again", by='wait_to_book_time')
            print("Wake up & check time again at {0}".format(debut_time.strftime('%d %b %X')))

    def calc_date(self):
        loc_time = self.get_server_time()
        debut_time = self.get_debut_time(loc_time)
        book_date = self.get_book_date(debut_time)
        return book_date, debut_time, loc_time

    def get_debut_time(self, loc_time):
        """
        """
        now_is_later_than_debut = lambda: ((loc_time.hour == self.debut_hour and loc_time.minute > self.debut_minute) or
                                            loc_time.hour >= self.debut_hour + 1)
        user_wants_later_than = lambda day: (self.lesson_date is not None and
                                             self.lesson_date - timedelta(days=self.days_in_advance) > day)
        today = loc_time
        tomorrow = loc_time + timedelta(days=1)
        some_days_later = today
        if self.lesson_date is not None:
            some_days_later = self.lesson_date - timedelta(self.days_in_advance)

        if now_is_later_than_debut() and user_wants_later_than(tomorrow):
            book_day = some_days_later
        elif now_is_later_than_debut():
            book_day = tomorrow
        elif user_wants_later_than(today):
            book_day = some_days_later
        else:
            book_day = today
        debut_time = loc_time.replace(year=book_day.year, month=book_day.month, day=book_day.day,
                                      hour=self.debut_hour, minute=self.debut_minute,
                                      second=0, microsecond=0)
        return debut_time

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

    def get_book_date(self, debut_time):
        the_day_of_do_booking = ((debut_time + timedelta(self.days_in_advance)) if self.lesson_date is None
                                 else self.lesson_date)
        book_date = debut_time.replace(year=the_day_of_do_booking.year,
                                       month=the_day_of_do_booking.month,
                                       day=the_day_of_do_booking.day)
        return book_date

    def __str__(self):
        book_date, debut_time, _ = self.calc_date()

        return "WaitingTimer: {0} => {1}".format(debut_time.strftime('%d %b %X'),
                                                 book_date.strftime('%d %b %X'))

    @property
    def schedule_date(self):
        book_date, debut_time, loc_time = self.calc_date()
        if self.lesson_date is None:
            schedule_date = loc_time
        elif ((debut_time.year, debut_time.month, debut_time.day) ==
                  (loc_time.year, loc_time.month, loc_time.day)):
            schedule_date = loc_time
        else:
            schedule_date = debut_time - timedelta(day=1)
        return schedule_date.strftime(self.return_date_format)
