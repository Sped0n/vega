from math import sqrt
from queue import Queue, Empty

from core.utils import DroneInfo


def is_around(
    status_queue: Queue[DroneInfo],
    z_Queue: Queue[int],
    target: DroneInfo,
    pos_tolerance: int = 100,
    yaw_tolerance: int = 5,
) -> bool:
    """
    check if the current status is around the target

    >>> sq = Queue()
    >>> sq.put(DroneInfo(0, 0, 0, 0))
    >>> sq.put(DroneInfo(100, 100, 100, 100))
    >>> is_around(sq, DroneInfo(0, 0, 0, 0), 5, 5)
    True
    >>> is_around(sq, DroneInfo(0, 0, 0, 0), 5, 5)
    False

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
