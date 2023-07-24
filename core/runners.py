from queue import Queue
from random import random
from threading import Thread
from time import sleep


class toy_prototype:
    def __init__(self) -> None:
        self.queue = Queue(5)

    def producer(self):
        for _ in range(3):
            value = random()
            sleep(value)
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
