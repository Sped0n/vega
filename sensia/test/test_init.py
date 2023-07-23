import pyrealsense2 as rs
import os
from ctyper import DeviceInitError, FetchError

from sensia import T265, D435
from warnings import warn

ctx = rs.context()
no_device = False
if len(ctx.query_devices()) == 0:
    warn("no device, skipping test")
    no_device = True


def test_t265_init():
    if not no_device:
        t = T265()
        assert isinstance(t, T265)
        t.stop()


def test_t265_fetch():
    if not no_device:
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


def test_d435_init():
    if not no_device:
        try:
            h = D435()
            assert isinstance(h, D435)
            h.stop()
        except RuntimeError or DeviceInitError:
            assert os.system == "Darwin"
            warn("pyrs2 issue on macos")


def test_d435_fetch_depth_only():
    if not no_device:
        try:
            h = D435(depth_only=True)
            try:
                d = h.fetch()
            except FetchError:
                h.restart()
                d = h.fetch()
            assert d.dvalid is True
            assert d.depth.shape == (720, 1280)
            assert d.cvalid is False
            h.stop()
        except RuntimeError or DeviceInitError:
            assert os.system == "Darwin"
            warn("pyrs2 issue on macos")


def test_d435_fetch_default():
    if not no_device:
        try:
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
            h.stop()
        except RuntimeError or DeviceInitError:
            assert os.system == "Darwin"
            warn("pyrs2 issue on macos")


def test_d435_fetch_default_align():
    if not no_device:
        try:
            h = D435(align=True)
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
        except RuntimeError or DeviceInitError:
            assert os.system == "Darwin"
            warn("pyrs2 issue on macos")


def test_d435_fetch_hd():
    if not no_device:
        try:
            h = D435(hd=True)
            try:
                d = h.fetch()
            except FetchError:
                h.restart()
                d = h.fetch()
            assert d.dvalid is True
            assert d.depth.shape == (720, 1280)
            assert d.cvalid is True
            assert d.color.shape == (1080, 1920, 3)
            h.stop()
        except RuntimeError or DeviceInitError:
            assert os.system == "Darwin"
            warn("pyrs2 issue on macos")


def test_d435_fetch_hd_align():
    if not no_device:
        try:
            h = D435(hd=True, align=True)
            try:
                d = h.fetch()
            except FetchError:
                h.restart()
                d = h.fetch()
            assert d.dvalid is True
            assert d.depth.shape == (1080, 1920)
            assert d.cvalid is True
            assert d.color.shape == (1080, 1920, 3)
            h.stop()
        except RuntimeError or DeviceInitError:
            assert os.system == "Darwin"
            warn("pyrs2 issue on macos")
