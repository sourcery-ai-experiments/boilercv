"""Generate documentation from experiment notebooks.

Not using this stage currently. Instead, keep experiment notebooks directly in the docs.
"""

from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from shlex import split
from subprocess import run

from boilercore.paths import fold, modified
from ploomber_engine import execute_notebook

from boilercv.docs import insert_tags
from boilercv.docs_generation import clean_notebooks, different
from boilercv.models.params import PARAMS

ROOT = PARAMS.paths.package / "stages"
"""Replicate directories in documentation relative to this package."""

E230920 = "experiments_e230920"
"""Subcooling experiment."""


def main():
    nbs = get_changed_e230920_notebooks()
    if not nbs:
        return
    clean_notebooks(*nbs)
    run(split(f"git add {nbs}"), check=True)  # noqa: S603
    docs_nbs: list[str] = []
    with ProcessPoolExecutor() as executor:
        for nb in get_changed_e230920_notebooks():
            docs_nb = fold(PARAMS.paths.docs / Path(nb).relative_to(ROOT))
            if Path(docs_nb).exists() and not different(nb, docs_nb):
                continue
            docs_nbs.append(docs_nb)
            executor.submit(execute_notebook, input_path=nb, output_path=docs_nb)
    for docs_nb in docs_nbs:
        insert_tags(Path(docs_nb), ["hide-input"])
    if docs_nbs:
        clean_notebooks(*docs_nbs)
        run(split(f"git add {nbs}"), check=True)  # noqa: S603


def get_changed_e230920_notebooks() -> Iterator[str]:
    """Yield changed notebooks corresponding to experiment e230920."""
    yield from (
        fold(experiment)
        for stage, experiment in PARAMS.paths.stages.items()
        if stage.startswith(E230920)
        and experiment.suffix == ".ipynb"
        and modified(experiment)
    )


if __name__ == "__main__":
    main()
