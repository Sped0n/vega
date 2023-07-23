import pyrealsense2 as rs

from sensia import T265

ctx = rs.context()
no_device = False
if len(ctx.query_devices()) == 0:
    print("\nno device, skipping test")
    no_device = True


def test_t265_init():
    if not no_device:
        t = T265()
        assert isinstance(t, T265)


def test_t265_fetch():
    if not no_device:
        t = T265()
        d = t.fetch()
        assert isinstance(d.roll, float)
        assert isinstance(d.pitch, float)
        assert isinstance(d.yaw, float)
        assert isinstance(d.x, float)
        assert isinstance(d.y, float)
        assert isinstance(d.z, float)
        assert isinstance(d.confidence, int)
