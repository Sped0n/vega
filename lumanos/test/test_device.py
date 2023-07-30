from cfg import is_arm, is_darwin, is_linux
from lumanos.device import OLED1306, Mocker


def test_mocker():
    if (is_arm and is_darwin) is False:
        return None
    m = Mocker()
    m.capabilities(width=128, height=64, rotate=0, mode="1")
    assert m.width == 128
    assert m.height == 64


def test_OLED1306():
    if (is_arm and is_linux) is False:
        return None
    o = OLED1306(port=5, address=0x3C)
    o.capabilities(width=128, height=64, rotate=0, mode="1")
    assert o.width == 128
    assert o.height == 64
