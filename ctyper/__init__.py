import dataclasses
from typing import TypeAlias

import numpy as np

# custom type alias
Image: TypeAlias = np.ndarray
Color: TypeAlias = tuple[int, int, int]
Array: TypeAlias = np.ndarray


# custom dataclass
@dataclasses.dataclass
class InputSize:
    w: int
    h: int


@dataclasses.dataclass
class MLPreprocessParams:
    w0: int
    h0: int
    w1: int
    h1: int
    wpad: int
    hpad: int
    scale: float


# custom exceptions
class MatNotValid(Exception):
    pass
