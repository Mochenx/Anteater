# encoding=utf-8
from SleepWakeExecutor import SleepingExecutor, LoginAgain
from threading import Thread, active_count
import time
from datetime import datetime

try:
    # Python2
    from urllib import urlencode
except ImportError:
    # Python3
    from urllib.parse import urlencode

__author__ = 'mochenx'


class SleepingExecutorWithoutBooking(SleepingExecutor):
    def __init__(self, *args, **kwargs):
        super(SleepingExecutorWithoutBooking, self).__init__(*args, **kwargs)
        self.fire_cnt = 0

    def book_car(self, car_info):
        book_car_query_args = {'yyrq': car_info[u'YYRQ'],
                               'xnsd': car_info[u'XNSD'],
                               'cnbh': car_info[u'CNBH'],
                               'imgCode': '',
                               'KMID': '1'}
        encoded_book_car_query_args = urlencode([(k, v) for k, v in book_car_query_args.items()])
        book_car_service_url = 'http://haijia.bjxueche.net/Han/ServiceBooking.asmx/BookingCar?'
        self.logger.debug(book_car_service_url + encoded_book_car_query_args, extra={'source': 'fake_book_car'})

        self.fire_cnt += 1
        if self.fire_cnt > 30:
            self.logger.debug('Fake True', extra={'source': 'fake_book_car'})
            return True
        self.logger.debug('Fake False', extra={'source': 'fake_book_car'})
        return False


def main():
    # To avoid the bug of strptime in multiple threads, I invoke strptime before everything else
    # For more details, please refer to this: http://bugs.python.org/issue7980
    datetime.strptime('20141219', '%Y%m%d')

    def worker(*args, **kwargs):
        exector = SleepingExecutor(*args, **kwargs)
        exector.sleep_n_book_on_date()

    def fake_worker(*args, **kwargs):
        exector = SleepingExecutorWithoutBooking(*args, **kwargs)
        exector.sleep_n_book_on_date()

    all_args = [(worker, ['210106198404304617', 'chen84430mo', '2'], {'time_period': 'Morning'}),
                (worker, ['230107198706211520', '0621', '2'], {'time_period': 'Morning'}),
                #(worker, ['130221198312055114', '1205', '2'], {'time_period': 'Morning'})
    ]

    working_threads = [Thread(target=func, args=args, kwargs=kwargs) for func, args, kwargs in all_args]

    existed_threads = active_count()
    print('Before starting, {0} threads are running'.format(existed_threads))
    for a_thread in working_threads:
        rslt = a_thread.start()
        print(a_thread.is_alive())

    while active_count() > existed_threads:
        print('{0} threads are running'.format(active_count()))
        time.sleep(60)


if __name__ == '__main__':
    main()
