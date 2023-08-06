from __future__ import annotations

from multiprocessing import Queue as mQueue
from threading import Event, Thread
from time import sleep

from core.utils import get_cmd, pusher
from ctyper import Command, Image
from sensia import AsyncCam


class proc:
    def __init__(
        self,
        cam_queue: mQueue[Image],  # output
        vega2media_queue: mQueue[Command],  # input
    ) -> None:
        # device init
        sleep(0.5)
        sleep(0.5)  # need some time to start another rs pipe
        self.c = AsyncCam(width=1280, height=720)

        # proc queue init
        self.cam_queue = cam_queue
        self.vega2media_queue = vega2media_queue

        # default enable options
        self.cam_enable: Event = Event()
        self.cam_enable.clear()  # cam: default disable

        # run it
        self.run()

    def cam_core(self):
        while True:
            # trigger
            self.cam_enable.wait()

            tmp: Image = self.c.fetch()

            pusher(self.cam_queue, tmp)

    def manager(self):
        while True:
            cmd: Command = self.vega2media_queue.get()
            get_cmd(cmd, "cam", self.cam_enable)

    def run(self):
        # warm up
        sleep(1)

        manager_thread = Thread(target=self.manager, daemon=True)
        cam_thread = Thread(target=self.cam_core, daemon=True)

        manager_thread.start()
        cam_thread.start()

        manager_thread.join()
        cam_thread.join()
