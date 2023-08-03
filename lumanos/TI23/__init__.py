from ctyper import Number, Pixel, PixelOffset
from lumanos.utils import Offsetter


def mapper(draw, offset: PixelOffset = (28, 2), scale=1.5):
    o = Offsetter(offset, scale)
    # outline
    draw.rounded_rectangle(
        (o.calc(0, 0), o.calc(48, 40)), outline="white", fill="black"
    )
    # rectangle 1
    draw.rounded_rectangle(
        (o.calc(5, 6), o.calc(16, 15)), outline="white", fill="black"
    )
    # rectangle 2
    draw.rounded_rectangle(
        (o.calc(23, 6), o.calc(31, 15)), outline="white", fill="black"
    )
    # rectangle 3
    draw.rounded_rectangle(
        (o.calc(37, 6), o.calc(45, 15)), outline="white", fill="black"
    )
    # rectangle 4
    draw.rounded_rectangle(
        (o.calc(5, 21), o.calc(13, 29)), outline="white", fill="black"
    )
    # rectangle 5
    draw.rounded_rectangle(
        (o.calc(19, 21), o.calc(30, 29)), outline="white", fill="black"
    )
    # rectangle 6
    draw.rounded_rectangle(
        (o.calc(36, 21), o.calc(45, 36)), outline="white", fill="black"
    )


class trailer:
    def __init__(self) -> None:
        self.dot_list = []

    def add_dot(self, dot: Pixel):
        if dot not in self.dot_list:
            self.dot_list.append(dot)

    def darw(self, draw):
        draw.point(self.dot_list, fill="white")
