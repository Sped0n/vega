import ASUS.GPIO as GPIO  # type: ignore
from time import sleep
from ctyper import Number


class MatrixKeyBoard:
    def __init__(self, c1_pin: int, c2_pin: int, r1_pin: int, r2_pin: int) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        self.c1 = c1_pin
        self.c2 = c2_pin
        self.r1 = r1_pin
        self.r2 = r2_pin
        GPIO.setup(self.r1, GPIO.OUT)
        GPIO.setup(self.r2, GPIO.OUT)
        GPIO.setup(self.c1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.c2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def __readrow1(self) -> int:
        GPIO.output(self.r1, GPIO.HIGH)
        if GPIO.input(self.c1) == GPIO.HIGH:
            tmp = 1
        elif GPIO.input(self.c2) == GPIO.HIGH:
            tmp = 2
        else:
            tmp = -1
        GPIO.output(self.r1, GPIO.LOW)
        return tmp

    def __readrow2(self) -> int:
        GPIO.output(self.r2, GPIO.HIGH)
        if GPIO.input(self.c1) == GPIO.HIGH:
            tmp = 5
        elif GPIO.input(self.c2) == GPIO.HIGH:
            tmp = 6
        else:
            tmp = -1
        GPIO.output(self.r2, GPIO.LOW)
        return tmp

    def read(self) -> int:
        tmp = self.__readrow1()
        if tmp != -1:
            sleep(0.1)
            return tmp
        tmp = self.__readrow2()
        if tmp != -1:
            sleep(0.1)
            return tmp
        sleep(0.1)
        return -1
