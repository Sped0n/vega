from __future__ import annotations

from multiprocessing import Queue as mQueue
from queue import Empty, Queue
from threading import Event, Thread
from time import sleep

from luma.core.render import canvas

from compass import corrd2block
from core.utils import pusher, set_thread_event
from ctyper import Command, Image
from lumanos.device import OLED1306
from lumanos.TI23 import (
    mapper,
    trailer,
    welcome_screen,
    basic_confirm,
    advanced_confirm,
    basic_layout,
    advanced_layout,
)
from lumanos.utils import Offsetter
from pin.matrix import MatrixKeyBoard
from .vgcore.modules import Transmit
from compass import Odemeter


class proc:
    def __init__(
        self,
        transmit_queue: mQueue[Transmit],  # input
        ui2vega_queue: mQueue,  # output
    ) -> None:
        # device init
        self.disp_map = OLED1306(6)
        self.disp_info = OLED1306(7)
        self.disp_map.capabilities(width=128, height=64, rotate=0, mode="1")
        self.disp_info.capabilities(width=128, height=64, rotate=0, mode="1")

        # proc queue init
        self.transmit_queue = transmit_queue
        self.ui2vega_queue = ui2vega_queue

        # thread queue init
        self.key_queue = Queue(5)
        self.to_mapper_queue: Queue[tuple[int, int]] = Queue(5)

        # keypad
        self.k = MatrixKeyBoard(22, 24, 38, 40)

        # interacting flag
        self.interacting: bool = True

        # mapper flag
        self.mapper_enable = Event()
        self.mapper_enable.clear()

        # ui stage
        self.ui_stage: int = 0

        # run it
        self.run()

    def interact_core(self):
        keypress = -1
        accept_key_input = True
        o = Odemeter()
        while True:
            with canvas(self.disp_info) as draw_info:
                match self.ui_stage:
                    case 0:
                        welcome_screen(draw_info)
                        if keypress == 1:
                            self.ui_stage = 1  # basic
                        elif keypress == 2:
                            self.ui_stage = 2  # adv
                    case 1:
                        basic_confirm(draw_info)
                        if keypress == 1:
                            self.ui_stage = 3  # confirm
                        elif keypress == 2:
                            self.ui_stage = 0  # cancel, back to welcome screen
                    case 2:
                        advanced_confirm(draw_info)
                        if keypress == 1:
                            self.ui_stage = 4  # confirm
                        elif keypress == 2:
                            self.ui_stage = 0  # cancel, back to welcome screen
                    case 3:
                        if accept_key_input:
                            accept_key_input = False  # prevent keypress
                        t_pack = self.transmit_queue.get()
                        # send x and y to mapper
                        pusher(self.to_mapper_queue, (t_pack.x, t_pack.y))
                        # calculate mileage
                        mileage = o.add((t_pack.x, t_pack.y))
                        basic_layout(draw_info, (t_pack.x, t_pack.y), mileage)
                    case 4:
                        if accept_key_input:
                            accept_key_input = False  # prevent keypress
                        t_pack = self.transmit_queue.get()
                        # send x and y to mapper
                        pusher(self.to_mapper_queue, (t_pack.x, t_pack.y))
                        # calculate mileage
                        mileage = o.add((t_pack.x, t_pack.y))
                        if t_pack.fire_x is not None and t_pack.fire_y is not None:
                            advanced_layout(
                                draw_info,
                                mileage,
                                (t_pack.fire_x, t_pack.fire_y),
                            )
                        else:
                            advanced_layout(draw_info, mileage)
            if accept_key_input:
                keypress = self.key_queue.get()

    def mapper_core(self):
        t = trailer()
        o_trail = Offsetter((28, 2), 1)
        with canvas(self.disp_map) as draw_map:
            # draw a map first, kinda like welcome screen
            mapper(draw_map)
            while True:
                self.mapper_enable.wait()
                coord = self.to_mapper_queue.get()
                mapper(draw_map)
                a, b = corrd2block(coord[0], coord[1])
                t.add_dot(o_trail.calc(a, b))
                t.darw(draw_map)

    def keyboard(self):
        while True:
            pusher(self.key_queue, self.k.read())

    def run(self):
        # warm up
        sleep(1)

        display_thread = Thread(target=self.interact_core, daemon=True)
        keyboard_thread = Thread(target=self.keyboard, daemon=True)

        display_thread.start()
        keyboard_thread.start()

        display_thread.join()
        keyboard_thread.start()
