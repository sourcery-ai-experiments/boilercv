"""Update experiment notebooks from documentation.

Not using this stage currently. Instead, keep experiment notebooks directly in the docs.
"""

from collections.abc import Iterator
from pathlib import Path
from shlex import split
from shutil import copy
from subprocess import run

from boilercore.paths import fold

from boilercv.docs import remove_tags
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
    clean_notebooks(*[docs_nb for docs_nb in nbs if Path(docs_nb).exists()])
    run(split(f"git add {nbs}"), check=True)  # noqa: S603

    for docs_nb, nb in nbs.items():
        if not Path(docs_nb).exists():
            continue
        if Path(docs_nb).exists() and not different(nb, docs_nb):
            continue
        copy(docs_nb, nb)
        remove_tags(Path(nb), ["hide-input"])
    clean_notebooks(*nbs.values())
    run(split(f"git add {nbs}"), check=True)  # noqa: S603


def get_e230920_notebooks() -> Iterator[str]:
    """Yield changed notebooks corresponding to experiment e230920."""
    yield from (
        fold(experiment)
        for stage, experiment in PARAMS.paths.stages.items()
        if stage.startswith(E230920) and experiment.suffix == ".ipynb"
    )


if __name__ == "__main__":
    main()
