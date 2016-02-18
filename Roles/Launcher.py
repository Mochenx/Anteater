# encoding=utf-8

from threading import Thread, Semaphore, Event
from threading import enumerate
import time
from random import randrange
from Logger import Logger

__author__ = 'mochenx'


class Launcher(Logger):
    """ Launcher initiates car booking threads simultaneously, and manges these threads """

    def __init__(self, max_thread_number=10):
        super(Launcher, self).__init__()

        self.work_threads = None
        self._supervisor = Thread(target=self._supervise)

        self._right_of_trigger_event = Semaphore()
        self._thread_done = Event()
        self.working = {}

        self.max_thread_number = max_thread_number
        self.thread_index = 0

    def load_workers(self, workers):
        """ Load a list of callable objects, which supports keyword arguments when being called """
        assert isinstance(workers, list)
        self.work_threads = [Thread(target=worker, kwargs={'work_done': self.work_done}) for worker in workers]

    def run(self):
        """ Start all threads, wait until all have finished """

        # Start supervising thread before all others
        self._supervisor.start()

        for i in range(self.max_thread_number):
            self.start_new_thread()
            self.burst_intervals()

        self._supervisor.join()

    def burst_intervals(self):
        """ For future use, to tweak the interval in bursting threads"""
        time.sleep(randrange(1, 100)/100)

    def _supervise(self):
        """ A task, run in background, supervises and forks new thread """
        all_threads_end = False

        while not all_threads_end:
            self._thread_done.wait()
            all_threads_end = self.manage_working()
            self.start_new_thread()
            self._thread_done.clear()
            self._right_of_trigger_event.release()

    def manage_working(self):
        """ Find which thread has ended and delete it in working queue """

        # Find the terminated threads
        for a_thread in self.working.keys():
            self.working[a_thread] = False
        for a_thread in enumerate():
            if a_thread in self.working.keys():
                self.working[a_thread] = True
        ended_works = [a_thread for a_thread, status in self.working.items() if status is False]

        # Delete all of them
        for a_thread in ended_works:
            del self.working[a_thread]

        return False if len(self.working.keys()) > 0 else True

    def start_new_thread(self):
        """ Start a new thread, and put it in working queue """
        if self.thread_index >= len(self.work_threads):
            return

        new_thread = self.work_threads[self.thread_index]
        self.working[new_thread] = True
        self.thread_index += 1
        new_thread.start()

    def work_done(self):
        """ A method passed to all workers. Each worker call this method when it's going to terminate """
        self._right_of_trigger_event.acquire()
        self._thread_done.set()
