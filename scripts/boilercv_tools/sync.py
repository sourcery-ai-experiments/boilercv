"""CLI for tools."""

from collections.abc import Iterable, Mapping, Sequence
from datetime import date, time
from pathlib import Path
from platform import platform
from re import sub
from shlex import join, split
from sys import stdout, version_info
from typing import TypeAlias

# ! For local dev config tooling
PYRIGHTCONFIG = Path("pyrightconfig.json")
"""Resulting pyright configuration file."""
PYTEST = Path("pytest.ini")
"""Resulting pytest configuration file."""

# ! Dependencies
PYPROJECT = Path("pyproject.toml")
"""Path to `pyproject.toml`."""
REQS = Path("requirements")
"""Requirements."""
SYNC = REQS / "sync.in"
"""Core dependencies for syncing."""
DEV = REQS / "dev.in"
"""Other development tools and editable local dependencies."""
DVC = REQS / "dvc.in"
"""Separate DVC dependency due to occasional VSCode extension sync conflict."""
NODEPS = REQS / "nodeps.in"
"""Dependencies appended to locks without compiling their dependencies."""

# ! Platform
PLATFORM = platform(terse=True)
"""Platform identifier."""
match PLATFORM.casefold().split("-")[0]:
    case "macos":
        _runner = "macos-13"
    case "windows":
        _runner = "windows-2022"
    case "linux":
        _runner = "ubuntu-22.04"
    case _:
        raise ValueError(f"Unsupported platform: {PLATFORM}")
RUNNER = _runner
"""Runner associated with this platform."""
match version_info[:2]:
    case (3, 8):
        _python_version = "3.8"
    case (3, 9):
        _python_version = "3.9"
    case (3, 10):
        _python_version = "3.10"
    case (3, 11):
        _python_version = "3.11"
    case (3, 12):
        _python_version = "3.12"
    case (3, 13):
        _python_version = "3.13"
    case _:
        _python_version = "3.11"
VERSION = _python_version
"""Python version associated with this platform."""

# ! Compilation and locking
COMPS = Path(".comps")
"""Platform-specific dependency compilations."""
COMPS.mkdir(exist_ok=True, parents=True)
LOCK = Path("lock.json")
"""Locked set of dependency compilations for different runner/Python combinations."""


def get_comp_path(high: bool) -> Path:
    """Get a dependency compilation.

    Args:
        high: Highest dependencies.
    """
    return COMPS / f"{get_comp_name(high)}.txt"


def get_comp_name(high: bool) -> str:
    """Get name of a dependency compilation.

    Args:
        high: Highest dependencies.
    """
    return "_".join(["requirements", RUNNER, VERSION, *(["high"] if high else [])])


def log(obj):
    """Send an object to `stdout` and return it."""
    print(obj, file=stdout)  # noqa: T201
    return obj


Leaf: TypeAlias = int | float | bool | date | time | str
"""Leaf node."""
Node: TypeAlias = Leaf | Sequence["Node"] | Mapping[str, "Node"]
"""General node."""


def add_pyright_includes(
    config: dict[str, Node], others: Iterable[Path | str]
) -> dict[str, Node]:
    """Include additional paths in pyright configuration.

    Args:
        config: Pyright configuration.
        others: Local paths to add to includes.

    Returns:
        Modified pyright configuration.
    """
    includes = config.pop("include", [])
    if not isinstance(includes, Sequence):
        raise TypeError("Expected a sequence of includes.")
    return {
        "include": [*includes, *[str(Path(incl).as_posix()) for incl in others]],
        **config,
    }


def disable_concurrent_tests(addopts: str) -> str:
    """Normalize `addopts` string and disable concurrent pytest tests.

    Normalizes `addopts` to a space-separated one-line string.

    Args:
        addopts: Pytest `addopts` value.

    Returns:
        Modified `addopts` value.
    """
    return sub(pattern=r"-n\s*[^\s]+", repl="-n 0", string=join(split(addopts)))
