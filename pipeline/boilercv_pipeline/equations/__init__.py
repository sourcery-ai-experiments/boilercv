"""Equations."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping, MutableMapping, Sequence
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


class Morph(
    RootModel[dict[K, V]],
    MutableMapping[K, V],
    Generic[K, V],
    arbitrary_types_allowed=True,
):
    """Type-checked, generic, morphable mapping."""

    root: dict[K, V] = Field(default_factory=dict)
    """Type-checked dictionary as the root data."""

    def pipe(
        self, f: MutableMappingMorph[K, V, RK, RV, P], *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, RV]:
        """Pipe."""
        result = f(self, *args, **kwds)
        k, v = self.get_result_types(f, result)
        return Morph[k, v](dict(result))

    def pipe_keys(
        self, f: ValueMorph[K, RK, P], *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, V]:
        """Pipe, morphing each key."""
        k, v = self.get_inner_types()
        result = [f(k, *args, **kwds) for k in self.keys()]
        k = self.get_inner_result_type(f, result) or k
        return Morph[k, v](dict(zip(result, self.values(), strict=False)))

    def pipe_values(
        self, f: ValueMorph[V, RV, P], *args: P.args, **kwds: P.kwargs
    ) -> Morph[K, RV]:
        """Pipe, morphing each value."""
        k, v = self.get_inner_types()
        result = [f(k, *args, **kwds) for k in self.values()]
        v = self.get_inner_result_type(f, result) or v
        return Morph[k, v](dict(zip(self.keys(), result, strict=False)))

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

    # `MutableMapping` methods adapted from `collections.UserDict`, but with `data`
    # replaced by `root`and `hasattr` guard changed to equivalent `getattr(..., None)`
    # pattern in `__getitem__`. This is done to prevent inheriting directly from
    # `UserDict`, which doesn't play nicely with `pydantic.RootModel`.
    # Source: https://github.com/python/cpython/blob/7d7eec595a47a5cd67ab420164f0059eb8b9aa28/Lib/collections/__init__.py#L1121-L1211

    def __len__(self):
        return len(self.root)

    def __getitem__(self, key):
        if key in self.root:
            return self.root[key]
        if missing := getattr(self.__class__, "__missing__", None):
            return missing(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        self.root[key] = item

    def __delitem__(self, key):
        del self.root[key]

    def __iter__(self):  # pyright: ignore[reportIncompatibleMethodOverride]  # Iterate over `root` instead of `self`.
        return iter(self.root)

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key):
        return key in self.root

    def __repr__(self):
        k, v = (t.__name__ for t in self.get_inner_types())
        return f"{self.get_base().__name__}[{k}, {v}]({self.root})"

    def __or__(self, other):
        if isinstance(other, Morph):
            return self.__class__(self.root | other.root)
        if isinstance(other, dict):
            return self.__class__(self.root | other)
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, Morph):
            return self.__class__(other.root | self.root)
        if isinstance(other, dict):
            return self.__class__(other | self.root)
        return NotImplemented

    def __ior__(self, other):
        if isinstance(other, Morph):
            self.root |= other.root
        else:
            self.root |= other
        return self

    @classmethod
    def fromkeys(cls, iterable, value=None):  # noqa: D102
        d = cls()
        for key in iterable:
            d[key] = value
        return d


KT = TypeVar("KT", bound=type)
VT = TypeVar("VT", bound=type)


class Types(NamedTuple, Generic[KT, VT]):
    """Mapping types."""

    key: KT
    value: VT


KM = TypeVar("KM", bound=Hashable)
RKM = TypeVar("RKM", bound=Hashable)
VM = TypeVar("VM")
RVM = TypeVar("RVM")


class MutableMappingMorph(Protocol[KM, VM, RKM, RVM, P]):
    """Morph a mutable mapping."""

    def __call__(  # noqa: D102
        self, i: Morph[KM, VM], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RKM, RVM] | MutableMapping[RKM, RVM]: ...


T = TypeVar("T", contravariant=True)
R = TypeVar("R", covariant=True)


class ValueMorph(Protocol[T, R, P]):
    """Morph a value."""

    def __call__(self, i: T, /, *args: P.args, **kwds: P.kwargs) -> R: ...  # noqa: D102
