from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Empty, Queue
from threading import Event

from ctyper import Command


class DroneInfo:
    def __init__(
        self, x: int = 0, y: int = 0, z: int = 0, yaw: int = 0, land: bool = False
    ) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.land = land

    def __eq__(self, __value: DroneInfo) -> bool:
        return (
            self.x == __value.x
            and self.y == __value.y
            and self.z == __value.z
            and self.yaw == __value.yaw
            and self.land == __value.land
        )

    def __ne__(self, __value: DroneInfo) -> bool:
        return not self.__eq__(__value)


def flush_queue(queue: Queue | mQueue, timeout: float = 0.2) -> None:
    """
    flush queue

    >>> q = Queue(2)
    >>> q.put(1)
    >>> q.put(2)
    >>> flush_queue(q)
    >>> q.empty()
    True

    :param queue: multithreading or multiprocessing queue
    :param timeout: timeout for queue flush
    """
    while not queue.empty():
        try:
            queue.get(timeout=timeout)
        except Empty:
            pass


def set_thread_event(e: Event, status: bool) -> None:
    """
    use a more readable way to set event

    >>> e = Event()
    >>> e.set()
    >>> set_thread_event(e, False)
    >>> e.is_set()
    False
    >>> set_thread_event(e, True)
    >>> e.is_set()
    True

    :param e: threading event
    :param status: status that need to set
    """
    if status is True:
        e.set()
    else:
        e.clear()


def pusher(queue: Queue | mQueue, data: object, flush_timeout: float = 0.1) -> None:
    """
    push data into queue, and flush the queue if it is full

    >>> q = Queue(1)
    >>> q.put(1)
    >>> pusher(q, 0)
    >>> q.get()
    0

    :param queue: multithreading or multiprocessing queue
    :param data: data to push
    :param flush_timeout: timeout for queue flush
    """
    if queue.full() is True:
        flush_queue(queue, flush_timeout)
    queue.put(data)


def get_cmd(cmd_dict: dict[str, bool], key: str, event: Event) -> None:
    """
    get cmd from cmd_dict, and set the event

    >>> e = Event()
    >>> e.clear()
    >>> cmd_dict = {'a': True}
    >>> get_cmd(cmd_dict, 'a', e)
    a --> True
    >>> e.is_set()
    True

    :param cmd_dict: command dict
    :param key: key for dict
    :param event: threading event
    """
    try:
        if cmd_dict[key] != event.is_set():
            set_thread_event(event, cmd_dict[key])
            print(f"{key} -->", cmd_dict[key])
    except KeyError:
        pass


def set_cmd(queue: mQueue[Command], key: str, status: bool) -> None:
    """
    send cmd into queue
    >>> q = Queue(1)
    >>> set_cmd(q, 'a', True)
    >>> q.get()["a"]
    True

    :param queue: multiprocessing queue
    :param key: key for dict
    :param status: status that need to set
    """
    pusher(queue, {key: status})
