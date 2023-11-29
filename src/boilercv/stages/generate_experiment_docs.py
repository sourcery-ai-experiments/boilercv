"""Generate documentation from experiment notebooks."""

from collections.abc import Iterable, Iterator
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from shlex import join, split
from subprocess import run

from boilercore.paths import fold, modified
from ploomber_engine import execute_notebook

from boilercv.models.params import PARAMS

ROOT = PARAMS.paths.package / "stages"
"""Replicate directories in documentation relative to this package."""

E230920 = "experiments_e230920"
"""Subcooling experiment."""


def main():
    if nbs := get_changed_e230920_notebooks():
        clean_notebooks(nbs)
    else:
        return
    docs_nbs: list[str] = []
    with ProcessPoolExecutor() as executor:
        for nb in get_changed_e230920_notebooks():
            docs_nb = fold(PARAMS.paths.docs / Path(nb).relative_to(ROOT))
            if Path(docs_nb).exists() and not different(nb, docs_nb):
                continue
            executor.submit(execute_notebook, input_path=nb, output_path=docs_nb)
            docs_nbs.append(docs_nb)
    if docs_nbs:
        clean_notebooks(docs_nbs, docs=True)


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


def get_changed_e230920_notebooks() -> Iterator[str]:
    """Yield changed notebooks corresponding to experiment e230920."""
    yield from (
        fold(experiment)
        for stage, experiment in PARAMS.paths.stages.items()
        if stage.startswith(E230920)
        and experiment.suffix == ".ipynb"
        and modified(experiment)
    )


def clean_notebooks(nbs: Iterable[str], docs: bool = False):  # type: ignore
    nbs: str = join(nbs)
    files = f"--files {nbs}"
    for cmd in [
        split(f".venv/scripts/pre-commit run {subcmd}")
        for subcmd in [
            f"nb-clean{'-docs' if docs else ''} {files}",
            f"ruff {files}",
            f"ruff-format {files}",
        ]
    ]:
        run(cmd, check=False)  # noqa: S603
    run(split(f"git add {nbs}"), check=True)  # noqa: S603


if __name__ == "__main__":
    main()
