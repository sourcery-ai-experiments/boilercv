"""Test the pipeline."""

from pathlib import Path
from shutil import copytree
from types import ModuleType

import pytest

TEST_DATA = Path("tests/data")


@pytest.mark.slow()
def test_pipeline(monkeypatch, tmp_path):
    """Test the pipeline."""

    def main():
        for module in get_patched_modules():
            module.main()

    def get_patched_modules() -> tuple[ModuleType, ...]:
        """Test the pipeline by patching constants before importing stages."""

        import boilercv

        monkeypatch.setattr(boilercv, "PARAMS_FILE", tmp_path / "params.yaml")
        monkeypatch.setattr(boilercv, "DATA_DIR", tmp_path / "cloud")
        monkeypatch.setattr(boilercv, "LOCAL_DATA", tmp_path / "local")

        from boilercv.models import params
        from boilercv.models.params import PARAMS

        monkeypatch.setattr(params, "SOURCES_TO_ENUMERATE", PARAMS.local_paths.cines)
        copytree(TEST_DATA / "local", PARAMS.local_paths.data, dirs_exist_ok=True)
        copytree(TEST_DATA / "cloud", PARAMS.paths.data, dirs_exist_ok=True)

        from boilercv.manual import binarize, convert
        from boilercv.stages import contours, fill
        from boilercv.stages.update_previews import binarized, filled, gray

        return (binarize, binarized, contours, convert, fill, filled, gray)

    main()
