"""Equations."""

from __future__ import annotations

from collections.abc import Hashable, Mapping, MutableMapping
from contextlib import contextmanager
from hashlib import sha512
from typing import (
    Any,
    Generic,
    NamedTuple,
    ParamSpec,
    Protocol,
    Self,
    TypeVar,
    get_args,
    get_type_hints,
    overload,
)

from pydantic import ConfigDict, Field, RootModel, ValidationError

T = TypeVar("T", contravariant=True)
R = TypeVar("R", covariant=True)
P = ParamSpec("P")


class TypeType(Protocol[T, R, P]):  # noqa: D101
    def __call__(self, i: T, /, *args: P.args, **kwds: P.kwargs) -> R: ...  # noqa: D102


K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class TypeMap(Protocol[T, K, V, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: T, /, *args: P.args, **kwds: P.kwargs
    ) -> MutableMapping[K, V]: ...


class TypeDict(Protocol[T, K, V, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: T, /, *args: P.args, **kwds: P.kwargs
    ) -> dict[K, V]: ...


class MapType(Protocol[K, V, R, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: MutableMapping[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> R: ...


class DictType(Protocol[K, V, R, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: dict[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> R: ...


RK = TypeVar("RK", bound=Hashable)
RV = TypeVar("RV")


class MapMap(Protocol[K, V, RK, RV, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: MutableMapping[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> MutableMapping[RK, RV]: ...


class DictDict(Protocol[K, V, RK, RV, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: dict[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> dict[RK, RV]: ...


KT = TypeVar("KT", bound=type)
VT = TypeVar("VT", bound=type)


class Types(NamedTuple, Generic[KT, VT]):
    """Mapping types."""

    key: KT
    value: VT


class Morph(  # noqa: PLR0904
    RootModel[MutableMapping[K, V]], MutableMapping[K, V], Generic[K, V]
):
    """Type-checked, generic, morphable mapping."""

    model_config = ConfigDict(strict=True, frozen=True)
    """Root configuration, merged with subclass configs."""
    root: MutableMapping[K, V] = Field(default_factory=dict)
    """Type-checked dictionary as the root data."""

    def __repr__(self):
        return f"{self.get_cls().__name__}({self.root})"

    # ! (([K, V] -> [K, V]) -> Self)
    @overload
    def pipe(
        self, f: MapMap[K, V, K, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    @overload
    def pipe(
        self, f: DictDict[K, V, K, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    # ! ((Self -> [K, V]) -> Self)
    @overload
    def pipe(
        self, f: TypeMap[Self, K, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    @overload
    def pipe(
        self, f: TypeDict[Self, K, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    # ! ((Self -> [RK, RV]) -> Morph[RK, RV])
    @overload
    def pipe(
        self, f: TypeMap[Self, RK, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, RV]: ...
    @overload
    def pipe(
        self, f: TypeDict[Self, RK, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, RV]: ...
    # ! (([K, V] -> R) -> R)
    @overload
    def pipe(self, f: MapType[K, V, R, P], /, *args: P.args, **kwds: P.kwargs) -> R: ...
    @overload
    def pipe(
        self, f: DictType[K, V, R, P], /, *args: P.args, **kwds: P.kwargs
    ) -> R: ...
    # ! ((Self -> R) -> R)
    @overload
    def pipe(
        self, f: TypeType[Self, R, P], /, *args: P.args, **kwds: P.kwargs
    ) -> R: ...
    # ! ((Any -> Any) -> Any)
    def pipe(
        self, f: TypeType[Any, Any, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self | Morph[Any, Any] | Any:
        """Pipe."""
        with (copy := self.model_copy()).thaw():
            result = f(copy, *args, **kwds)
        if isinstance(result, self.get_cls()):
            return self.model_validate(result)
        return_hint = get_type_hints(f).get("return")
        if not isinstance(result, Mapping) or (not return_hint and not len(result)):
            return result
        if not return_hint:
            first_key, first_value = next(iter(result.items()))
            return self.model_nearest_valid(result, type(first_key), type(first_value))
        if len(hints := get_args(return_hint)) == 2:
            hint_k, hint_v = hints
            self_k, self_v = self.get_inner_types()
            return self.model_nearest_valid(
                result,
                self_k if isinstance(hint_k, TypeVar) else hint_k,
                self_v if isinstance(hint_v, TypeVar) else hint_v,
            )
        if issubclass(return_hint, self.get_base()):
            return self.model_nearest_valid(result, *return_hint.get_inner_types())
        return result

    def model_nearest_valid(
        self, result: Self | Mapping[Any, Any], k: type, v: type
    ) -> Self | Mapping[Any, Any]:
        """Try returning validated mapping from parent models."""
        if Types(k, v) == self.get_inner_types():
            try:
                return self.model_validate(result)
            except ValidationError:
                pass
        base = previous_base = self
        while (base := base.get_parent()) is not previous_base:
            try:
                return base[k, v](result)
            except ValidationError:
                previous_base = base
                continue
        return result

    # ! (([K] -> [K]) -> Self)
    @overload
    def pipe_keys(
        self, f: TypeType[list[K], list[K], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    # ! (([K] -> [RK]) -> Morph[RK, V])
    @overload
    def pipe_keys(
        self, f: TypeType[list[K], list[RK], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, V]: ...
    # ! (([K] -> [Any]) -> Self | Morph[Any, V]
    def pipe_keys(
        self, f: TypeType[list[K], list[Any], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self | Morph[Any, V]:
        """Pipe, morphing keys."""

        def pipe(_, *args: P.args, **kwds: P.kwargs):
            return dict(
                zip(f(list(self.keys()), *args, **kwds), self.values(), strict=False)
            )

        return self.pipe(pipe, *args, **kwds)

    # ! (([V] -> [V]) -> Self)
    @overload
    def pipe_values(
        self, f: TypeType[list[V], list[V], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    # ! (([V] -> [RV]) -> Morph[K, RV])
    @overload
    def pipe_values(
        self, f: TypeType[list[V], list[RV], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[K, RV]: ...
    # ! (([V] -> [Any]) -> Self | Morph[K, Any]
    def pipe_values(
        self, f: TypeType[list[V], list[Any], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self | Morph[K, Any]:
        """Pipe, morphing values."""

        def pipe(_, *args: P.args, **kwds: P.kwargs):
            return dict(
                zip(self.keys(), f(list(self.values()), *args, **kwds), strict=False)
            )

        return self.pipe(pipe, *args, **kwds)

    def __hash__(self):
        # ? https://github.com/pydantic/pydantic/issues/1303#issuecomment-2052395207
        return int.from_bytes(
            sha512(
                f"{self.__class__.__qualname__}::{self.model_dump_json()}".encode(
                    "utf-8", errors="ignore"
                )
            ).digest()
        )

    @classmethod
    def get_base(cls) -> type:
        """Get base model class."""
        base = previous_base = cls
        while (base := base.get_parent()) is not previous_base:
            previous_base = base
        return base

    @classmethod
    def get_parent(cls) -> type:
        """Get parent model class."""
        return cls.__pydantic_generic_metadata__["origin"] or super().__thisclass__  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_cls(cls) -> type:
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
            return self.model_validate(self | dict(other))
        return NotImplemented

    def __ror__(self, other) -> Self:
        if isinstance(other, Mapping):
            return self.model_validate(dict(other) | dict(self))
        return NotImplemented

    def __ior__(self, other) -> Self:
        return self | other
