"""Helper functions for tests."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from shutil import copy
from tempfile import _RandomNameSequence  # type: ignore
from types import SimpleNamespace
from typing import Any

import pytest
from _pytest.mark.structures import ParameterSet
from boilercore.notebooks.namespaces import get_nb_ns
from boilercore.paths import get_module_name, get_module_rel, walk_modules
from matplotlib.pyplot import style
from seaborn import color_palette, set_theme

import boilercv
from boilercv.docs_generation import clean_notebooks

PACKAGE = get_module_name(boilercv)
"""Name of the package to test."""
MPLSTYLE = Path("data/plotting/base.mplstyle")
"""Styling for test plots."""
NAMER = _RandomNameSequence()
"""Random name sequence for case files."""
TEST_TEMP_NBS = Path("src/tests")
"""Temporary notebooks directory."""


def init():
    """Initialize test plot formats.

    Implementation copied from `boilercv.docs.init` for now, to avoid circular imports.
    """
    set_theme(
        context="notebook", style="whitegrid", palette="bright", font="sans-serif"
    )
    color_palette("deep")
    style.use(style=MPLSTYLE)


init()


def get_nb(exp: Path, name: str) -> Path:
    return (exp / name).with_suffix(".ipynb")


boilercv_dir = Path("src") / PACKAGE
STAGES: list[ParameterSet] = []
for module in walk_modules(boilercv_dir):
    if module.startswith("boilercv.manual"):
        stage = get_module_rel(module, "manual")
        match stage.split("."):
            case ("generate_experiment_docs", *_):
                marks = [pytest.mark.skip(reason="Local-only documentation.")]
            case ("update_experiments_from_docs", *_):
                marks = [pytest.mark.skip(reason="Local-only documentation.")]
            case _:
                marks = []
        STAGES.append(
            pytest.param(module, id=get_module_rel(module, PACKAGE), marks=marks)
        )
        continue
    if not module.startswith("boilercv.stages"):
        continue
    stage = get_module_rel(module, "stages")
    match stage.split("."):
        case ("experiments", "e230920_subcool", *_):
            marks = [pytest.mark.skip(reason="Test data missing.")]
        case ("generate_reports", *_):
            marks = [pytest.mark.skip(reason="Local-only documentation.")]
        case ("compare_theory" | "find_tracks" | "find_unobstructed", *_):
            marks = [pytest.mark.skip(reason="Implementation trivially does nothing.")]
        case _:
            marks = []
    STAGES.append(pytest.param(module, id=get_module_rel(module, PACKAGE), marks=marks))


@dataclass
class Case:
    """Notebook test case.

    Args:
        path: Path to the notebook.
        suffix: Test ID suffix.
        params: Parameters to pass to the notebook.
        results: Variable names to retrieve and optional expectations on their values.
    """

    path: Path
    """Path to the notebook."""
    id: str = "_"
    """Test ID suffix."""
    params: dict[str, Any] = field(default_factory=dict)
    """Parameters to pass to the notebook."""
    results: dict[str, Any] = field(default_factory=dict)
    """Variable names to retrieve and optional expectations on their values."""
    marks: Sequence[pytest.Mark] = field(default_factory=list)
    """Pytest marks."""

    @property
    def nb(self) -> str:
        """Notebook contents."""
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""

    @contextmanager
    def clean_nb(self) -> Iterator[str]:
        """Cleaned notebook contents."""
        temp_nb = (TEST_TEMP_NBS / next(NAMER)).with_suffix(".ipynb")
        copy(self.path, temp_nb)
        clean_notebooks(temp_nb)
        yield temp_nb.read_text(encoding="utf-8")
        temp_nb.unlink()

    def get_ns(self) -> SimpleNamespace:
        """Get notebook namespace for this check."""
        return get_nb_ns(nb=self.nb, params=self.params, attributes=self.results)


def normalize_cases(*cases: Case) -> Iterable[Case]:
    """Normalize cases to minimize number of caches.

    Assign the same results to cases with the same path and parameters, preserving
    expectations. Sort parameters and results.

    Args:
        *cases: Cases to normalize.

    Returns:
        Normalized cases.
    """
    seen: dict[Path, dict[str, Any]] = {}
    all_cases: list[list[Case]] = []
    # Find cases with the same path and parameters and sort parameters
    for c in cases:
        for i, (path, params) in enumerate(seen.items()):
            if c.path == path and c.params == params:
                all_cases[i].append(c)
                break
        else:
            # If the loop doesn't break, no match was found
            seen[c.path] = c.params
            all_cases.append([c])
        c.params = dict(sorted(c.params.items()))
    # Assign the same results to common casees and sort results
    for cs in all_cases:
        all_results: set[str] = set()
        all_results.update(chain.from_iterable(c.results.keys() for c in cs))
        for c in cs:
            c.results |= {r: None for r in all_results if r not in c.results}
            c.results = dict(sorted(c.results.items()))
    return cases


def parametrize_by_cases(*cases: Case):
    """Parametrize this test by cases."""
    return pytest.mark.parametrize(
        "ns", [pytest.param(c, marks=c.marks, id=c.id) for c in cases], indirect=["ns"]
    )


EMPTY_DICT = {}
"""Empty dictionary."""
EMPTY_LIST = []
"""Empty list."""


@dataclass
class Caser:
    exp: Path
    cases: list[Case] = field(default_factory=list)

    def __call__(
        self,
        name: str,
        id: str = "_",  # noqa: A002
        params: dict[str, Any] = EMPTY_DICT,
        results: dict[str, Any] | Iterable[Any] = EMPTY_DICT,
        marks: Sequence[pytest.Mark] = EMPTY_LIST,
    ) -> Case:
        case = Case(
            get_nb(self.exp, name),
            id,
            params,
            results if isinstance(results, dict) else dict.fromkeys(results),
            marks,
        )
        self.cases.append(case)
        return case
