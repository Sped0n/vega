from core.runners import toy_prototype
from multiprocessing import Queue as mQueue
from multiprocessing import Process
from core.vgcore import basic as vg_basic
from core.sensiacore import basic as sensia_basic


def test_toy_prototype():
    toy_prototype().run()


def test_basic():
    pq = mQueue(5)
    sc = Process(
        target=sensia_basic,
        args=(
            pq,
            True,
        ),
    )
    vc = Process(
        target=vg_basic,
        args=(
            pq,
            True,
        ),
    )
    sc.start()
    vc.start()
    sc.join()
    vc.join()
