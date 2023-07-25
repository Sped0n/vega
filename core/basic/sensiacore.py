from threading import Thread
from time import sleep
from sensia import T265
from multiprocessing import Queue as mQueue
from itertools import count


class basic:
    def __init__(self, pose_queue: mQueue, debug: bool = False) -> None:
        self.t = T265()
        self.pose_queue = pose_queue
        self.debug = debug
        if self.debug:
            self.loop_limit = count()
        self.run()

    def loop_condition(self):
        if self.debug:
            return next(self.loop_limit) <= 500000
        return True

    def core(self):
        while self.loop_condition():
            if not self.pose_queue.full():
                self.pose_queue.put(self.t.fetch())
            else:
                pass

    def run(self):
        # warm up
        sleep(1)

        core_thread = Thread(target=self.core)
        core_thread.start()
        core_thread.join()
        self.t.stop()
