# encoding=utf-8

import re
import json
from lxml import etree
from six import with_metaclass, text_type
import six.moves.urllib.parse as urlparse

from Roles.Role import RoleCreatorWithLogger, Role, Logger
from Roles.Session import URLsForHJ

__author__ = 'mochenx'


class Car(with_metaclass(RoleCreatorWithLogger, Role, Logger)):
    def __init__(self, **kwargs):
        super(Car, self).__init__(**kwargs)

    @classmethod
    def create(cls):
        cls.new_property('session')
        cls.new_property('lesson_type')
        cls.new_property('car_info')
        return Car()

    def load_properties(self, **kwargs):
        if 'session' in kwargs and 'lesson_type' in kwargs and 'car_info' in kwargs:
            self.session = kwargs['session']
            self.lesson_type = kwargs['lesson_type']
            self.car_info = kwargs['car_info']
        elif self.session is None:
            raise ValueError('Properties session, date and car_info are needed for class Car')

    def run(self):
        book_car_query_args = BookCarQuery(lesson_type=self.lesson_type, car_info=self.car_info)
        book_car_service_url = str(book_car_query_args)
        self.debug(msg=book_car_service_url, by='Car')
        resp, resp_body = self.session.open_url_n_read(url=book_car_service_url, timeout=5)

        self.write_html('car.{0}.html'.format(book_car_query_args.query_id), resp.text)
        try:
            tree = etree.fromstring(resp_body)
            book_rslt = json.loads(re.sub(r'_0', '', tree.text))
        except Exception as e:
            self.debug(msg=u'Car[{0}] stop at parsing responded JSON'.format(book_car_query_args.query_id),
                       by='Car')
            return False
        self.debug(msg=u'Car[{0}]: {1}'.format(book_car_query_args.query_id, text_type(book_rslt)), by='Car')

        try:
            for rslt in book_rslt:
                if rslt['Result'] is True:
                    return True
        except Exception as e:
            self.debug(msg=text_type(e), by='Car')
            return False
        return False

    def __call__(self, *args, **kwargs):
        work_done = kwargs['work_done'] if 'work_done' in kwargs else None
        try:
            self.run()
        except Exception as e:
            pass
        if work_done is not None:
            work_done()


class BookCarQuery(dict):
    def __init__(self, lesson_type, car_info):
        self['yyrq'] = car_info[u'YYRQ']
        self['xnsd'] = car_info[u'XNSD']
        self['cnbh'] = car_info[u'CNBH']
        self['imgCode'] = ''
        self['KMID'] = lesson_type
        self.book_car_service_url = URLsForHJ.book_car

    def __str__(self):
        encoded_book_car_query_args = urlparse.urlencode([(k, v) for k, v in self.items()])
        return self.book_car_service_url + encoded_book_car_query_args

    @property
    def query_id(self):
        return '{0}.{1}'.format(self['xnsd'], self['cnbh'])
