"""CLI for tools."""

import tomllib
from collections.abc import Callable, Collection
from json import dumps
from pathlib import Path
from re import finditer

from cyclopts import App

from boilercv_tools import sync
from boilercv_tools.sync import (
    COMPS,
    PYPROJECT,
    PYRIGHTCONFIG,
    PYTEST,
    add_pyright_includes,
    disable_concurrent_tests,
    get_comp_path,
)

APP = App()
"""CLI."""


def main():
    """Invoke the CLI."""
    APP()


@APP.command()
def get_actions() -> list[str]:
    """Get actions used by this repository.

    For additional security, select "Allow <user> and select non-<user>, actions and
    reusable workflows" in the General section of your Actions repository settings, and
    paste the output of this command into the "Allow specified actions and reusable
    workflows" block.

    Args:
        high: Highest dependencies.
    """
    actions: list[str] = []
    for contents in [
        path.read_text("utf-8") for path in Path(".github/workflows").iterdir()
    ]:
        actions.extend([
            f"{match['action']}@*,"
            for match in finditer(r'uses:\s?"?(?P<action>.+)@', contents)
        ])
    return log(sorted(set(actions)))


@APP.command()
def check() -> str:
    """Verify current dependencies are in the lock."""
    return log("true" if sync.check() else "false")


@APP.command()
def lock() -> Path:
    return log(sync.lock())


@APP.command()
def get_comp(high: bool = False, no_deps: bool = False) -> Path:
    return prep_comp(high, no_deps, sync.get_comp)


@APP.command()
def compile(high: bool = False, no_deps: bool = False) -> Path:  # noqa: A001
    return prep_comp(high, no_deps, sync.compile)


def prep_comp(high: bool, no_deps: bool, op: Callable[[bool, bool], str]) -> Path:
    COMPS.mkdir(exist_ok=True, parents=True)
    comp = get_comp_path(high, no_deps)
    comp.write_text(encoding="utf-8", data=op(high, no_deps))
    return log(comp)


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


def log(obj):
    """Send an object to `stdout` and return it."""
    match obj:
        case Collection():
            if len(obj):
                print(*obj, sep="\n")  # noqa: T201
        case _:
            print(obj)  # noqa: T201
    return obj


if __name__ == "__main__":
    main()
