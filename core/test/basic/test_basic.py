from multiprocessing import Process
from multiprocessing import Queue as mQueue
from time import time

from core.basic.sensiacore import basic as sensia_basic
from core.basic.vgcore import basic as vg_basic
from core.basic.vgcore import toy_prototype


def test_toy_prototype():
    toy_prototype().run()


def test_basic():
    pq = mQueue(5)
    sc = Process(
        target=sensia_basic,
        args=(pq,),
    )
    vc = Process(
        target=vg_basic,
        args=(pq,),
    )
    sc.start()
    vc.start()

    start = time()
    while time() - start < 5:
        pass

    sc.kill()
    vc.kill()
