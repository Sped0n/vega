# incase pyrealsense2 fucked up
# try:
#     import pyrealsense2 as rs
#
#     assert rs.__version__ == "2.50.0"
# except AttributeError:
#     import pyrealsense2.pyrealsense2 as rs

import numpy as np
import pyrealsense2 as rs

from ctyper import DeviceInitError, NoDeviceError, FetchError

from .utils import PoseData, pose_data_process, rs_device_init, DCData


class T265:
    def __init__(self) -> None:
        try:
            self.pipe, self.cfg = rs_device_init("Stereo Module")
        except NoDeviceError:
            raise DeviceInitError("T265 init failed")
        self.cfg.enable_stream(rs.stream.pose)
        self.pipe.start(self.cfg)
        self.fail_count: int = 0

    def fetch(self) -> PoseData:
        try:
            frames = self.pipe.wait_for_frames()
        except RuntimeError:
            self.fail_count += 1
            raise FetchError("T265 fetch failed")
        pose = frames.get_pose_frame()
        if pose:
            data = pose.get_pose_data()
            return pose_data_process(data)
        else:
            return PoseData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1)

    def stop(self) -> None:
        try:
            self.pipe.stop()
        except RuntimeError as e:
            assert "stop() cannot be called before start()" in str(e)

    def restart(self) -> None:
        self.stop()
        self.pipe.start(self.cfg)


class D435:
    def __init__(
        self, depth_only: bool = False, hd: bool = False, align: bool = False
    ) -> None:
        if depth_only and align:
            raise ValueError("Cannot align depth only stream")
        try:
            self.pipe, self.cfg = rs_device_init("RGB Camera")
        except NoDeviceError:
            raise DeviceInitError("D435 init failed")
        self.depth_only = depth_only
        self.hd = hd
        self.align = align
        self.cfg.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        if not self.depth_only:
            if hd:
                self.cfg.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)
            else:
                self.cfg.enable_stream(rs.stream.color, 1280, 720, rs.format.rgb8, 30)
        if self.align:
            self.align = rs.align(rs.stream.color)  # type: ignore
        self.pipe.start(self.cfg)
        self.fail_count: int = 0

    def fetch(self) -> DCData:
        try:
            frames = self.pipe.wait_for_frames()
        except RuntimeError:
            self.fail_count += 1
            raise FetchError("D435 fetch failed")
        if self.align:
            frames = self.align.process(frames)  # type: ignore
        depth_frame = frames.get_depth_frame()
        depth_array = np.asanyarray(depth_frame.get_data())
        if self.depth_only:
            return DCData(depth_array, np.zeros(1), True, False)
        color_frame = frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())
        return DCData(depth_array, color_image, True, True)

    def stop(self) -> None:
        try:
            self.pipe.stop()
        except RuntimeError as e:
            assert "stop() cannot be called before start()" in str(e)

    def restart(self) -> None:
        self.stop()
        self.pipe.start(self.cfg)
