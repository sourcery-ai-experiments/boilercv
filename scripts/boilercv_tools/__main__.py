"""CLI for tools."""

import tomllib
from collections.abc import Collection
from pathlib import Path
from re import finditer
from shlex import split
from subprocess import run

from cyclopts import App

from boilercv_tools.sync import (
    PYTEST,
    CompPaths,
    disable_concurrent_tests,
    escape,
    get_comps,
    synchronize,
)

APP = App(help_format="markdown")
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.command
def sync(high: bool = False):
    """Sync."""
    synchronize()
    comps = get_comps()
    run(
        input=comps.high if high else comps.low,
        args=split("bin/uv pip sync -"),
        check=True,
        text=True,
    )


@APP.command
def get_actions():
    """Get actions used by this repository.

    For additional security, select "Allow <user> and select non-<user>, actions and
    reusable workflows" in the General section of your Actions repository settings, and
    paste the output of this command into the "Allow specified actions and reusable
    workflows" block.

    Parameters
    ----------
    high
        Highest dependencies.
    """
    actions: list[str] = []
    for contents in [
        path.read_text("utf-8") for path in Path(".github/workflows").iterdir()
    ]:
        actions.extend([
            f"{match['action']}@*,"
            for match in finditer(r'uses:\s?"?(?P<action>.+)@', contents)
        ])
    log(sorted(set(actions)))


@APP.command
def sync_local_dev_configs():
    """Synchronize local dev configs to shadow `pyproject.toml`, with some changes.

    Duplicate pytest configuration from `pyproject.toml` to `pytest.ini`. These files
    shadow the configuration in `pyproject.toml`, which drives CI or if shadow configs
    are not present. Shadow configs are in `.gitignore` to facilitate local-only
    shadowing. Concurrent test runs are disabled in the local pytest configuration which
    slows down the usual local, granular test workflow.
    """
    config = tomllib.loads(Path("pyproject.toml").read_text("utf-8"))
    pytest = config["tool"]["pytest"]["ini_options"]
    pytest["addopts"] = disable_concurrent_tests(pytest["addopts"])
    PYTEST.write_text(
        encoding="utf-8",
        data="\n".join(["[pytest]", *[f"{k} = {v}" for k, v in pytest.items()], ""]),
    )


def log(obj):
    """Send object to `stdout`."""
    match obj:
        case str():
            print(obj)  # noqa: T201
        case CompPaths():
            for comp in obj:
                log(comp)
        case Collection():
            for o in obj:
                log(o)
        case Path():
            log(escape(obj))
        case _:
            print(obj)  # noqa: T201


if __name__ == "__main__":
    main()
