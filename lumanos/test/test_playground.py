import os
from queue import Queue

import cv2

from cfg import VDBG
from lumanos.device import Mocker
from lumanos.playground import hello_world


def test_hello_world():
    dq = Queue()
    m = Mocker(dbg_queue=dq)
    hello_world(m)
    assert dq.empty() is False
    print(str(os.environ.get("VDBG")))
    if VDBG:
        print("\nvisual debugging")
        while not dq.empty():
            cv2.imshow("pytest", dq.get())
            cv2.waitKey(20)
    else:
        while not dq.empty():
            assert dq.get().shape == (128, 256, 3)
