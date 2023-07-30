from multiprocessing import Process
from multiprocessing import Queue as mQueue
from time import sleep

from cfg import NORS
from core.TI22.sensiacore import proc as sensiaproc
from core.TI22.vgcore import proc as vgproc
from core.TI22.visioncore import proc as visionproc
from core.TI22.mlcore import proc as mlproc


def test_ti22():
    if NORS is True:
        return None
    pose_q = mQueue(5)
    depth_q = mQueue(5)
    cam_q = mQueue(3)
    vega2sensia_q = mQueue(5)
    vega2vision_q = mQueue(5)
    vega2ml_q = mQueue(5)
    hula2vega_q = mQueue(5)
    ti2vega_q = mQueue(5)

    cp = Process(
        target=vgproc,
        args=(
            pose_q,
            hula2vega_q,
            ti2vega_q,
            vega2vision_q,
            vega2sensia_q,
            vega2ml_q,
        ),
        daemon=True,
    )

    sp = Process(
        target=sensiaproc,
        args=(
            pose_q,
            depth_q,
            cam_q,
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

    mp = Process(
        target=mlproc,
        args=(
            cam_q,
            vega2ml_q,
            ti2vega_q,
        ),
        daemon=True,
    )

    cp.start()
    sp.start()
    vp.start()
    mp.start()

    sleep(10)

    cp.kill()
    sp.kill()
    vp.kill()
    mp.kill()
