"""Tools."""

import json
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, time
from json import dumps
from pathlib import Path
from platform import platform
from re import sub
from shlex import join, split
from subprocess import run
from sys import base_prefix, executable, prefix, stdout, version_info
from typing import TypeAlias

from cyclopts import App

APP = App()
"""Cyclopts CLI."""

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
UV = REQS / "uv.in"
"""Requirements file containing the `uv` version pin for bootstrapping installs."""
DEV = REQS / "dev.in"
"""Other development requirements including editable local package installs."""
NODEPS = REQS / "nodeps.in"
"""Requirements that should be appended to locks without solving for dependencies."""

# ! Platform
GLOBAL_PYTHON = prefix == base_prefix
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
LOCKS = Path("locks.json")
"""Locked set of dependency compilations for different runner/Python combinations."""


@APP.command()
def sync(high: bool = False, compile: bool = False, lock: bool = False):  # noqa: A002
    """Synchronize the environment."""
    sep = " "
    run(
        args=split(
            sep.join([
                f"{Path(executable).as_posix()} -m uv pip sync",
                "--system --break-system-packages" if GLOBAL_PYTHON else "",
                (compile_deps(high) if compile else get_compiled_deps(high)).as_posix(),
            ])
        ),
        check=True,
    )
    if lock:
        lock_deps()


def lock_deps() -> Path:
    """Lock all local dependency compilations."""
    LOCKS.write_text(
        encoding="utf-8",
        data=json.dumps(
            indent=2,
            sort_keys=True,
            obj={
                **(json.loads(LOCKS.read_text("utf-8")) if LOCKS.exists() else {}),
                **{
                    comp.stem.removeprefix("requirements_"): comp.read_text("utf-8")
                    for comp in COMPS.iterdir()
                },
            },
        )
        + "\n",
    )
    return log(LOCKS)


def get_compiled_deps(high: bool = False) -> Path:
    """Compile dependencies for a system.

    Args:
        high: Highest dependencies.
    """
    if LOCKS.exists():
        comp = get_compiled_deps_path(high)
        if existing_comp := json.loads(LOCKS.read_text("utf-8")).get(comp.stem):
            comp.write_text(encoding="utf-8", data=existing_comp)
            return comp
    return compile_deps(high)


def compile_deps(high: bool = False) -> Path:
    """Recompile dependencies for a system.

    Args:
        high: Highest dependencies.
    """
    sep = " "
    result = run(
        args=split(
            sep.join([
                f"{Path(executable).as_posix()} -m uv",
                f"pip compile --python-version {VERSION}",
                f"--resolution {'highest' if high else 'lowest-direct'}",
                f"--exclude-newer {datetime.now(UTC).isoformat().replace('+00:00', 'Z')}",
                "--all-extras",
                sep.join([p.as_posix() for p in [PYPROJECT, DEV, UV]]),
            ])
        ),
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    comp = get_compiled_deps_path(high)
    comp.write_text(
        encoding="utf-8",
        data=(
            "\n".join([
                *[r.strip() for r in [result.stdout]],
                *[
                    line.strip()
                    for line in NODEPS.read_text("utf-8").splitlines()
                    if not line.strip().startswith("#")
                ],
            ])
            + "\n"
        ),
    )
    return log(comp)


def get_compiled_deps_path(high: bool) -> Path:
    """Get a dependency compilation.

    Args:
        high: Highest dependencies.
    """
    return COMPS / f"{get_compiled_deps_name(high)}.txt"


def get_compiled_deps_name(high: bool) -> str:
    """Get name of a dependency compilation.

    Args:
        high: Highest dependencies.
    """
    return "_".join(["requirements", RUNNER, VERSION, *(["high"] if high else [])])


def log(obj):
    """Send an object to `stdout` and return it."""
    print(obj, file=stdout)  # noqa: T201
    return obj


@APP.command()
def sync_local_dev_configs():
    """Synchronize local dev configs to shadow `pyproject.toml`, with some changes.

    Duplicate pyright and pytest configuration from `pyproject.toml` to
    `pyrightconfig.json` and `pytest.ini`, respectively. These files shadow the
    configuration in `pyproject.toml`, which drives CI or if shadow configs are not
    present. Shadow configs are in `.gitignore` to facilitate local-only shadowing.

    Local pyright configuration includes the editable local `boilercore` dependency to
    facilitate refactoring and runing on the latest uncommitted code of that dependency.
    Concurrent test runs are disabled in the local pytest configuration which slows down
    the usual local, granular test workflow.
    """
    config = tomllib.loads(PYPROJECT.read_text("utf-8"))
    # Write pyrightconfig.json
    pyright = config["tool"]["pyright"]
    data = dumps(
        add_pyright_includes(pyright, [".", Path("../boilercore/src")]), indent=2
    )
    PYRIGHTCONFIG.write_text(encoding="utf-8", data=f"{data}\n")
    # Write pytest.ini
    pytest = config["tool"]["pytest"]["ini_options"]
    pytest["addopts"] = disable_concurrent_tests(pytest["addopts"])
    PYTEST.write_text(
        encoding="utf-8",
        data="\n".join(["[pytest]", *[f"{k} = {v}" for k, v in pytest.items()], ""]),
    )


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


if __name__ == "__main__":
    APP()
