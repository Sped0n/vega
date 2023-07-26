from itertools import count
from multiprocessing import Queue as mQueue
from threading import Lock, Thread
from time import sleep

from core.utils import flush_queue
from ctyper import FetchError
from sensia import D435, T265
from sensia.utils import plane_radar_filter


class proc:
    def __init__(
        self,
        pose_queue: mQueue,  # output
        depth_queue: mQueue,  # output
        vega2sensia_queue: mQueue,  # input
    ) -> None:
        # device init
        self.t = T265()
        sleep(0.5)  # need some time to start another rs pipe
        self.d = D435(depth_only=True)

        # proc queue init
        self.pose_queue = pose_queue
        self.depth_queue = depth_queue
        self.vega2sensia_queue = vega2sensia_queue

        # default enable options
        self.depth_enable = False
        self.pose_enable = True

        # run it
        self.run()

    def pose_core(self):
        while True:
            if self.pose_enable is not True:
                continue

            # will put in if not full, so we won't get blocking by the queue put func,
            # and always put the latest frame into queue
            if self.pose_queue.full() is True:
                flush_queue(self.pose_queue)
            self.pose_queue.put(self.t.fetch())

    def depth_core(self):
        while True:
            if self.depth_enable is not True:
                continue

            attempts = count()
            # retry if fetch failed
            while True:
                try:
                    tmp = self.d.fetch(plane_radar_filter)
                except FetchError:
                    self.d.restart()
                    if next(attempts) <= 3:
                        continue
                    else:
                        raise
                break
            if tmp.dvalid is False:
                continue
            if self.depth_queue.full() is True:
                flush_queue(self.depth_queue)
            self.depth_queue.put(tmp.depth)

    def manager(self):
        while True:
            cmd: dict[str, bool] = self.vega2sensia_queue.get()
            try:
                if cmd["depth"] != self.depth_enable:
                    with Lock():
                        self.depth_enable = cmd["depth"]
            except KeyError:
                pass

    def run(self):
        # warm up
        sleep(1)

        manager_thread = Thread(target=self.manager, daemon=True)
        pose_thread = Thread(target=self.pose_core, daemon=True)
        depth_thread = Thread(target=self.depth_core, daemon=True)

        manager_thread.start()
        pose_thread.start()
        depth_thread.start()

        manager_thread.join()
        pose_thread.join()
        depth_thread.join()
