from multiprocessing import Process
from multiprocessing import Queue as mQueue
from time import time

from core.TI22.sensiacore import proc as sensiaproc
from core.TI22.vgcore import proc as vgproc
from core.TI22.visioncore import proc as visionproc


def test_ti22():
    pose_q = mQueue(5)
    depth_q = mQueue(5)
    vega2sensia_q = mQueue(5)
    vega2vision_q = mQueue(5)
    hula2vega_q = mQueue(5)

    cp = Process(
        target=vgproc,
        args=(
            pose_q,
            hula2vega_q,
            vega2vision_q,
            vega2sensia_q,
        ),
        daemon=True,
    )

    sp = Process(
        target=sensiaproc,
        args=(
            pose_q,
            depth_q,
            vega2sensia_q,
        ),
        daemon=True,
    )

    vp = Process(
        target=visionproc,
        args=(
            depth_q,
            vega2vision_q,
            hula2vega_q,
        ),
        daemon=True,
    )

    cp.start()
    sp.start()
    vp.start()

    start = time()

    while time() - start < 15:
        pass

    cp.kill()
    sp.kill()
    vp.kill()
