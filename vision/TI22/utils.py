import cv2
import numpy as np
from ctyper import Image, Array, Number
import dataclasses


@dataclasses.dataclass
class HulaROI:
    x: Number
    y: Number
    bx: int
    by: int
    bw: int
    bh: int
    angle: float
    distance: float


def open_op(src: Image, kernel_size: tuple[int, int]) -> Image:
    """
    perform open operation on src image
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    return cv2.morphologyEx(src, cv2.MORPH_OPEN, kernel)


def close_op(src: Image, kernel_size: tuple[int, int]) -> Image:
    """
    perform close operation on src image
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    return cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel)


def array2image(src: Array, norm_value: Number | None = None) -> Image:
    """
    convert numpy array to image
    """
    if norm_value is None:
        norm_value = src.max() + 1
    return (src / norm_value * 255).astype(np.uint8)


def simple_dilate(src: Image, kernel_size: tuple[int, int], iter: int = 1) -> Image:
    """
    perform simple dilate operation on src image
    """
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.dilate(src, kernel, iterations=iter)


def simple_erode(src: Image, kernel_size: tuple[int, int], iter: int = 1) -> Image:
    """
    perform simple erode operation on src image
    """
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.erode(src, kernel, iterations=iter)


def p2p_distance(x0: Number, x1: Number, y0: Number, y1: Number) -> int:
    """
    calculate the euclidean distance between two points

    >>> p2p_distance(0, 3, 0, 4)
    5
    """
    return int(np.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2))
