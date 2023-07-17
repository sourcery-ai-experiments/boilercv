"""Test pipeline stages."""

import importlib
from pathlib import Path

import pytest


@pytest.mark.slow()
@pytest.mark.usefixtures("tmp_project")
@pytest.mark.parametrize(
    "stage",
    [stage.stem for stage in sorted(Path("src/boilercv/manual").glob("[!__]*.py"))],
)
def test_manual(stage: str):
    """Test that manual stages can run."""
    importlib.import_module(f"boilercv.manual.{stage}").main()


STAGES = sorted(Path("src/boilercv/stages").glob("[!__]*.py"))


@pytest.mark.slow()
@pytest.mark.usefixtures("tmp_project")
@pytest.mark.parametrize(
    ("stage", "x"),
    (
        {stage.stem: "" for stage in STAGES}
        | {
            stage.stem: "xfail"
            for stage in STAGES
            if stage.stem in {"build_docs": "Can't run DVC in CI."}
        }
    ).items(),
)
def test_stages(stage: str, x: str):
    """Test that stages can run."""
    if x == "xfail":
        pytest.xfail("Stage or test not yet implemented.")
    importlib.import_module(f"boilercv.stages.{stage}").main()


@pytest.mark.slow()
@pytest.mark.usefixtures("tmp_project")
@pytest.mark.parametrize(
    "stage",
    [
        stage.stem
        for stage in sorted(Path("src/boilercv/stages/preview").glob("[!__]*.py"))
    ],
)
def test_preview(stage: str):
    """Test that preview update stages can run."""
    importlib.import_module(f"boilercv.stages.preview.{stage}").main()


@pytest.mark.slow()
@pytest.mark.usefixtures("tmp_project")
@pytest.mark.parametrize(
    "stage",
    [stage.stem for stage in sorted(Path("src/boilercv/previews").glob("[!__]*.py"))],
)
def test_previews(stage: str):
    """Test that manual stages can run."""
    importlib.import_module(f"boilercv.previews.{stage}").main()
