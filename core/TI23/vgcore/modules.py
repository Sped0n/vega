from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Queue
from threading import Event
from time import sleep, time

from bt import BTClient
from compass import is_around
from core.utils import DroneInfo, pusher, set_thread_event
from ctyper import ConntectionError


def bt_tx(client: BTClient, send_queue: Queue[str]) -> None:
    while True:
        try:
            tmp = send_queue.get()
            client.send(tmp)
            print("==> bt sent: ", tmp)
        except ConntectionError:
            client.error_handle()


def bt_rx(client: BTClient, bt_start_event: Event) -> None:
    while True:
        try:
            tmp = client.recieve()
            print("==> bt recv: ", tmp)
            if tmp == "PTTO":
                set_thread_event(bt_start_event, True)
        except ConntectionError:
            client.error_handle()


class Scheduler:
    def __init__(
        self,
        task_id: int,
        rx_start: Event,
        bt_start: Event,
        status_queue: Queue[DroneInfo],
        z_queue: Queue[int],
        vega2sensia_queue: mQueue,  # cmd
        vega2ml_queue: mQueue,  # cmd
        ml2vega_queue: mQueue,  # recv
        target_queue: Queue[DroneInfo],
        stage_queue: Queue[int],
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
        self.stage_queue = stage_queue

        # counter init
        self.detect_count: int = 0
        self.fail_count: int = 0
        self.around_count: int = 0
        self.stage: int = 0
        self.roaming: bool = True

        # start
        self.rx_start = rx_start
        self.bt_start = bt_start

        # current target for comparsion
        self.curr_target: DroneInfo = DroneInfo(0, 0, 0, 0)

    def __stage_jump(self, jump_to: int | None = None) -> None:
        if jump_to is None:
            assert jump_to is not None
            self.stage = jump_to
        else:
            self.stage += 1
        pusher(self.stage_queue, self.stage)
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
                    self.bt_start.wait()
                    print("bt start")
                    self.rx_start.wait()
                    print("rx start")
                    self.__stage_jump(1)
                case 1:
                    # Drone takes off and hovers at the starting point
                    if self.roaming is False:
                        tmp_target = DroneInfo(50, -50, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(2)
                case 2:
                    if self.roaming is False:
                        tmp_target = DroneInfo(850, -50, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(3)
                case 3:
                    if self.roaming is False:
                        tmp_target = DroneInfo(1650, -50, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(4)
                case 4:
                    if self.roaming is False:
                        tmp_target = DroneInfo(2450, -50, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(5)
                case 5:
                    if self.roaming is False:
                        tmp_target = DroneInfo(3250, -50, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(6)
                case 6:
                    if self.roaming is False:
                        tmp_target = DroneInfo(3250, -850, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(7)
                case 7:
                    if self.roaming is False:
                        tmp_target = DroneInfo(2450, -850, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(8)
                case 8:
                    if self.roaming is False:
                        tmp_target = DroneInfo(1650, -850, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(9)
                case 9:
                    if self.roaming is False:
                        tmp_target = DroneInfo(850, -850, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(10)
                case 10:
                    if self.roaming is False:
                        tmp_target = DroneInfo(850, -1650, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(11)
                case 11:
                    if self.roaming is False:
                        tmp_target = DroneInfo(1650, -1650, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(12)
                case 12:
                    if self.roaming is False:
                        tmp_target = DroneInfo(2450, -1650, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(13)
                case 13:
                    if self.roaming is False:
                        tmp_target = DroneInfo(3250, -1650, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(14)
                case 14:
                    if self.roaming is False:
                        tmp_target = DroneInfo(3250, -2450, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(15)
                case 15:
                    if self.roaming is False:
                        tmp_target = DroneInfo(2450, -2450, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(16)
                case 16:
                    if self.roaming is False:
                        tmp_target = DroneInfo(1650, -2450, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(17)
                case 17:
                    if self.roaming is False:
                        tmp_target = DroneInfo(850, -2450, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(18)
                case 18:
                    if self.roaming is False:
                        tmp_target = DroneInfo(850, -3250, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(19)
                case 19:
                    if self.roaming is False:
                        tmp_target = DroneInfo(1650, -3250, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(20)
                case 20:
                    if self.roaming is False:
                        tmp_target = DroneInfo(3250, -3250, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(21)
                case 21:
                    if self.roaming is False:
                        tmp_target = DroneInfo(3250, -4050, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(22)
                case 22:
                    if self.roaming is False:
                        tmp_target = DroneInfo(2450, -4050, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(23)
                case 23:
                    if self.roaming is False:
                        tmp_target = DroneInfo(1650, -4050, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(24)
                case 24:
                    if self.roaming is False:
                        tmp_target = DroneInfo(850, -4050, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(25)
                case 25:
                    if self.roaming is False:
                        tmp_target = DroneInfo(850, -4050, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(26)
                case 26:
                    if self.roaming is False:
                        tmp_target = DroneInfo(50, -4050, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(27)
                case 27:
                    if self.roaming is False:
                        tmp_target = DroneInfo(50, -3250, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(28)
                case 28:
                    if self.roaming is False:
                        tmp_target = DroneInfo(50, -2450, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(29)
                case 29:
                    if self.roaming is False:
                        tmp_target = DroneInfo(50, -1650, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(30)
                case 30:
                    if self.roaming is False:
                        tmp_target = DroneInfo(50, -850, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(31)
                case 31:
                    if self.roaming is False:
                        tmp_target = DroneInfo(0, 0, 1600, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.z_queue, self.curr_target):
                            self.around_count += 1
                        # reset counter, we need to be around for 5 times in a row
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 3:
                            self.__stage_jump(32)
                case 32:
                    if self.roaming is False:
                        tmp_target = DroneInfo(0, 0, 0, 0, True)
                    else:
                        sleep(5)

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
