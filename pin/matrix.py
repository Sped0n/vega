import ASUS.GPIO as GPIO  # type: ignore
from time import sleep
from ctyper import Number


class MatrixKeyBoard:
    def __init__(self, c1_pin: int, c2_pin: int, r1_pin: int, r2_pin: int) -> None:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarings(False)
        self.c1 = c1_pin
        self.c2 = c2_pin
        self.r1 = r1_pin
        self.r2 = r2_pin

    def __column_set_in(self) -> None:
        GPIO.setup(self.c1, GPIO.IN)
        GPIO.setup(self.c2, GPIO.INPUT)

    def __column_get_in(self, match: int) -> int:
        if GPIO.input(self.c1) == match:
            return 1
        elif GPIO.input(self.c2) == match:
            return 2
        else:
            return -1

    def __column_set_out(self, status: int) -> None:
        GPIO.setup(self.c1, GPIO.OUT)
        GPIO.output(self.c1, status)
        GPIO.setup(self.c2, GPIO.OUT)
        GPIO.output(self.c2, status)

    def __row_set_in(self) -> None:
        GPIO.setup(self.r1, GPIO.IN)
        GPIO.setup(self.r2, GPIO.IN)

    def __row_get_in(self, match: int) -> int:
        if GPIO.input(self.r1) == match:
            return 1
        elif GPIO.input(self.r2) == match:
            return 2
        else:
            return -1

    def __row_set_out(self, status: int) -> None:
        GPIO.setup(self.r1, GPIO.OUT)
        GPIO.output(self.r1, status)
        GPIO.setup(self.r2, GPIO.OUT)
        GPIO.output(self.r2, status)

    def __scan_row(self, duration: Number) -> int:
        # scan row, set column to output low
        self.__column_set_out(0)
        self.__row_set_in()
        tmp = self.__row_get_in(0)
        if tmp == -1:
            return -1
        sleep(duration)  # anti shake
        if not self.__row_get_in(0) == tmp:
            return -1
        return tmp

    def __scan_column(self, duration: Number) -> int:
        # scan column, set row to output low
        self.__column_set_in()
        self.__row_set_out(0)
        tmp = self.__column_get_in(0)
        if tmp == -1:
            return -1
        sleep(duration)  # anti shake
        if not self.__column_get_in(0) == tmp:
            return -1
        return tmp

    def get_key(self, anti_shake_time: Number = 0.05) -> int:
        row_val = self.__scan_row(anti_shake_time)
        column_val = self.__scan_column(anti_shake_time)
        if row_val == 1 and column_val == 1:
            return 1
        elif row_val == 1 and column_val == 2:
            return 2
        elif row_val == 2 and column_val == 1:
            return 5
        elif row_val == 2 and column_val == 2:
            return 6
        else:
            return -1
