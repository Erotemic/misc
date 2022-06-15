"""
mypy ~/misc/learn/numpy_type_checking.py
"""
import numpy as np
from typing import Any, Tuple, Literal, TypeVar, Union
# from numpy.typing import NDArray
from nptyping import Shape, NDArray, Int, DType, Float, Floating
import nptyping

"""

"""

# import numpy.typing
# DT1 = TypeVar("T1", bound=numpy.typing.NBitBase)
# DT2 = TypeVar("T2", bound=numpy.typing.NBitBase)


# # https://github.com/ramonhagenaars/nptyping/blob/master/USERDOCS.md#Shape-expressions
# DT1 = TypeVar('DT1', bound=np.generic)
# DT2 = TypeVar('DT2', bound=np.generic)

# from functools import reduce
# import operator as op
# reduce(op.xor, nptyping.typing_.dtype_per_name.values())

# Union[list(nptyping.typing_.dtype_per_name.values())]

# NDArray[Any, Any]
# NDArray[Any, Int]
# NDArray[Any, DT1]

NDArray[Shape['2, 2'], Any]
NDArray[Shape['*, ...'], Any]  # Any shape, any dims
NDArray[Shape['*, *'], Any]  # 2 dims of any size

NDArray[Shape['2, 2'], Any]

ARR_T1 = NDArray[Shape['2, 2'], DType]
ARR_T2 = NDArray[Shape['Any, ...'], DType]

# dtype1 = np.dtype[int]

# type1 = np.typing.NDArray
# type1 = np.ndarray[3, np.int32]
type1 = np.ndarray[Any, Any]
# type1 = np.ndarray

# type2 = np.typing.NDArray[Any]
# type2 = np.typing.NDArray[Tuple[Literal[20], Literal[20]]]
# type2 = NDArray[Tuple[Literal[20], Literal[20]]]
type2 = NDArray[Shape["2, 2"], Int]
# type2 = np.typing.NDArray[int]


def func1(x: type1):
    pass


def func2(x: type2):
    pass


def main():
    x = np.array([1, 2, 3.], dtype=np.float32)
    func1(x)
    func2(x)


# https://stackoverflow.com/questions/51003146/python-3-6-signature-of-method-incompatible-with-super-type-class
class Parent:
    @classmethod
    def random(cls, rng: int = 3):
        return


class Child(Parent):
    @classmethod
    def random(cls, rng: int = 3, n=None):
        return


class Parent1:
    @classmethod
    def random(cls, *, rng: int = 3):
        return


# class Child1(Parent1):
#     @classmethod
#     def random(cls, n, *, rng: int = 3):
#         return


class Child2(Parent1):
    @classmethod
    def random(cls, n, *, rng: int = 3):
        return
