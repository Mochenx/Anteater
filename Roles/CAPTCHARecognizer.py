# encoding=utf-8
import cv2
from io import BytesIO
import os
import re
from PIL import Image
import numpy as np
import random

__author__ = 'mochenx'


class CAPTCHAError(BaseException):
    def __init__(self, err_captcha):
        self.err_captcha = err_captcha

    def __str__(self):
        return self.err_captcha


class CAPTCHARecognizer(object):
    def __init__(self, session, prefix_fname=None):
        self.session = session
        if not isinstance(prefix_fname, str):
            prefix_fname = ''
        self.ocr_txt_name = 'login_captcha_ocr' if prefix_fname is None else prefix_fname + '.login_captcha_ocr'
        self.ocr_jpg_name = 'login_captcha' if prefix_fname is None else prefix_fname + '.login_captcha'

    def get_captcha(self):
        self.get_n_recognize_captcha()
        return self.validate_captcha()

    def get_n_recognize_captcha(self):
        rand_num_for_server = float(random.randrange(1, 100))/999

        url_captcha_login = 'http://haijia.bjxueche.net/tools/CreateCode.ashx?key=ImgCode&amp;' \
                            'random={0}'.format(rand_num_for_server)
        _, image_byt = self.session.open_url_n_read(url=url_captcha_login)
        # if save_html:
        #     with open('captcha.jpg', 'wb') as h:
        #         h.write(image_byt)

        img_login_captcha_cv = self.get_opencv_img_from_gif(image_byt)
        img_only_channel_v = self.sel_v_with_threshold(img_login_captcha_cv)
        cv2.imwrite(self.ocr_jpg_name + '.jpg', img_only_channel_v)

        ocr_exe_path = os.path.join(os.path.abspath(os.curdir), 'Tesseract-OCR/tesseract.exe')
        print(ocr_exe_path)
        os.system("{0} {1} {2}".format(ocr_exe_path, self.ocr_jpg_name + '.jpg', self.ocr_txt_name))

        return self.ocr_txt_name + '.txt'

    @staticmethod
    def get_opencv_img_from_gif(img_in_fmt_gif_bytes):
        im = Image.open(BytesIO(img_in_fmt_gif_bytes))
        return np.array(im.convert('RGB'))

    @staticmethod
    def sel_v_with_threshold(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # Otsu's thresholding after Gaussian filtering
        blur = cv2.GaussianBlur(v, (3, 3), 0)
        _, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return th3

    def validate_captcha(self):
        captcha_fname = self.ocr_txt_name + '.txt'
        with open(captcha_fname, 'r') as f:
            s_login_captcha = f.read()
        s_login_captcha = re.sub(r'\s+', '', s_login_captcha)
        if len(s_login_captcha) < 4 or re.search(r'\W', s_login_captcha):
            raise CAPTCHAError(s_login_captcha)
        return s_login_captcha