"""Helper functions for tests."""

from pathlib import Path

import pytest
from boilercore.paths import get_module_rel, walk_modules

BOILERCV = Path("src") / "boilercv"
STAGES = [
    pytest.param(module, id=get_module_rel(module, "boilercv"))
    for module in walk_modules(package=BOILERCV / "manual", top=BOILERCV)
]
for module in walk_modules(BOILERCV / "stages", BOILERCV):
    rel_to_stages = get_module_rel(module, "stages")
    if rel_to_stages in {"compare_theory", "find_tracks", "find_unobstructed"}:
        marks = [pytest.mark.xfail]
    else:
        marks = []
    STAGES.append(
        pytest.param(module, id=get_module_rel(module, "boilercv"), marks=marks)
    )
