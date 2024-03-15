"""Tools."""

import json
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, time
from json import dumps
from pathlib import Path
from platform import platform
from re import sub
from shlex import join, split
from subprocess import run
from sys import executable, stdout, version_info
from tomllib import loads
from typing import Literal, TypeAlias

import tomlkit
from cyclopts import App
from packaging.requirements import Requirement
from tomlkit.items import Array

# * -------------------------------------------------------------------------------- * #
# * Types

# ! For local dev config tooling
Leaf: TypeAlias = int | float | bool | date | time | str
"""Leaf node."""
Node: TypeAlias = Leaf | Sequence["Node"] | Mapping[str, "Node"]
"""General nde."""

# * -------------------------------------------------------------------------------- * #
# * Constants

# ! CLI
APP = App()
"""Cyclopts CLI."""

# ! Dependencies in `pyproject.toml`
PYPROJECT = Path("pyproject.toml")
"""Path to `pyproject.toml`."""
USER_EXTRAS = ["cv"]
"""User-facing extras in `pyproject.toml`."""
DEV_EXTRAS = ["dev"]
"""Development-specific pins of main dependencies in `pyproject.toml`."""

# ! Requirements
REQS = Path("requirements")
"""Requirements."""
UV = REQS / "uv.in"
"""Requirements file containing the `uv` version pin for bootstrapping installs."""
DEV = REQS / "dev.in"
"""Other development requirements including editable local package installs."""
NODEPS = REQS / "nodeps.in"
"""Requirements that should be appended to locks without solving for dependencies."""

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

# ! Locks
LOCKS = Path(".locks")
"""Locks computed or retrieved for this platform."""
ENVIRONMENT = "_".join(["requirements", RUNNER, VERSION])
"""Unique environment identifier, also used for the artifact name."""
LOCKSFILE = Path("locks.json")
"""Merged locks for all platforms."""

# ! For local dev config tooling
PYRIGHTCONFIG = Path("pyrightconfig.json")
"""Resulting pyright configuration file."""
PYTEST = Path("pytest.ini")
"""Resulting pytest configuration file."""

# * -------------------------------------------------------------------------------- * #
# * Module-level initialization

LOCKS.mkdir(exist_ok=True, parents=True)

# * -------------------------------------------------------------------------------- * #
# * CLI


@APP.command()
def sync_paired_deps():
    """Synchronize paired dependencies within a TOMLKit array."""
    content = PYPROJECT.read_text("utf-8")
    pyproject = tomlkit.loads(content)
    sync_paired_dependency(
        deps=pyproject["project"]["optional-dependencies"]["dev"],  # pyright: ignore[reportArgumentType, reportIndexIssue]  # pyright==1.1.350, packaging==24.0
        src="pandas",
        dst="pandas-stubs",
    )
    if content != (content := tomlkit.dumps(pyproject)):
        PYPROJECT.write_text(encoding="utf-8", data=content)
    return log(f"{PLATFORM = }")


@APP.command()
def lock(kind: Literal["dev", "low", "high"] = "dev") -> Path:
    """Lock requirements.

    Args:
        kind: Lock kind.
    """
    match kind:
        case "dev":
            resolution = "lowest-direct"
            extras = USER_EXTRAS + DEV_EXTRAS
        case "low":
            resolution = "lowest-direct"
            extras = USER_EXTRAS
        case "high":
            resolution = "highest"
            extras = USER_EXTRAS
        case _:  # pyright: ignore[reportUnnecessaryComparison]  # Validate outside of CLI
            raise ValueError(f'Kind {kind} is not one of "dev", "low", or "high".')
    sep = " "
    result = run(
        args=split(
            sep.join([
                f"{Path(executable).as_posix()} -m uv",
                f"pip compile --python-version {VERSION}",
                f"--resolution {resolution}",
                f"--exclude-newer {datetime.now(UTC).isoformat().replace('+00:00', 'Z')}",
                sep.join([f"--extra {e}" for e in extras]),
                sep.join([p.as_posix() for p in [PYPROJECT, DEV, UV]]),
            ])
        ),
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    lockfile = get_lockfile(kind)
    lockfile.write_text(
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
    return log(lockfile)


@APP.command()
def merge_locks() -> Path:
    """Combine locks into a single file."""
    LOCKSFILE.write_text(
        encoding="utf-8",
        data=json.dumps(
            indent=2,
            obj={
                lock.stem: lock.read_text("utf-8")
                for lock in LOCKS.rglob("requirements_*.txt")
            },
        )
        + "\n",
    )
    return log(LOCKSFILE)


@APP.command()
def get_lock(kind: Literal["dev", "low", "high"] = "dev") -> Path:
    """Get lock.

    Args:
        kind: Lock kind.
    """
    if LOCKSFILE.exists():
        lockfile = get_lockfile(kind)
        if existing_lock := json.loads(LOCKSFILE.read_text("utf-8")).get(lockfile.stem):
            lockfile.write_text(encoding="utf-8", data=existing_lock)
            return lockfile
    return lock(kind)


def log(obj):
    """Send an object to `stdout` and return it."""
    print(obj, file=stdout)  # noqa: T201
    return obj


def get_lockfile(kind: Literal["dev", "low", "high"] = "dev") -> Path:
    """Get the path to a lock.

    Args:
        kind: Lock kind.
    """
    return LOCKS / f"{ENVIRONMENT}_{kind}.txt"


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
    config = loads(PYPROJECT.read_text("utf-8"))
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


def sync_paired_dependency(deps: Array, src: str, dst: str):
    """Synchronize a dependency within a TOMLKit array.

    Synchronize `dst` dependency version from the `src` dependency version to maintain
    coupled dependency relationships. For example, since the major/minor/patch version
    numbers should match between `pandas` and `pandas-stubs`, this means that
    `pandas-stubs` needs a`~=` relationship to the same version that `pandas` has a
    `==*.*.*` relationship to.

    Args:
        deps: List of dependencies to synchronize.
        src: Source dependency name.
        dst: Destination dependency name.
    """
    reqs = [Requirement(r) for r in deps]
    src_req = next(r for r in reqs if r.name == src)
    specs = src_req.specifier
    if len(specs) != 1:
        raise ValueError(f"Expected exactly one specifier in {src_req}.")
    src_ver = next(iter(specs)).version
    for i, dst_req in enumerate(reqs):
        if dst_req.name != dst:
            continue
        specs = dst_req.specifier
        if len(specs) != 1:
            raise ValueError(f"Expected exactly one specifier in {dst_req}.")
        dst_spec = next(iter(specs))
        deps[i] = str(Requirement(f"{dst_req.name}{dst_spec.operator}{src_ver}"))


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


# * -------------------------------------------------------------------------------- * #

if __name__ == "__main__":
    APP()
