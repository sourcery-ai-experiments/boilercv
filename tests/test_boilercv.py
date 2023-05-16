from pathlib import Path

from boilercv import models


def test_pipeline(monkeypatch, tmp_path):
    """Generate new expected results."""
    ...
    # monkeypatch.setattr(models, "PARAMS_FILE", tmp_path / "params.yaml")
    # monkeypatch.setattr(models, "DATA_DIR", Path("tests/data"))
    # monkeypatch.setattr(models, "LOCAL_MEDIA", tmp_path / "local_media")
    # monkeypatch.setattr(models, "LOCAL_DATA", tmp_path / "local_data")
    # from boilercv.stages import contours, fill, schema
    # from boilercv.stages.update_previews import binarized, filled, gray

    # for module in schema, contours, fill, binarized, gray, filled:
    #     module.main()
