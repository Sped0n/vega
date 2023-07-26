from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Queue

from ctyper import Number


class Target:
    def __init__(
        self, x: Number = 0, y: Number = 0, z: Number = 0, yaw: Number = 0
    ) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw


def flush_queue(queue: Queue | mQueue):
    while not queue.empty():
        queue.get()
