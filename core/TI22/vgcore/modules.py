from __future__ import annotations
from multiprocessing import Queue as mQueue
from queue import Queue, Empty

from core.utils import DroneInfo, pusher
from compass import is_around


class Scheduler:
    def __init__(
        self,
        task_id: int,
        status_queue: Queue[DroneInfo],
        vision2vega_queue: mQueue,
        ml2vega_queue: mQueue,
        target_array: Queue[DroneInfo],
    ) -> None:
        # task id init
        self.task_id = task_id

        # info queues init
        self.status_queue = status_queue
        self.vision2vega_queue = vision2vega_queue
        self.ml2vega_queue = ml2vega_queue
        self.target_array = target_array

        # counter init
        self.detect_count: int = 0
        self.fail_count: int = 0
        self.around_count: int = 0
        self.stage: int = 0
        self.roaming: bool = True

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

    def __task(self) -> None:
        while True:
            tmp_target = DroneInfo(-1, -1, -1, -1)
            match self.stage:
                case -1:
                    tmp_target = DroneInfo(0, 0, 0, 0)
                case 0:
                    # Drone takes off and hovers at the starting point
                    if self.roaming is False:
                        tmp_target = DroneInfo(0, 0, 1500, 0)
                    else:
                        # is around check
                        if is_around(self.status_queue, self.curr_target):
                            self.around_count += 1
                        else:
                            self.around_count = 0
                        # if we are around the target for 5 times in a row,
                        # we are good to go
                        if self.around_count >= 5:
                            self.__stage_jump(1)
                case 1:
                    pass

            # if we have a new target, push it to the target array
            if tmp_target != self.curr_target and tmp_target != DroneInfo(
                -1, -1, -1, -1
            ):
                pusher(self.target_array, tmp_target)
                self.curr_target = tmp_target
                # send the target, start roaming to reach the target
                self.roaming = True
