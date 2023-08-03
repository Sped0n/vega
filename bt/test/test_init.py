from bt import BTServer, BTClient
from threading import Thread
from queue import Queue
import time
from itertools import count


def test_bt_client():
    c = BTClient("94f39d29-7d6d-437d-973b-fba39e49d4ee", "69:5D:D9:F8:52:E9")
    send_q = Queue(20)
    recv_q = Queue(20)

    send_t = Thread(target=c.send_thread, args=(send_q,), daemon=True)
    recv_t = Thread(target=c.recv_thread, args=(recv_q,), daemon=True)

    def io(send_q, recv_q):
        start = time.time()
        c = count()
        while True:
            if time.time() - start > 1:
                tmp = "client send" + str(next(c))
                send_q.put(tmp)
                start = time.time()
            if recv_q.empty() is False:
                print(recv_q.get())

    io_t = Thread(target=io, args=(send_q, recv_q), daemon=True)

    io_t.start()
    send_t.start()
    recv_t.start()

    io_t.join()
    send_t.join()
    recv_t.join()


def test_bt_server():
    c = BTServer("94f39d29-7d6d-437d-973b-fba39e49d4ee")
    send_q = Queue(20)
    recv_q = Queue(20)

    send_t = Thread(target=c.send_thread, args=(send_q,), daemon=True)
    recv_t = Thread(target=c.recv_thread, args=(recv_q,), daemon=True)

    def io(send_q, recv_q):
        start = time.time()
        c = count()
        while True:
            if time.time() - start > 1:
                tmp = "server send" + str(next(c))
                send_q.put(tmp)
                start = time.time()
            if recv_q.empty() is False:
                print(recv_q.get())

    io_t = Thread(target=io, args=(send_q, recv_q), daemon=True)

    io_t.start()
    send_t.start()
    recv_t.start()

    io_t.join()
    send_t.join()
    recv_t.join()
