from __future__ import annotations

import sys
from collections.abc import Hashable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Union

import numpy
import numpy.typing
from pandas import DataFrame, Index, Series
from xarray import DataArray
from xarray.core.coordinates import DataArrayCoordinates, DatasetCoordinates

if sys.version_info >= (3, 10):
    from types import EllipsisType, NotImplementedType
    from typing import TypeAlias
else:
    EllipsisType = type(Ellipsis)
    NotImplementedType = type(NotImplemented)
    TypeAlias = type(Union)


if TYPE_CHECKING:
    pass


CoordsLike: TypeAlias = (
    Sequence[Sequence | Index | DataArray]
    | Mapping
    | DataArrayCoordinates
    | DatasetCoordinates
)
DimsLike: TypeAlias = str | Iterable[Hashable]

ConstantLike: TypeAlias = (
    int
    | float
    | numpy.floating
    | numpy.integer
    | numpy.ndarray
    | DataArray
    | Series
    | DataFrame
)
SignLike: TypeAlias = str | numpy.ndarray | DataArray | Series | DataFrame
VariableLike: TypeAlias = "ScalarVariable | Variable"
ExpressionLike: TypeAlias = (
    "ScalarLinearExpression | LinearExpression | QuadraticExpression"
)
ConstraintLike: TypeAlias = "Constraint | AnonymousScalarConstraint"
MaskLike: TypeAlias = numpy.ndarray | DataArray | Series | DataFrame
SideLike: TypeAlias = Union[ConstantLike, VariableLike, ExpressionLike]
PathLike: TypeAlias = str | Path
