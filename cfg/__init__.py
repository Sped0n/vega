try:
    import pyrealsense2 as rs

    assert "2." in str(rs.__version__)
except AttributeError:
    import pyrealsense2.pyrealsense2 as rs

    assert "2." in str(rs.__version__)

import multiprocessing
import os
import platform
import random
from warnings import warn

import numpy as np

from ctyper import Color, Array

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

# serial mode, default true if on arm64 linux(board)
SER: bool = is_linux and is_arm
SER = str(os.environ.get("SER")) == "1" and os.environ.get("SER") is not None

# random color for object detection display
colors_80: list[Color] = [
    tuple([random.randint(0, 255) for _ in range(3)]) for _ in range(80)
]

# set global spawn mode
try:
    multiprocessing.set_start_method("spawn")
except RuntimeError:
    pass

lower_red1: Array = np.array([0, 50, 50])
upper_red1: Array = np.array([10, 255, 255])

lower_red2: Array = np.array([170, 50, 50])
upper_red2: Array = np.array([180, 255, 255])
