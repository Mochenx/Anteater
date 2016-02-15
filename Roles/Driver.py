# encoding=utf-8

import re
from datetime import datetime
from lxml import etree
from io import StringIO
from six import with_metaclass, text_type
import six.moves.urllib.parse as urlparse

from Roles.Role import RoleCreatorWithLogger, Role, Logger
from Roles.CAPTCHARecognizer import CAPTCHAError, CAPTCHARecognizer

__author__ = 'mochenx'


class Driver(with_metaclass(RoleCreatorWithLogger, Role, Logger)):
    """
        Driver is the class which takes the charge of login, though "user" would be the proper name usually.
        However, current package is developed for booking drive lessons, Driver is a better name.
    """

    login_repeat_times = 10

    def __init__(self, **kwargs):
        super(Driver, self).__init__(**kwargs)

    @classmethod
    def create(cls):
        cls.new_property('drivername')
        cls.new_property('password')
        cls.new_property('session')
        return Driver()

    def load_properties(self, **kwargs):
        if 'drivername' in kwargs and 'password' in kwargs and 'session' in kwargs:
            self.drivername = kwargs['drivername']
            self.password = kwargs['password']
            self.session = kwargs['session']
        else:
            raise ValueError('Properties drivername, password and session are needed for class Driver')

    def login(self):
        """
        """
        CAPTCHA_rdr = CAPTCHARecognizer(self.session, prefix_fname=self.drivername)

        for i in range(self.login_repeat_times):
            try:
                login_post_data = self._get_login_form()
                captcha = CAPTCHA_rdr.get_captcha()
                self.debug(msg='CAPTCHA:{0}'.format(captcha), by='Login')
                login_post_data.load_captcha(captcha)
                self._post_login_form(login_post_data.urlencode())
            except CAPTCHAError as e:
                self.debug(msg='CAPTCHA recognition error:{0}'.format(str(e)), by='Login')
                self._get_net_text()
                continue
            except Exception as e:
                raise LoginAgain(str(e), logger=self)
            return
        raise LoginFail()

    def _get_login_form(self):
        home_page_url = 'http://haijia.bjxueche.net/'

        self.debug(msg='{0} at time {1}'.format(home_page_url, datetime.now()), by='get_form')
        _, resp_body = self.session.open_url_n_read(url=home_page_url)

        login_post_data = LoginForm(self.drivername, self.password)
        # body is a UTF-8 encoded bytes-type variable, so decode it firstly
        login_post_data.load_form_with_parsed_html(resp_body)

        return login_post_data

    def _post_login_form(self, data_being_posted):
        login_url = 'http://haijia.bjxueche.net/'

        self.debug(msg='{0} at time {1}'.format(data_being_posted, datetime.now()),
                   by='post_login_data')
        resp, body = self.session.post_with_response(url=login_url, data=bytes(data_being_posted), timeout=5)

        self._is_captcha_error(body)
        self.debug(msg='Post login data done at time {0}'.format(datetime.now()),
                   by='post_login_data')

    @staticmethod
    def _is_captcha_error(resp_body):
        re_captcha_error = re.compile(text_type(u"验证码错误了"), re.U)
        tree = etree.parse(StringIO(resp_body.decode(encoding='utf-8')), etree.HTMLParser())

        # Iterates all <input> tags
        captcha_error = False
        for u in tree.iterfind('.//script'):
            if u.text is None:
                continue
            captcha_error = True if re_captcha_error.search(u.text) else captcha_error
        if captcha_error:
            raise CAPTCHAError('CAPTCHAError found after post')

    def _get_net_text(self):
        net_text_url = r'http://haijia.bjxueche.net/Login.aspx/GetNetText'

        self.debug(msg='{0} at time {1}'.format(net_text_url, datetime.now()), by='get_net_text')
        _, resp = self.session.open_url_n_read(url=net_text_url)

    def __str__(self):
        return 'Driver: {0}'.format(self.drivername)


class LoginAgain(BaseException):
    def __init__(self, *args, **kwargs):
        if 'logger' in kwargs.keys():
            logger = kwargs['logger']
            logger.debug(msg='Unknown Exception in login:\n{0}'.format(args[0]), by='Login')


class LoginFail(BaseException):
    pass


class LoginForm(dict):
    def __init__(self, drivername, password):
        self['__VIEWSTATE'] = None
        self['__EVENTVALIDATION'] = None
        self['txtUserName'] = drivername
        self['txtPassword'] = password
        self['txtIMGCode'] = None
        self['rcode'] = None

    def load_form_with_parsed_html(self, resp_body):
        tree = etree.parse(StringIO(resp_body.decode(encoding='utf-8')), etree.HTMLParser())
        # Iterates all <input> tags
        for u in tree.iterfind('.//input'):
            name = u.get('id')
            if name in self:
                self[name] = u.get('value') if self[name] is None else self[name]

    def load_captcha(self, captcha):
        self['txtIMGCode'] = captcha
        self['rcode'] = ''

    def urlencode(self):
        s_data_being_posted = urlparse.urlencode([(k, v) for k, v in self.items()])
        s_data_being_posted += '&BtnLogin=%E7%99%BB++%E5%BD%95'
        return s_data_being_posted

    def __str__(self):
        return '\n'.join(['{0}: {1}'.format(key, v) for key, v in self.items()])
