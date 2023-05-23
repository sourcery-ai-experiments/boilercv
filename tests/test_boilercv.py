"""Test the pipeline."""

from dataclasses import InitVar, dataclass, field
from pathlib import Path
from shutil import copytree
from types import ModuleType

import pandas as pd
import pytest
import xarray as xr

TEST_DATA = Path("tests/data")


@pytest.mark.slow()
def test_pipeline(check, monkeypatch, tmp_path):
    """Test the pipeline."""

    def main():
        stage_result_paths = get_stages()
        for module, result_paths in stage_result_paths.items():
            stage = Stage(module, result_paths, tmp_path)
            for result, expected in stage.expectations.items():
                with check:
                    assert_stage_result(result, expected)

    def get_stages() -> dict[ModuleType, tuple[Path, ...]]:
        """Test the pipeline by patching constants before importing stages."""

        import boilercv

        monkeypatch.setattr(boilercv, "PARAMS_FILE", tmp_path / "params.yaml")
        monkeypatch.setattr(boilercv, "DATA_DIR", tmp_path / "cloud")
        monkeypatch.setattr(boilercv, "LOCAL_DATA", tmp_path / "local")

        from boilercv.models import params
        from boilercv.models.params import PARAMS

        monkeypatch.setattr(params, "SOURCES_TO_ENUMERATE", PARAMS.local_paths.cines)
        copytree(
            TEST_DATA / "local/cines", PARAMS.local_paths.cines, dirs_exist_ok=True
        )

        from boilercv.manual import binarize, convert
        from boilercv.stages import contours, fill
        from boilercv.stages.update_previews import binarized, filled, gray

        return {
            convert: (PARAMS.local_paths.large_sources,),
            binarize: (PARAMS.paths.sources, PARAMS.paths.rois),
            contours: (PARAMS.paths.contours,),
            fill: (PARAMS.paths.filled,),
            binarized: (PARAMS.paths.binarized_preview,),
            filled: (PARAMS.paths.filled_preview,),
            gray: (PARAMS.paths.gray_preview,),
        }

    main()


def assert_stage_result(result_file: Path, expected_file: Path):
    """Assert that the result of a stage is as expected.

    Args:
        result_file: The file produced by the stage.
        expected_file: The file that the stage should produce.

    Raises:
        AssertionError: If the result is not as expected.
    """
    if expected_file.suffix == ".nc":
        assert xr.open_dataset(result_file).identical(xr.open_dataset(expected_file))
    elif expected_file.suffix == ".h5":
        result_df = pd.read_hdf(result_file)
        expected_df = pd.read_hdf(expected_file)
        pd.testing.assert_index_equal(result_df.index, expected_df.index)
    else:
        assert result_file.read_bytes() == expected_file.read_bytes()


@dataclass
class Stage:
    """Results of running a pipeline stage.

    Args:
        module: The module corresponding to this pipeline stage.
        result_paths: The directories or a single file produced by the stage.
        tmp_path: The results directory.

    Attributes:
        name: The name of the pipeline stage.
        expectations: A mapping from resulting to expected files.
    """

    module: InitVar[ModuleType]
    result_paths: InitVar[tuple[Path, ...]]
    tmp_path: InitVar[Path]

    name: str = field(init=False)
    expectations: dict[Path, Path] = field(init=False)

    def __post_init__(
        self, module: ModuleType, result_paths: tuple[Path, ...], tmp_path: Path
    ):
        self.name = module.__name__.removeprefix(f"{module.__package__}.")
        module.main()
        results: list[Path] = []
        expectations: list[Path] = []
        for path in result_paths:
            expected = TEST_DATA / path.relative_to(tmp_path)
            if expected.is_dir():
                results.extend(sorted(path.iterdir()))
                expectations.extend(sorted(expected.iterdir()))
            else:
                results.append(path)
                expectations.append(expected)
        self.expectations = dict(zip(results, expectations, strict=True))
