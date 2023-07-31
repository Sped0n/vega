from multiprocessing import Queue as mQueue
from queue import Queue
from random import random
from threading import Thread
from time import sleep

from core.utils import flush_queue
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
    def __init__(self, pose_queue: mQueue) -> None:
        self.pose_queue = pose_queue
        self.tx_queue = Queue(5)
        self.run()

    def tx(self):
        while True:
            tmp = self.tx_queue.get()
            assert len(tmp) == 3
            assert isinstance(tmp[0], int)
            assert isinstance(tmp[1], int)
            assert isinstance(tmp[2], int)

    def core(self):
        while True:
            data: PoseData = self.pose_queue.get()
            tmp = [int(data.x), int(data.y), int(data.z)]
            if self.tx_queue.full():
                flush_queue(self.tx_queue)
            self.tx_queue.put(tmp)

    def run(self):
        # warm up
        sleep(0.5)

        core_thread = Thread(target=self.core, daemon=True)
        tx_thread = Thread(target=self.tx, daemon=True)

        core_thread.start()
        tx_thread.start()

        core_thread.join()
        tx_thread.join()
