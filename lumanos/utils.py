from ctyper import PixelOffset, Number


class Offsetter:
    def __init__(self, o: PixelOffset, scale: float) -> None:
        self.offset = o
        self.scale = scale

    def calc(self, x: Number, y: Number) -> tuple[int, int]:
        return (
            int(self.offset[0] + x * self.scale),
            int(self.offset[1] + y * self.scale),
        )
