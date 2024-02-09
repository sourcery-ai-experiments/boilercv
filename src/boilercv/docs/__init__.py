"""Documentation utilities."""

from os import chdir, environ
from pathlib import Path
from shutil import copy, copytree


def init_docs():
    """Ensure we're in the docs directory. Then, copy dependencies."""
    for key in [
        key
        for key in [
            "PIP_DISABLE_PIP_VERSION_CHECK",
            "PYTHONIOENCODING",
            "PYTHONSTARTUP",
            "PYTHONUTF8",
            "PYTHONWARNDEFAULTENCODING",
            "PYTHONWARNINGS",
        ]
        if environ.get(key) is not None
    ]:
        del environ[key]
    if Path.cwd().name != "docs":
        chdir("docs")
        if not Path("conf.py").exists():
            raise RuntimeError("Not in documentation directory.")
    deps = Path("../tests/root")
    copy(deps / "params.yaml", dst=Path.cwd())
    copytree(src=deps / "data", dst=Path.cwd() / "data", dirs_exist_ok=True)
    Path("params_schema.json").unlink(missing_ok=True)
