import numpy as np

from vision.TI22.utils import (
    open_op,
    close_op,
    array2image,
    simple_dilate,
    simple_erode,
)

src = np.random.randint(0, 255, (100, 100), dtype=np.uint8)


def test_open_op():
    res = open_op(src, (3, 3))
    assert res.shape == src.shape
    assert np.max(res) <= 255
    assert res.dtype == np.uint8


def test_close_op():
    res = close_op(src, (3, 3))
    assert res.shape == src.shape
    assert np.max(res) <= 255
    assert res.dtype == np.uint8


def test_array2image():
    src_array = np.random.randint(0, 5000, (100, 100))
    res = array2image(src_array, 6000)
    assert res.shape == src_array.shape
    assert np.max(res) <= 255
    assert res.dtype == np.uint8
    res = array2image(src_array)
    assert res.shape == src_array.shape
    assert np.max(res) <= 255
    assert res.dtype == np.uint8


def test_simple_dilate():
    res = simple_dilate(src, (2, 2))
    assert res.shape == src.shape
    assert np.max(res) <= 255
    assert res.dtype == np.uint8
    res = simple_dilate(src, (2, 2), 3)
    assert res.shape == src.shape
    assert np.max(res) <= 255
    assert res.dtype == np.uint8


def test_simple_erode():
    res = simple_erode(src, (2, 2))
    assert res.shape == src.shape
    assert np.max(res) <= 255
    assert res.dtype == np.uint8
    res = simple_erode(src, (2, 2), 3)
    assert res.shape == src.shape
    assert np.max(res) <= 255
    assert res.dtype == np.uint8
