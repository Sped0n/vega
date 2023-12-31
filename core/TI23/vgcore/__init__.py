from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Queue
from threading import Event, Thread
from time import sleep, time

from objprint import op

from bt import BTClient
from cfg import SER, is_arm, is_darwin, is_linux
from core.utils import DroneInfo, pusher, set_cmd
from ctyper import PackCorruptedError
from pin import SerDevice
from pin.utils import create_uart_buf, depack_recv_list_to_z
from sensia.utils import PoseData

from .modules import Scheduler, bt_rx, bt_tx


class proc:
    def __init__(
        self,
        pose_queue: mQueue,  # input
        ml2vega_queue: mQueue,  # input
        vega2sensia_queue: mQueue,  # output
        vega2ml_queue: mQueue,  # output
        vega2gpio_queue: mQueue,  # output
    ) -> None:
        # proc queue init
        self.pose_queue = pose_queue
        self.ml2vega_queue = ml2vega_queue
        self.vega2sensia_queue = vega2sensia_queue
        self.vega2ml_queue = vega2ml_queue
        self.vega2gpio_queue = vega2gpio_queue

        # thread queue init
        self.tx_queue = Queue(5)
        self.status_queue: Queue[DroneInfo] = Queue(3)
        self.target_queue: Queue[DroneInfo] = Queue(3)
        self.z_queue: Queue[int] = Queue(3)
        self.z_queue2: Queue[int] = Queue(15)
        self.xy_queue: Queue[tuple[int, int]] = Queue(15)
        self.bt_rx_queue: Queue[str] = Queue(3)  # queue for take off message
        self.to_base_queue: Queue[str] = Queue(3)  # queue for sending coord to bt_tx
        self.stage_queue: Queue[int] = Queue(3)  # queue for sending stage to bt_tx
        self.fire_queue: Queue[int] = Queue(1)

        # start flag
        self.rx_start = Event()  # receive z from stm32
        self.rx_start.clear()
        self.bt_start = Event()  # receive bt message
        self.bt_start.clear()
        self.adv_event = Event()  # advanced mode
        self.adv_event.clear()

        # bluetooth
        self.bt = BTClient("875c95f9-e17d-4877-b96a-f559e5bff58c", "EC:2E:98:45:0C:4C")

        # serial device
        if is_darwin and SER is True:
            self.uart = SerDevice(port="usbserial", baudrate=115200)
        elif is_linux and is_arm and SER is True:
            self.uart = SerDevice(port="/dev/ttyS3", baudrate=115200)

        # run it
        self.run()

    def tx(self):
        # init target
        curr_target = DroneInfo(0, 0, 0, 0, False)
        txstart = time()
        while True:
            curr_pos = self.tx_queue.get()
            # refresh target if not empty
            if self.target_queue.empty() is False:
                curr_target = self.target_queue.get()
            if SER is True:
                # create uart buf
                tmp = create_uart_buf(current=curr_pos, target=curr_target)
                # send pose and target
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
            tmp: list[int] = self.uart.read_buf_to_list()
            try:
                z: int = depack_recv_list_to_z(tmp)
            except PackCorruptedError:
                continue
            # push to queue
            self.rx_start.set()
            pusher(self.z_queue, z)
            pusher(self.z_queue2, z)

    def pose_handler(self):
        start = time()
        last_stage = 0
        fire = 0
        while True:
            # get data from queue
            pose: PoseData = self.pose_queue.get()

            # send pose to stm32
            pusher(self.tx_queue, pose)

            # push pose to xy queue for pixel to coord
            pusher(self.xy_queue, (pose.x, pose.y))

            # status queue for is_around detect
            pusher(self.status_queue, DroneInfo(pose.x, pose.y, pose.z, pose.yaw))

            # status queue for sending coord to base
            if time() - start > 0.5:
                if self.stage_queue.empty() is False:
                    tmp_stage = self.stage_queue.get()
                    if tmp_stage != last_stage:
                        last_stage = tmp_stage
                if self.fire_queue.empty() is False:
                    fire = self.fire_queue.get()
                tmp: str = (
                    str(pose.x)
                    + ","
                    + str(pose.y)
                    + ",N/A,N/A"
                    + ","
                    + str(last_stage)
                    + ","
                    + str(fire)
                )
                pusher(self.to_base_queue, tmp)
                start = time()

    def missionary(self):
        Scheduler(
            1,
            self.rx_start,
            self.bt_start,
            self.adv_event,
            self.status_queue,
            self.z_queue,
            self.z_queue2,
            self.xy_queue,
            self.vega2sensia_queue,
            self.vega2ml_queue,
            self.vega2gpio_queue,
            self.ml2vega_queue,
            self.target_queue,
            self.stage_queue,
            self.fire_queue,
        ).run()

    def run(self):
        # warm up
        sleep(1)

        tx_thread = Thread(target=self.tx, daemon=True)
        rx_thread = Thread(target=self.rx, daemon=True)
        bt_send_thread = Thread(
            target=bt_tx,
            args=(
                self.bt,
                self.to_base_queue,
            ),
            daemon=True,
        )
        bt_recv_thread = Thread(
            target=bt_rx,
            args=(self.bt, self.bt_start, self.adv_event),
            daemon=True,
        )
        pose_thread = Thread(target=self.pose_handler, daemon=True)
        mission_thread = Thread(target=self.missionary, daemon=True)

        tx_thread.start()
        rx_thread.start()
        bt_send_thread.start()
        bt_recv_thread.start()
        pose_thread.start()
        mission_thread.start()

        tx_thread.join()
        rx_thread.join()
        bt_send_thread.join()
        bt_recv_thread.join()
        pose_thread.join()
        mission_thread.join()
