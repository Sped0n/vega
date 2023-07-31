from __future__ import annotations

from multiprocessing import Queue as mQueue
from pathlib import Path
from queue import Empty
from threading import Event, Thread
from time import sleep

from core.utils import get_cmd, pusher
from ctyper import Command, Image, InputSize
from ml import Model

DATA_DIR = str(Path(__file__).resolve().parent / "data") + "/"


class proc:
    def __init__(
        self,
        cam_queue: mQueue[Image],  # input
        vega2ml_queue: mQueue[Command],  # input
        ml2vega_queue: mQueue[dict],  # output
    ) -> None:
        isize = InputSize(416, 416)
        # model init
        self.ti = Model(DATA_DIR + "ti2022", isize, "ncnn")

        # proc queue init
        self.cam_queue = cam_queue
        self.ml2vega_queue = ml2vega_queue
        self.vega2ml_queue = vega2ml_queue

        # default enable options
        self.ti_enable: Event = Event()
        self.ti_enable.clear()  # default disable

        self.run()

    def ti2022(self):
        while True:
            self.ti_enable.wait()

            # data fetch
            try:
                frame = self.cam_queue.get(timeout=3)
            except Empty:
                continue

            # data process
            results = self.ti.infer(frame)
            pusher(self.ml2vega_queue, {"ti": results})

    def manager(self):
        while True:
            # no new command, continue
            cmd: Command = self.vega2ml_queue.get()
            get_cmd(cmd, "ti", self.ti_enable)

    def run(self):
        # warm up
        sleep(1)

        manager_thread = Thread(target=self.manager, daemon=True)
        ti2022_thread = Thread(target=self.ti2022, daemon=True)

        manager_thread.start()
        ti2022_thread.start()

        manager_thread.join()
        ti2022_thread.join()
