try:
    import pyrealsense2 as rs

    assert "2." in str(rs.__version__)
except AttributeError:
    import pyrealsense2.pyrealsense2 as rs

    assert "2." in str(rs.__version__)

import os
import platform
import random
from warnings import warn

from ctyper import Color

is_x86: bool = platform.machine() in ("i386", "AMD64", "x86_64")
is_arm: bool = platform.machine() in ("arm64", "aarch64")
is_darwin: bool = platform.system() == "Darwin"
is_linux: bool = platform.system() == "Linux"

# visual debug mode
VDBG: bool = str(os.environ.get("VDBG")) == "1"

# no realsense mode
NORS: bool = str(os.environ.get("NORS")) == "1"
if len(rs.context().query_devices()) == 0:
    warn("no realsense device, skipping test")
    NORS = True  # force NORS if no device connected


colors_80: list[Color] = [
    tuple([random.randint(0, 255) for _ in range(3)]) for _ in range(80)
]
