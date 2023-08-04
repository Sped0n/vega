from pathlib import Path

import cv2
import numpy as np

from cfg import VDBG, colors_80
from ctyper import InputSize, ObjDetected
from ml import Model
from objprint import op
from vision.TI23 import filter_box

TEST_DATA_DIR = str(Path(__file__).resolve().parent / "data") + "/"


def infer_validator_v8n_bus(res: list[ObjDetected]):
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
        for i, e in enumerate(expected[:]):
            if (cx - e[0]) / e[0] <= 0.1 and (cy - e[1]) / e[1] <= 0.1:
                founded = True
                cmp = expected.pop(i)
                break
        assert founded is True
        if not founded:
            continue
        assert result.clsid == cmp[3]
        assert result.score >= cmp[2]


def infer_validator_v8n_ti0(res: list[ObjDetected]):
    # only for ti0.jpg!!!
    expected = [
        (2040, 483, 0.5, 2),
        (2623, 1662, 0.5, 5),
        (3142, 320, 0.5, 1),
        (653, 634, 0.5, 1),
        (908, 2086, 0.5, 0),
    ]
    # number of detected objects
    assert len(res) == 5
    # label/score/box center verification
    for result in res:
        cx = (result.box.x0 + result.box.x1) // 2
        cy = (result.box.y0 + result.box.y1) // 2
        founded = False
        cmp = (0, 0, 0, 0)
        for i, e in enumerate(expected[:]):
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
    results = model.infer(frame, conf_thres=0.25, nms_thres=0.65)
    infer_validator_v8n_bus(results)
    if VDBG:
        for result in results:
            color = colors_80[result.clsid]
            cv2.rectangle(
                frame,
                (result.box.x0, result.box.y0),
                (result.box.x1, result.box.y1),
                color,
                2,
            )
            cv2.putText(
                frame,
                f"{result.clsid}: {result.score:.2f}",
                (result.box.x0, result.box.y0 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
        cv2.imshow("onnx_infer_bus", frame)
        cv2.waitKey(4000)
        cv2.destroyAllWindows()


def test_onnx_reinit():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ort")
    frame = cv2.imread(TEST_DATA_DIR + "bus.jpg")
    infer_validator_v8n_bus(model.infer(frame, conf_thres=0.25, nms_thres=0.65))
    model.reinit(TEST_DATA_DIR + "ti2022.onnx", isize)
    frame = cv2.imread(TEST_DATA_DIR + "ti0.jpg")
    infer_validator_v8n_ti0(model.infer(frame, conf_thres=0.25, nms_thres=0.65))


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
    results = model.infer(frame, conf_thres=0.25, nms_thres=0.65)
    infer_validator_v8n_bus(results)
    if VDBG:
        for result in results:
            color = colors_80[result.clsid]
            cv2.rectangle(
                frame,
                (result.box.x0, result.box.y0),
                (result.box.x1, result.box.y1),
                color,
                2,
            )
            cv2.putText(
                frame,
                f"{result.clsid}: {result.score:.2f}",
                (result.box.x0, result.box.y0 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
        cv2.imshow("ncnn_infer_bus", frame)
        cv2.waitKey(4000)
        cv2.destroyAllWindows()


def test_ncnn_reinit():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "test", isize, "ncnn")
    frame = cv2.imread(TEST_DATA_DIR + "bus.jpg")
    infer_validator_v8n_bus(model.infer(frame, conf_thres=0.25, nms_thres=0.65))
    model.reinit(TEST_DATA_DIR + "ti2022", isize)
    frame = cv2.imread(TEST_DATA_DIR + "ti0.jpg")
    infer_validator_v8n_ti0(model.infer(frame, conf_thres=0.25, nms_thres=0.65))


# test ti2022
def test_onnx_ti2022():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "ti2022", isize, "ort")
    frame = cv2.imread(TEST_DATA_DIR + "ti0.jpg")
    results = model.infer(frame, conf_thres=0.25, nms_thres=0.65)
    infer_validator_v8n_ti0(results)
    if VDBG:
        for result in results:
            color = colors_80[result.clsid]
            cv2.rectangle(
                frame,
                (result.box.x0, result.box.y0),
                (result.box.x1, result.box.y1),
                color,
                2,
            )
            cv2.putText(
                frame,
                f"{result.clsid}: {result.score:.2f}",
                (result.box.x0, result.box.y0 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
        cv2.imshow("onnx_infer_ti2022", frame)
        cv2.waitKey(4000)
        cv2.destroyAllWindows()


def test_ncnn_ti2022():
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "ti2022", isize, "ncnn")
    frame = cv2.imread(TEST_DATA_DIR + "ti0.jpg")
    results = model.infer(frame, conf_thres=0.25, nms_thres=0.65)
    infer_validator_v8n_ti0(results)
    if VDBG:
        for result in results:
            color = colors_80[result.clsid]
            cv2.rectangle(
                frame,
                (result.box.x0, result.box.y0),
                (result.box.x1, result.box.y1),
                color,
                2,
            )
            cv2.putText(
                frame,
                f"{result.clsid}: {result.score:.2f}",
                (result.box.x0, result.box.y0 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
        cv2.imshow("ncnn_infer_ti2022", frame)
        cv2.waitKey(4000)
        cv2.destroyAllWindows()


def test_ncnn_fov():
    if VDBG is False:
        return None  # skip
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "ti2023", isize, "ncnn")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
        k = cv2.waitKey(1)
        if k == 27:
            break
        results = model.infer(frame, conf_thres=0.25, nms_thres=0.65)
        for result in results:
            color = colors_80[result.clsid]
            cv2.rectangle(
                frame,
                (result.box.x0, result.box.y0),
                (result.box.x1, result.box.y1),
                color,
                2,
            )
            cv2.putText(
                frame,
                f"{result.clsid}: {result.score:.2f}({(result.box.x0 + result.box.x1) / 2 - 640},{(result.box.y0 + result.box.y1) / 2 - 360}",  # noqa: E501
                (result.box.x0, result.box.y0 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
        cv2.imshow("capture", frame)
    cap.release()
    cv2.destroyAllWindows()


# TI2023
def test_ncnn_ti2023():
    if VDBG is False:
        return None  # skip
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "ti2023", isize, "ncnn")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
        k = cv2.waitKey(1)
        if k == 27:
            break
        results = model.infer(frame, conf_thres=0.25, nms_thres=0.65)
        op(filter_box(results, frame))
        for result in results:
            color = colors_80[result.clsid]
            cx = (result.box.x0 + result.box.x1) / 2
            cy = (result.box.y0 + result.box.y1) / 2
            w = result.box.x1 - result.box.x0
            h = result.box.y1 - result.box.y0
            # square
            if not abs(w - h) / (w + h) < 0.04:
                continue
            roi = frame[
                int(cy - 0.17 * h) : int(cy + 0.17 * h),
                int(cx - 0.17 * w) : int(cx + 0.17 * w),
            ]
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            lower_red = np.array([0, 50, 50])
            upper_red = np.array([10, 255, 255])
            mask0 = cv2.inRange(roi, lower_red, upper_red)

            lower_red = np.array([170, 50, 50])
            upper_red = np.array([180, 255, 255])
            mask1 = cv2.inRange(roi, lower_red, upper_red)

            mask = mask0 + mask1

            if not (len(mask[mask > 0]) / len(mask) > 0.25):
                continue

            cv2.rectangle(
                frame,
                (int(cx - 0.17 * h), int(cy - 0.17 * h)),
                (int(cx + 0.17 * h), int(cy + 0.17 * h)),
                color,
                2,
            )
            cv2.rectangle(
                frame,
                (result.box.x0, result.box.y0),
                (result.box.x1, result.box.y1),
                color,
                2,
            )
            cv2.putText(
                frame,
                f"{result.clsid}: {result.score:.2f} --> fire: {(len(mask[mask>0])/len(mask)):.2f}",  # noqa: E501
                (result.box.x0, result.box.y0 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
        cv2.imshow("capture", frame)
    cap.release()
    cv2.destroyAllWindows()
