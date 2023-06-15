from os import chdir
from pathlib import Path
from shutil import copytree, rmtree
from tempfile import mkdtemp


def patch() -> Path | None:
    """Patch the project if we're running notebooks in the documentation directory."""

    if Path().resolve().name != "docs":
        return

    chdir("..")
    tmp_project = Path(mkdtemp(prefix="boilercv-docs"))

    import boilercv

    boilercv.PARAMS_FILE = tmp_project / "params.yaml"
    boilercv.DATA_DIR = tmp_project / "cloud"
    boilercv.LOCAL_DATA = tmp_project / "local"

    from boilercv.models import params
    from boilercv.models.params import PARAMS

    params.SOURCES_TO_ENUMERATE = PARAMS.local_paths.cines
    test_data = Path("tests/data")
    copytree(test_data / "local", PARAMS.local_paths.data, dirs_exist_ok=True)
    copytree(test_data / "cloud", PARAMS.paths.data, dirs_exist_ok=True)

    return tmp_project


def unpatch(tmp_project: Path | None):
    """Remove the temporary project directory."""
    if tmp_project:
        rmtree(tmp_project)
