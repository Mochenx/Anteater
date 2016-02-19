# encoding=utf-8

import re
from datetime import datetime
from lxml import etree
from io import StringIO
from six import with_metaclass, text_type, PY3
import six.moves.urllib.parse as urlparse
from codecs import open

from Roles.Role import RoleCreatorWithLogger, Role, Logger
from Roles.CAPTCHARecognizer import CAPTCHAError, CAPTCHARecognizer
from Roles.Session import URLsForHJ

__author__ = 'mochenx'

if PY3:
    to_bytes = lambda x: bytes(x, encoding='utf-8')
else:
    to_bytes = lambda x: bytes(x)


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
        CAPTCHA_rdr = CAPTCHARecognizer(self.session, prefix_fname=self.log_path)

        for i in range(self.login_repeat_times):
            try:
                login_post_data = self._get_login_form()
                self._get_net_text()
                captcha = CAPTCHA_rdr.get_captcha()
                self.debug(msg=u'CAPTCHA:{0}'.format(captcha), by='Login')
                login_post_data.load_captcha(captcha)
                self._post_login_form(login_post_data)
            except CAPTCHAError as e:
                self.debug(msg=u'CAPTCHA recognition error:{0}'.format(str(e)), by='Login')
                self._get_net_text()
                continue
            except Exception as e:
                raise LoginAgain(str(e), logger=self)
            return True
        raise LoginFail()

    def _get_login_form(self):
        home_page_url = URLsForHJ.connect

        self.debug(msg=u'{0} at time {1}'.format(home_page_url, datetime.now()), by='get_form')
        resp, _ = self.session.open_url_n_read(url=home_page_url)

        login_post_data = LoginForm(self.drivername, self.password)
        # body is a UTF-8 encoded bytes-type variable, so decode it firstly
        self.write_html('{0}.loginform.html'.format(self.drivername), resp.text)
        login_post_data.load_form_with_parsed_html(resp.text)

        return login_post_data

    def _post_login_form(self, login_post_data):
        data_being_posted = login_post_data.urlencode()

        self.debug(msg=u'{0} at time {1}'.format(data_being_posted, datetime.now()),
                   by='post_login_data')
        resp, body = self.session.post_with_response(url=URLsForHJ.login_url,
                                                     data=to_bytes(data_being_posted), timeout=5,
                                                     headers={'content-type': 'application/x-www-form-urlencoded'})

        self._is_captcha_error(resp)
        self.debug(msg=u'Post login data done at time {0}'.format(datetime.now()),
                   by='post_login_data')

    def _is_captcha_error(self, resp):
        re_captcha_error = re.compile(text_type(u"验证码错误了"), re.U)
        self.write_html('{0}.post_resp.html'.format(self.drivername), resp.text)
        tree = etree.parse(StringIO(resp.text), etree.HTMLParser())

        # Iterates all <input> tags
        captcha_error = False
        for u in tree.iterfind('.//script'):
            if u.text is None:
                continue
            captcha_error = True if re_captcha_error.search(u.text) else captcha_error
        if captcha_error:
            raise CAPTCHAError('CAPTCHAError found after post')

    def _get_net_text(self):
        self.debug(msg=u'{0} at time {1}'.format(URLsForHJ.net_text_url, datetime.now()), by='get_net_text')
        resp, _ = self.session.post_with_response(url=URLsForHJ.net_text_url, data=to_bytes(u''),
                                                  headers={'accept': 'application/json',
                                                           'content-type': 'application/json'})
        return resp

    def __str__(self):
        return 'Driver: {0}'.format(self.drivername)


class LoginAgain(BaseException):
    def __init__(self, *args, **kwargs):
        if 'logger' in kwargs.keys():
            logger = kwargs['logger']
            logger.debug(msg=u'Unknown Exception in login:\n{0}'.format(args[0]), by='Login')


class LoginFail(BaseException):
    pass


class LoginForm(dict):
    def __init__(self, drivername, password):
        self['__VIEWSTATE'] = None
        self['__EVENTVALIDATION'] = None
        self['__VIEWSTATEGENERATOR'] = None
        self['txtUserName'] = drivername
        self['txtPassword'] = password
        self['txtIMGCode'] = None

    def load_form_with_parsed_html(self, resp_body):
        tree = etree.parse(StringIO(resp_body), etree.HTMLParser())
        # Iterates all <input> tags
        for u in tree.iterfind('.//input'):
            name = u.get('id')
            if name in self:
                self[name] = u.get('value') if self[name] is None else self[name]

    def load_captcha(self, captcha):
        self['txtIMGCode'] = captcha

    def urlencode(self):
        s_data_being_posted = urlparse.urlencode([(k, v) for k, v in self.items()])
        s_data_being_posted += '&BtnLogin=%E7%99%BB++%E5%BD%95'
        return s_data_being_posted

    def __str__(self):
        return '\n'.join(['{0}: {1}'.format(key, v) for key, v in self.items()])
