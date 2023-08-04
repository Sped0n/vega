import bluetooth
from ctyper import ConntectionError
import itertools
from queue import Queue
from time import sleep


class BTServer:
    def __init__(self, uuid: str):
        """
        Bluetooth Server
        :param uuid: uuid fingerprint
        """
        # use RFCOMM
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        # default setup
        self.server_sock.bind(("", bluetooth.PORT_ANY))
        self.server_sock.listen(1)
        self.port = self.server_sock.getsockname()[1]
        # uuid fingerprint
        self.uuid = uuid
        # advertise service
        bluetooth.advertise_service(
            self.server_sock,
            "BTServer",
            service_id=self.uuid,
            service_classes=[self.uuid, bluetooth.SERIAL_PORT_CLASS],
            profiles=[bluetooth.SERIAL_PORT_PROFILE],
        )
        # status for error handling
        self.__running: bool = False
        # wait for client to connect
        self.__hold_for_device()

    def __hold_for_device(self):
        print("==> Waiting for connection on RFCOMM channel", self.port)
        # establish connection
        self.client_sock, self.client_info = self.server_sock.accept()
        print("==> Accepted connection from", self.client_info)
        self.running = True

    def recieve(self, bytes: int = 1024) -> str:
        try:
            data = self.client_sock.recv(bytes)  # type: ignore
        except OSError:
            if self.__running:
                print("Server Connection lost (recv)")
            raise ConntectionError("Server to client Connection lost")
        return data.decode()

    def send(self, data: str) -> None:
        try:
            self.client_sock.send(data)  # type: ignore
        except OSError:
            if self.__running:
                print("Server Connection lost (send)")
            raise ConntectionError("Server to client Connection lost")

    def error_handle(self) -> None:
        if self.__running:
            self.__running = False
            self.__hold_for_device()

    def send_thread(self, send_queue: Queue[str]) -> None:
        while True:
            try:
                self.send(send_queue.get())
            except ConntectionError:
                self.error_handle()

    def recv_thread(self, recv_queue: Queue[str]) -> None:
        while True:
            try:
                if recv_queue.full() is False:
                    recv_queue.put(self.recieve())
            except ConntectionError:
                self.error_handle()


class BTClient:
    def __init__(self, uuid: str, ser_addr: str) -> None:
        # use RFCOMM
        self.client_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        # uuid fingerprint
        self.uuid = uuid
        # server mac address
        self.ser_addr = ser_addr
        # status for error handling
        self.__running: bool = False
        # connect to server(keep trying)
        self.__robust_connect(-1)

    def __connect(self) -> None:
        # find service
        service_matches = bluetooth.find_service(uuid=self.uuid, address=self.ser_addr)

        if len(service_matches) == 0:
            print("Couldn't find the Server service")
            raise ConnectionError("Couldn't find the Server service")

        first_match = service_matches[0]
        port = first_match["port"]
        host = first_match["host"]
        name = first_match["name"]

        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        print('==> Connecting to "{}" on {}'.format(name, host))
        try:
            self.sock.connect((host, port))
        except OSError:
            print("socket connect failed")
            raise ConnectionError("Couldn't connect to server")
        print("==> Connected to server")
        self.__running = True

    def __robust_connect(self, max_attempts: int = -1) -> None:
        # keep retry parameter
        if max_attempts == -1:
            keep_trying = True
        else:
            keep_trying = False
        # retry counter
        attempts = itertools.count()
        while True:
            try:
                self.__connect()
            except ConnectionError:
                # wait 2 seconds before retrying
                sleep(2)
                if next(attempts) <= max_attempts or keep_trying is True:
                    continue
                else:
                    raise
            break

    def recieve(self, bytes: int = 1024) -> str:
        try:
            data = self.sock.recv(bytes)  # type: ignore
        except OSError:
            if self.__running:
                print("Client to Server Connection lost")
            raise ConntectionError("Client Connection lost (recv)")
        return data.decode()

    def send(self, data: str) -> None:
        try:
            self.sock.send(data)  # type: ignore
        except OSError:
            if self.__running:
                print("Client to Server Connection lost (send)")
            raise ConntectionError("Client Connection lost")

    def error_handle(self):
        if self.__running:
            self.__running = False
            self.__robust_connect()

    def send_thread(self, send_queue: Queue[str]) -> None:
        while True:
            try:
                self.send(send_queue.get())
            except ConntectionError:
                self.error_handle()

    def recv_thread(self, recv_queue: Queue[str]) -> None:
        while True:
            try:
                if recv_queue.full() is False:
                    recv_queue.put(self.recieve())
            except ConntectionError:
                self.error_handle()
