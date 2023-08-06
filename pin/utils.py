from core.utils import DroneInfo
from ctyper import PackCorruptedError
from sensia.utils import PoseData


def create_uart_buf(current: PoseData, target: DroneInfo):
    cx_flag = 0x02 if current.x < 0 else 0x01
    cy_flag = 0x02 if current.y < 0 else 0x01
    cz_flag = 0x02 if current.z < 0 else 0x01
    cyaw_flag = 0x02 if current.yaw < 0 else 0x01

    tx_flag = 0x02 if target.x < 0 else 0x01
    ty_flag = 0x02 if target.y < 0 else 0x01
    tz_flag = 0x02 if target.z < 0 else 0x01
    tyaw_flag = 0x02 if target.yaw < 0 else 0x01
    landa = 0x01 if target.land else 0x00

    return bytearray(
        [
            0x55,
            0xAA,
            0x50,
            0x18,  # dec 24, hex 18
            cx_flag,
            (abs(current.x) & 0xFF00) >> 8,
            abs(current.x) & 0x00FF,
            cy_flag,
            (abs(current.y) & 0xFF00) >> 8,
            abs(current.y) & 0x00FF,
            cz_flag,
            (abs(current.z) & 0xFF00) >> 8,
            abs(current.z) & 0x00FF,
            cyaw_flag,
            abs(current.yaw) & 0x00FF,
            current.confidence & 0x00FF,
            tx_flag,
            (abs(target.x) & 0xFF00) >> 8,
            abs(target.x) & 0x00FF,
            abs(ty_flag),
            (abs(target.y) & 0xFF00) >> 8,
            abs(target.y) & 0x00FF,
            tz_flag,
            (abs(target.z) & 0xFF00) >> 8,
            abs(target.z) & 0x00FF,
            tyaw_flag,
            target.yaw & 0x00FF,
            landa,
            0xAA,
        ]
    )


def depack_recv_list_to_z(recv: list[int]) -> int:
    # pack length
    if len(recv) != 7:
        raise PackCorruptedError("length error")
    # pack head and tail check
    if not (recv[0] == 85 and recv[1] == 170 and recv[2] == 255 and recv[6] == 170):
        raise PackCorruptedError("head or tail error")
    return int(recv[4] << 8) + int(recv[5])


def create_uart_buf_car(fire: int):
    return bytearray(
        [
            0x55,
            0xAA,
            0x50,
            0x01,  # dec 1, hex 1
            abs(fire) & 0x00FF,
            0xAA,
        ]
    )
