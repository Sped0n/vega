import dataclasses
import math

import pyrealsense2 as rs

from ctyper import NoDeviceError


@dataclasses.dataclass
class PoseData:
    x: float
    y: float
    z: float
    pitch: float
    roll: float
    yaw: float
    confidence: int


def rs_device_init(needed_cam_info: str) -> tuple[rs.pipeline, rs.config]:
    """
    init realsense device and return rs pipeline and config
    """
    ctx = rs.context()
    if len(ctx.query_devices()) == 0:
        raise NoDeviceError("No realsense device connected")
    pipe = rs.pipeline()
    cfg = rs.config()
    pipe_wrap = rs.pipeline_wrapper(pipe)
    pipe_prof = cfg.resolve(pipe_wrap)
    sensors = pipe_prof.get_device().sensors
    found: bool = False
    for s in sensors:
        if s.get_info(rs.camera_info.name) == needed_cam_info:
            found = True
            break
    if not found:
        raise NoDeviceError(f"No {needed_cam_info} device connected")
    return pipe, cfg


def pose_data_process(data: rs.pose) -> PoseData:
    rw = data.rotation.w
    rx = -data.rotation.z
    ry = data.rotation.x
    rz = -data.rotation.y

    pitch = float(-math.asin(2.0 * (rx * rz - rw * ry)) * 180.0 / math.pi)
    roll = float(
        math.atan2(2.0 * (rw * rx + ry * rz), rw * rw - rx * rx - ry * ry + rz * rz)
        * 180.0
        / math.pi
    )
    yaw = float(
        math.atan2(2.0 * (rw * rz + rx * ry), rw * rw + rx * rx - ry * ry - rz * rz)
        * 180.0
        / math.pi
    )

    x = data.translation.x
    y = data.translation.y
    z = data.translation.z

    confidence = data.tracker_confidence

    return PoseData(x, y, z, pitch, roll, yaw, confidence)
