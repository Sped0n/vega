# incase pyrealsense2 fucked up
# try:
#     import pyrealsense2 as rs
#
#     assert rs.__version__ == "2.50.0"
# except AttributeError:
#     import pyrealsense2.pyrealsense2 as rs

import pyrealsense2 as rs

from ctyper import DeviceInitError, NoDeviceError

from .utils import PoseData, pose_data_process, rs_device_init


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
            return PoseData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1)
        pose = frames.get_pose_frame()
        if pose:
            data = pose.get_pose_data()
            return pose_data_process(data)
        else:
            return PoseData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1)

    def stop(self) -> None:
        self.pipe.stop()
