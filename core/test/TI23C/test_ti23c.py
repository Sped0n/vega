from multiprocessing import Process
from multiprocessing import Queue as mQueue
from time import sleep

from cfg import NORS
from core.TI23C.mediacore import proc as mproc
from core.TI23.vgcore import proc as vgproc
from core.TI23.mlcore import proc as mlproc


def test_ti23():
    if NORS is True:
        return None
    pose_q = mQueue(5)
    cam_q = mQueue(3)
    vega2sensia_q = mQueue(5)
    vega2ml_q = mQueue(5)
    ml2vega_q = mQueue(5)
    pos2ml_q = mQueue(5)

    cp = Process(
        target=vgproc,
        args=(
            pose_q,
            ml2vega_q,
            pos2ml_q,
            vega2sensia_q,
            vega2ml_q,
        ),
        daemon=True,
    )

    sp = Process(
        target=mproc,
        args=(pose_q, cam_q, vega2sensia_q, pos2ml_q),
        daemon=True,
    )

    mp = Process(
        target=mlproc,
        args=(
            cam_q,
            vega2ml_q,
            ml2vega_q,
        ),
        daemon=True,
    )

    cp.start()
    sp.start()
    mp.start()

    sleep(10)

    cp.kill()
    sp.kill()
    mp.kill()
