"""Helper functions for tests."""

from pathlib import Path

import pytest
from _pytest.mark.structures import ParameterSet
from boilercore.paths import get_module_rel, walk_module_paths, walk_modules

BOILERCV = Path("src") / "boilercv"
STAGES_DIR = BOILERCV / "stages"
STAGES = [
    pytest.param(module, id=get_module_rel(module, "boilercv"))
    for module in (f"boilercv.{module}" for module in walk_modules(BOILERCV / "manual"))
]
for module in (f"boilercv.{module}" for module in walk_modules(STAGES_DIR)):
    rel_to_stages = get_module_rel(module, "stages")
    if "experiments" in rel_to_stages or rel_to_stages in {
        "compare_theory",
        "generate_reports",
        "find_collapse",
        "find_tracks",
        "find_unobstructed",
    }:
        marks = [pytest.mark.skip]
    else:
        marks = []
    STAGES.append(
        pytest.param(module, id=get_module_rel(module, "boilercv"), marks=marks)
    )
nbs_to_execute: list[ParameterSet] = [
    pytest.param(path, id=str(path.relative_to(STAGES_DIR)), marks=[pytest.mark.xfail])
    for path in list(walk_module_paths(STAGES_DIR, suffixes=[".ipynb"]))
]
