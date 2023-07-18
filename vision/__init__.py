import cv2

from ctyper import Color, Image


def resize_with_pad(
    image: Image,
    new_shape: tuple[int, int],
    padding_color: Color = (255, 255, 255),
) -> Image:
    """
    maintains aspect ratio and resizes with padding.
    :param image: Image to be resized.
    :param new_shape: Expected (width, height) of new image.
    :param padding_color: Tuple in BGR of padding color
    :return: resized image with padding
    """
    original_shape: tuple[int, int] = (image.shape[1], image.shape[0])
    ratio: float = float(max(new_shape)) / max(original_shape)
    new_size: tuple[int, int] = tuple([int(x * ratio) for x in original_shape])
    res: Image = cv2.resize(image, new_size)
    delta_w: int = new_shape[0] - new_size[0]
    delta_h: int = new_shape[1] - new_size[1]
    top: int = delta_h // 2
    bottom: int = delta_h - (delta_h // 2)
    left: int = delta_w // 2
    right: int = delta_w - (delta_w // 2)
    res = cv2.copyMakeBorder(
        res, top, bottom, left, right, cv2.BORDER_CONSTANT, value=padding_color
    )
    return res
