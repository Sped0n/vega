from pathlib import Path

import cv2
import numpy as np

from cfg import VDBG, colors_80
from ctyper import InputSize
from ml import Model
from objprint import op
from vision.TI23 import filter_box
from compass import pixel_to_coord

TEST_DATA_DIR = str(Path(__file__).resolve().parent / "data") + "/"


# TI2023
def test_pixel_ti23():
    if VDBG is False:
        return None  # skip
    isize = InputSize(416, 416)
    model = Model(TEST_DATA_DIR + "ti2023", isize, "ncnn")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
        k = cv2.waitKey(1)
        if k == 27:
            break
        results = model.infer(frame, conf_thres=0.15, nms_thres=0.5)
        # op(filter_box(results, frame))
        for result in results:
            color = colors_80[result.clsid]
            cx = int((result.box.x0 + result.box.x1) / 2)
            cy = int((result.box.y0 + result.box.y1) / 2)
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

            if not (len(mask[mask > 0]) / len(mask) > 0.3):
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
            print(pixel_to_coord((320, 240), (cx, cy), (0, 0), 1600))
        cv2.imshow("capture", frame)
    cap.release()
    cv2.destroyAllWindows()
