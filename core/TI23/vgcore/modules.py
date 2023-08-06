from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Queue, Empty
from threading import Event
from time import sleep, time

from bt import BTClient
from compass import is_around, pixel_to_coord, get_avg_coord
from core.utils import DroneInfo, pusher, set_thread_event, set_cmd, flush_queue
from ctyper import ConntectionError


def bt_tx(client: BTClient, send_queue: Queue[str]) -> None:
    while True:
        try:
            tmp = send_queue.get()
            client.send(tmp)
            print("==> bt sent: ", tmp)
        except ConntectionError:
            client.error_handle()


def bt_rx(client: BTClient, bt_start_event: Event, adv_event: Event) -> None:
    while True:
        try:
            tmp = client.recieve()
            print("==> bt recv: ", tmp)
            if tmp == "PTTO1":
                sleep(10)
                set_thread_event(bt_start_event, True)
                set_thread_event(adv_event, False)
            elif tmp == "PTTO2":
                sleep(10)
                set_thread_event(bt_start_event, True)
                set_thread_event(adv_event, True)
        except ConntectionError:
            client.error_handle()


class Scheduler:
    def __init__(
        self,
        task_id: int,
        rx_start: Event,
        bt_start: Event,
        adv_event: Event,
        status_queue: Queue[DroneInfo],
        z_queue: Queue[int],
        z_queue2: Queue[int],
        xy_queue: Queue[tuple[int, int]],
        vega2sensia_queue: mQueue,  # cmd
        vega2ml_queue: mQueue,  # cmd
        vega2gpio_queue: mQueue,  # cmd
        ml2vega_queue: mQueue,  # recv
        target_queue: Queue[DroneInfo],
        stage_queue: Queue[int],
        fire_queue: Queue[int],
    ) -> None:
        # task id init
        self.task_id = task_id

        # info queues init
        self.status_queue = status_queue
        self.z_queue = z_queue
        self.z_queue2 = z_queue2
        self.xy_queue = xy_queue
        self.vega2sensia_queue = vega2sensia_queue
        self.vega2ml_queue = vega2ml_queue
        self.vega2gpio_queue = vega2gpio_queue
        self.ml2vega_queue = ml2vega_queue
        self.target_queue = target_queue
        self.stage_queue = stage_queue
        self.adv_event = adv_event
        self.fire_queue = fire_queue

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

    def __go_square(
        self,
        x: int,
        y: int,
        fix_h: int,
        to_stage: int,
        dac: int,
        enable_laser: bool = False,
    ) -> None:
        if enable_laser:
            set_cmd(self.vega2gpio_queue, "laser", True)
        if self.roaming is False:
            self.tmp_target = DroneInfo(x, y, fix_h, 0)
        else:
            # is around check
            if is_around(self.status_queue, self.z_queue, self.curr_target):
                self.around_count += 1
            # reset counter, we need to be around for 5 times in a row
            else:
                self.around_count = 0
            # if we are around the target for 5 times in a row,
            # we are good to go
            if self.around_count >= dac:
                self.__stage_jump(to_stage)

    def __go_block(self, x, y, fix_h, to_stage, dac) -> None:
        # go to block 6
        # disable laser
        set_cmd(self.vega2gpio_queue, "laser", False)
        if self.roaming is False:
            self.tmp_target = DroneInfo(x, y, fix_h, 0)
        else:
            # is around check
            if is_around(self.status_queue, self.z_queue, self.curr_target):
                self.around_count += 1
            # reset counter, we need to be around for 5 times in a row
            else:
                self.around_count = 0
            # if we are around the target for 5 times in a row,
            # we are good to go
            if self.around_count >= dac:
                if self.adv_event.is_set() is True:
                    self.__stage_jump(to_stage)
                else:
                    self.__stage_jump(to_stage + 1)

    def __go_fire(self, fix_drop_h, to_stage, dac, block_id) -> None:
        # clear result before
        flush_queue(self.ml2vega_queue)
        # activate device
        set_cmd(self.vega2ml_queue, "ti", True)
        set_cmd(self.vega2sensia_queue, "cam", True)
        coord_list: list[tuple[int, int]] = []
        for _ in range(30):
            try:
                results = self.ml2vega_queue.get(timeout=0.1)
                for result in results:
                    cx = int((result.box.x0 + result.box.x1) / 2)
                    cy = int((result.box.y0 + result.box.y1) / 2)
                    coord_list.append(
                        pixel_to_coord(
                            (320, 240),
                            (cx, cy),
                            self.xy_queue.get(),
                            self.z_queue2.get(),
                        )
                    )
            except Empty:
                continue
        set_cmd(self.vega2ml_queue, "ti", False)
        set_cmd(self.vega2sensia_queue, "cam", False)
        if len(coord_list) > 10:
            pusher(self.fire_queue, block_id)
            set_cmd(self.vega2gpio_queue, "rlight", True)
            avg = get_avg_coord(coord_list)
            if self.roaming is False:
                self.tmp_target = DroneInfo(avg[0], avg[1], fix_drop_h, 0)
            else:
                # is around check
                if is_around(self.status_queue, self.z_queue, self.curr_target):
                    self.around_count += 1
                # reset counter, we need to be around for 5 times in a row
                else:
                    self.around_count = 0
                # if we are around the target for 5 times in a row,
                # we are good to go
                if self.around_count >= dac:
                    set_cmd(self.vega2gpio_queue, "drop", True)
                    set_cmd(self.vega2gpio_queue, "rlight", False)
                    self.__stage_jump(to_stage)
        else:
            self.__stage_jump(to_stage)

    def __task1(self) -> None:
        start = time()
        self.tmp_target = DroneInfo(-1, -1, -1, -1)
        fix_h = 1600
        fix_drop_h = 1000
        dac = 1
        set_cmd(self.vega2gpio_queue, "laser", True)
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
                    # start
                    self.__go_square(0, 0, fix_h, 2, dac)

                case 2:
                    # col 1 4
                    self.__go_square(850, -250, fix_h, 3, dac)

                case 3:
                    # col 1 3
                    self.__go_square(1650, -250, fix_h, 4, dac)

                case 4:
                    # col 1 2
                    self.__go_square(2450, -250, fix_h, 5, dac)

                case 5:
                    # col 1 1
                    self.__go_square(3050, -250, fix_h, 6, dac)

                case 6:
                    # col 2 1
                    self.__go_square(3050, -850, fix_h, 7, dac)

                case 7:
                    # block 6
                    self.__go_block(2700, -850, fix_h, 8, dac)

                case 8:
                    # fire 6
                    self.__go_fire(fix_drop_h, 9, dac, 6)

                case 9:
                    # col 2 2
                    self.__go_square(2450, -850, fix_h, 10, dac)

                case 10:
                    # col 2 3
                    self.__go_square(1650, -850, fix_h, 11, dac, True)

                case 11:
                    # block 1
                    self.__go_block(1200, -650, fix_h, 12, dac)

                case 12:
                    # fire 1
                    self.__go_fire(fix_drop_h, 13, dac, 1)

                case 13:
                    # col 2 4
                    self.__go_square(850, -850, fix_h, 14, dac)

                case 14:
                    # col 3 4
                    self.__go_square(850, -1650, fix_h, 15, dac, True)

                case 15:
                    # col 3 3
                    self.__go_square(1650, -1650, fix_h, 16, dac)

                case 16:
                    # col 3 2
                    self.__go_square(2450, -1650, fix_h, 17, dac)

                case 17:
                    # col 3 1
                    self.__go_square(3050, -1650, fix_h, 18, dac)

                case 18:
                    # col 4 1
                    self.__go_square(3050, -2450, fix_h, 19, dac)

                case 19:
                    # block 5
                    self.__go_block(2700, -2350, fix_h, 20, dac)

                case 20:
                    # fire 5
                    self.__go_fire(fix_drop_h, 21, dac, 5)

                case 21:
                    # col 4 2
                    self.__go_square(2450, -2450, fix_h, 22, dac)

                case 22:
                    # col 4 3
                    self.__go_square(1650, -2450, fix_h, 23, dac, True)

                case 23:
                    # block 2
                    self.__go_block(1200, -2200, fix_h, 24, dac)

                case 24:
                    # fire 2
                    self.__go_fire(fix_drop_h, 25, dac, 2)

                case 25:
                    # col 4 4
                    self.__go_square(850, -2450, fix_h, 26, dac)

                case 26:
                    # col 5 4
                    self.__go_square(850, -3250, fix_h, 27, dac, True)

                case 27:
                    # col 5 3
                    self.__go_square(1650, -3250, fix_h, 28, dac)

                case 28:
                    # col 5 2
                    self.__go_square(2450, -3250, fix_h, 29, dac)

                case 29:
                    # col 5 1
                    self.__go_square(3050, -3250, fix_h, 30, dac)

                case 30:
                    # col 6 1
                    self.__go_square(3650, -3850, fix_h, 31, dac)

                case 31:
                    # block 4
                    self.__go_block(2700, -3750, fix_h, 32, dac)

                case 32:
                    # fire 4
                    self.__go_fire(fix_drop_h, 33, dac, 4)

                case 33:
                    # col 6 2
                    self.__go_square(2450, -3850, fix_h, 34, dac)

                case 34:
                    # col 6 3
                    self.__go_square(1650, -3850, fix_h, 35, dac, True)

                case 35:
                    # block 3(1)
                    self.__go_block(1250, -3750, fix_h, 36, dac)

                case 36:
                    # fire 3(1)
                    self.__go_fire(fix_drop_h, 37, dac, 3)

                case 37:
                    # col 6 4-1
                    self.__go_square(1050, -3850, fix_h, 38, dac)

                case 38:
                    # col 6 4-2
                    self.__go_square(650, -3850, fix_h, 39, dac, True)

                case 39:
                    # block 3(2)
                    self.__go_block(460, -3750, fix_h, 40, dac)

                case 40:
                    # fire 3(2)
                    self.__go_fire(fix_drop_h, 41, dac, 3)

                case 41:
                    # col 6 5
                    self.__go_square(50, -3850, fix_h, 42, dac)

                case 41:
                    # col 5 5
                    self.__go_square(50, -3250, fix_h, 42, dac, True)

                case 42:
                    # col 4 5
                    self.__go_square(50, -2450, fix_h, 43, dac)

                case 43:
                    # col 3 5
                    self.__go_square(50, -1650, fix_h, 44, dac)

                case 44:
                    # col 2 5
                    self.__go_square(50, -850, fix_h, 45, dac)

                case 45:
                    # col 1 5
                    self.__go_square(0, 0, fix_h, 46, dac)

                case 46:
                    if self.roaming is False:
                        self.tmp_target = DroneInfo(0, 0, 0, 0, True)
                    else:
                        sleep(5)

            # if we have a new target, push it to the target array
            if self.tmp_target != self.curr_target and self.tmp_target != DroneInfo(
                -1, -1, -1, -1
            ):
                pusher(self.target_queue, self.tmp_target)
                self.curr_target = self.tmp_target
                # send the target, start roaming to reach the target
                self.roaming = True

    def run(self) -> None:
        match self.task_id:
            case 1:
                self.__task1()
