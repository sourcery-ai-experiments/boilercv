"""Utilities for generating documentation."""

from collections.abc import Iterable
from shlex import join, split
from subprocess import run


def clean_notebooks(nbs: Iterable[str]):  # type: ignore  # `nbs` redefined
    nbs: str = join(nbs)
    files = f"--files {nbs}"
    for cmd in [
        split(f".venv/scripts/pre-commit run {subcmd}")
        for subcmd in [f"nb-clean {files}", f"ruff {files}", f"ruff-format {files}"]
    ]:
        run(cmd, check=False)  # noqa: S603
    run(split(f"git add {nbs}"), check=True)  # noqa: S603


def different(nb: str, docs_nb: str) -> bool:
    """Check whether notebooks have different cell contents."""
    return bool(
        run(
            split(  # noqa: S603
                f".venv/scripts/nbdiff {nb} {docs_nb}"
                " --ignore-outputs --ignore-metadata --ignore-details"
            ),
            capture_output=True,
            check=True,
        ).stdout
    )
