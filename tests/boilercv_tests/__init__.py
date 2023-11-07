"""Helper functions for tests."""

from pathlib import Path

import pytest
from _pytest.mark.structures import ParameterSet
from boilercore.paths import get_module_rel, walk_module_map, walk_modules

boilercv_dir = Path("src") / "boilercv"
NB_STAGES = {
    module: path
    for module, path in walk_module_map(boilercv_dir, suffixes=[".ipynb"])
    if module.startswith("boilercv.stages")
}
STAGES: list[ParameterSet] = []
for module in walk_modules(boilercv_dir):
    if not module.startswith("boilercv.stages"):
        continue
    if module.startswith("boilercv.manual"):
        STAGES.append(pytest.param(module, id=get_module_rel(module, "boilercv")))
        continue
    stage = get_module_rel(module, "stages")
    match stage.split("."):
        case ("experiments", "e230920_subcool", *_):
            marks = [pytest.mark.skip(reason="Test data missing.")]
        case ("generate_reports", *_):
            marks = [pytest.mark.skip]
        case ("compare_theory" | "find_tracks" | "find_unobstructed", *_):
            marks = [pytest.mark.skip(reason="Implementation trivially does nothing.")]
        case _:
            marks = []
    STAGES.append(
        pytest.param(module, id=get_module_rel(module, "boilercv"), marks=marks)
    )
