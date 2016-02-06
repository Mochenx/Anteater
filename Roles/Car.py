# encoding=utf-8

import re
import json
from lxml import etree
from six import with_metaclass
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
        self.debug(msg=book_car_service_url, by='book_car')
        _, resp_body = self.session.open_url_n_read(url=book_car_service_url, timeout=2)
        try:
            tree = etree.fromstring(resp_body)
            book_rslt = json.loads(re.sub(r'_0', '', tree.text))
        except Exception as e:
            return False
        self.debug(msg=str(book_rslt), by='book_car')
        with open('book_car_xml.html', 'wb') as h:
            h.write(resp_body)
        try:
            for rslt in book_rslt:
                if rslt['Result'] is True:
                    return True
        except Exception as e:
            self.debug(msg=str(e), by='book_car')
            return False
        return False


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
