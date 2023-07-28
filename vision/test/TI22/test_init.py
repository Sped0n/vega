from pathlib import Path

import cv2
import numpy as np

from cfg import VDBG
from vision.TI22 import plane_detect_hulaloop

TEST_DATA_DIR = str(Path(__file__).resolve().parent / "data") + "/"


def test_plane_detect_hulaloop_with_valid_result():
    desire_cxs = (2, 71, -116, 88)
    desire_cys = (1103, 1118, 1011, 1015)
    desire_x_differ = (-300, 858, -879, -352)
    desire_angle_differ = (16, -36, 38, 24)
    for i in range(4):
        array = np.load(TEST_DATA_DIR + f"depth{i}.npy")
        res = plane_detect_hulaloop(array)
        # get result check
        assert res.res_valid is True

        # result validation
        assert (int(res.cx_and_cy[0]) - desire_cxs[i]) / desire_cxs[i] < 0.05
        assert (int(res.cx_and_cy[1]) == desire_cys[i]) / desire_cys[i] < 0.05
        assert (int(res.x_and_angle_differ[0]) - desire_x_differ[i]) / desire_x_differ[
            i
        ] < 0.05
        assert (
            int(res.x_and_angle_differ[1]) - desire_angle_differ[i]
        ) / desire_angle_differ[i] < 0.05

        # dbg frame
        frame = res.visual_debug
        if VDBG:
            cv2.imshow("valid hula", frame)
            cv2.waitKey(1000)
        else:
            assert frame.shape == (20, 160, 3)


def test_plane_detect_hulaloop_visual_debug():
    array = np.zeros((92, 160))
    res = plane_detect_hulaloop(array)
    assert res.res_valid is False
    frame = res.visual_debug
    assert frame.shape == (20, 160, 3)
