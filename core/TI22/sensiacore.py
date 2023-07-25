from threading import Thread
from time import sleep
from sensia import T265, D435
from sensia.utils import plane_radar_filter
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
            return next(self.loop_limit) <= 1000000
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


class hulaloop:
    def __init__(
        self, pose_queue: mQueue, depth_queue: mQueue, debug: bool = False
    ) -> None:
        self.t = T265()
        sleep(0.5)
        self.d = D435(depth_only=True)
        self.pose_queue = pose_queue
        self.depth_queue = depth_queue
        self.debug = debug
        if self.debug:
            self.loop_limit = count()
        self.run()

    def loop_condition(self):
        if self.debug:
            return next(self.loop_limit) <= 1000000
        return True

    def pose_core(self):
        while self.loop_condition():
            if not self.pose_queue.full():
                self.pose_queue.put(self.t.fetch())
            else:
                pass

    def depth_core(self):
        while self.loop_condition():
            if not self.depth_queue.full():
                self.depth_queue.put(self.d.fetch(plane_radar_filter))
            else:
                pass

    def run(self):
        # warm up
        sleep(1)

        pose_thread = Thread(target=self.pose_core)
        depth_thread = Thread(target=self.depth_core)
        pose_thread.start()
        depth_thread.start()
        pose_thread.join()
        depth_thread.join()
