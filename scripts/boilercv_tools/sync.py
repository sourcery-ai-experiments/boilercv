"""Sync tools."""

from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, time
from json import dumps, loads
from pathlib import Path
from platform import platform
from re import finditer, sub
from shlex import join, split
from subprocess import run
from sys import executable, version_info
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
LOCK = Path("lock.json")
"""Locked set of dependency compilations for different runner/Python combinations."""

# ! Checking
SUB_PAT = r"(?m)^# submodules/(?P<name>[^\s]+)\s(?P<rev>[^\s]+)$"
"""Pattern for stored submodule revision comments."""
DEP_PAT = r"(?mi)^(?:[A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])==.+$"
"""Pattern for compiled dependencies.

See: https://packaging.python.org/en/latest/specifications/name-normalization/#name-format
"""


def check() -> bool:
    """Verify current dependencies are in the lock."""
    old = get_comp(high=False, no_deps=False)
    if not old:
        raise ValueError("Compilation missing from lock.")
    new = compile(high=False, no_deps=True)
    subs = dict(zip(finditer(SUB_PAT, old), finditer(SUB_PAT, new), strict=False))
    return all((
        all(old_sub.groups() == new_sub.groups() for old_sub, new_sub in subs.items()),
        all(dep.group() in old for dep in finditer(DEP_PAT, new)),
    ))


def get_comp(high: bool, no_deps: bool) -> str:
    """Get existing dependency compilation.

    Args:
        high: Highest dependencies.
        no_deps: Without transitive dependencies.
        fallback: Compile if the compilation does not exist.
    """
    comp_key = get_comp_name(high, no_deps).removeprefix("requirements_")
    if LOCK.exists() and (
        existing_comp := loads(LOCK.read_text("utf-8")).get(comp_key)
    ):
        return existing_comp
    return ""


def lock() -> Path:
    """Lock all local dependency compilations."""
    LOCK.write_text(
        encoding="utf-8",
        data=dumps(
            indent=2,
            sort_keys=True,
            obj={
                **(loads(LOCK.read_text("utf-8")) if LOCK.exists() else {}),
                **{
                    comp.stem.removeprefix("requirements_"): comp.read_text("utf-8")
                    for comp in COMPS.iterdir()
                },
            },
        )
        + "\n",
    )
    return LOCK


def compile(high: bool, no_deps: bool) -> str:  # noqa: A001
    """Compile dependencies for a system.

    Args:
        comp: Path to the compilation.
        high: Highest dependencies.
        no_deps: Without transitive dependencies.
    """
    sep = " "
    result = run(
        args=split(
            sep.join([
                f"{Path(executable).as_posix()} -m uv",
                f"pip compile --python-version {VERSION}",
                f"--resolution {'highest' if high else 'lowest-direct'}",
                f"--exclude-newer {datetime.now(UTC).isoformat().replace('+00:00', 'Z')}",
                f"--all-extras {'--no-deps' if no_deps else ''}",
                sep.join([p.as_posix() for p in [PYPROJECT, DEV, DVC, SYNC]]),
            ])
        ),
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    deps = result.stdout
    submodules = {
        sub.group(): run(
            split(f"git rev-parse HEAD:{sub.group()}"),  # noqa: S603
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        for sub in finditer(r"submodules/.+\b", DEV.read_text("utf-8"))
    }
    return (
        "\n".join([
            *[f"# {sub} {rev}" for sub, rev in submodules.items()],
            *[line.strip() for line in deps.splitlines()],
            *[line.strip() for line in NODEPS.read_text("utf-8").splitlines()],
        ])
        + "\n"
    )


def get_comp_path(high: bool, no_deps: bool) -> Path:
    """Get a dependency compilation.

    Args:
        high: Highest dependencies.
        no_deps: Without transitive dependencies.
    """
    return COMPS / f"{get_comp_name(high, no_deps)}.txt"


def get_comp_name(high: bool, no_deps: bool) -> str:
    """Get name of a dependency compilation.

    Args:
        high: Highest dependencies.
        no_deps: Without transitive dependencies.
    """
    if high and no_deps:
        raise ValueError("Cannot specify both `high` and `no_deps`.")
    return "_".join([
        "requirements",
        RUNNER,
        VERSION,
        *(["high"] if high else []),
        *(["no_deps"] if no_deps else []),
    ])


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
