import os
import platform
import random

is_x86: bool = platform.machine() in ("i386", "AMD64", "x86_64")
is_arm: bool = platform.machine() in ("arm64", "aarch64")
is_darwin: bool = platform.system() == "Darwin"
is_linux: bool = platform.system() == "Linux"

VDBG: bool = str(os.environ.get("VDBG")) == "1"

colors_80 = [[random.randint(0, 255) for _ in range(3)] for _ in range(80)]
