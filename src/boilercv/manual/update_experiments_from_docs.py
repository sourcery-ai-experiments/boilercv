"""Update experiment notebooks from documentation."""

from collections.abc import Iterator
from pathlib import Path
from shutil import copy

from boilercore.paths import fold

from boilercv.docs_generation import clean_notebooks, different
from boilercv.models.params import PARAMS

ROOT = PARAMS.paths.package / "stages"
"""Replicate directories in documentation relative to this package."""

E230920 = "experiments_e230920"
"""Subcooling experiment."""


def main():
    nbs = {
        fold(PARAMS.paths.docs / Path(nb).relative_to(ROOT)): nb
        for nb in get_e230920_notebooks()
    }
    clean_notebooks([docs_nb for docs_nb in nbs if Path(docs_nb).exists()])
    for docs_nb, nb in nbs.items():
        if not Path(docs_nb).exists():
            continue
        if Path(docs_nb).exists() and not different(nb, docs_nb):
            continue
        copy(docs_nb, nb)
    clean_notebooks(nbs.values())


def get_e230920_notebooks() -> Iterator[str]:
    """Yield changed notebooks corresponding to experiment e230920."""
    yield from (
        fold(experiment)
        for stage, experiment in PARAMS.paths.stages.items()
        if stage.startswith(E230920) and experiment.suffix == ".ipynb"
    )


if __name__ == "__main__":
    main()
