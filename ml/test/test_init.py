from pathlib import Path

import cv2

from ctyper import InputSize, ObjDetected
from ml import Model

TEST_DATA_DIR = str(Path(__file__).resolve().parent / "data") + "/"


def infer_validator(res: list[ObjDetected]):
    # only for bus.jpg!!!
    expected = [
        (146, 650, 0.7, 0),
        (416, 492, 0.7, 5),
        (284, 627, 0.65, 0),
        (739, 634, 0.6, 0),
        (32, 720, 0.25, 0),
    ]
    # number of detected objects
    assert len(res) == 5
    # label/score/box center verification
    for result in res:
        cx = (result.box.x0 + result.box.x1) // 2
        cy = (result.box.y0 + result.box.y1) // 2
        founded = False
        cmp = (0, 0, 0, 0)
        for i, e in enumerate(expected):
            if (cx - e[0]) / e[0] <= 0.1 and (cy - e[1]) / e[1] <= 0.1:
                founded = True
                cmp = expected.pop(i)
                break
        assert founded is True
        if not founded:
            continue
        assert result.clsid == cmp[3]
        assert result.score >= cmp[2]


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


def test_onnx_infer_runnable():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ort")
    frame = cv2.imread(TEST_DATA_DIR + "bus.jpg")
    assert model.infer(frame) is not None


def test_onnx_infer_valid():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ort")
    frame = cv2.imread(TEST_DATA_DIR + "bus.jpg")
    infer_validator(model.infer(frame, conf_thres=0.25, nms_thres=0.65))


def test_onnx_reinit():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ort")
    frame = cv2.imread(TEST_DATA_DIR + "bus.jpg")
    infer_validator(model.infer(frame, conf_thres=0.25, nms_thres=0.65))
    model.reinit(TEST_DATA_DIR + "test.onnx", isize)
    infer_validator(model.infer(frame, conf_thres=0.25, nms_thres=0.65))


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


def test_ncnn_infer_runnable():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ncnn")
    frame = cv2.imread(TEST_DATA_DIR + "bus.jpg")
    assert model.infer(frame) is not None


def test_ncnn_infer_valid():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ncnn")
    frame = cv2.imread(TEST_DATA_DIR + "bus.jpg")
    infer_validator(model.infer(frame, conf_thres=0.25, nms_thres=0.65))


def test_ncnn_reinit():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ncnn")
    frame = cv2.imread(TEST_DATA_DIR + "bus.jpg")
    infer_validator(model.infer(frame, conf_thres=0.25, nms_thres=0.65))
    model.reinit(TEST_DATA_DIR + "test.bin", isize)
    infer_validator(model.infer(frame, conf_thres=0.25, nms_thres=0.65))
