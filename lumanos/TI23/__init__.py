from ctyper import Pixel, PixelOffset
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


def welcome_screen(draw):
    draw.text((30, 20), "1: basic", fill="white")
    draw.text((30, 30), "2: advanced", fill="white")


def basic_confirm(draw):
    draw.text((10, 15), "sclecting -> basic", fill="white")
    draw.text((30, 30), "1: confirm", fill="white")
    draw.text((30, 40), "2: cancel", fill="white")


def advanced_confirm(draw):
    draw.text((15, 15), "sclecting -> adv", fill="white")
    draw.text((30, 30), "1: confirm", fill="white")
    draw.text((30, 40), "2: cancel", fill="white")


def basic_layout(
    draw, coord: tuple[int, int], mileage_in_cm: int, stage: int | None = None
):
    draw.rectangle((0, 0, 127, 63), outline="white", fill="black")
    # heading
    draw.text((43, 4), "*basic*", fill="white")
    # line 1: coord
    draw.line((1, 17, 128, 17), fill="white")
    draw.text((1, 17), "coord -> ", fill="white")
    draw.text(
        (1, 27),
        f"x:{(coord[0]/ 1000):.2f}m y:{(coord[1]/ 1000):.2f}m",  # noqa: E501
        fill="white",
        spacing=2,
    )
    draw.line((1, 37, 128, 37), fill="white")
    # line2: mileage
    draw.text((1, 38), "mileage -> ", fill="white")
    draw.text(
        (65, 39),
        f"{mileage_in_cm}cm",  # noqa: E501
        fill="white",
    )
    draw.line((1, 49, 128, 49), fill="white")
    # line3: stage
    draw.text((1, 50), "stage -> ", fill="white")
    if stage is None:
        draw.text((65, 50), "N/A", fill="white")
    else:
        draw.text(
            (65, 50),
            f"{stage}",  # noqa: E501
            fill="white",
        )


def adcanced_layout(
    draw, fire: tuple[int, int], mileage_in_cm: int, stage: int | None = None
):
    draw.rectangle((0, 0, 127, 63), outline="white", fill="black")
    # heading
    draw.text((45, 4), "*adv*", fill="white")
    # line 1: fire
    draw.line((1, 17, 128, 17), fill="white")
    draw.text((1, 17), "fire -> ", fill="white")
    draw.text(
        (1, 27),
        f"x:{(fire[0]/ 1000):.2f}m y:{(fire[1]/ 1000):.2f}m",  # noqa: E501
        fill="white",
        spacing=2,
    )
    draw.line((1, 37, 128, 37), fill="white")
    # line2: mileage
    draw.text((1, 38), "mileage -> ", fill="white")
    draw.text(
        (65, 39),
        f"{mileage_in_cm}cm",  # noqa: E501
        fill="white",
    )
    draw.line((1, 49, 128, 49), fill="white")
    # line3: stage
    draw.text((1, 50), "stage -> ", fill="white")
    if stage is None:
        draw.text((65, 50), "N/A", fill="white")
    else:
        draw.text(
            (65, 50),
            f"{stage}",  # noqa: E501
            fill="white",
        )
