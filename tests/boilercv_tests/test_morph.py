"""Test `MorphMap`."""

from __future__ import annotations

from collections.abc import Hashable, Mapping, Sized
from typing import Literal, TypeAlias, TypeVar

import pytest
from boilercv_pipeline.equations import Morph

K = TypeVar("K", bound=Hashable)
V = TypeVar("V", bound=Sized)
Fruit: TypeAlias = Literal["apple", "banana", "cherry"]
m = Morph[Fruit, str]({"apple": "delicious"})
m2 = Morph[str, str]({"anything": "unsure"})


def f1(m: Mapping[K, Sized]) -> Mapping[K, int]:  # noqa: D103
    return {k: len(v) for k, v in m.items()}


def f2(m: Mapping[K, V]) -> Mapping[K, V]:  # noqa: D103
    vs = list(m.values())
    (len(v) for v in vs)
    return m


@pytest.mark.parametrize("f", [f1, f2])
def test_generic_with_other(f):
    """`MorphMap` pipe with generic morph works on other `MorphMap`s."""
    m2.pipe(f)  # pyright: ignore[reportCallIssue]


def f3(m: Mapping[Fruit, str]) -> Mapping[Fruit, int]:  # noqa: D103
    return {k: len(v) for k, v in m.items()}


def f4(m: Mapping[str, str]) -> Mapping[str, int]:  # noqa: D103
    return {k: len(v) for k, v in m.items()}


def f5(m: Mapping[Fruit, str]) -> Morph[str, int]:  # noqa: D103
    return Morph[str, int]({k: len(v) for k, v in m.items()})


def f6(m: Mapping[Fruit, str]):  # noqa: D103
    return Morph[str, int]({k: len(v) for k, v in m.items()})


@pytest.mark.parametrize("f", [f1, f2, f3, f4, f5, f6])
def test_pipe(f):
    """`MorphMap` pipe works as expected."""
    m.pipe(f)  # pyright: ignore[reportCallIssue]


def f7(m: Mapping[Fruit, str]) -> int:  # noqa: D103
    return 1


def test_pipe_raises():
    """`MorphMap` pipe raises error as expected."""
    with pytest.raises(TypeError):
        m.pipe(f7)  # pyright: ignore[reportArgumentType]


def f8(i: Fruit):  # noqa: D103
    return "yes" if i == "foo" else "no"


def f9(i: Fruit) -> str:  # noqa: D103
    return "yes" if i == "foo" else "no"


@pytest.mark.parametrize("f", [f8, f9])
def test_keys(f):
    """`MorphMap` key pipe works as expected."""
    m.pipe_values(f)  # pyright: ignore[reportCallIssue]


def f10(i: str):  # noqa: D103
    return 1 if i == "some" else 0


def f11(i: str) -> int:  # noqa: D103
    return 1 if i == "some" else 0


@pytest.mark.parametrize("f", [f10, f11])
def test_values(f):
    """`MorphMap` value pipe works as expected."""
    m.pipe_values(f)  # pyright: ignore[reportCallIssue]
