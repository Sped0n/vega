from itertools import count

import pytest

pin = pytest.importorskip("pin")
from pin.matrix import MatrixKeyBoard  # noqa: E402


def test_matrix():
    attempts = count()
    m = MatrixKeyBoard(22, 24, 38, 40)
    while next(attempts) < 150:
        key = m.get_key()
        if key != -1:
            print(key)
