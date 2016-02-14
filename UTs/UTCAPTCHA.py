# encoding=utf-8

import unittest
from Roles.CAPTCHARecognizer import CAPTCHAError, CAPTCHARecognizer
from Roles.Session import Session
from PIL import Image
import numpy as np


class UTCAPTCHA(unittest.TestCase):
    def setUp(self):
        self.session = Session()
        self.dut = CAPTCHARecognizer(self.session)
        CAPTCHARecognizer.ocr_exe_path = 'tesseract'

    def do_test(self, file_name, expect_chars):
        with Image.open('CAPTCHA files/{0}.gif'.format(file_name)) as im:
            img_login_captcha_cv = np.array(im.convert('RGB'))

            self.dut.recognize_captcha(img_login_captcha_cv)
            str_captcha = self.dut.validate_captcha()
            str_captcha = str_captcha.upper()
            expect_chars = expect_chars.upper()
            self.assertEquals(expect_chars, str_captcha)

    def test_file1to5(self):
        expect_chars = ['vfff', 'kfqq', 'q9mc', 'tm41', 'CUHG', 'av85']  # '3yjb']
        for i, the_char in enumerate(expect_chars):
            self.do_test(file_name='{0}'.format(i + 1), expect_chars=the_char)
