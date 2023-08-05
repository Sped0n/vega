from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Queue
from threading import Thread
from time import sleep


from bt import BTServer
from core.utils import pusher

from .modules import bt_rx, bt_tx, Transmit


class proc:
    def __init__(
        self,
        ml2vega_queue: mQueue,  # input
        ui2vega_queue: mQueue,  # input, used for set take off sending op flag
        transmit_queue: mQueue[Transmit],  # output
        vega2media_queue: mQueue,  # output
        vega2ml_queue: mQueue,  # output
    ) -> None:
        # proc queue init
        self.ml2vega_queue = ml2vega_queue
        self.transmit_queue = transmit_queue
        self.vega2media_queue = vega2media_queue
        self.vega2ml_queue = vega2ml_queue
        self.ui2vega_queue = ui2vega_queue

        # thread queue init
        self.bt_tx_queue: Queue[str] = Queue(15)  # queue for take off message
        self.bt_rx_queue: Queue[str] = Queue(3)  # queue for sending coord to bt_tx
        self.key1_queue: Queue[int] = Queue(3)  # queue for keyboard stream 1
        self.key2_queue: Queue[int] = Queue(3)  # basically the same as stream 1

        # bt server
        self.bt = BTServer("875c95f9-e17d-4877-b96a-f559e5bff58c")

        # run it
        self.run()

    def tx(self):
        # init target
        pass

    def rx(self):
        pass

    def transmit_handler(self):
        while True:
            # get data from queue
            tmp: str = self.bt_rx_queue.get()
            _slice = tmp.split(",")
            if len(_slice) != 5:
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
