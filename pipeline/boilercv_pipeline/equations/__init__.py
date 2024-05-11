"""Equations."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterator, Mapping, Sequence
from hashlib import sha512
from inspect import get_annotations
from types import GenericAlias
from typing import Generic, NamedTuple, ParamSpec, Protocol, Self, TypeVar, get_args

from pydantic import Field, RootModel

P = ParamSpec("P")

K = TypeVar("K", bound=Hashable)
RK = TypeVar("RK", bound=Hashable)
V = TypeVar("V")
RV = TypeVar("RV")


class MorphMap(
    RootModel[dict[K, V]], Mapping[K, V], Generic[K, V], arbitrary_types_allowed=True
):
    """Type-checked, generic, morphable mapping."""

    root: dict[K, V] = Field(default_factory=dict)
    """Type-checked dictionary as the root data."""

    def pipe(
        self, f: MappingMorph[K, V, RK, RV, P], *args: P.args, **kwds: P.kwargs
    ) -> MorphMap[RK, RV]:
        """Pipe."""
        result = f(self.model_dump(), *args, **kwds)
        k, v = self.get_result_types(f, result)
        return MorphMap[k, v](result)

    def pipe_keys(
        self, f: ValueMorph[K, RK, P], *args: P.args, **kwds: P.kwargs
    ) -> MorphMap[RK, V]:
        """Pipe, morphing each key."""
        k, v = self.get_inner_types()
        result = [f(k, *args, **kwds) for k in self.keys()]
        k = self.get_inner_result_type(f, result) or k
        return MorphMap[k, v](dict(zip(result, self.values(), strict=False)))

    def pipe_values(
        self, f: ValueMorph[V, RV, P], *args: P.args, **kwds: P.kwargs
    ) -> MorphMap[K, RV]:
        """Pipe, morphing each value."""
        k, v = self.get_inner_types()
        result = [f(k, *args, **kwds) for k in self.values()]
        v = self.get_inner_result_type(f, result) or v
        return MorphMap[k, v](dict(zip(self.keys(), result, strict=False)))

    def get_result_types(
        self, f: Callable[..., Mapping[RK, RV] | tuple[RK, RV]], result: Mapping[RK, RV]
    ) -> Types[type[RK], type[RV]]:
        """Get morphed types of keys and values."""
        annotations = get_annotations(f, eval_str=True)
        return_types: None | GenericAlias | type[Self] = annotations.get("return")
        if return_types is None and not len(result):
            raise TypeError("Cannot infer return type from empty mapping.")
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
        raise TypeError(f"Unsupported return type: {return_types}")

    def get_inner_result_type(
        self, f: Callable[..., R], result: Sequence[R]
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

    def __hash__(self):
        # ? https://github.com/pydantic/pydantic/issues/1303#issuecomment-2052395207
        return int.from_bytes(
            sha512(
                f"{self.__class__.__qualname__}::{self.model_dump_json()}".encode(
                    "utf-8", errors="ignore"
                )
            ).digest()
        )

    def __iter__(self) -> Iterator[K]:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Iterate over root rather than the `RootModel` instance."""
        return iter(self.root)

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


KPD = TypeVar("KPD", bound=Hashable)
RKPD = TypeVar("RKPD", bound=Hashable)
VPD = TypeVar("VPD")
RVPD = TypeVar("RVPD")


class DictMorph(Protocol[KPD, VPD, RKPD, RVPD, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: dict[KPD, VPD], *args: P.args, **kwds: P.kwargs
    ) -> dict[RKPD, RVPD]: ...


KM = TypeVar("KM", bound=Hashable)
RKM = TypeVar("RKM", bound=Hashable)
VM = TypeVar("VM", contravariant=True)
RVM = TypeVar("RVM")


class MappingMorph(Protocol[KM, VM, RKM, RVM, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: Mapping[KM, VM], *args: P.args, **kwds: P.kwargs
    ) -> dict[RKM, RVM]: ...


T = TypeVar("T", contravariant=True)
R = TypeVar("R", covariant=True)


class ValueMorph(Protocol[T, R, P]):  # noqa: D101
    def __call__(self, i: T, *args: P.args, **kwds: P.kwargs) -> R: ...  # noqa: D102
