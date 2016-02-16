# encoding=utf-8

import unittest
from requests.exceptions import Timeout, RequestException, ConnectionError, HTTPError, ReadTimeout
from Roles.CAPTCHARecognizer import CAPTCHAError, CAPTCHARecognizer
from Roles.Session import Session
from PIL import Image
import numpy as np
from os.path import exists
from time import sleep
import random

from six import PY3
if PY3:
    import opencvpy3.cv2 as cv2
else:
    import opencvpy2.cv2 as cv2


class UTCAPTCHA(unittest.TestCase):
    def setUp(self):
        self.session = Session()
        self.dut = CAPTCHARecognizer(self.session)
        CAPTCHARecognizer.ocr_exe_path = 'tesseract'

    def do_test(self, file_name, expect_chars, do_func):
        with Image.open(file_name) as im:
            img_login_captcha_cv = np.array(im.convert('RGB'))

            self.dut.recognize_captcha(img_login_captcha_cv)
            str_captcha = self.dut.validate_captcha()
            str_captcha = str_captcha.upper()
            expect_chars = expect_chars.upper()
            do_func(expect_chars, str_captcha)

    def test_file1to5(self):
        do_func = lambda expt, obsv: self.assertEquals(expt, obsv)
        expect_chars = ['vfff', 'kfqq', 'q9mc', 'tm41', 'CUHG', 'av85']  # '3yjb']
        for i, the_char in enumerate(expect_chars):
            self.do_test(file_name='CAPTCHA files/{0}.gif'.format(i + 1), expect_chars=the_char, do_func=do_func)

    def test_recognition_rate(self):
        expect_chars_file_path = 'CAPTCHA Rate Eval/dwnld_done'
        dwnld_num = 100
        self.rate = dwnld_num

        def do_func(expt, obsv):
            if expt != obsv:
                self.rate -= 1
                print('{0} <-> {1}'.format(expt, obsv))

        if not exists(expect_chars_file_path):
            for i in range(0, dwnld_num):
                for _ in range(5):
                    try:
                        image_byt = self.dut.download_captcha()
                        img_login_captcha_cv = self.dut.get_opencv_img_from_gif(image_byt)
                        cv2.imwrite('CAPTCHA Rate Eval/{0}.jpg'.format(i), img_login_captcha_cv)
                        sleep(random.randrange(3, 8))
                        break
                    except (Timeout, RequestException, ConnectionError, ReadTimeout, HTTPError):
                        continue
            with open(expect_chars_file_path, 'w') as f:
                f.write('')
            return

        with open(expect_chars_file_path, 'r') as f:
            s_all = f.read()
            expect_chars = s_all.split('\n')

        for i in range(0, dwnld_num):
            try:
                self.do_test(file_name='CAPTCHA Rate Eval/{0}.jpg'.format(i), expect_chars=expect_chars[i],
                             do_func=do_func)
            except CAPTCHAError:
                self.rate -= 1
        print('{0}/{1}'.format(self.rate, dwnld_num))  # Currently 21/39
