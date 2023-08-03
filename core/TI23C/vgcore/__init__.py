from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Queue
from threading import Event, Thread
from time import sleep, time

from objprint import op

from bt import BTServer
from core.utils import pusher


class proc:
    def __init__(
        self,
        ml2vega_queue: mQueue,  # input
        pos2media_queue: mQueue[tuple[int, int, int]],  # output
        vega2media_queue: mQueue,  # output
        vega2ml_queue: mQueue,  # output
    ) -> None:
        # proc queue init
        self.ml2vega_queue = ml2vega_queue
        self.pos2media_queue = pos2media_queue
        self.vega2media_queue = vega2media_queue
        self.vega2ml_queue = vega2ml_queue

        # thread queue init
        self.bt_tx_queue: Queue[str] = Queue(3)  # queue for take off message
        self.to_base_queue: Queue[str] = Queue(3)  # queue for sending coord to bt_tx

        # start flag
        self.start = Event()
        self.start.clear()

        # bt server
        self.bt = BTServer("875c95f9-e17d-4877-b96a-f559e5bff58c")

        # run it
        self.run()

    def tx(self):
        # init target
        pass

    def rx(self):
        pass

    def pos_handler(self):
        while True:
            # get data from queue
            tmp: str = self.to_base_queue.get()
            _slice = tmp.split(",")
            if len(_slice) == 3:
                pusher(
                    self.pos2media_queue,
                    (int(_slice[0]), int(_slice[1]), int(_slice[2])),
                )

    def missionary(self):
        pass

    def run(self):
        # warm up
        sleep(1)

        tx_thread = Thread(target=self.tx, daemon=True)
        rx_thread = Thread(target=self.rx, daemon=True)
        bt_send_thread = Thread(
            target=self.bt.send_thread, args=(self.bt_tx_queue,), daemon=True
        )
        bt_recv_thread = Thread(
            target=self.bt.recv_thread, args=(self.to_base_queue,), daemon=True
        )
        pos_thread = Thread(target=self.pos_handler, daemon=True)
        mission_thread = Thread(target=self.missionary, daemon=True)

        tx_thread.start()
        rx_thread.start()
        bt_send_thread.start()
        bt_recv_thread.start()
        pos_thread.start()
        mission_thread.start()

        tx_thread.join()
        rx_thread.join()
        bt_send_thread.join()
        bt_recv_thread.join()
        pos_thread.join()
        mission_thread.join()
