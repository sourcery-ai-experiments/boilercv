"""Test configuration."""

from pathlib import Path
from shutil import copytree
from sys import path

import pytest

from tests import NOTEBOOK_STAGES, get_nb_content

TEST_DATA = Path("tests/data")


@pytest.fixture()
def tmp_project(monkeypatch, tmp_path: Path) -> Path:
    """Produce a temporary project directory."""

    import boilercv

    monkeypatch.setattr(boilercv, "PARAMS_FILE", tmp_path / "params.yaml")
    monkeypatch.setattr(boilercv, "DATA_DIR", tmp_path / "cloud")
    monkeypatch.setattr(boilercv, "LOCAL_DATA", tmp_path / "local")

    from boilercv.models import params
    from boilercv.models.params import PARAMS

    monkeypatch.setattr(params, "SOURCES_TO_ENUMERATE", PARAMS.local_paths.cines)
    copytree(TEST_DATA / "local", PARAMS.local_paths.data, dirs_exist_ok=True)
    copytree(TEST_DATA / "cloud", PARAMS.paths.data, dirs_exist_ok=True)

    return tmp_path


@pytest.fixture()
def _tmp_project_with_nb_stages(tmp_project: Path):
    """Enable importing of notebook stages like `importlib.import_module("stage")`."""
    path.insert(0, str(tmp_project))  # For importing tmp_project stages in tests
    for nb in NOTEBOOK_STAGES:
        (tmp_project / nb.with_suffix(".py").name).write_text(
            encoding="utf-8", data=get_nb_content(nb)
        )
