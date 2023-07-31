from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Queue
from threading import Thread
from time import sleep, time

from objprint import op

from core.utils import DroneInfo, flush_queue, set_cmd
from sensia.utils import PoseData
from pin import create_uart_buf


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
        self.status_queue: Queue[DroneInfo] = Queue(3)
        self.target_array: Queue[DroneInfo] = Queue(3)

        # run it
        self.run()

    def tx(self):
        curr_target = DroneInfo(0, 0, 0, 0)
        while True:
            curr_pos = self.tx_queue.get()
            # refresh target
            if self.target_array.empty is False:
                curr_target = self.target_array.get()
            # create uart buf
            tmp = create_uart_buf(current=curr_pos, target=curr_target, land=False)

            # simulate tx
            # print(tmp)
            # check the data type
            print(tmp)

    def pose_handler(self):
        while True:
            # get data from queue
            pose: PoseData = self.pose_queue.get()

            if self.tx_queue.full() is True:
                flush_queue(self.tx_queue)
            self.tx_queue.put(pose)

            # status
            if self.status_queue.full() is True:
                flush_queue(self.status_queue)
            self.status_queue.put(DroneInfo(pose.x, pose.y, pose.z, pose.yaw))

    def missionary(self):
        case = 0
        count = 0
        while True:
            status = self.status_queue.get()
            match case:
                case 0:
                    set_cmd(self.vega2ml_queue, "ti", True)
                    set_cmd(self.vega2sensia_queue, "cam", True)
                    start = time()
                    self.ml2vega_queue.get()["ti"]
                    print("ml process fps: ", 1 / (time() - start))
                    count += 1
                    if count >= 60:
                        case = 1
                        set_cmd(self.vega2ml_queue, "ti", False)
                        set_cmd(self.vega2sensia_queue, "cam", False)

                case 1:
                    print("case 1")
                    set_cmd(self.vega2sensia_queue, "depth", True)
                    set_cmd(self.vega2vision_queue, "hula", True)
                    x = self.vision2vega_queue.get()["hula"]
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
