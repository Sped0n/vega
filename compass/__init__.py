from math import sqrt
from queue import Queue, Empty

from core.utils import DroneInfo


def is_around(
    status_queue: Queue[DroneInfo],
    z_Queue: Queue[int],
    target: DroneInfo,
    pos_tolerance: int = 150,
    yaw_tolerance: int = 7,
) -> bool:
    """
    check if the current status is around the target

    :param status: current status
    :param target: target
    :return: if the current status is around the target
    """
    # get status_queue
    try:
        status = status_queue.get(timeout=1)
    except Empty:
        return False
    try:
        z = z_Queue.get(timeout=3)
    except Empty:
        return False
    # get z_Queue
    pos_around: bool = (
        sqrt(
            (status.x - target.x) ** 2
            + (status.y - target.y) ** 2
            + 0.7 * ((z - target.z) ** 2)
        )
        <= pos_tolerance
    )
    yaw_around: bool = abs(status.yaw - target.yaw) <= yaw_tolerance
    return pos_around and yaw_around


def corrd2block(x, y):
    y_tmp = 60 - round(x / 100 / 40 * 60)
    x_tmp = -round(y / 100 / 48 * 72)
    return x_tmp, y_tmp


class Odemeter:
    def __init__(self):
        self.x: int = 0
        self.y: int = 0
        self.last_x: int = 0
        self.last_y: int = 0
        self.distance: int = 0

    def add(self, coord: tuple[int, int]):
        tmpx: int = round(coord[0] / 10)
        tmpy: int = round(coord[1] / 10)
        diff = int(sqrt((tmpx - self.x) ** 2 + (tmpy - self.y) ** 2))
        if diff > 10:
            self.distance += diff
            self.x = tmpx
            self.y = tmpy
        return self.distance
