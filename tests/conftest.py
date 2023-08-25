"""Test configuration."""

from pathlib import Path
from shutil import copytree

import pytest
from boilercore.testing import make_tmp_project_with_nb_stages

from tests import NOTEBOOK_STAGES, TEST_DATA


# Need autouse until all monkeypatching is eradicated from this fixture.
@pytest.fixture(autouse=True)
def _tmp_project(monkeypatch, tmp_path: Path):
    """Produce a temporary project directory."""
    copytree(TEST_DATA / "cloud", tmp_path / "data")

    # Won't need to chdir until test time after monkeypatching below is done away with.
    with monkeypatch.context() as m:
        m.chdir(tmp_path)
        import boilercv

    # Needed because of some configs outside of PACKAGE_DIR we depend on.
    # Consider moving truly necessary things into DATA_DIR, and eliminate others.
    monkeypatch.setattr(boilercv, "PROJECT_DIR", Path.cwd())

    # Won't need to monkeypatch LOCAL_DATA anymore once it's in the data directory.
    local_data = tmp_path / "local"
    copytree(TEST_DATA / "local", local_data)
    monkeypatch.setattr(boilercv, "LOCAL_DATA", local_data)


_tmp_project_with_nb_stages = pytest.fixture(
    make_tmp_project_with_nb_stages(NOTEBOOK_STAGES)
)
