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
t = NDArray[Shape['*, *'], Any]

t = NDArray[Shape['N, M, * ...'], Any]
a = np.random.rand(3, 5, 7)
isinstance(a, t)




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


import lark
SHAPE_GRAMMAR = (
    '''
    // https://github.com/ramonhagenaars/nptyping/blob/master/USERDOCS.md#Shape-expressions
    ?start: shape_expression

    shape_expression     :  dimensions | dimensions "," ellipsis
    dimensions           :  dimension | dimension "," dimensions
    dimension            :  unlabeled_dimension | labeled_dimension
    labeled_dimension    :  unlabeled_dimension " " label
    unlabeled_dimension  :  number | variable | wildcard | dimension_breakdown
    wildcard             :  "*"
    dimension_breakdown  :  "[" labels "]"
    labels               :  label | label "," labels
    label                :  lletter | lletter word
    variable             :  uletter | uletter word
    word                 :  letter | word underscore | word number
    letter               :  lletter | uletter
    uletter              :  "A"|"B"|"C"|"D"|"E"|"F"|"G"|"H"|"I"|"J"|"K"|"L"|"M"|"N"|"O"|"P"|"Q"|"R"|"S"|"T"|"U"|"V"|"W"|"X"|"Y"|"Z"
    lletter              :  "a"|"b"|"c"|"d"|"e"|"f"|"g"|"h"|"i"|"j"|"k"|"l"|"m"|"n"|"o"|"p"|"q"|"r"|"s"|"t"|"u"|"v"|"w"|"x"|"y"|"z"
    number               :  digit | number digit
    digit                :  "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9"
    underscore           :  "_"
    ellipsis             :  "..."
    ''')
# shape_parser = lark.Lark(SHAPE_GRAMMAR,  start='start', parser='lalr')
shape_parser = lark.Lark(SHAPE_GRAMMAR,  start='start', parser='earley')
print(shape_parser.parse('3').pretty())
print(shape_parser.parse('N,M').pretty())
print(shape_parser.parse('N,3').pretty())
print(shape_parser.parse('*,*').pretty())
print(shape_parser.parse('2,...').pretty())
print(shape_parser.parse('*,...').pretty())
print(shape_parser.parse('1,3,4,5,...').pretty())
print(shape_parser.parse('*,*,...').pretty())
