from __future__ import annotations

from multiprocessing import Queue as mQueue
from threading import Event, Thread
from time import sleep

from core.utils import get_cmd, pusher
from ctyper import Array, Command, Image
from vision.TI22 import plane_detect_hulaloop


class proc:
    def __init__(
        self,
        depth_queue: mQueue[Array],  # input
        vega2vision_queue: mQueue[Command],  # input
        vision2vega_queue: mQueue[dict],  # output
    ) -> None:
        # proc queue init
        self.depth_queue = depth_queue
        self.vision2vega_queue = vision2vega_queue
        self.vega2vision_queue = vega2vision_queue

        # default enable options
        self.hula_enable: Event = Event()
        self.hula_enable.clear()  # default disable

        self.run()

    def hula_scan(self):
        while True:
            self.hula_enable.wait()

            # data fetch
            depth = self.depth_queue.get()

            # data process
            res = plane_detect_hulaloop(depth)
            if res.res_valid is True:
                pusher(self.vision2vega_queue, {"hula": res.x_and_angle_differ})
            img: Image = res.visual_debug
            # print(img.shape)

    def manager(self):
        while True:
            # no new command, continue
            cmd: Command = self.vega2vision_queue.get()
            get_cmd(cmd, "hula", self.hula_enable)

    def run(self):
        # warm up
        sleep(1)

        manager_thread = Thread(target=self.manager, daemon=True)
        hula_thread = Thread(target=self.hula_scan, daemon=True)

        manager_thread.start()
        hula_thread.start()

        manager_thread.join()
        hula_thread.join()
