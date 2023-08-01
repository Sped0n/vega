import os
import re
from typing import Callable

import cv2
import numpy as np

from cfg import is_linux, rs
from ctyper import DeviceInitError, FetchError, Image, NoDeviceError

from .utils import DCData, PoseData, pose_data_process, rs_device_init


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
            raise FetchError(
                "T265 has got the frame, but the frame doesn't contain pose data"
            )

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

    def fetch(
        self, depth_filter: Callable[[rs.depth_frame], rs.depth_frame] | None = None
    ) -> DCData:
        try:
            frames = self.pipe.wait_for_frames()
        except RuntimeError:
            self.fail_count += 1
            raise FetchError("D435 fetch failed")
        if self.align:
            frames = self.align.process(frames)  # type: ignore
        depth_frame = frames.get_depth_frame()
        if depth_filter is not None:
            depth_frame = depth_filter(depth_frame)
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


class AsyncCam:
    def __init__(self, width: int, height: int, id: int = 0) -> None:
        self.reinit_with(width, height, id)

    def fetch(self) -> Image:
        ret, frame = self.cap.read()
        if not ret:
            raise FetchError("AsyncCam fetch failed")
        return frame

    def stop(self) -> None:
        try:
            self.cap.release()
            del self.cap
        except AttributeError:
            pass

    def reinit_with(self, width: int, height: int, id: int = 0) -> None:
        self.stop()
        self.device_id = id
        if self.device_id == 0 and is_linux:
            DEFAULT_CAM_NAME = "usb-RYS_USB_Camera_200901010001-video-index0"
            if os.path.exists(DEFAULT_CAM_NAME):
                device_path: str = os.path.realpath(DEFAULT_CAM_NAME)
                device_re: re.Pattern = re.compile("\/dev\/video(\d+)")  # type: ignore
                info: re.Match[str] | None = device_re.match(device_path)
                if info:
                    self.device_id = int(info.group(1))
        try:
            if is_linux:
                # init with v4l2
                self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_V4L2)
            else:
                self.cap = cv2.VideoCapture(self.device_id)
        except cv2.error:
            raise DeviceInitError("AsyncCam init failed")
        self.width = width
        self.height = height

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        # force MJPG
        if is_linux:
            self.cap.set(
                cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc("M", "J", "P", "G")
            )
