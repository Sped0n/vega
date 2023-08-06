from math import sqrt
from queue import Queue, Empty

from core.utils import DroneInfo
import numpy as np
from ctyper import Number


def is_around(
    status_queue: Queue[DroneInfo],
    z_Queue: Queue[int],
    target: DroneInfo,
    pos_tolerance: int = 250,
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
            + (z - target.z) ** 2
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


def pixel_to_coord(
    center: tuple[int, int],
    pixel: tuple[int, int],
    coord: tuple[int, int],
    height,
    wfov: float = 42.3,
    hfov: float = 33,
    w=640,
    h=480,
):
    pixel_x_diff = center[0] - pixel[0]
    x_diff_degree = (pixel_x_diff / w) * wfov
    x_rad = np.deg2rad(x_diff_degree)
    x_diff = abs(height * np.tan(x_rad))
    if pixel_x_diff < 0:
        x_diff = -x_diff
    pixel_y_diff = center[1] - pixel[1]
    y_diff_degree = (pixel_y_diff / h) * hfov
    y_rad = np.deg2rad(y_diff_degree)
    y_diff = abs(height * np.tan(y_rad))
    if pixel_y_diff < 0:
        y_diff = -y_diff
    return coord[0] + y_diff, coord[1] + x_diff


def get_avg_coord(coord_list: list[tuple[int, int]]) -> tuple[int, int]:
    x: int = 0
    y: int = 0
    for i in coord_list:
        x += i[0]
        y += i[1]
    return int(x / len(coord_list)), (y // len(coord_list))
