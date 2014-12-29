# encoding=utf-8
import unittest
from BookingExecutor import BookingExecutor
from LoginExecutor import LoginExecutor

__author__ = 'mochenx'


class UTBooking(unittest.TestCase):
    def setUp(self):
        self.dut = BookingExecutor('1'*18, '8'*6, '1')




    # TODO: Test cases for BookingExecutor.BookingExecutor#get_car_stat, need a fake HJSession object
    # TODO: Test cases for BookingExecutor.BookingExecutor#book_car, need a fake HJSession object

    def test_get_booking_status(self):
        exector = LoginExecutor('210106198404304617', 'chen84430mo', self.dut.session)
        self.dut.get_cookie()
        exector.run()
        self.dut.get_booking_status('20141220')
