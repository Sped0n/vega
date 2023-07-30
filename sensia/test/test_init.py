import itertools
from warnings import warn
from cfg import NORS, is_darwin, VDBG

from ctyper import DeviceInitError, FetchError
from sensia import D435, T265, AsyncCam


# t265
def test_t265_init():
    if NORS is False:
        t = T265()
        assert isinstance(t, T265)
        t.stop()


def test_t265_fetch():
    if NORS is False:
        t = T265()
        try:
            d = t.fetch()
        except FetchError:
            t.restart()
            d = t.fetch()
        assert isinstance(d.roll, float)
        assert isinstance(d.pitch, float)
        assert isinstance(d.yaw, float)
        assert isinstance(d.x, float)
        assert isinstance(d.y, float)
        assert isinstance(d.z, float)
        assert isinstance(d.confidence, int)
        t.stop()


def test_t265_restart():
    if NORS is False:
        t = T265()
        try:
            d = t.fetch()
        except FetchError:
            t.restart()
            d = t.fetch()
        assert isinstance(d.roll, float)
        assert isinstance(d.pitch, float)
        assert isinstance(d.yaw, float)
        assert isinstance(d.x, float)
        assert isinstance(d.y, float)
        assert isinstance(d.z, float)
        assert isinstance(d.confidence, int)
        t.restart()
        try:
            d = t.fetch()
        except FetchError:
            t.restart()
            d = t.fetch()
        assert isinstance(d.roll, float)
        assert isinstance(d.pitch, float)
        assert isinstance(d.yaw, float)
        assert isinstance(d.x, float)
        assert isinstance(d.y, float)
        assert isinstance(d.z, float)
        assert isinstance(d.confidence, int)
        t.stop()


# d435
def test_d435_init():
    if NORS is False:
        try:
            h = D435()
            assert isinstance(h, D435)
            h.stop()
        except RuntimeError as e:
            assert "fetch" not in str(e)
            assert is_darwin is True
            warn("pyrs2 issue on macos")


def test_d435_fetch_depth_only():
    if NORS is False:
        try:
            h = D435(depth_only=True)
            attempts = itertools.count()
            while True:
                try:
                    d = h.fetch()
                except FetchError:
                    h.restart()
                    if next(attempts) <= 3:
                        continue
                    else:
                        raise
                break
            assert d.dvalid is True
            assert d.depth.shape == (720, 1280)
            assert d.cvalid is False
            h.stop()
        except RuntimeError as e:
            assert "fetch" not in str(e)
            assert is_darwin is True
            warn("pyrs2 issue on macos")
        except DeviceInitError:
            assert is_darwin is True
            warn("pyrs2 issue on macos")


def test_d435_fetch_default():
    if NORS is False:
        try:
            h = D435()
            attempts = itertools.count()
            while True:
                try:
                    d = h.fetch()
                except FetchError:
                    h.restart()
                    if next(attempts) <= 3:
                        continue
                    else:
                        raise
                break
            assert d.dvalid is True
            assert d.depth.shape == (720, 1280)
            assert d.cvalid is True
            assert d.color.shape == (720, 1280, 3)
            h.stop()
        except RuntimeError as e:
            assert "fetch" not in str(e)
            assert is_darwin is True
            warn("pyrs2 issue on macos")
        except DeviceInitError:
            assert is_darwin is True
            warn("pyrs2 issue on macos")


def test_d435_fetch_default_align():
    if NORS is False:
        try:
            h = D435(align=True)
            attempts = itertools.count()
            while True:
                try:
                    d = h.fetch()
                except FetchError:
                    h.restart()
                    if next(attempts) <= 3:
                        continue
                    else:
                        raise
                break
            assert d.dvalid is True
            assert d.depth.shape == (720, 1280)
            assert d.cvalid is True
            assert d.color.shape == (720, 1280, 3)
            h.stop()
        except RuntimeError as e:
            assert "fetch" not in str(e)
            assert is_darwin is True
            warn("pyrs2 issue on macos")
        except DeviceInitError:
            assert is_darwin is True
            warn("pyrs2 issue on macos")


def test_d435_fetch_hd():
    if NORS is False:
        try:
            h = D435(hd=True)
            attempts = itertools.count()
            while True:
                try:
                    d = h.fetch()
                except FetchError:
                    h.restart()
                    if next(attempts) <= 3:
                        continue
                    else:
                        raise
                break
            assert d.dvalid is True
            assert d.depth.shape == (720, 1280)
            assert d.cvalid is True
            assert d.color.shape == (1080, 1920, 3)
            h.stop()
        except RuntimeError as e:
            assert "fetch" not in str(e)
            assert is_darwin is True
            warn("pyrs2 issue on macos")
        except DeviceInitError:
            assert is_darwin is True
            warn("pyrs2 issue on macos")


def test_d435_fetch_hd_align():
    if NORS is False:
        try:
            h = D435(hd=True, align=True)
            attempts = itertools.count()
            while True:
                try:
                    d = h.fetch()
                except FetchError:
                    h.restart()
                    if next(attempts) <= 3:
                        continue
                    else:
                        raise RuntimeError("failed to retry fetch")
                break
            assert d.dvalid is True
            assert d.depth.shape == (1080, 1920)
            assert d.cvalid is True
            assert d.color.shape == (1080, 1920, 3)
            h.stop()
        except RuntimeError as e:
            assert "fetch" not in str(e)
            assert is_darwin is True
            warn("pyrs2 issue on macos")
        except DeviceInitError:
            assert is_darwin is True
            warn("pyrs2 issue on macos")


def test_d435_restart():
    if NORS is False:
        h = D435()
        try:
            d = h.fetch()
        except FetchError:
            h.restart()
            d = h.fetch()
        assert d.dvalid is True
        assert d.depth.shape == (720, 1280)
        assert d.cvalid is True
        assert d.color.shape == (720, 1280, 3)
        h.restart()
        try:
            d = h.fetch()
        except FetchError:
            h.restart()
            d = h.fetch()
        assert d.dvalid is True
        assert d.depth.shape == (720, 1280)
        assert d.cvalid is True
        assert d.color.shape == (720, 1280, 3)
        h.stop()


# async camera
def test_async_camera():
    if VDBG is True:
        c = AsyncCam(width=640, height=480)
        assert c.fetch().shape == (480, 640, 3)
        c.reinit_with(width=1280, height=720)
        assert c.fetch().shape == (720, 1280, 3)
