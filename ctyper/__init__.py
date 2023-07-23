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
    dw: int
    dh: int


@dataclasses.dataclass
class RawDiagBbox:
    x0: float
    y0: float
    x1: float
    y1: float


@dataclasses.dataclass
class DiagBbox:
    x0: int
    y0: int
    x1: int
    y1: int


@dataclasses.dataclass
class RawObjDetected:
    box: RawDiagBbox
    score: float
    clsid: int


@dataclasses.dataclass
class ObjDetected:
    box: DiagBbox
    score: float
    clsid: int


# custom exceptions
class MatNotValid(Exception):
    pass


class InferError(Exception):
    pass


class InferExtractError(Exception):
    pass


class InferPreprocessError(Exception):
    pass


class InferPostprocessError(Exception):
    pass
