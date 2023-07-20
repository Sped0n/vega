from pathlib import Path

import cv2

from ctyper import InputSize
from ml import Model

TEST_DATA_DIR = str(Path(__file__).resolve().parent / "data") + "/"


# onnxruntime test
def test_onnx_abs_path_init():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ort")
    assert model.backend_type == "ort"


def test_onnx_abs_path_init_robust():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test.onnx", isize, "ort")
    assert model.backend_type == "ort"


def test_onnx_rel_path_init():
    isize = InputSize(416, 416)
    model = Model("./ml/test/data/test", isize, "ort")
    assert model.backend_type == "ort"


def test_onnx_rel_path_init_robust():
    isize = InputSize(h=416, w=416)
    model = Model("./ml/test/data/test.onnx", isize, "ort")
    assert model.backend_type == "ort"


def test_onnx_infer():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ort")
    frame = cv2.imread(TEST_DATA_DIR + "bus.jpg")
    result = model.infer(frame)
    # box, score, label
    assert len(result) == 3
    # label verification
    assert len(result[2]) == 5
    human_counter = 0
    bus_counter = 0
    for label_index in result[2]:
        if label_index == 0:
            human_counter += 1
        elif label_index == 5:
            bus_counter += 1
        else:
            pass
    assert human_counter == 4
    assert bus_counter == 1
    # score verification
    assert len(result[1]) == 5
    for score in result[1]:
        assert score > 0.25


# ncnn test
def test_ncnn_abs_path_init():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ncnn")
    assert model.backend_type == "ncnn"


def test_ncnn_abs_path_init_robust():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test.bin", isize, "ncnn")
    assert model.backend_type == "ncnn"


def test_ncnn_rel_path_init():
    isize = InputSize(416, 416)
    model = Model("./ml/test/data/test", isize, "ncnn")
    assert model.backend_type == "ncnn"


def test_ncnn_rel_path_init_robust():
    isize = InputSize(h=416, w=416)
    model = Model("./ml/test/data/test.bin", isize, "ncnn")
    assert model.backend_type == "ncnn"


def test_ncnn_infer():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ncnn")
    frame = cv2.imread(TEST_DATA_DIR + "bus.jpg")
    result = model.infer(frame)
    # box, score, label
    assert len(result) == 3
    # label verification
    assert len(result[2]) == 5
    human_counter = 0
    bus_counter = 0
    for label_index in result[2]:
        if label_index == 0:
            human_counter += 1
        elif label_index == 5:
            bus_counter += 1
        else:
            pass
    assert human_counter == 4
    assert bus_counter == 1
    # score verification
    assert len(result[1]) == 5
    for score in result[1]:
        assert score > 0.25
