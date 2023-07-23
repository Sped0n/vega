import pyrealsense2 as rs
from sensia.utils import pose_data_process


def test_pose_data_process():
    data = rs.pose()
    data.translation.x = 1.0
    data.translation.y = 2.0
    data.translation.z = 3.0
    data.rotation.w = 0.5
    data.rotation.x = 0.5
    data.rotation.y = 0.5
    data.rotation.z = 0.5
    data.tracker_confidence = 0
    d = pose_data_process(data)
    assert d.x == 1.0
    assert d.y == 2.0
    assert d.z == 3.0
    assert d.pitch == 0.0
    assert d.roll == -90.0
    assert d.yaw == -90.0
    assert d.confidence == 0
