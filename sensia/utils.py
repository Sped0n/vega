# incase pyrealsense2 fucked up
try:
    import pyrealsense2 as rs

    assert str(rs.__version__) == "2.50.0"
except AttributeError:
    import pyrealsense2.pyrealsense2 as rs

    assert str(rs.__version__) == "2.50.0"

import dataclasses
import numpy as np

from ctyper import DepthArray, Image, NoDeviceError


@dataclasses.dataclass
class PoseData:
    x: int
    y: int
    z: int
    yaw: int
    confidence: int


@dataclasses.dataclass
class DCData:
    depth: DepthArray
    color: Image
    dvalid: bool
    cvalid: bool


def rs_device_init(needed_cam_info: str) -> tuple[rs.pipeline, rs.config]:
    """
    init realsense device and return rs pipeline and config
    :param needed_cam_info: realsense camera info
    :return: realsense pipeline and realsense config
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
    """
    process pose data and return a PoseData object
    :param data: T265 pose data
    :return: PoseData
    """
    rw = data.rotation.w
    rx = -data.rotation.z
    ry = data.rotation.x
    rz = -data.rotation.y

    yaw = int(
        np.arctan2(2.0 * (rw * rz + rx * ry), rw * rw + rx * rx - ry * ry - rz * rz)
        * 180.0
        / np.pi
    )

    # forward is positive x
    x = -int(data.translation.z * 1000)
    # left is positive y
    y = -int(data.translation.x * 1000)
    # up is positive z
    z = int(data.translation.y * 1000)

    confidence = data.tracker_confidence

    return PoseData(x, y, z, yaw, confidence)


def plane_radar_filter(df: rs.depth_frame) -> rs.depth_frame:
    """
    filter for plane scan
    :param df: depth frame
    :return: filtered depth frame
    """
    dec = rs.decimation_filter()
    dec.set_option(rs.option.filter_magnitude, 2)

    ths = rs.threshold_filter()
    ths.set_option(rs.option.min_distance, 0.3)
    ths.set_option(rs.option.max_distance, 2.5)

    spa = rs.spatial_filter()
    spa.set_option(rs.option.filter_smooth_alpha, 0.5)
    spa.set_option(rs.option.filter_smooth_delta, 30)
    spa.set_option(rs.option.holes_fill, 2)

    tbf = rs.temporal_filter()
    tbf.set_option(rs.option.filter_smooth_alpha, 0.8)
    tbf.set_option(rs.option.filter_smooth_delta, 30)

    # 1280x720 -> 640x368
    tmp: rs.depth_frame = dec.process(df)
    tmp = spa.process(tmp)
    tmp = tbf.process(tmp)
    # 640x368 -> 320x184
    tmp = dec.process(tmp)
    # 320x184 -> 160x92
    tmp = dec.process(tmp)
    tmp = ths.process(tmp)

    return tmp
