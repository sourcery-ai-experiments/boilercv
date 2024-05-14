"""Equations."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping, MutableMapping, Sequence
from contextlib import contextmanager
from hashlib import sha512
from inspect import get_annotations
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
    overload,
)

from pydantic import ConfigDict, Field, RootModel

K = TypeVar("K", bound=Hashable)
RK = TypeVar("RK", bound=Hashable)
V = TypeVar("V")
RV = TypeVar("RV")
T = TypeVar("T", contravariant=True)
R = TypeVar("R", covariant=True)
P = ParamSpec("P")


class Morph(  # noqa: PLR0904
    RootModel[MutableMapping[K, V]], MutableMapping[K, V], Generic[K, V]
):
    """Type-checked, generic, morphable mapping."""

    model_config = ConfigDict(strict=True, frozen=True)
    root: MutableMapping[K, V] = Field(default_factory=dict)
    """Type-checked dictionary as the root data."""

    # ? Overloads are ordered by increasing generality, with the non-overloaded type
    # ? annotation being the most general of all. Shorthand notation in header comments
    # ? is ((T -> R1) -> R2), where (T -> R) is the signature of the positional-only
    # ? parameter `f`, conforming to its own `Protocol`, and (? -> R2) is the method
    # ? signature. `Protocol`s and comments use `Map` to refer to `MutableMapping`. Note
    # ? that mappings are mutable inside the `pipe`, and become `frozen` in the case of
    # ? returning `Morph` instances.
    # ?
    # ? Overloads which accept and return `MutableMapping`s are listed first,
    # ? then those which accept any value but still return `MutableMapping`s, then
    # ? those which return any value. Within these groups, overloads are ordered by
    # ? specificity of the return type, with `Self` being most specific.
    # ?
    # ? Note that we must differentiate between e.g. `Self` and `Morph[K, V]`, since
    # ? `Self` represents a specific, concrete, named subclass of `Morph`, while
    # ? `Morph[K, V]` is any subclass with those key- and value-types.

    # * MARK: ((Map -> Self) -> Self)
    @overload  # 1
    def pipe(self, f: SelfSelf[P], /, *args: P.args, **kwds: P.kwargs) -> Self: ...
    @overload  # 2
    def pipe(
        self, f: MorphSelf[K, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    @overload  # 3
    def pipe(self, f: MapSelf[K, V, P], /, *args: P.args, **kwds: P.kwargs) -> Self: ...
    # * MARK: ((Map -> Morph) -> Morph)
    @overload  # 4
    def pipe(
        self, f: SelfMorph[RK, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, RV]: ...
    @overload  # 5
    def pipe(
        self, f: MorphMorph[K, V, RK, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, RV]: ...
    @overload  # 6
    def pipe(
        self, f: MapMorph[K, V, RK, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, RV]: ...
    # * MARK: ((Map -> Map) -> dict)
    @overload  # 7
    def pipe(
        self, f: SelfMap[RK, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> dict[RK, RV]: ...
    @overload  # 8
    def pipe(
        self, f: MorphMap[K, V, RK, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> dict[RK, RV]: ...
    @overload  # 9
    def pipe(
        self, f: MapMap[K, V, RK, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> dict[RK, RV]: ...
    # * MARK: ((... -> Any) -> Any)
    @overload  # 10
    def pipe(self, f: ValueValue[T, R, P], /, *args: P.args, **kwds: P.kwargs) -> R: ...
    def pipe(self, f: Callable[..., Any], /, *args, **kwds):
        """Pipe."""
        copy = self.model_copy()
        with copy.thaw():
            result = f(copy, *args, **kwds)
        cls = self.get_class()
        k, v = self.get_result_types(f, result)
        kc, vc = cls.get_inner_types()
        if k is kc and v is vc:
            return cls(result)
        return self.get_base()[k, v](result)

    # * MARK: ((Value -> Map) -> Self | Morph | dict)
    @overload
    def pipe_keys(
        self, f: ValueSelf[K, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    @overload
    def pipe_keys(
        self, f: ValueMorph[K, RK, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, V]: ...
    @overload
    def pipe_keys(
        self, f: ValueMap[K, RK, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> dict[RK, V]: ...
    # * MARK: ((... -> Any) -> Any)
    @overload
    def pipe_keys(
        self, f: ValueValue[K, R, P], /, *args: P.args, **kwds: P.kwargs
    ) -> R: ...
    def pipe_keys(self, f: Callable[..., Any], *args, **kwds):
        """Pipe, morphing each key."""
        keys = [f(key, *args, **kwds) for key in self.keys()]
        result = dict(zip(keys, self.values(), strict=False))
        k, v = self.get_inner_types()
        k = self.get_inner_result_type(f, keys) or k
        cls = self.get_class()
        kc, vc = cls.get_inner_types()
        if k is kc and v is vc:
            return cls(result)
        return self.get_base()[k, v](result)

    # * MARK: ((Value -> Map) -> Self | Morph | dict)
    @overload
    def pipe_values(
        self, f: ValueSelf[V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    @overload
    def pipe_values(
        self, f: ValueMorph[V, K, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[K, RV]: ...
    @overload
    def pipe_values(
        self, f: ValueMap[V, K, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> dict[K, RV]: ...
    # * MARK: ((... -> Any) -> Any)
    @overload
    def pipe_values(
        self, f: ValueValue[V, R, P], /, *args: P.args, **kwds: P.kwargs
    ) -> R: ...
    def pipe_values(self, f: Callable[..., Any], *args, **kwds):
        """Pipe, morphing each value."""
        values = [f(val, *args, **kwds) for val in self.values()]
        result = dict(zip(self.keys(), values, strict=False))
        k, v = self.get_inner_types()
        v = self.get_inner_result_type(f, values) or v
        cls = self.get_class()
        kc, vc = cls.get_inner_types()
        if k is kc and v is vc:
            return cls(result)
        return self.get_base()[k, v](result)

    # TODO: Generalize to other entire overloaded union of allowed types
    def get_result_types(
        self, f: Callable[..., Mapping[RK, RV] | tuple[RK, RV]], result: Mapping[RK, RV]
    ) -> Types[type[RK], type[RV]]:
        """Get morphed types of keys and values."""
        annotations = get_annotations(f, eval_str=True)
        return_types: None | GenericAlias | type[Self] = annotations.get("return")
        self_types = self.get_inner_types()
        if return_types is None and not len(result):
            return self_types
        if return_types is None:
            first_key, first_value = next(iter(result.items()))
            return Types(type(first_key), type(first_value))
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

    # TODO: Generalize to other entire overloaded union of allowed types
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

    def __hash__(self):
        # ? https://github.com/pydantic/pydantic/issues/1303#issuecomment-2052395207
        return int.from_bytes(
            sha512(
                f"{self.__class__.__qualname__}::{self.model_dump_json()}".encode(
                    "utf-8", errors="ignore"
                )
            ).digest()
        )

    def __repr__(self):
        return f"{self.get_class().__name__}({self.root})"

    @classmethod
    def get_base(cls):
        """Get base model class."""
        return super().__thisclass__  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_class(cls) -> Any:  # Type inference is incorrect
        """Get this class."""
        return cls

    @classmethod
    def get_inner_types(cls) -> Types[type, type]:
        """Get types of the keys and values."""
        return Types(*get_args(cls.model_fields["root"].annotation))

    @classmethod
    def fromkeys(cls, iterable, value=None):  # noqa: D102
        return cls(dict.fromkeys(iterable, value))

    @classmethod
    @contextmanager
    def thaw(cls):
        """Temporarily thaw an instance."""
        original = cls.model_config
        cls.model_config = original | ConfigDict(frozen=False)
        yield
        cls.model_config = original

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
        self._check_frozen(key, item)
        self.root[key] = item

    def __delitem__(self, key):
        self._check_frozen(key, None)
        del self.root[key]

    def __iter__(self):  # pyright: ignore[reportIncompatibleMethodOverride]  # Iterate over `root` instead of `self`.
        return iter(self.root)

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key):
        return key in self.root

    def __or__(self, other) -> Self:
        if isinstance(other, Mapping):
            d = dict(self)
            d.update(other)
            return self.get_class()(d)
        return NotImplemented

    def __ror__(self, other) -> Self:
        if isinstance(other, Mapping):
            d = dict(other)
            d.update(dict(self))
            return self.get_class()(d)
        return NotImplemented

    def __ior__(self, other) -> Self:
        return self | other


KT = TypeVar("KT", bound=type)
VT = TypeVar("VT", bound=type)


class Types(NamedTuple, Generic[KT, VT]):
    """Mapping types."""

    key: KT
    value: VT


# * MARK: (Map -> Self)


class SelfSelf(Protocol[P]):  # noqa: D101
    def __call__(self, i: Self, /, *args: P.args, **kwds: P.kwargs) -> Self: ...  # noqa: D102


class MorphSelf(Protocol[K, V, P]):  # noqa: D101
    def __call__(self, i: Morph[K, V], /, *args: P.args, **kwds: P.kwargs) -> Self: ...  # noqa: D102


class MapSelf(Protocol[K, V, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: MutableMapping[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...


# * MARK: (Map -> Morph)


class SelfMorph(Protocol[K, V, P]):  # noqa: D101
    def __call__(self, i: Self, /, *args: P.args, **kwds: P.kwargs) -> Morph[K, V]: ...  # noqa: D102


class MorphMorph(Protocol[K, V, RK, RV, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: Morph[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, RV]: ...


class MapMorph(Protocol[K, V, RK, RV, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: MutableMapping[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, RV]: ...


# * MARK: (Map -> Map)


class SelfMap(Protocol[K, V, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: Self, /, *args: P.args, **kwds: P.kwargs
    ) -> MutableMapping[K, V]: ...


class MorphMap(Protocol[K, V, RK, RV, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: Morph[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> MutableMapping[RK, RV]: ...


class MapMap(Protocol[K, V, RK, RV, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: MutableMapping[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> MutableMapping[RK, RV]: ...


# * MARK: (... -> Map)


class ValueSelf(Protocol[T, P]):  # noqa: D101
    def __call__(self, i: T, /, *args: P.args, **kwds: P.kwargs) -> Self: ...  # noqa: D102


class ValueMorph(Protocol[T, K, V, P]):  # noqa: D101
    def __call__(self, i: T, /, *args: P.args, **kwds: P.kwargs) -> Morph[K, V]: ...  # noqa: D102


class ValueMap(Protocol[T, K, V, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: T, /, *args: P.args, **kwds: P.kwargs
    ) -> MutableMapping[K, V]: ...


# * MARK: (... -> Any)


class SelfValue(Protocol[R, P]):  # noqa: D101
    def __call__(self, i: Self, /, *args: P.args, **kwds: P.kwargs) -> R: ...  # noqa: D102


class ValueValue(Protocol[T, R, P]):  # noqa: D101
    def __call__(self, i: T, /, *args: P.args, **kwds: P.kwargs) -> R: ...  # noqa: D102
