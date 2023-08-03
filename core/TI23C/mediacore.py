from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Empty
from threading import Event, Thread
from time import sleep

from luma.core.render import canvas

from compass import corrd2block
from core.utils import get_cmd, pusher
from ctyper import Command, Image
from lumanos.device import OLED1306
from lumanos.TI23 import mapper, trailer
from lumanos.utils import Offsetter
from sensia import AsyncCam


class proc:
    def __init__(
        self,
        cam_queue: mQueue[Image],  # output
        vega2sensia_queue: mQueue[Command],  # input
        pos2media_queue: mQueue[tuple[int, int, int]],  # input
    ) -> None:
        # device init
        sleep(0.5)
        sleep(0.5)  # need some time to start another rs pipe
        self.c = AsyncCam(width=1280, height=720)
        self.disp = OLED1306(6)

        # proc queue init
        self.cam_queue = cam_queue
        self.vega2sensia_queue = vega2sensia_queue
        self.pos2media_queue = pos2media_queue

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

    def display_core(self):
        self.disp.capabilities(width=128, height=64, rotate=0, mode="1")
        t = trailer()
        o_trail = Offsetter((28, 2), 1)
        while True:
            try:
                tmp = self.pos2media_queue.get(timeout=0.5)
            except Empty:
                continue
            a, b = corrd2block(tmp[0], tmp[1])
            t.add_dot(o_trail.calc(a, b))
            with canvas(self.disp) as draw:
                mapper(draw)
                t.darw(draw)

    def manager(self):
        while True:
            cmd: Command = self.vega2sensia_queue.get()
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
