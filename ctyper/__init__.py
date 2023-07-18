import numpy as np
from typing import TypeAlias

# custom type alias
Image: TypeAlias = np.ndarray
Color: TypeAlias = tuple[int, int, int]
Array: TypeAlias = np.ndarray


# custom exceptions
class MatNotValid(Exception):
    pass
