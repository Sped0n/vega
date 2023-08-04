from multiprocessing import Process
from multiprocessing import Queue as mQueue
from time import sleep

from core.TI23C.mediacore import proc as mproc
from core.TI23C.vgcore import proc as vgproc
from core.TI23C.mlcore import proc as mlproc
from core.TI23C.uicore import proc as uiproc


def test_car_ti23():
    cam_q = mQueue(3)
    vega2media_q = mQueue(5)
    vega2ml_q = mQueue(5)
    ml2vega_q = mQueue(5)
    ui2vega_q = mQueue(5)
    transmit_q = mQueue(5)

    cp = Process(
        target=vgproc,
        args=(
            ml2vega_q,
            ui2vega_q,
            transmit_q,
            vega2media_q,
            vega2ml_q,
        ),
        daemon=True,
    )

    sp = Process(
        target=mproc,
        args=(cam_q, vega2media_q),
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

    up = Process(
        target=uiproc,
        args=(transmit_q, ui2vega_q),
        daemon=True,
    )

    cp.start()
    sp.start()
    mp.start()
    up.start()

    sleep(10)

    cp.kill()
    sp.kill()
    mp.kill()
    up.kill()
