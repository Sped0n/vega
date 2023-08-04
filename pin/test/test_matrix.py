import pytest
from itertools import count

MatrixKeyBoard = pytest.importorskip("pin").matrix.MatrixKeyBoard


def test_matrix():
    attempts = count()
    m = MatrixKeyBoard(22, 24, 38, 40)
    while next(attempts) < 150:
        key = m.get_key()
        if key != -1:
            print(key)
