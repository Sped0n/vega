from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Queue
from threading import Thread
from time import sleep, time

from objprint import op

from core.utils import Target, flush_queue
from sensia.utils import PoseData

from .missions import mission_detect_hula_loop


class proc:
    def __init__(
        self,
        pose_queue: mQueue,  # input
        vision2vega_queue: mQueue,  # input
        ml2vega_queue: mQueue,  # input
        vega2vision_queue: mQueue,  # output
        vega2sensia_queue: mQueue,  # output
        vega2ml_queue: mQueue,  # output
    ) -> None:
        # proc queue init
        self.pose_queue = pose_queue
        self.vision2vega_queue = vision2vega_queue
        self.ml2vega_queue = ml2vega_queue
        self.vega2vision_queue = vega2vision_queue
        self.vega2sensia_queue = vega2sensia_queue
        self.vega2ml_queue = vega2ml_queue

        # thread queue init
        self.tx_queue = Queue(5)
        self.status_queue = Queue(3)

        # run it
        self.run()

    def tx(self):
        while True:
            # src is not empty
            tmp = self.tx_queue.get()

            # simulate tx
            # print(tmp)
            # check the data type
            assert len(tmp) == 3
            assert isinstance(tmp[0], int)
            assert isinstance(tmp[1], int)
            assert isinstance(tmp[2], int)

    def pose_handler(self):
        while True:
            # get data from queue
            pose: PoseData = self.pose_queue.get()

            # tx
            tmp = [
                int(pose.roll),
                int(pose.pitch),
                int(pose.yaw),
            ]  # simulate the data processing
            if self.tx_queue.full() is True:
                flush_queue(self.tx_queue)
            self.tx_queue.put(tmp)

            # status
            if self.status_queue.full() is True:
                flush_queue(self.status_queue)
            self.status_queue.put(Target(pose.x, pose.y, pose.z, pose.yaw))

    def missionary(self):
        case = 0
        count = 0
        while True:
            status = self.status_queue.get()
            match case:
                case 0:
                    self.vega2ml_queue.put({"ti": True})
                    self.vega2sensia_queue.put({"cam": True})
                    start = time()
                    self.ml2vega_queue.get()["ti"]
                    print("ml process fps: ", 1 / (time() - start))
                    count += 1
                    if count >= 60:
                        case = 1
                        self.vega2ml_queue.put({"ti": False})
                        self.vega2sensia_queue.put({"cam": False})

                case 1:
                    print("case 1")
                    self.vega2sensia_queue.put({"depth": True})
                    self.vega2vision_queue.put({"hula": True})
                    x = mission_detect_hula_loop(self.vision2vega_queue, status)
                    op(x)

    def run(self):
        # warm up
        sleep(1)

        tx_thread = Thread(target=self.tx, daemon=True)
        pose_thread = Thread(target=self.pose_handler, daemon=True)
        mission_thread = Thread(target=self.missionary, daemon=True)

        tx_thread.start()
        pose_thread.start()
        mission_thread.start()

        tx_thread.join()
        pose_thread.join()
        mission_thread.join()
