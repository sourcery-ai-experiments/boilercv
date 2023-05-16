"""Generate expected results."""

from pathlib import Path
from tempfile import TemporaryDirectory

from boilercv import models


def main():
    """Generate expected results."""
    with TemporaryDirectory() as tmpdir:
        models.PARAMS_FILE = Path(tmpdir) / "params.yaml"
        models.DATA_DIR = Path("tests/data/cloud")
        models.LOCAL_DATA = Path("tests/data/local")
        from boilercv.manual import binarize, convert, decompress
        from boilercv.stages import contours, fill, schema
        from boilercv.stages.update_previews import binarized, filled, gray

        for module in (
            schema,
            convert,
            decompress,
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
