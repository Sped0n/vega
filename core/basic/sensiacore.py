from multiprocessing import Queue as mQueue
from threading import Thread
from time import sleep

from core.utils import flush_queue
from sensia import T265


class basic:
    def __init__(self, pose_queue: mQueue) -> None:
        self.t = T265()
        self.pose_queue = pose_queue
        self.run()

    def core(self):
        while True:
            if self.pose_queue.full():
                flush_queue(self.pose_queue)
            self.pose_queue.put(self.t.fetch())

    def run(self):
        # warm up
        sleep(0.5)

        core_thread = Thread(target=self.core, daemon=True)
        core_thread.start()
        core_thread.join()
        self.t.stop()
