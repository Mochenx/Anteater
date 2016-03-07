# encoding=utf-8

import unittest
import json

from Roles.Booker import Booker
from Roles.Role import Role
from Roles.Session import Session

__author__ = 'mochenx'


class UTBooker(unittest.TestCase):
    def setUp(self):
        self.shared_session = Session()
        self.dut = Role.get('Booker')

    def test_creation_n_properties_of_booker(self):
        self.assertTrue(hasattr(self.dut, 'time_periods'))
        self.assertTrue(hasattr(self.dut, 'lesson_type'))
        self.assertTrue(hasattr(self.dut, 'session'))
        self.assertEqual(self.dut.time_periods, None)
        self.assertEqual(self.dut.lesson_type, None)
        self.assertEqual(self.dut.session, None)
        self.dut.time_periods = 'Morning'
        self.assertEqual(self.dut.time_periods, 'Morning')
        print(self.dut.time_periods)
        print(self.dut.lesson_type)
        print(self.dut.session)

    def test_load_properties_success(self):
        self.dut.load_properties(time_periods=['Morning', 'Afternoon'], lesson_type='2', session=self.shared_session)
        self.assertEqual(self.dut.time_periods, ['Morning', 'Afternoon'])
        self.assertEqual(self.dut.lesson_type, '2')
        self.assertIs(self.dut.session, self.shared_session)

    def test_load_properties_fail(self):

        def _no_time_periods():
            self.dut.load_properties(lesson_type='2', session=self.shared_session)

        def _no_lesson_type():
            self.dut.load_properties(time_periods='Night', session=self.shared_session)

        def _no_session():
            self.dut.load_properties(drivername='Afternoon', lesson_type='2')

        self.assertRaises(ValueError, _no_time_periods)
        self.assertRaises(ValueError, _no_lesson_type)
        self.assertRaises(ValueError, _no_session)

    def test_convert_time_period_exception(self):
        self.assertRaises(ValueError, lambda: self.dut._convert_time_period(time_period='710'))
        self.assertRaises(ValueError, lambda: self.dut._convert_time_period(time_period='Morn ing'))

    def test_convert_time_period_morning(self):
        self.assertEqual('710', self.dut._convert_time_period(time_period='Morning'))
        self.assertEqual('710', self.dut._convert_time_period(time_period='   Morning'))
        self.assertEqual('710', self.dut._convert_time_period(time_period='Morning '))
        self.assertEqual('710', self.dut._convert_time_period(time_period='   morning  '))

    def test_convert_time_period_afternoon(self):
        self.assertEqual('1518', self.dut._convert_time_period(time_period='Afternoon'))
        self.assertEqual('1518', self.dut._convert_time_period(time_period='   Afternoon'))
        self.assertEqual('1518', self.dut._convert_time_period(time_period='Afternoon  '))
        self.assertEqual('1518', self.dut._convert_time_period(time_period='   afternoon  '))

    def test_convert_time_period_evening(self):
        self.assertEqual('1820', self.dut._convert_time_period(time_period='Evening'))
        self.assertEqual('1820', self.dut._convert_time_period(time_period='   Evening'))
        self.assertEqual('1820', self.dut._convert_time_period(time_period='Evening  '))
        self.assertEqual('1820', self.dut._convert_time_period(time_period='   evening  '))

    def test_convert_time_period_night(self):
        self.assertEqual('1820', self.dut._convert_time_period(time_period='Night'))
        self.assertEqual('1820', self.dut._convert_time_period(time_period='   Night'))
        self.assertEqual('1820', self.dut._convert_time_period(time_period='Night  '))
        self.assertEqual('1820', self.dut._convert_time_period(time_period='   night  '))

    def exe_test_of_get_car_stat_qurey(self, expt_time_periods, date):
        if not isinstance(expt_time_periods, list):
            expt_time_periods = [expt_time_periods]
        all_expt_str = []
        for expt_time_period in expt_time_periods:
            expt_str = 'http://haijia.bjxueche.net/Han/ServiceBooking.asmx/GetCars?' \
                       'pageNum=1&pageSize=40&xllxID=1&yyrq={0}&yysd={1}'.format(date, expt_time_period)
            all_expt_str.append(expt_str)
        obsv_urls = sorted(self.dut._get_car_stat_qureies(date))
        self.assertEqual(sorted(all_expt_str), obsv_urls)

    def test_get_car_stat_qurey_morning(self):
        stimu = {'date': '20141213', 'time_periods': 'Morning', 'lesson_type': '1'}
        self.dut.load_properties(session=self.shared_session, **stimu)
        self.exe_test_of_get_car_stat_qurey('710', stimu['date'])

    def test_get_car_stat_qurey_night(self):
        stimu = {'date': '20141228', 'time_periods': 'night', 'lesson_type': '1'}
        self.dut.load_properties(session=self.shared_session, **stimu)
        self.exe_test_of_get_car_stat_qurey('1820', stimu['date'])

    def test_get_car_stat_qurey_morning_afternoon(self):
        stimu = {'date': '20141213', 'time_periods': ['Morning', 'afternoon'], 'lesson_type': '1'}
        self.dut.load_properties(session=self.shared_session, **stimu)
        self.exe_test_of_get_car_stat_qurey(['1518', '710'], stimu['date'])

    def test_get_car_stat_qurey_whole_day(self):
        stimu = {'date': '20141213', 'time_periods': ['Morning', 'afternoon', 'Night'], 'lesson_type': '1'}
        self.dut.load_properties(session=self.shared_session, **stimu)
        self.exe_test_of_get_car_stat_qurey(['1518', '710', '1820'], stimu['date'])

    def test_parse_car_info_json_tc0(self):
        """
            XML in cars_xml_1 is end of _0
        """
        cars_info = self.dut._parse_car_info_json(car_xmls.cars_xml_0)
        self.assertEqual(35, len(cars_info))
        self.assertEqual('70038', cars_info[19]['CNBH'])
        self.assertEqual('70047', cars_info[29]['CNBH'])
        self.assertEqual('70051', cars_info[-1]['CNBH'])

    def test_parse_car_info_json_tc1(self):
        """
            XML in cars_xml_1 is end of _1
        """
        cars_info = self.dut._parse_car_info_json(car_xmls.cars_xml_1)
        self.assertEqual(6, len(cars_info))
        self.assertEqual('05121', cars_info[2]['CNBH'])
        self.assertEqual('05178', cars_info[-1]['CNBH'])

    def test_create_cars(self):
        stimu = [{"YYRQ": "20141221", "XNSD": "710", "CNBH": "70032"},
                 {"YYRQ": "20141221", "XNSD": "710", "CNBH": "70040"},
                 {"YYRQ": "20141221", "XNSD": "710", "CNBH": "70041"},
                 {"YYRQ": "20141221", "XNSD": "710", "CNBH": "70058"}]
        self.dut.load_properties(session=self.shared_session, time_periods='Morning', lesson_type='2')
        cars = self.dut._create_cars(stimu)
        for i, v in enumerate(stimu):
            self.assertEqual(cars[i].session, self.shared_session)
            self.assertEqual(cars[i].lesson_type, '2')
            self.assertEqual(cars[i].car_info["YYRQ"], v["YYRQ"])
            self.assertEqual(cars[i].car_info["XNSD"], v["XNSD"])
            self.assertEqual(cars[i].car_info["CNBH"], v["CNBH"])

    def test_parse_book_status(self):
        with open('book_rslt.html', 'r') as f:
            html = f.read()
        self.assertTrue(self.dut.parse_book_status(html, '20160227'))
        self.assertTrue(self.dut.parse_book_status(html, '20160222'))
        self.assertFalse(self.dut.parse_book_status(html, '20160223'))


class car_xmls(object):
    cars_xml_0 = """<?xml version="1.0" encoding="utf-8"?>
        <string xmlns="http://tempuri.org/">
        [   { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70032" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70040" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70041" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70058" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70064" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70063" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70073" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70035" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70050" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70055" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70068" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70034" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70039" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70045" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70046" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70027" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70062" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70065" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70033" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70038" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70042" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70066" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70037" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70053" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70059" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70060" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70061" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70067" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70044" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70047" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70049" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70052" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70036" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70069" },
            { "YYRQ": "20141221", "XNSD": "710", "CNBH": "70051" } ]_0
        </string>
        """
    cars_xml_1 = """<?xml version="1.0" encoding="utf-8"?>
                <string xmlns="http://tempuri.org/">[
                  {
                    "YYRQ": "20141224",
                    "XNSD": "710",
                    "CNBH": "05093"
                  },
                  {
                    "YYRQ": "20141224",
                    "XNSD": "710",
                    "CNBH": "05122"
                  },
                  {
                    "YYRQ": "20141224",
                    "XNSD": "710",
                    "CNBH": "05121"
                  },
                  {
                    "YYRQ": "20141224",
                    "XNSD": "710",
                    "CNBH": "05171"
                  },
                  {
                    "YYRQ": "20141224",
                    "XNSD": "710",
                    "CNBH": "05175"
                  },
                  {
                    "YYRQ": "20141224",
                    "XNSD": "710",
                    "CNBH": "05178"
                  }
                ]_1</string>
        """

    # TODO: Apply new car structure
    """
        {\r\n    \"YYRQ\": \"20160307\",\r\n    \"XNSD\": \"710\",\r\n    \"CNBH\": \"08163\"\r\n  }
        {\r\n    \"YYRQ\": \"20160307\",\r\n    \"XNSD\": \"1112\",\r\n    \"CNBH\": \"08163\"\r\n  }
        {\r\n    \"YYRQ\": \"20160308\",\r\n    \"XNSD\": \"1315\",\r\n    \"CNBH\": \"08079\"\r\n  }
        {\r\n    \"YYRQ\": \"20160308\",\r\n    \"XNSD\": \"1518\",\r\n    \"CNBH\": \"08264\"\r\n  }
    """
