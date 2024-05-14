"""Test `MorphMap`."""

from __future__ import annotations

from collections.abc import Callable, Hashable, MutableMapping
from contextlib import suppress
from typing import Any, Generic, Literal, TypeAlias

import pytest
from boilercv_pipeline.equations import K, Morph, V
from pydantic import ValidationError

# TODO: Implement existing behavior outlined here
# TODO: After that's working, also handle nested mappings

SKIP = True
REASON = "Mixed pass/fail parametrized test. Will implement functionality later."


# * MARK: Constants
# fmt: off
Fruit: TypeAlias = Literal["apple", "banana", "cherry"]
ANY_MAP: dict[Hashable, Any] = {"any": "map"}
FRUIT: list[Fruit] = ["apple", "banana", "cherry"]
FruitDescriptionsDict: TypeAlias = dict[Fruit, str]
DICT_FRUIT_DESCRIPTIONS: FruitDescriptionsDict = {"apple": "delicious"}
FruitCountsDict: TypeAlias = dict[Fruit, int]
DICT_FRUIT_COUNTS: FruitCountsDict = dict.fromkeys(FRUIT, 0)
# fmt: on

# * MARK: Concrete morphs
# fmt: off
# ! Descriptions
FruitDescriptionsMorph: TypeAlias = Morph[Fruit, str]
MORPH_FRUIT_DESCRIPTIONS = FruitDescriptionsMorph(DICT_FRUIT_DESCRIPTIONS)
class FruitDescriptions(FruitDescriptionsMorph): ...
FRUIT_DESCRIPTIONS = FruitDescriptions(DICT_FRUIT_DESCRIPTIONS)
# ! Counts
FruitCountsMorph: TypeAlias = Morph[Fruit, int]
aliased_fruit_counts = FruitCountsMorph(DICT_FRUIT_COUNTS)
class FruitCounts(FruitCountsMorph): ...
FRUIT_COUNTS = FruitCounts(DICT_FRUIT_COUNTS)
# fmt: on


# * MARK: Generic morphs and concrete morphs based on generic morph
# fmt: off
# ! Note that `TypeAlias`es cannot be `Generic`, e.g. they don't support `TypeVar`s.
class MyMorph(Morph[K, V], Generic[K, V]): ...
my_morph = MyMorph(ANY_MAP)
# ! Descriptions
FruitDescriptionsAlias2: TypeAlias = MyMorph[Fruit, str]
aliased_fruit_descriptions_2 = FruitDescriptionsAlias2(DICT_FRUIT_DESCRIPTIONS)
class FruitDescriptions2(FruitDescriptionsAlias2): ...
concrete_fruit_descriptions_2 = FruitDescriptions2(DICT_FRUIT_DESCRIPTIONS)
# ! Counts
FruitCountsAlias2: TypeAlias = Morph[Fruit, int]
aliased_fruit_counts_2 = FruitCountsAlias2(DICT_FRUIT_COUNTS)
class FruitCounts2(FruitCountsAlias2): ...
concrete_fruit_counts_2 = FruitCounts2(DICT_FRUIT_COUNTS)
# fmt: on


# * MARK: Define string-taking functions
# fmt: off
# ! (str -> UNANNOTATED)
def str_any(i: str): return len(i)
# ! (str -> int)
def str_int(i: str) -> int: return len(i)
# ! (str -> Map)
def str_map(i: str) -> MutableMapping[str, int]: return {i: len(i)}
def str_dict(_: str) -> FruitDescriptionsDict: return DICT_FRUIT_DESCRIPTIONS
# ! (str -> Morph)
def str_morph(_: str) -> FruitDescriptionsMorph: return MORPH_FRUIT_DESCRIPTIONS
# ! (str -> FruitDescriptions)
def str_self(_: str) -> FruitDescriptions: return FRUIT_DESCRIPTIONS
# ! Concrete subclasses are compatible with matching aliases, but not vice versa
def str_aliased_desc_2(_: str) -> FruitDescriptionsMorph: return FRUIT_DESCRIPTIONS
def str_desc_2(_: str) -> FruitDescriptions: return MORPH_FRUIT_DESCRIPTIONS  # type: ignore
# fmt: on
StrTaking: TypeAlias = Callable[[str], Any]
str_taking: list[StrTaking] = [
    str_any,
    str_int,
    str_map,
    str_dict,
    str_morph,
    str_self,
    str_aliased_desc_2,
    str_desc_2,
]

# * MARK: Test string-taking functions
with suppress(TypeError, ValidationError):
    for f in str_taking:
        # TODO: Should raise `TypeError`
        v1 = FRUIT_DESCRIPTIONS.pipe(f)  # type: ignore
        # TODO: Should raise `ValidationError` after pipe due to invalid key type
        v2 = FRUIT_DESCRIPTIONS.pipe_keys(f)
        # TODO: Should work
        v3 = FRUIT_DESCRIPTIONS.pipe_values(f)


@pytest.mark.skipif(SKIP, reason=REASON)
@pytest.mark.parametrize("f", str_taking)
def test_pipe_bad_annotation_raises(f: StrTaking):
    """Functions not taking maps raise `TypeError` when `pipe`d."""
    with pytest.raises(TypeError):
        FRUIT_DESCRIPTIONS.pipe(f)


@pytest.mark.skipif(SKIP, reason=REASON)
@pytest.mark.parametrize("f", str_taking)
def test_pipe_bad_key_annotation_raises(f: StrTaking):
    """Functions taking improper keys raise `ValidationError` when `pipe_keys`ed."""
    with pytest.raises(TypeError):
        FRUIT_DESCRIPTIONS.pipe_keys(f)


@pytest.mark.skipif(SKIP, reason=REASON)
@pytest.mark.parametrize("f", str_taking)
def test_pipe_values(f: StrTaking):
    """Functions work when `pipe_values`ed."""
    FRUIT_DESCRIPTIONS.pipe(f)


# * MARK: Define map-taking functions
# fmt: off
# ! (MutableMapping -> FruitDescriptions)
def map_morph(i: MutableMapping[Fruit, str]) -> FruitDescriptionsMorph: return FruitDescriptionsMorph(i)
def map_self(i: MutableMapping[Fruit, str]) -> FruitDescriptions: return FruitDescriptions(i)
# ! (dict -> FruitDescriptions)
def dict_morph(i: dict[Fruit, str]) -> FruitDescriptionsMorph: return FruitDescriptionsMorph(i)
def dict_self(i: dict[Fruit, str]) -> FruitDescriptions: return FruitDescriptions(i)
# ! (FruitDescriptionsMorph -> FruitDescriptions)
def morph_morph(i: FruitDescriptionsMorph) -> FruitDescriptionsMorph: return FruitDescriptionsMorph(i)
def morph_self(i: FruitDescriptionsMorph) -> FruitDescriptions: return FruitDescriptions(i)
# ! (FruitDescriptions -> FruitDescriptions)
def self_self(i: FruitDescriptions) -> FruitDescriptions: return i
# ! (Map -> *UNANNOTATED*)
def map_any(i: MutableMapping[Fruit, str]): return FruitDescriptionsMorph(i)
def dict_any(i: dict[Fruit, str]): return FruitDescriptionsMorph(i)
def morph_any(i: FruitDescriptionsMorph): return FruitDescriptionsMorph(i)
def self_any(i: FruitDescriptions): return i
# ! (FruitDescriptionsMorph -> FruitCounts)
def morph1_self2(_: FruitDescriptionsMorph) -> FruitCounts: return FRUIT_COUNTS
# ! (FruitDescriptions -> FruitCounts)
def self1_self2(_: FruitDescriptions) -> FruitCounts: return FRUIT_COUNTS
# fmt: on
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
]

# * MARK: Test map-taking functions

with suppress(TypeError, ValidationError):
    for f in map_taking:
        # TODO: Should work
        v10 = FRUIT_DESCRIPTIONS.pipe(f)
        # TODO: Should raise `TypeError`
        v11 = FRUIT_DESCRIPTIONS.pipe_keys(f)  # type: ignore
        v12 = FRUIT_DESCRIPTIONS.pipe_values(f)  # type: ignore


@pytest.mark.parametrize("f", map_taking)
def test_pipe_works(f: AnyTaking):
    """Functions work when `pipe`d."""
    FRUIT_DESCRIPTIONS.pipe(f)


@pytest.mark.skipif(SKIP, reason=REASON)
@pytest.mark.parametrize("f", map_taking)
def test_pipe_map_key_raises(f: AnyTaking):
    """Functions taking maps raise `TypeError` when `pipe_keys`ed."""
    with pytest.raises(TypeError):
        FRUIT_DESCRIPTIONS.pipe_keys(f)


@pytest.mark.skipif(SKIP, reason=REASON)
@pytest.mark.parametrize("f", map_taking)
def test_pipe_map_value_raises(f: AnyTaking):
    """Functions taking maps raise `TypeError` when `pipe_values`ed."""
    with pytest.raises(TypeError):
        FRUIT_DESCRIPTIONS.pipe(f)
