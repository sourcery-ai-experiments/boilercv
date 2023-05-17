"""Generate expected results."""

from pathlib import Path
from tempfile import TemporaryDirectory

import boilercv


def main():
    """Generate expected results."""
    with TemporaryDirectory() as tmpdir:
        boilercv.PARAMS_FILE = Path(tmpdir) / "params.yaml"
        boilercv.DATA_DIR = Path("tests/data/cloud")
        boilercv.LOCAL_DATA = Path("tests/data/local")
        from boilercv.manual import binarize, convert
        from boilercv.stages import contours, fill, schema
        from boilercv.stages.update_previews import binarized, filled, gray

        for module in (
            schema,
            convert,
            binarize,
            contours,
            fill,
            binarized,
            filled,
            gray,
        ):
            module.main()


if __name__ == "__main__":
    main()
