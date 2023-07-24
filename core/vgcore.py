from queue import Empty, Queue
from threading import Thread
from time import sleep
from sensia.utils import PoseData
from multiprocessing import Queue as mQueue
from itertools import count


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
            return next(self.loop_limit) <= 1000000
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
