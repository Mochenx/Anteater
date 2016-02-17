# encoding=utf-8

from threading import Thread, Semaphore, Event
from threading import enumerate
import time
from random import randrange

__author__ = 'mochenx'


class Launcher(object):
    """ Launcher initiates car booking threads simultaneously, and manges these threads """

    # TODO: All printings will be substituted to logger.debug
    def __init__(self):
        self.workers = None
        self.working_threads = None
        self._right_of_trigger_event = Semaphore()
        self._thread_done = Event()
        self._supervisor = Thread(target=self._supervise)

    def load_workers(self, workers):
        """ Load a list of callable objects, which supports keyword arguments when being called """
        assert isinstance(workers, list)
        self.workers = workers
        self.working_threads = [Thread(target=worker, kwargs={'work_done': self.work_done}) for worker in self.workers]

    def run(self):
        """ Start all threads, wait until all have finished """

        # Start supervising thread before all others
        self._supervisor.start()
        print(self._supervisor.is_alive())

        for a_thread in self.working_threads:
            a_thread.start()
            print(a_thread.is_alive())
            time.sleep(randrange(1, 100)/100)

    def _supervise(self):
        while True:
            self._thread_done.wait()
            # TODO: Clean up and start new thread if necessary
            self._thread_done.clear()
            self._right_of_trigger_event.release()

    def work_done(self):
        """ A method passed to all workers. Each worker call this method when it's going to terminate """
        self._right_of_trigger_event.acquire()
        self._thread_done.set()
