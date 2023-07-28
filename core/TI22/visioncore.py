from multiprocessing import Queue as mQueue
from queue import Queue
from threading import Event, Thread
from time import sleep

from core.utils import flush_queue, set_thread_event
from ctyper import Image
from vision.TI22 import plane_detect_hulaloop


class proc:
    def __init__(
        self,
        depth_queue: mQueue,  # input
        vega2vision_queue: mQueue,  # input
        hula2vega_queue: mQueue,  # output
    ) -> None:
        # proc queue init
        self.depth_queue = depth_queue
        self.hula2vega_queue = hula2vega_queue
        self.vega2vision_queue = vega2vision_queue

        # thread queue init
        self.tx_queue = Queue(5)

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
                if self.hula2vega_queue.full() is True:
                    flush_queue(self.hula2vega_queue)
                self.hula2vega_queue.put(res.x_and_angle_differ)
            img: Image = res.visual_debug
            # print(img.shape)

    def manager(self):
        while True:
            # no new command, continue
            cmd: dict[str, bool] = self.vega2vision_queue.get()
            try:
                if cmd["hula"] != self.hula_enable:
                    set_thread_event(self.hula_enable, cmd["hula"])
            except KeyError:
                pass

    def run(self):
        # warm up
        sleep(1)

        manager_thread = Thread(target=self.manager, daemon=True)
        hula_thread = Thread(target=self.hula_scan, daemon=True)

        manager_thread.start()
        hula_thread.start()

        manager_thread.join()
        hula_thread.join()
