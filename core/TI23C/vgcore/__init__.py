from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Queue
from threading import Thread
from time import sleep
from pin import SerDevice


from bt import BTServer
from core.utils import pusher
from pin.utils import create_uart_buf_car

from .modules import bt_rx, bt_tx, Transmit


class proc:
    def __init__(
        self,
        ui2vega_queue: mQueue,  # input, used for set take off sending op flag
        transmit_queue: mQueue[Transmit],  # output
    ) -> None:
        # proc queue init
        self.transmit_queue = transmit_queue
        self.ui2vega_queue = ui2vega_queue

        # thread queue init
        self.bt_tx_queue: Queue[str] = Queue(15)  # queue for take off message
        self.bt_rx_queue: Queue[str] = Queue(3)  # queue for sending coord to bt_tx
        self.key1_queue: Queue[int] = Queue(3)  # queue for keyboard stream 1
        self.key2_queue: Queue[int] = Queue(3)  # basically the same as stream 1

        # fire queue
        self.fire_queue = Queue(3)

        # bt server
        self.bt = BTServer("875c95f9-e17d-4877-b96a-f559e5bff58c")
        self.uart = SerDevice("/dev/ttyS4", 115200)

        # run it
        self.run()

    def tx(self):
        # init target
        while True:
            tmp = self.fire_queue.get()
            # create uart buf
            buf = create_uart_buf_car(tmp)
            # send pose and target
            self.uart.write(buf)

    def rx(self):
        pass

    def transmit_handler(self):
        while True:
            # get data from queue
            tmp: str = self.bt_rx_queue.get()
            _slice = tmp.split(",")
            if len(_slice) != 6:
                continue
            tmp1 = Transmit(
                x=int(_slice[0]),
                y=int(_slice[1]),
            )
            if _slice[2] != "N/A" and _slice[3] != "N/A":
                tmp1.fire_x = int(_slice[2])
                tmp1.fire_y = int(_slice[3])
            if _slice[4] != "N/A":
                tmp1.stage = int(_slice[4])
            tmp1.fire = int(_slice[5])
            # push fire
            pusher(self.fire_queue, tmp1.fire)

            pusher(self.transmit_queue, tmp1)

    def take_off_handler(self):
        while True:
            cmd = self.ui2vega_queue.get()
            for _ in range(10):
                pusher(self.bt_tx_queue, cmd)

    def run(self):
        # warm up
        sleep(1)

        tx_thread = Thread(target=self.tx, daemon=True)
        rx_thread = Thread(target=self.rx, daemon=True)
        bt_send_thread = Thread(
            target=bt_tx,
            args=(
                self.bt,
                self.bt_tx_queue,
            ),
            daemon=True,
        )
        bt_recv_thread = Thread(
            target=bt_rx,
            args=(
                self.bt,
                self.bt_rx_queue,
            ),
            daemon=True,
        )
        pos_thread = Thread(target=self.transmit_handler, daemon=True)
        take_off_thread = Thread(target=self.take_off_handler, daemon=True)

        tx_thread.start()
        rx_thread.start()
        bt_send_thread.start()
        bt_recv_thread.start()
        pos_thread.start()
        take_off_thread.start()

        tx_thread.join()
        rx_thread.join()
        bt_send_thread.join()
        bt_recv_thread.join()
        pos_thread.join()
        take_off_thread.join()
