"""Tests."""

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
        {stage.stem: "xpass" for stage in STAGES}
        | {
            stage.stem: "xfail"
            for stage in STAGES
            if stage.stem in ["correlations", "lifetimes", "tracks", "unobstructed"]
        }
    ).items(),
)
def test_stages(stage: str, x: str):
    """Test that stages can run."""
    if x == "xfail":
        pytest.xfail("Stage not yet implemented.")
    importlib.import_module(f"boilercv.stages.{stage}").main()


@pytest.mark.slow()
@pytest.mark.usefixtures("tmp_project")
@pytest.mark.parametrize(
    "stage",
    [
        stage.stem
        for stage in sorted(
            Path("src/boilercv/stages/update_previews").glob("[!__]*.py")
        )
    ],
)
def test_update_previews(stage: str):
    """Test that preview update stages can run."""
    importlib.import_module(f"boilercv.stages.update_previews.{stage}").main()


@pytest.mark.slow()
@pytest.mark.usefixtures("tmp_project")
@pytest.mark.parametrize(
    "stage",
    [stage.stem for stage in sorted(Path("src/boilercv/previews").glob("[!__]*.py"))],
)
def test_previews(stage: str):
    """Test that manual stages can run."""
    importlib.import_module(f"boilercv.previews.{stage}").main()
