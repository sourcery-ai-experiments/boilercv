"""Helper functions for tests."""

from pathlib import Path
from typing import NamedTuple

import pytest
from _pytest.mark.structures import ParameterSet
from boilercore.paths import get_module_rel, walk_modules
from boilercore.testing import NO_PARAMS, Params


def get_nb(exp: Path, name: str) -> Path:
    return exp / f"{name}.ipynb"


class NsArgs(NamedTuple):
    """Indirect parameters for notebook namespace fixture."""

    nb: Path
    params: Params = NO_PARAMS


boilercv_dir = Path("src") / "boilercv"
STAGES: list[ParameterSet] = []
for module in walk_modules(boilercv_dir):
    if module.startswith("boilercv.manual"):
        STAGES.append(pytest.param(module, id=get_module_rel(module, "boilercv")))
        continue
    if not module.startswith("boilercv.stages"):
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
