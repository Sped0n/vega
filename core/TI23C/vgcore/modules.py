from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Empty, Queue
from threading import Event
from time import sleep, time

from bt import BTServer
from compass import is_around
from core.utils import DroneInfo, pusher
from ctyper import ConntectionError


class Transmit:
    def __init__(
        self,
        x,
        y,
        fire_x: int | None = None,
        fire_y: int | None = None,
        stage: int | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.fire_x = fire_x
        self.fire_y = fire_y
        self.stage = stage


def bt_tx(client: BTServer, send_queue: Queue[str]) -> None:
    while True:
        try:
            tmp = send_queue.get()
            client.send(tmp)
            print("=> bt sent: ", tmp)
        except ConntectionError:
            client.error_handle()


def bt_rx(client: BTServer, recv_queue: Queue[str]) -> None:
    while True:
        try:
            pusher(recv_queue, client.recieve())
        except ConntectionError:
            client.error_handle()


class Scheduler:
    def __init__(
        self,
        task_id: int,
        start: Event,
        status_queue: Queue[DroneInfo],
        z_queue: Queue[int],
        vega2sensia_queue: mQueue,  # cmd
        vega2ml_queue: mQueue,  # cmd
        ml2vega_queue: mQueue,  # recv
        target_queue: Queue[DroneInfo],
    ) -> None:
        # task id init
        self.task_id = task_id

        # info queues init
        self.status_queue = status_queue
        self.z_queue = z_queue
        self.vega2sensia_queue = vega2sensia_queue
        self.vega2ml_queue = vega2ml_queue
        self.ml2vega_queue = ml2vega_queue
        self.target_queue = target_queue

        # counter init
        self.detect_count: int = 0
        self.fail_count: int = 0
        self.around_count: int = 0
        self.stage: int = 0
        self.roaming: bool = True

        # start
        self.start = start

        # current target for comparsion
        self.curr_target: DroneInfo = DroneInfo(0, 0, 0, 0)

    def __stage_jump(self, jump_to: int | None = None) -> None:
        if jump_to is None:
            assert jump_to is not None
            self.stage = jump_to
        else:
            self.stage += 1
        self.detect_count = 0
        self.fail_count = 0
        self.around_count = 0
        self.roaming = False

    def __task1(self) -> None:
        start = time()
        tmp_target = DroneInfo(-1, -1, -1, -1)
        while True:
            if time() - start > 1:
                print("stage: ", self.stage)
                start = time()
            match self.stage:
                case 0:
                    self.start.wait()
                    self.__stage_jump(1)
                case 1:
                    # Drone takes off and hovers at the starting point
                    if self.roaming is False:
                        tmp_target = DroneInfo(0, 0, 1500, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 5:
                            self.__stage_jump(2)
                case 2:
                    if self.roaming is False:
                        tmp_target = DroneInfo(500, 0, 1500, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 5:
                            self.__stage_jump(3)
                case 3:
                    if self.roaming is False:
                        tmp_target = DroneInfo(500, -500, 1500, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 5:
                            self.__stage_jump(4)
                case 4:
                    if self.roaming is False:
                        tmp_target = DroneInfo(0, -500, 1500, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 5:
                            self.__stage_jump(5)
                case 5:
                    if self.roaming is False:
                        tmp_target = DroneInfo(0, 0, 1500, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 5:
                            self.__stage_jump(6)
                case 6:
                    if self.roaming is False:
                        tmp_target = DroneInfo(0, 0, 0, 0, True)
                    else:
                        sleep(1)

            # if we have a new target, push it to the target array
            if tmp_target != self.curr_target and tmp_target != DroneInfo(
                -1, -1, -1, -1
            ):
                pusher(self.target_queue, tmp_target)
                self.curr_target = tmp_target
                # send the target, start roaming to reach the target
                self.roaming = True

    def run(self) -> None:
        match self.task_id:
            case 1:
                self.__task1()
