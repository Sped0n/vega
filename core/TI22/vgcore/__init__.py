from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Queue
from threading import Thread
from time import sleep, time

from objprint import op

from core.utils import DroneInfo, flush_queue, set_cmd, pusher
from ctyper import PackCorruptedError
from sensia.utils import PoseData
from pin.utils import create_uart_buf, depack_recv_list_to_z
from pin import SerDevice
from cfg import is_darwin, is_linux, is_arm, SER


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
        self.target_queue: Queue[DroneInfo] = Queue(3)
        self.z_queue: Queue[int] = Queue(3)

        # serial device
        if is_darwin and SER is True:
            self.uart = SerDevice(port="usbserial", baudrate=115200)
        elif is_linux and is_arm and SER is True:
            self.uart = SerDevice(port="/dev/ttyS3", baudrate=115200)

        # run it
        self.run()

    def tx(self):
        curr_target = DroneInfo(0, 0, 0, 0, False)
        txstart = time()
        while True:
            curr_pos = self.tx_queue.get()
            # refresh target if not empty
            if self.target_queue.empty is False:
                curr_target = self.target_queue.get()

            if SER is True:
                # create uart buf
                tmp = create_uart_buf(current=curr_pos, target=curr_target)
                self.uart.write(tmp)
            else:
                if time() - txstart > 1:
                    txstart = time()
                    op(curr_pos, curr_target)

    def rx(self):
        while True:
            # read from uart
            if SER is False:
                continue
            tmp = self.uart.read_buf_to_list()
            try:
                z: int = depack_recv_list_to_z(tmp)
            except PackCorruptedError:
                continue
            # push to queue
            print(z)
            pusher(self.z_queue, z)

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
                    mlstart = time()
                    self.ml2vega_queue.get()["ti"]
                    print("ml process fps: ", 1 / (time() - mlstart))
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
        rx_thread = Thread(target=self.rx, daemon=True)
        pose_thread = Thread(target=self.pose_handler, daemon=True)
        mission_thread = Thread(target=self.missionary, daemon=True)

        tx_thread.start()
        rx_thread.start()
        pose_thread.start()
        mission_thread.start()

        tx_thread.join()
        rx_thread.join()
        pose_thread.join()
        mission_thread.join()
