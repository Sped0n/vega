from typing import Sequence

import cv2
import numpy as np

from ctyper import Array, Image, InputSize, MatNotValid, MLPreprocessParams


def sigmoid(x: Array) -> Array:
    """
    sigmoid function

    >>> sigmoid(0)
    0.5

    :param x: input
    :return: sigmoid(x)
    """
    return 1.0 / (1.0 + np.exp(-x))


def softmax(x: Array, axis: int = -1) -> Array:
    """
    softmax function

    >>> softmax([0, 1, 2])
    array([0.09003057, 0.24472847, 0.66524096])

    :param x: input
    :param axis: axis
    :return: softmax(x)
    """
    e_x: Array = np.exp(x - np.max(x, axis=axis, keepdims=True))
    y: Array = e_x / e_x.sum(axis=axis, keepdims=True)
    return y


def post_process(
    mats: list[Array],
    conf_thres: float = 0.25,
    nms_thres: float = 0.65,
    reg_max: int = 16,
):
    """
    post process for yolov8
    :param mats: 3 output tensors(detector head) from model output
    :param conf_thres: confidence threshold
    :param nms_thres: nms threshold
    :param reg_max: regression max
    """
    dfl: Array = np.arange(0, reg_max, dtype=np.float32)
    raw_scores: list[float] = []
    raw_boxes: list[Array] = []
    raw_labels: list[int] = []
    for i, mat in enumerate(mats):
        # like (52, 52, 13)
        if mat.ndim == 3:
            pass
        # like (1, 52, 52, 13)
        elif mat.ndim == 4 and mat.shape[0] == 1:
            mat = mat[0]
        else:
            raise MatNotValid(f"mat must be 3d or 4d(shape[0] is 1), got{mat.shape}")

        # 8 -> 16 -> 32
        stride: int = 8 << i
        # split box and class
        bboxes_feat, classes_feat = np.split(
            mat,
            [
                64,
            ],
            -1,
        )

        # process class feat
        classes_feat: Array = sigmoid(classes_feat)
        _argmax: Array = classes_feat.argmax(-1)
        _max: Array = classes_feat.max(-1)

        hi: Array
        wi: Array
        hi, wi = np.where(_max > conf_thres)
        num_proposal: int = hi.size

        # no confidence score above threshold
        if num_proposal == 0:
            continue

        # prepare class and box
        classes = _max[hi, wi]
        bboxes = bboxes_feat[hi, wi].reshape(-1, 4, reg_max)
        bboxes = softmax(bboxes, -1) @ dfl
        argmax = _argmax[hi, wi]

        # iterate over all proposals that have a score above threshold
        for j in range(num_proposal):
            h, w = hi[j], wi[j]
            cls = classes[j]
            # boxes
            x0, y0, x1, y1 = bboxes[j]

            x0 = (w + 0.5 - x0) * stride
            y0 = (h + 0.5 - y0) * stride
            x1 = (w + 0.5 + x1) * stride
            y1 = (h + 0.5 + y1) * stride

            # classes
            clsid = argmax[j]

            raw_scores.append(float(cls))
            raw_boxes.append(np.array([x0, y0, x1 - x0, y1 - y0], dtype=np.float32))
            raw_labels.append(clsid)

    # non maximum suppression
    nms_indices: Sequence[int] = cv2.dnn.NMSBoxesBatched(
        raw_boxes, raw_scores, raw_labels, conf_thres, nms_thres
    )
    scores: list[float] = []
    boxes: list[Array] = []
    labels: list[int] = []
    for idx in nms_indices:
        scores.append(raw_scores[idx])
        boxes.append(raw_boxes[idx])
        labels.append(raw_labels[idx])
    return boxes, scores, labels


def preprocess_params_gen(frame: Image, input_size: InputSize) -> MLPreprocessParams:
    """
    generate preprocess params, like params for resizing and padding
    :param frame: input frame
    :param input_size: input size
    :return: preprocess params
    """
    params = MLPreprocessParams(
        w0=frame.shape[1], h0=frame.shape[0], w1=-1, h1=-1, wpad=-1, hpad=-1, scale=-1.0
    )

    if params.w0 > params.h0:
        params.scale = float(input_size.w / params.w0)
        params.w1 = input_size.w
        params.h1 = int(params.h0 * params.scale)
        params.wpad = 0
        params.hpad = input_size.h - params.h1
    else:
        params.scale = float(input_size.h / params.h0)
        params.h1 = input_size.h
        params.w1 = int(params.w0 * params.scale)
        params.hpad = 0
        params.wpad = input_size.w - params.w1
    return params
