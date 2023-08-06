from multiprocessing import Process
from multiprocessing import Queue as mQueue
from time import sleep

from core.TI23C.mediacore import proc as mproc
from core.TI23C.vgcore import proc as vgproc
from core.TI23C.mlcore import proc as mlproc
from core.TI23C.uicore import proc as uiproc


def test_car_ti23():
    ui2vega_q = mQueue(5)
    transmit_q = mQueue(5)

    cp = Process(
        target=vgproc,
        args=(
            ui2vega_q,
            transmit_q,
        ),
        daemon=True,
    )

    up = Process(
        target=uiproc,
        args=(transmit_q, ui2vega_q),
        daemon=True,
    )

    cp.start()
    up.start()

    cp.join()
    up.join()
