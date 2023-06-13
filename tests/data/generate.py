"""Generate expected results."""

from pathlib import Path
from tempfile import TemporaryDirectory

import boilercv
from boilercv.stages import find_contours
from boilercv.stages.preview import preview_binarized, preview_filled


def main():
    """Generate expected results."""
    with TemporaryDirectory() as tmpdir:
        boilercv.PARAMS_FILE = Path(tmpdir) / "params.yaml"
        boilercv.DATA_DIR = Path("tests/data/cloud")
        boilercv.LOCAL_DATA = Path("tests/data/local")
        from boilercv.manual import binarize, convert
        from boilercv.stages import fill
        from boilercv.stages.preview import preview_gray

        for module in (
            binarize,
            preview_binarized,
            find_contours,
            convert,
            fill,
            preview_filled,
            preview_gray,
        ):
            module.main()


if __name__ == "__main__":
    main()
