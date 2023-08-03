import bluetooth
from ctyper import ConntectionError
import itertools
from queue import Queue


class BTServer:
    def __init__(self, uuid: str):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock.bind(("", bluetooth.PORT_ANY))
        self.server_sock.listen(1)
        self.port = self.server_sock.getsockname()[1]
        self.uuid = uuid
        bluetooth.advertise_service(
            self.server_sock,
            "BTServer",
            service_id=self.uuid,
            service_classes=[self.uuid, bluetooth.SERIAL_PORT_CLASS],
            profiles=[bluetooth.SERIAL_PORT_PROFILE],
        )
        self.__hold_for_device()

    def __hold_for_device(self):
        print("==> Waiting for connection on RFCOMM channel", self.port)
        self.client_sock, self.client_info = self.server_sock.accept()
        print("==> Accepted connection from", self.client_info)

    def __recieve(self, bytes: int = 1024) -> str:
        try:
            data = self.client_sock.recv(bytes)  # type: ignore
        except OSError:
            print("Server Connection lost (recv)")
            raise ConntectionError("Server to client Connection lost")
        return data.decode()

    def __send(self, data: str) -> None:
        try:
            self.client_sock.send(data)  # type: ignore
        except OSError:
            print("Server Connection lost (send)")
            raise ConntectionError("Server to client Connection lost")

    def send_thread(self, send_queue: Queue[str]) -> None:
        while True:
            try:
                self.__send(send_queue.get())
            except ConntectionError:
                self.__hold_for_device()

    def recv_thread(self, recv_queue: Queue[str]) -> None:
        while True:
            try:
                if recv_queue.full() is False:
                    recv_queue.put(self.__recieve())
            except ConntectionError:
                self.__hold_for_device()


class BTClient:
    def __init__(self, uuid: str, target_addr: str) -> None:
        self.client_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.uuid = uuid
        self.addr = target_addr
        self.__robust_connect()

    def __connect(self) -> None:
        service_matches = bluetooth.find_service(uuid=self.uuid, address=self.addr)

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

    def __robust_connect(self, max_attempts: int = 5) -> None:
        attempts = itertools.count()
        while True:
            try:
                self.__connect()
            except ConnectionError:
                if next(attempts) <= max_attempts:
                    continue
                else:
                    raise
            break

    def __recieve(self, bytes: int = 1024) -> str:
        try:
            data = self.sock.recv(bytes)  # type: ignore
        except OSError:
            print("Client to Server Connection lost")
            raise ConntectionError("Client Connection lost (recv)")
        return data.decode()

    def __send(self, data: str) -> None:
        try:
            self.sock.send(data)  # type: ignore
        except OSError:
            print("Client to Server Connection lost (send)")
            raise ConntectionError("Client Connection lost")

    def send_thread(self, send_queue: Queue[str]) -> None:
        while True:
            try:
                self.__send(send_queue.get())
            except ConntectionError:
                self.__robust_connect()

    def recv_thread(self, recv_queue: Queue[str]) -> None:
        while True:
            try:
                if recv_queue.full() is False:
                    recv_queue.put(self.__recieve())
            except ConntectionError:
                self.__robust_connect()
