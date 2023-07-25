from itertools import count
from multiprocessing import Queue as mQueue
from queue import Empty, Queue
from random import random
from threading import Thread
from time import sleep

from sensia.utils import PoseData


class toy_prototype:
    def __init__(self) -> None:
        self.queue = Queue(5)

    def producer(self):
        for _ in range(3):
            value = random()
            sleep(value / 10)
            if not self.queue.full():
                self.queue.put(value)

    def consumer(self):
        while True:
            _ = self.queue.get()
            self.queue.task_done()

    def run(self):
        consumer_thread = Thread(target=self.consumer, daemon=True)
        consumer_thread.start()
        producers_thread = [Thread(target=self.producer) for _ in range(3)]
        for producer_thread in producers_thread:
            producer_thread.start()
        for producer_thread in producers_thread:
            producer_thread.join()
        self.queue.join()


class basic:
    def __init__(self, pose_queue: mQueue, debug: bool = False) -> None:
        self.pose_queue = pose_queue
        self.tx_queue = Queue(5)
        self.debug = debug
        if self.debug:
            self.loop_limit = count()
        self.run()

    def loop_condition(self):
        if self.debug:
            return next(self.loop_limit) <= 500000
        return True

    def tx(self):
        while self.loop_condition():
            if not self.tx_queue.empty():
                try:
                    tmp = self.tx_queue.get(timeout=0.5)
                    assert len(tmp) == 3
                    assert isinstance(tmp[0], int)
                    assert isinstance(tmp[1], int)
                    assert isinstance(tmp[2], int)
                except Empty:
                    continue
            else:
                pass

    def core(self):
        while self.loop_condition():
            if not self.pose_queue.empty() and not self.tx_queue.full():
                try:
                    data: PoseData = self.pose_queue.get(timeout=0.5)
                except Empty:
                    continue
                tmp = [int(data.roll), int(data.pitch), int(data.yaw)]
                self.tx_queue.put(tmp)
            else:
                pass

    def run(self):
        # warm up
        sleep(1)

        core_thread = Thread(target=self.core)
        core_thread.start()
        tx_thread = Thread(target=self.tx)
        tx_thread.start()
        core_thread.join()
        tx_thread.join()
