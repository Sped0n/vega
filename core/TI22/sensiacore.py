from __future__ import annotations

from itertools import count
from multiprocessing import Queue as mQueue
from threading import Event, Thread
from time import sleep

from core.utils import get_cmd, pusher
from ctyper import Array, Command, FetchError, Image
from sensia import D435, T265, AsyncCam
from sensia.utils import DCData, PoseData, plane_radar_filter


class proc:
    def __init__(
        self,
        pose_queue: mQueue[PoseData],  # output
        depth_queue: mQueue[Array],  # output
        cam_queue: mQueue[Image],  # output
        vega2sensia_queue: mQueue[Command],  # input
    ) -> None:
        # device init
        self.t = T265()
        sleep(0.5)  # need some time to start another rs pipe
        self.d = D435(depth_only=True)
        self.c = AsyncCam(width=1280, height=720)

        # proc queue init
        self.pose_queue = pose_queue
        self.depth_queue = depth_queue
        self.cam_queue = cam_queue
        self.vega2sensia_queue = vega2sensia_queue

        # default enable options
        self.depth_enable: Event = Event()
        self.depth_enable.clear()  # depth: default disable
        self.pose_enable: Event = Event()
        self.pose_enable.set()  # pose: default enable
        self.cam_enable: Event = Event()
        self.cam_enable.clear()  # cam: default disable

        # run it
        self.run()

    def pose_core(self):
        while True:
            # trigger
            self.pose_enable.wait()

            attempts = count()
            # retry if fetch failed
            while True:
                try:
                    tmp: PoseData = self.t.fetch()
                except FetchError:
                    self.d.restart()
                    if next(attempts) <= 3:
                        continue
                    else:
                        raise
                break

            pusher(self.pose_queue, tmp)

    def depth_core(self):
        while True:
            # trigger
            self.depth_enable.wait()

            attempts = count()
            # retry if fetch failed
            while True:
                try:
                    tmp: DCData = self.d.fetch(plane_radar_filter)
                except FetchError:
                    self.d.restart()
                    if next(attempts) <= 3:
                        continue
                    else:
                        raise
                break
            if tmp.dvalid is False:
                continue

            pusher(self.depth_queue, tmp.depth)

    def cam_core(self):
        while True:
            # trigger
            self.cam_enable.wait()

            attempts = count()
            # retry if fetch failed
            while True:
                try:
                    tmp: Image = self.c.fetch()
                except FetchError:
                    self.d.restart()
                    if next(attempts) <= 3:
                        continue
                    else:
                        raise
                break

            pusher(self.cam_queue, tmp)

    def manager(self):
        while True:
            cmd: Command = self.vega2sensia_queue.get()
            get_cmd(cmd, "pose", self.pose_enable)
            get_cmd(cmd, "depth", self.depth_enable)
            get_cmd(cmd, "cam", self.cam_enable)

    def run(self):
        # warm up
        sleep(1)

        manager_thread = Thread(target=self.manager, daemon=True)
        pose_thread = Thread(target=self.pose_core, daemon=True)
        depth_thread = Thread(target=self.depth_core, daemon=True)
        cam_thread = Thread(target=self.cam_core, daemon=True)

        manager_thread.start()
        pose_thread.start()
        depth_thread.start()
        cam_thread.start()

        manager_thread.join()
        pose_thread.join()
        depth_thread.join()
        cam_thread.join()
