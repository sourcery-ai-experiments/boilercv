from pathlib import Path
from shutil import copytree

import pandas as pd
import pytest
import xarray as xr

import boilercv


@pytest.mark.slow()
def test_pipeline(monkeypatch, tmp_path):
    """Test the pipeline."""

    monkeypatch.setattr(boilercv, "PARAMS_FILE", tmp_path / "params.yaml")
    monkeypatch.setattr(boilercv, "DATA_DIR", tmp_path / "cloud")
    monkeypatch.setattr(boilercv, "LOCAL_DATA", tmp_path / "local")

    from boilercv.models import params
    from boilercv.models.params import PARAMS

    monkeypatch.setattr(params, "SOURCES_TO_ENUMERATE", PARAMS.local_paths.cines)
    copytree(
        Path("tests/data/local/cines"), PARAMS.local_paths.cines, dirs_exist_ok=True
    )

    from boilercv.manual import binarize, convert
    from boilercv.stages import contours, fill, schema
    from boilercv.stages.update_previews import binarized, filled, gray

    for module, result in {
        schema: (PARAMS.paths.project_schema,),
        convert: (PARAMS.local_paths.large_sources,),
        binarize: (
            PARAMS.paths.sources,
            PARAMS.paths.rois,
        ),
        contours: (
            PARAMS.paths.contours,
            PARAMS.local_paths.uncompressed_sources,
            PARAMS.local_paths.uncompressed_contours,
        ),
        fill: (PARAMS.paths.filled,),
        binarized: (PARAMS.paths.binarized_preview,),
        filled: (PARAMS.local_paths.uncompressed_filled,),
        gray: (),
    }.items():
        module.main()
        skip_asserts = [
            f"boilercv.stages.{module_name}" for module_name in ("schema", "contours")
        ]
        if module.__name__ in skip_asserts:
            continue
        for path in result:
            expected = "tests/data" / path.relative_to(tmp_path)
            if expected.is_dir():
                results = path.iterdir()
                expectations = expected.iterdir()
            else:
                results = (path,)
                expectations = (expected,)
            for result_file, expected_file in zip(results, expectations, strict=True):
                if expected_file.suffix == ".nc":
                    assert xr.open_dataset(result_file).identical(
                        xr.open_dataset(expected_file)
                    )
                elif expected_file.suffix == ".h5":
                    assert pd.testing.assert_frame_equal(
                        pd.read_hdf(result_file), pd.read_hdf(expected_file)  # type: ignore
                    )
                else:
                    assert result_file.read_bytes() == expected_file.read_bytes()
