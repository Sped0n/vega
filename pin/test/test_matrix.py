from itertools import count

from pin.matrix import MatrixKeyBoard  # noqa: E402


def test_matrix():
    attempts = count()
    m = MatrixKeyBoard(22, 24, 38, 40)
    while next(attempts) < 150:
        key = m.read()
        if key != -1:
            print(key)
