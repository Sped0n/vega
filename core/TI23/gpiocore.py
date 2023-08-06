from __future__ import annotations
import wiringpi as wpi  # type:ignore
from wiringppi import GPIO  # type:ignore
from ctyper import Command
from core.utils import get_cmd
from multiprocessing import Queue as mQueue
from threading import Thread, Event


class proc:
    def __init__(
        self,
        ctl_queue: mQueue[Command],
        # output
    ) -> None:
        self.ctl_queue = ctl_queue
        wpi.wiringpiSetup()
        # high io
        wpi.pinMode(3, GPIO.OUTPUT)
        wpi.pinMode(16, GPIO.OUTPUT)
        wpi.softPwmCreate(16, 25, 50)
        # laser flag
        self.laser_flag = Event()
        self.laser_flag.set()
        # drop flag
        self.drop_flag = Event()
        self.drop_flag.clear()
        # red light flag
        self.rlight_flag = Event()
        self.rlight_flag.clear()

        self.run()

    def laser(self):
        while True:
            if self.laser_flag.is_set():
                wpi.digitalWrite(3, GPIO.HIGH)
            else:
                wpi.digitalWrite(3, GPIO.LOW)

    def motor(self):
        while True:
            if self.drop_flag.is_set():
                wpi.softPwmWrite(16, 25)
            else:
                wpi.softPwmWrite(16, 7)

    def red_light(self):
        while True:
            if self.rlight_flag.is_set():
                wpi.digitalWrite(4, GPIO.HIGH)
            else:
                wpi.digitalWrite(4, GPIO.LOW)

    def manager(self):
        while True:
            # no new command, continue
            cmd: Command = self.ctl_queue.get()
            get_cmd(cmd, "laser", self.laser_flag)
            get_cmd(cmd, "drop", self.drop_flag)
            get_cmd(cmd, "rlight", self.rlight_flag)

    def run(self):
        # warm up

        manager_thread = Thread(target=self.manager, daemon=True)
        laser_thread = Thread(target=self.laser, daemon=True)
        motor_thread = Thread(target=self.motor, daemon=True)
        red_light_thread = Thread(target=self.red_light, daemon=True)

        manager_thread.start()
        laser_thread.start()
        motor_thread.start()
        red_light_thread.start()

        manager_thread.join()
        laser_thread.join()
        motor_thread.join()
        red_light_thread.join()
