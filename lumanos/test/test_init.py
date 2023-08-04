from queue import Queue
from time import time, sleep

import cv2

from cfg import VDBG
from lumanos.device import Mocker
from lumanos.TI23 import mapper, trailer
from luma.core.render import canvas
from compass import corrd2block
from lumanos.utils import Offsetter


def test_ti23_mapper():
    dq = Queue()
    device = Mocker(dbg_queue=dq)
    device.capabilities(width=128, height=64, rotate=0, mode="1")
    start = time()
    t = trailer()
    o_trail = Offsetter((28, -2), 1)
    a, b = corrd2block(1000, -500)
    t.add_dot(o_trail.calc(a, b))
    while True:
        with canvas(device) as draw:
            mapper(draw)
            t.darw(draw)

        sleep(0.02)
        if time() - start > 3:
            break
    device.clear()

    assert dq.empty() is False
    if VDBG:
        print("\nvisual debugging")
        while not dq.empty():
            cv2.imshow("pytest", dq.get())
            cv2.waitKey(20)
        cv2.destroyAllWindows()
    else:
        while not dq.empty():
            assert dq.get().shape == (128, 256, 3)
