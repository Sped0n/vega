import serial
from cfg import is_darwin
from serial.tools import list_ports

from ctyper import DeviceInitError


class SerDevice:
    def __init__(self, port: str, baudrate: int = 115200) -> None:
        tmp: str = ""
        if "/" not in port:
            if is_darwin is False:
                raise NotImplementedError(
                    "set serial port with name is only available on macOS"
                )
            ports: list = list(list_ports.comports())
            founded: bool = False
            for p in ports:
                if port in p.device:
                    founded = True
                    tmp = p.device
                    break
            if not founded:
                raise DeviceInitError("serial port not found")
        else:
            tmp = port
        try:
            self.__device = serial.Serial(port=tmp, baudrate=baudrate)
        except FileNotFoundError:
            raise DeviceInitError("serial port not found")

    def read_buf_to_list(self) -> list[int]:
        buf_len: int = self.__device.in_waiting
        if buf_len == 0:
            return []
        return list(self.__device.read(buf_len))

    def write(self, datapack: bytearray):
        self.__device.write(datapack)
