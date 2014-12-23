# encoding=utf-8
import unittest
from BookingExecutor import BookingExecutor
from LoginExecutor import LoginExecutor

__author__ = 'mochenx'


class UTBooking(unittest.TestCase):
    def setUp(self):
        self.dut = BookingExecutor('1'*18, '8'*6, '1')
        self.cars_xml_0 = """<?xml version="1.0" encoding="utf-8"?>
        <string xmlns="http://tempuri.org/">
        [   { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70032" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70040" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70041" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70058" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70064" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70063" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70073" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70035" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70050" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70055" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70068" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70034" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70039" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70045" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70046" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70027" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70062" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70065" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70033" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70038" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70042" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70066" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70037" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70053" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70059" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70060" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70061" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70067" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70044" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70047" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70049" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70052" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70036" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70069" },
            { "YYRQ": "20141221", "XNSD": "812", "CNBH": "70051" } ]_0
        </string>
        """
        self.cars_xml_1 = """<?xml version="1.0" encoding="utf-8"?>
                <string xmlns="http://tempuri.org/">[
                  {
                    "YYRQ": "20141224",
                    "XNSD": "812",
                    "CNBH": "05093"
                  },
                  {
                    "YYRQ": "20141224",
                    "XNSD": "812",
                    "CNBH": "05122"
                  },
                  {
                    "YYRQ": "20141224",
                    "XNSD": "812",
                    "CNBH": "05121"
                  },
                  {
                    "YYRQ": "20141224",
                    "XNSD": "812",
                    "CNBH": "05171"
                  },
                  {
                    "YYRQ": "20141224",
                    "XNSD": "812",
                    "CNBH": "05175"
                  },
                  {
                    "YYRQ": "20141224",
                    "XNSD": "812",
                    "CNBH": "05178"
                  }
                ]_1</string>
        """

    def test_convert_time_period_exception(self):
        self.assertRaises(ValueError, lambda: BookingExecutor.convert_time_period(time_period='812'))
        self.assertRaises(ValueError, lambda: BookingExecutor.convert_time_period(time_period='Morn ing'))

    def test_convert_time_period_morning(self):
        self.assertEqual('812', BookingExecutor.convert_time_period(time_period='Morning'))
        self.assertEqual('812', BookingExecutor.convert_time_period(time_period='   Morning'))
        self.assertEqual('812', BookingExecutor.convert_time_period(time_period='Morning '))
        self.assertEqual('812', BookingExecutor.convert_time_period(time_period='   morning  '))

    def test_convert_time_period_afternoon(self):
        self.assertEqual('15', BookingExecutor.convert_time_period(time_period='Afternoon'))
        self.assertEqual('15', BookingExecutor.convert_time_period(time_period='   Afternoon'))
        self.assertEqual('15', BookingExecutor.convert_time_period(time_period='Afternoon  '))
        self.assertEqual('15', BookingExecutor.convert_time_period(time_period='   afternoon  '))

    def test_convert_time_period_evening(self):
        self.assertEqual('58', BookingExecutor.convert_time_period(time_period='Evening'))
        self.assertEqual('58', BookingExecutor.convert_time_period(time_period='   Evening'))
        self.assertEqual('58', BookingExecutor.convert_time_period(time_period='Evening  '))
        self.assertEqual('58', BookingExecutor.convert_time_period(time_period='   evening  '))

    def test_convert_time_period_night(self):
        self.assertEqual('58', BookingExecutor.convert_time_period(time_period='Night'))
        self.assertEqual('58', BookingExecutor.convert_time_period(time_period='   Night'))
        self.assertEqual('58', BookingExecutor.convert_time_period(time_period='Night  '))
        self.assertEqual('58', BookingExecutor.convert_time_period(time_period='   night  '))

    def exe_test_of_get_car_stat_qurey(self, expt_time_period, *stimu):
        expt_str = 'http://haijia.bjxueche.net/Han/ServiceBooking.asmx/GetCars?' \
                   'yyrq={0}&pageNum=1&pageSize=40&xllxID=1&yysd={1}'.format(stimu[0], expt_time_period)
        self.assertEqual(expt_str, BookingExecutor.get_car_stat_qurey(*stimu))

    def test_get_car_stat_qurey_morning(self):
        stimu = ['20141213', '1', 'Morning']
        self.exe_test_of_get_car_stat_qurey('812', *stimu)

    def test_get_car_stat_qurey_night(self):
        stimu = ['20141228', '1', 'night']
        self.exe_test_of_get_car_stat_qurey('58', *stimu)

    def test_parse_car_info_json_tc0(self):
        """
            XML in cars_xml_1 is end of _0
        """
        cars_info = self.dut.parse_car_info_json(self.cars_xml_0)
        self.assertEqual(35, len(cars_info))
        self.assertEqual('70038', cars_info[19]['CNBH'])
        self.assertEqual('70047', cars_info[29]['CNBH'])
        self.assertEqual('70051', cars_info[-1]['CNBH'])

    def test_parse_car_info_json_tc1(self):
        """
            XML in cars_xml_1 is end of _1
        """
        cars_info = self.dut.parse_car_info_json(self.cars_xml_1)
        self.assertEqual(6, len(cars_info))
        self.assertEqual('05121', cars_info[2]['CNBH'])
        self.assertEqual('05178', cars_info[-1]['CNBH'])

    # TODO: Test cases for BookingExecutor.BookingExecutor#get_car_stat, need a fake HJSession object
    # TODO: Test cases for BookingExecutor.BookingExecutor#book_car, need a fake HJSession object

    def test_get_booking_status(self):
        exector = LoginExecutor('210106198404304617', 'chen84430mo', self.dut.session)
        self.dut.get_cookie()
        exector.run()
        self.dut.get_booking_status('20141220')
