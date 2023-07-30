from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Empty, Queue
from threading import Event

from ctyper import Number


class Target:
    def __init__(
        self, x: Number = 0, y: Number = 0, z: Number = 0, yaw: Number = 0
    ) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw


def flush_queue(queue: Queue | mQueue, timeout: float = 0.2):
    while not queue.empty():
        try:
            queue.get(timeout=timeout)
        except Empty:
            pass


def set_thread_event(e: Event, status: bool):
    if status is True:
        e.set()
    else:
        e.clear()


def pusher(queue: Queue | mQueue, data: object, flush_timeout: float = 0.2):
    """
    push data into queue, and flush the queue if it is full
    """
    if queue.full() is True:
        flush_queue(queue, flush_timeout)
    queue.put(data)


def get_cmd(cmd_dict: dict[str, bool], key: str, event: Event):
    """
    get cmd from cmd_dict, and set the event
    :param cmd_dict: command dict
    :param key: key for dict
    :param event: threading event
    """
    try:
        if cmd_dict[key] != event.is_set():
            set_thread_event(event, cmd_dict[key])
            print(f"{key} change", cmd_dict[key])
    except KeyError:
        pass
