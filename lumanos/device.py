from queue import Empty, Queue

import pygame
from luma.core.interface.serial import i2c
from luma.emulator.device import capture
from luma.oled.device import ssd1306


class Mocker(capture):
    def __init__(
        self,
        width=128,
        height=64,
        rotate=0,
        mode="RGB",
        transform="scale2x",
        scale=2,
        dbg_queue: Queue | None = None,
    ):
        super(capture, self).__init__(width, height, rotate, mode, transform, scale)
        self.dbg = True if dbg_queue is not None else False
        self.dbg_queue = dbg_queue

    def display(self, image) -> None:
        assert image.size == self.size
        image = self.preprocess(image)
        surface = self.to_surface(image, alpha=self._contrast)
        disp = pygame.surfarray.array3d(surface)
        disp = disp.swapaxes(0, 1)
        if self.dbg is False:
            return None
        assert self.dbg_queue is not None
        try:
            self.dbg_queue.put(disp, timeout=0.5)
        except Empty:
            pass


def OLED1306(port: int = 5, address: int = 0x3C):
    serial = i2c(port=port, address=address)
    return ssd1306(serial)
