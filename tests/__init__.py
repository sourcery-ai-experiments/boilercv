"""Helper functions for tests."""

from pathlib import Path
from typing import Any

import pytest
from boilercore.testing import get_module_rel, walk_modules

PARAMS = Path("params.yaml")
DATA = Path("data")
TEST_DATA = Path("tests") / DATA
BOILERCV = Path("src") / "boilercv"
NOTEBOOK_STAGES = list(BOILERCV.glob("[!__]*.ipynb"))
STAGES: list[Any] = list(walk_modules(package=BOILERCV / "manual", top=BOILERCV))

for module in walk_modules(BOILERCV / "stages", BOILERCV):
    rel_to_stages = get_module_rel(module, "stages")
    if rel_to_stages in {"compare_theory", "find_tracks", "find_unobstructed"}:
        marks = [pytest.mark.xfail]
    else:
        marks = []
    STAGES.append(pytest.param(module, marks=marks))
