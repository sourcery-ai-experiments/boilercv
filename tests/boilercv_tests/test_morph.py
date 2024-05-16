"""Test `MorphMap`."""

from __future__ import annotations

from collections.abc import Callable, Hashable, MutableMapping
from contextlib import suppress
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeAlias

import pytest
from boilercv_pipeline.equations import K, Morph, TypeType, V
from pydantic import ValidationError

# TODO: Implement existing behavior outlined here
# TODO: After that's working, also handle nested mappings

SKIP = False
REASON = "Mixed pass/fail parametrized test. Will implement functionality later."


# * MARK: Constants
# fmt: off
Fruit: TypeAlias = Literal["apple", "banana", "cherry"]
ANY_MAP: dict[Hashable, Any] = {"any": "map"}
FRUIT: list[Fruit] = ["apple", "banana", "cherry"]
_SelfMap: TypeAlias = MutableMapping[Fruit, str]
_SelfDict: TypeAlias = dict[Fruit, str]
SELF_DICT: _SelfDict = {"apple": "delicious"}
_OtherDict: TypeAlias = dict[Fruit, int]
OTHER_DICT: _OtherDict = dict.fromkeys(FRUIT, 0)
# fmt: on

# * MARK: Concrete morphs
# fmt: off
# ! Descriptions
Morph_: TypeAlias = Morph[Fruit, str]
SELF_MORPH = Morph_(SELF_DICT)
class _Self(Morph_): ...
SELF = _Self(SELF_DICT)

# ! Counts
_OtherMorph: TypeAlias = Morph[Fruit, int]
OTHER_MORPH = _OtherMorph(OTHER_DICT)
class _Other(_OtherMorph): ...
OTHER = _Other(OTHER_DICT)
# fmt: on


# * MARK: Generic morphs and concrete morphs based on generic morph
# fmt: off
# ! Note that `TypeAlias`es cannot be `Generic`, e.g. they don't support `TypeVar`s.
class _GenericMorph(Morph[K, V], Generic[K, V]): ...
GENERIC_MORPH = _GenericMorph(ANY_MAP)

# ! Descriptions
_SubSelfMorph: TypeAlias = _GenericMorph[Fruit, str]
SUB_SELF_MORPH = _SubSelfMorph(SELF_DICT)
class _SubSelf(_SubSelfMorph): ...
SUB_SELF = _SubSelf(SELF_DICT)

# ! Counts
_SubOtherMorph: TypeAlias = _GenericMorph[Fruit, int]
SUB_OTHER_MORPH = _SubOtherMorph(OTHER_DICT)
class _SubOther(_SubOtherMorph): ...
SUB_OTHER = _SubOther(OTHER_DICT)
# fmt: on


# * MARK: ((Any -> Any) -> Any)
# fmt: off
# ! (str -> UNANNOTATED)
def str_unk(i: str
    ): return len(i)
def _():
    return SELF.pipe(str_unk)  # type: ignore

# ! (str -> Any)
def str_any(i: str
    ) -> Any: return len(i)
def _():
    return SELF.pipe(str_any)  # type: ignore

# ! (str -> int)
def str_int(i: str
    ) -> int: return len(i)
def _():
    return SELF.pipe(str_int)  # type: ignore

# ! (str -> Map)
def str_map(i: str
    ) -> MutableMapping[str, int]: return {i: len(i)}
def _():
    return SELF.pipe(str_map)  # type: ignore
def str_dict(_: str
    ) -> _SelfDict: return SELF_DICT
def _():
    return SELF.pipe(str_dict)  # type: ignore

# ! (str -> Morph)
def str_morph(_: str
    ) -> Morph_: return SELF_MORPH
def _():
    return SELF.pipe(str_morph)  # type: ignore

# ! (str -> Self)
def str_self(_: str
    ) -> _Self: return SELF
def _():
    return SELF.pipe(str_self)  # type: ignore

# * MARK: ((*[K2, V2] -> R) -> R)

# ! (UNANNOTATED -> str)
def unk_str(i
    ) -> str: return str(i)
def _():
    return SELF.pipe(unk_str)

# ! (Any -> str)
def any_str(i: Any
    ) -> str: return str(i)
def _():
    return SELF.pipe(any_str)

# ! (Map -> str)
def map_str(i: _SelfMap
    ) -> str: return str(i)
def _():
    return SELF.pipe(map_str)

# ! (dict -> str)
def dict_str(i: _SelfDict
    ) -> str: return str(i)
def _():
    return SELF.pipe(dict_str)

# ! (otherdict -> str)
def otherdict_str(i: _OtherDict
    ) -> str: return str(i)
def _():
    return SELF.pipe(otherdict_str)  # type: ignore

# ! (Morph -> str)
def morph_str(i: Morph_
    ) -> str: return str(i)
def _():
    return SELF.pipe(morph_str)

# ! (Self -> str)
def self_str(i: _Self
    ) -> str: return str(i)
def _():
    return SELF.pipe(self_str)

# ! Concrete subclasses are compatible with matching aliases, but not vice versa
def str_aliased_desc_2(_: str
    ) -> Morph_: return SELF
def _():
    return SELF.pipe(str_aliased_desc_2)  # type: ignore
def str_desc_2(_: str
    ) -> _Self: return SELF_MORPH  # type: ignore
def _():
    return SELF.pipe(str_desc_2)  # type: ignore

# fmt: on

# * MARK: Test string-taking functions

Pipe: TypeAlias = TypeType[Any, Any, Any]
StrTaking: TypeAlias = Callable[[str], Any]
str_taking: list[StrTaking] = [
    str_unk,
    str_any,
    str_int,
    str_map,
    str_self,
    otherdict_str,  # type: ignore
    str_aliased_desc_2,
]


with suppress(TypeError, ValidationError):
    if TYPE_CHECKING:
        for f in str_taking:
            # TODO: Should raise `TypeError`
            v1 = SELF.pipe(f)  # type: ignore


@pytest.mark.skipif(SKIP, reason=REASON)
@pytest.mark.parametrize("f", str_taking)
def test_pipe_str_taking(f: Pipe):
    """Functions not taking maps raise `TypeError` when `pipe`d."""
    assert SELF.pipe(f) == f(SELF)


SelfLikeMapReturning: TypeAlias = Callable[..., _SelfMap]
self_like_map_returning: list[SelfLikeMapReturning] = [str_dict, str_morph, str_desc_2]


@pytest.mark.skipif(SKIP, reason=REASON)
@pytest.mark.parametrize("f", self_like_map_returning)
def test_pipe_self_returning(f: Pipe):
    """Functions not taking maps raise `TypeError` when `pipe`d."""
    assert SELF.pipe(f) == _Self(f(SELF))


def list_int_str(i: list[Fruit]) -> list[int]:
    return [len(j) for j in i]


FruitListTaking: TypeAlias = Callable[[list[Fruit]], Any]


@pytest.mark.skipif(SKIP, reason=REASON)
@pytest.mark.parametrize("f", [list_int_str])
def test_pipe_keys(f: FruitListTaking):
    result = SELF.pipe_keys(f)
    k, v = result.get_inner_types()
    assert result == Morph[k, v](
        dict(zip(f(list(SELF.keys())), SELF.values(), strict=False))
    )


def list_str_int(i: list[str]) -> list[int]:
    return [len(j) for j in i]


IntListTaking: TypeAlias = Callable[[list[str]], Any]


@pytest.mark.skipif(SKIP, reason=REASON)
@pytest.mark.parametrize("f", [list_str_int])
def test_pipe_values(f: IntListTaking):
    result = SELF.pipe_values(f)
    k, v = result.get_inner_types()
    assert result == Morph[k, v](
        dict(zip(SELF.keys(), f(list(SELF.values())), strict=False))
    )


# * MARK: Define map-taking functions
# fmt: off

# ! (Map -> Unk)
def map_unk(i: _SelfMap
    ): return Morph_(i)
def _():
    return SELF.pipe(map_unk)
def dict_unk(i: dict[Fruit, str]
    ): return Morph_(i)
def _():
    return SELF.pipe(dict_unk)
def morph_unk(i: Morph_
    ): return Morph_(i)
def _():
    return SELF.pipe(morph_unk)
def self_unk(i: _Self
    ): return i
def _():
    return SELF.pipe(self_unk)

# ! (Map -> Any)
def map_any(i: _SelfMap
    ) -> Any: return Morph_(i)
def _():
    return SELF.pipe(map_any)
def dict_any(i: dict[Fruit, str]
    ) -> Any: return Morph_(i)
def _():
    return SELF.pipe(dict_any)
def morph_any(i: Morph_
    ) -> Any: return Morph_(i)
def _():
    return SELF.pipe(morph_any)
def self_any(i: _Self
    ) -> Any: return i
def _():
    return SELF.pipe(self_any)

# ! (MutableMapping -> Morph)
def map_morph(i: _SelfMap
    ) -> Morph_: return Morph_(i)
def _():
    return SELF.pipe(map_morph)
def map_self(i: _SelfMap
    ) -> _Self: return _Self(i)
def _():
    return SELF.pipe(map_self)

# ! (dict -> Self)
def dict_morph(i: dict[Fruit, str]
    ) -> Morph_: return Morph_(i)
def _():
    return SELF.pipe(dict_morph)
def dict_self(i: dict[Fruit, str]
    ) -> _Self: return _Self(i)
def _():
    return SELF.pipe(dict_self)

# ! (Morph -> Self)
def morph_morph(i: Morph_
    ) -> Morph_: return Morph_(i)
def _():
    return SELF.pipe(morph_morph)
def morph_self(i: Morph_
    ) -> _Self: return _Self(i)
def _():
    return SELF.pipe(morph_self)

# ! (Self -> Self)
def self_self(i: _Self
    ) -> _Self: return i
def _():
    return SELF.pipe(self_self)

# ! (Morph -> Other)
def morph1_self2(_: Morph_
    ) -> _Other: return OTHER
def _():
    return SELF.pipe(morph1_self2)

# ! (Self -> Other)
def self1_self2(_: _Self
    ) -> _Other: return OTHER
def _():
    return SELF.pipe(self1_self2)

# ! (Self -> Other)
def other_dict(_: _GenericMorph[Fruit, int]
    ) -> _SelfDict: return SELF_DICT
def _():
    return SELF.pipe(other_dict)  # type: ignore

# fmt: on

# * MARK: Test map-taking functions

AnyTaking: TypeAlias = Callable[..., Any]
map_taking: list[AnyTaking] = [
    map_morph,
    map_self,
    dict_morph,
    dict_self,
    morph_morph,
    morph_self,
    self_self,
    map_any,
    dict_any,
    morph_any,
    self_any,
    morph1_self2,
    self1_self2,
    other_dict,
]

with suppress(TypeError, ValidationError):
    if TYPE_CHECKING:
        for f in map_taking:
            # TODO: Should work
            v10 = SELF.pipe(f)


@pytest.mark.parametrize("f", map_taking)
def test_pipe_works(f: AnyTaking):
    """Functions work when `pipe`d."""
    SELF.pipe(f)
