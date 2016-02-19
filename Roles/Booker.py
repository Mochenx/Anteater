# encoding=utf-8

import re
import json
from lxml import etree
from six import with_metaclass, text_type
import six.moves.urllib.parse as urlparse
from datetime import datetime
from io import StringIO

from Roles.Role import RoleCreatorWithLogger, Role, Logger
from Roles.Car import Car
from Roles.Session import URLsForHJ
from Roles.Driver import LoginAgain

__author__ = 'mochenx'


class Booker(with_metaclass(RoleCreatorWithLogger, Role, Logger)):

    def __init__(self, **kwargs):
        super(Booker, self).__init__(**kwargs)

    @classmethod
    def create(cls):
        cls.new_property('session')
        cls.new_property('time_periods')
        cls.new_property('lesson_type')
        return Booker()

    def load_properties(self, **kwargs):
        if 'session' in kwargs and 'time_periods' in kwargs and 'lesson_type' in kwargs:
            self.session = kwargs['session']
            self.time_periods = kwargs['time_periods']
            self.lesson_type = kwargs['lesson_type']
        elif self.session is None:
            raise ValueError('Properties session, time_periods and lesson_type are needed for class Booker')

    def get_cars(self, date):
        get_car_service_queries = self._get_car_stat_qureies(date)
        car_infos = []
        for query in get_car_service_queries:
            self.debug(msg=query, by='get_cars')

            resp, resp_body = self.session.open_url_n_read(url=query, timeout=5)

            self.debug(msg=u'Query Cars response: {0} at time {1}'.format(resp.text, datetime.now()),
                       by='get_cars')
            # Get car information from response
            car_info = self._parse_car_info_json(resp_body)
            self.debug(msg=u'Cars: {0} at time {1}'.format(text_type(car_info), datetime.now()),
                       by='get_cars')

            if 'LoginOut' in car_info:
                self.debug(msg=u'LoginOut is returned in response, login again'.format(text_type(car_info),
                                                                                       datetime.now()),
                           by='get_cars')
                raise LoginAgain()
            assert isinstance(car_info, list)
            car_infos.extend(car_info)
        cars = self._create_cars(car_infos)

        return cars

    def get_booking_status(self, date):
        re_book_date = datetime.strptime(date, '%Y%m%d').strftime('\s*%Y\s*-\s*%m-\s*%d\s*')
        try:
            resp, booking_rslt = self.session.open_url_n_read(URLsForHJ.booking_rslt_url)
        except Exception:
            return False
        if booking_rslt is None:
            return False

        self.write_html('booking_status.html', resp.text)

        tree = etree.parse(StringIO(booking_rslt.decode(encoding='utf-8')), etree.HTMLParser())

        for u in tree.iterfind('.//table'):
            name = u.get('id')
            if name == 'tblMain':
                for u_inner in tree.iterfind('.//td'):
                    if u_inner.text is not None and re.search(re_book_date, u_inner.text):
                        self.debug(msg='Got booking results of {0}: Ture'.format(date), by='get_booking_status')
                        return True
        self.debug(msg='Got booking results of {0}: False'.format(date), by='get_booking_status')
        return False

    def _get_car_stat_qureies(self, date):
        periods = self.time_periods if isinstance(self.time_periods, list) else [self.time_periods]
        get_car_query_args = [ToGetCarsQuery(date=date, time_period=Booker._convert_time_period(time_period),
                                             lesson_type=self.lesson_type)
                              for time_period in periods]

        query_url = [text_type(query_args) for query_args in get_car_query_args]
        return query_url

    def _create_cars(self, car_infos):
        cars = []
        for car_info in car_infos:
            car = Role.get('Car')
            car.load_properties(session=self.session, lesson_type=self.lesson_type, car_info=car_info)
                            # date=car_info['YYRQ'], time_period=car_info['XNSD'], car_id=car_info['CNBH'])
            car.log_path = self.log_path
            car.logger = self.logger
            cars.append(car)
        return cars

    @staticmethod
    def _parse_car_info_json(resp_body):
        tree = etree.fromstring(resp_body)
        car_info_in_json = re.sub(r'\]_+.*', r']', tree.text)
        car_info = json.loads(car_info_in_json)
        return car_info

    @staticmethod
    def _convert_time_period(time_period='Morning'):
        if re.match(r'^\s*Morning\s*$', time_period, re.IGNORECASE) is not None:
            time_period_in_server_fmt = '812'
        elif re.match(r'^\s*Afternoon\s*$', time_period, re.IGNORECASE) is not None:
            time_period_in_server_fmt = '15'
        elif re.match(r'^\s*(Evening|Night)\s*$', time_period, re.IGNORECASE) is not None:
            time_period_in_server_fmt = '58'
        else:
            raise ValueError('Time span should be Morning, Afternoon or Evening/Night, '
                             'instead of {0}'.format(time_period))
        return time_period_in_server_fmt

    def __str__(self):
        return 'Booker: lession-{0} at {1}'.format(self.lesson_type, self.time_periods)


class ToGetCarsQuery(dict):
    def __init__(self, date, time_period, lesson_type):
        self['yyrq'] = date
        self['yysd'] = time_period
        self['xllxID'] = lesson_type
        self['pageSize'] = '40'
        self['pageNum'] = '1'
        self.get_car_service_url = URLsForHJ.get_cars

    def __str__(self):
        encoded_get_car_query_args = urlparse.urlencode([(k, v) for k, v in sorted(self.items())])
        return self.get_car_service_url + encoded_get_car_query_args
