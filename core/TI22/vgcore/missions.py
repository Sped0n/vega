from multiprocessing import Queue as mQueue
from queue import Empty

from core.utils import Target


def mission_detect_hula_loop(hula2vega_queue: mQueue, status: Target):
    # allow block
    tmp = hula2vega_queue.get()["hula"]
    return tmp
