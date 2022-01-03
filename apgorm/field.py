# MIT License
#
# Copyright (c) 2021 TrigonDev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar

from apgorm.converter import Converter
from apgorm.exceptions import UndefinedFieldValue
from apgorm.migrations.describe import DescribeField
from apgorm.undefined import UNDEF

if TYPE_CHECKING:
    from apgorm.model import Model

    from .types.base_type import SqlType


_T = TypeVar("_T")
_C = TypeVar("_C")
_F = TypeVar("_F", bound="SqlType")


class BaseField(Generic[_F, _T, _C]):
    name: str  # populated by Database
    model: Type[Model]  # populated by Database

    def __init__(
        self,
        sql_type: _F,
        *,
        default: str | BaseField | None = None,
        one_time_default: _T | None = None,
        not_null: bool = False,
        use_repr: bool = True,
        use_eq: bool = False,
    ):
        self.sql_type = sql_type

        if isinstance(default, BaseField):
            default = default.name
        self.default = default
        self.one_time_default = one_time_default

        self.not_null = not_null

        self.use_repr = use_repr
        self.use_eq = use_eq

        self.changed: bool = False
        self._value: _T | UNDEF = UNDEF.UNDEF

    def describe(self) -> DescribeField:
        return DescribeField(
            self.name,
            self.sql_type.sql,
            self.not_null,
            self.default,
            self.one_time_default,
        )

    @property
    def full_name(self) -> str:
        return f"{self.model.tablename}.{self.name}"

    @property
    def v(self) -> _C:
        raise NotImplementedError

    @v.setter
    def v(self, other: _C):
        raise NotImplementedError

    def _copy_kwargs(self) -> dict[str, Any]:
        return dict(
            sql_type=self.sql_type,
            default=self.default,
            one_time_default=self.one_time_default,
            not_null=self.not_null,
            use_repr=self.use_repr,
            use_eq=self.use_eq,
        )

    def copy(self) -> BaseField[_F, _T, _C]:
        n = self.__class__(**self._copy_kwargs())
        if hasattr(self, "name"):
            n.name = self.name
        if hasattr(self, "model"):
            n.model = self.model
        return n


class Field(BaseField[_F, _T, _T]):
    @property
    def v(self) -> _T:
        if self._value is UNDEF.UNDEF:
            raise UndefinedFieldValue(self)
        return self._value

    @v.setter
    def v(self, other: _T):
        self._value = other
        self.changed = True

    def with_converter(
        self, converter: Converter[_T, _C] | Type[Converter[_T, _C]]
    ) -> ConverterField[_F, _T, _C]:
        if isinstance(converter, type) and issubclass(converter, Converter):
            converter = converter()
        f: ConverterField[_F, _T, _C] = ConverterField(
            **self._copy_kwargs(), converter=converter
        )
        if hasattr(self, "name"):
            f.name = self.name
        if hasattr(self, "model"):
            f.model = self.model
        return f


class ConverterField(BaseField[_F, _T, _C]):
    def __init__(self, *args, **kwargs):
        self.converter: Converter[_T, _C] = kwargs.pop("converter")
        super().__init__(*args, **kwargs)

    @property
    def v(self) -> _C:
        if self._value is UNDEF.UNDEF:
            raise UndefinedFieldValue(self)
        return self.converter.from_stored(self._value)

    @v.setter
    def v(self, other: _C):
        self._value = self.converter.to_stored(other)
        self.changed = True

    def _copy_kwargs(self) -> dict[str, Any]:
        dct = super()._copy_kwargs()
        dct["converter"] = self.converter
        return dct
