from itertools import count
from warnings import warn

from cfg import NORS, is_darwin, rs
from ctyper import DeviceInitError, FetchError
from sensia import D435
from sensia.utils import plane_radar_filter, pose_data_process


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


def test_d435_fetch_depth_only():
    if NORS is True:
        return None
    try:
        h = D435(depth_only=True)
        attempts = count()
        while True:
            try:
                d = h.fetch(plane_radar_filter)
            except FetchError:
                h.restart()
                if next(attempts) <= 3:
                    continue
                else:
                    raise
            break
        assert d.dvalid is True
        assert d.depth.shape == (92, 160)
        assert d.cvalid is False
        h.stop()
    except RuntimeError as e:
        assert "fetch" not in str(e)
        assert is_darwin is True
        warn("pyrs2 issue on macos")
    except DeviceInitError:
        assert is_darwin is True
        warn("pyrs2 issue on macos")
