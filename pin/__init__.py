from core.utils import DroneInfo
from sensia.utils import PoseData


def create_uart_buf(current: PoseData, target: DroneInfo, land: bool):
    cx_flag = 0x02 if current.x < 0 else 0x01
    cy_flag = 0x02 if current.y < 0 else 0x01
    cz_flag = 0x02 if current.z < 0 else 0x01
    cyaw_flag = 0x02 if current.yaw < 0 else 0x01

    tx_flag = 0x02 if target.x < 0 else 0x01
    ty_flag = 0x02 if target.y < 0 else 0x01
    tz_flag = 0x02 if target.z < 0 else 0x01
    tyaw_flag = 0x02 if target.yaw < 0 else 0x01
    landa = 0x01 if land else 0x00

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