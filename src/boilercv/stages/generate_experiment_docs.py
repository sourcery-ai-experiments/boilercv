"""Generate documentation from experiment notebooks."""

from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

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
            insert_tags(Path(docs_nb), ["hide-input"])
            docs_nbs.append(docs_nb)
    if docs_nbs:
        clean_notebooks(docs_nbs)


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
