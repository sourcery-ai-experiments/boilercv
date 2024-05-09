"""Equations."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterator, Mapping
from inspect import get_annotations
from pathlib import Path
from shlex import quote
from types import GenericAlias
from typing import (
    Any,
    Generic,
    NamedTuple,
    ParamSpec,
    Protocol,
    Self,
    TypeVar,
    get_args,
)

from pydantic import Field, RootModel

PIPX = quote((Path(".venv") / "scripts" / "pipx").as_posix())
"""Escaped path to `pipx` executable suitable for `subprocess.run` invocation."""

K = TypeVar("K", bound=Hashable)
KR = TypeVar("KR", bound=Hashable)
V = TypeVar("V", covariant=True)
VR = TypeVar("VR", contravariant=True)
P = ParamSpec("P")


class MorphMap(
    RootModel[dict[K, Any]], Mapping[K, V], Generic[K, V], arbitrary_types_allowed=True
):
    """Type-checked, generic, morphable mapping."""

    root: dict[K, V] = Field(default_factory=dict)
    """Type-checked dictionary as the root data."""

    def asdict(self) -> dict[K, V]:
        """Get as dictionary."""
        return dict(self)

    def pipe(
        self, f: Morph[K, V, KR, VR, P], *args: P.args, **kwds: P.kwargs
    ) -> MorphMap[KR, VR]:
        """Pipe."""
        morphed = self.morph(f, *args, **kwds)
        k, v = self.get_result_types(f, morphed)
        return MorphMap[k, v](morphed)

    def pipe_keys(
        self, f: InnerMorph[K, KR, P], *args: P.args, **kwds: P.kwargs
    ) -> MorphMap[KR, V]:
        """Pipe, morphing only keys."""
        morphed_keys = [f(k, *args, **kwds) for k in self.keys()]
        self_k, v = self.get_inner_types()
        k = self.get_inner_result_type(f, morphed_keys) or self_k
        return MorphMap[k, v](dict(zip(morphed_keys, self.values(), strict=False)))

    def pipe_vals(
        self, f: InnerMorph[V, VR, P], *args: P.args, **kwds: P.kwargs
    ) -> MorphMap[K, VR]:
        """Pipe, morphing only values."""
        morphed_vals = [f(k, *args, **kwds) for k in self.values()]
        k, self_v = self.get_inner_types()
        v = self.get_inner_result_type(f, morphed_vals) or self_v
        return MorphMap[k, v](dict(zip(self.keys(), morphed_vals, strict=False)))

    def morph(
        self,
        f: Morph[K, V, KR, VR, P] | Callable[..., Any],
        *args: P.args,
        **kwds: P.kwargs,
    ) -> dict[KR, VR]:
        """Morph."""
        morphed = f(dict(self), *args, **kwds)
        if not isinstance(morphed, Mapping):
            raise TypeError(f"Unsupported return type: {type(morphed)}")
        return dict(morphed)

    def get_result_types(
        self, f: Callable[..., Mapping[KR, VR]], result: dict[KR, VR]
    ) -> Types[type[KR], type[VR]]:
        """Get morphed types of keys and values."""
        annotations = get_annotations(f, eval_str=True)
        return_types: None | GenericAlias | type[Self] = annotations.get("return")
        if return_types is None and not len(result):
            raise ValueError("Cannot infer return type from empty mapping.")
        if return_types is None:
            first_key, first_value = next(iter(result.items()))
            return Types(type(first_key), type(first_value))
        self_types = self.get_inner_types()
        if not return_types:
            return self_types
        if isinstance(return_types, GenericAlias):
            typed_returns = get_args(return_types)
            ret_k, ret_v = Types(*typed_returns)
            self_k, self_v = Types(*self_types)
            return Types(
                self_k if isinstance(ret_k, TypeVar) else ret_k,
                self_v if isinstance(ret_v, TypeVar) else ret_v,
            )
        if issubclass(return_types, self.get_base()):
            return return_types.get_inner_types()
        raise ValueError(f"Unsupported return type: {return_types}")

    def get_inner_result_type(
        self, f: Callable[..., R], result: list[R]
    ) -> type | None:
        """Get morphed type of keys or values."""
        annotations = get_annotations(f, eval_str=True)
        return_type: None | TypeVar | type = annotations.get("return")
        if return_type is None and not len(result):
            raise ValueError("Cannot infer return type from empty mapping.")
        if return_type is None:
            first = next(iter(result))
            return type(first)
        if not return_type:
            return None
        return None if isinstance(return_type, TypeVar) else return_type

    def get_base(self) -> type[Self]:
        """Get base model."""
        return super().__thisclass__  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def make(cls, d: Mapping[K, V]) -> MorphMap[K, V]:
        """Create a `MorphMap` from a dictionary."""
        first_key, first_value = next(iter(d.items()))
        k, v = Types(type(first_key), type(first_value))
        return MorphMap[k, v](dict(d))

    @classmethod
    def get_inner_types(cls) -> Types[type, type]:
        """Get types of the keys and values."""
        return Types(*get_args(cls.model_fields["root"].annotation))

    def __iter__(self) -> Iterator[K]:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Iterate over root rather than the `RootModel` instance."""
        return iter(dict(self.root))

    def __getitem__(self, key: K) -> V:
        return self.root[key]

    def __len__(self) -> int:
        return len(self.root)


KT = TypeVar("KT", bound=type)
VT = TypeVar("VT", bound=type)


class Types(NamedTuple, Generic[KT, VT]):
    """Mapping types."""

    key: KT
    value: VT


GK = TypeVar("GK", bound=Hashable)
GKR = TypeVar("GKR", bound=Hashable)
GV = TypeVar("GV", contravariant=True)
GVR = TypeVar("GVR", covariant=True)
GP = ParamSpec("GP")


class Morph(Protocol[GK, GV, GKR, GVR, GP]):  # noqa: D101
    def __call__(  # noqa: D102
        self, m: Mapping[GK, GV], *args: GP.args, **kwds: GP.kwargs
    ) -> Mapping[GKR, GVR]: ...


T = TypeVar("T", contravariant=True)
R = TypeVar("R", covariant=True)


class InnerMorph(Protocol[T, R, P]):  # noqa: D101
    def __call__(self, i: T, *args: P.args, **kwds: P.kwargs) -> R: ...  # noqa: D102
