"""Update script to run after tool dependencies are installed, but before others."""

import json
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from platform import platform
from shlex import split
from subprocess import run
from sys import executable, version_info

import tomlkit
from cyclopts import App
from dulwich.porcelain import submodule_list
from dulwich.repo import Repo
from packaging.requirements import Requirement
from tomlkit.items import Array

app = App()

PYPROJECT = Path("pyproject.toml").as_posix()


@app.command()
def sync():
    *_, submodule_deps = get_submodules()
    original_content = content = Path(PYPROJECT).read_text("utf-8")
    pyproject = tomlkit.loads(content)
    deps: Array = pyproject["project"]["optional-dependencies"]["dev"]  # pyright: ignore[reportAssignmentType, reportIndexIssue]  # pyright==1.1.350, packaging==24.0
    sync_paired_dependency(deps, "pandas", "pandas-stubs")
    for dep in submodule_deps:
        sync_submodule_dependency(deps, dep)
    content = tomlkit.dumps(pyproject)
    if content != original_content:
        Path(PYPROJECT).write_text(encoding="utf-8", data=content)


PLATFORM = platform(terse=True).casefold().split("-")[0]

print(f"welp {PLATFORM}")  # noqa: T201

match PLATFORM:
    case "macos":
        RUNNER = "macos-12"
    case "windows":
        RUNNER = "windows-2022"
    case "linux":
        RUNNER = "ubuntu-22.04"
    case _:
        raise ValueError(f"Unsupported platform: {PLATFORM}")

match version_info[:2]:
    case (3, 8):
        PYTHON_VERSION = "3.8"
    case (3, 9):
        PYTHON_VERSION = "3.9"
    case (3, 10):
        PYTHON_VERSION = "3.10"
    case (3, 11):
        PYTHON_VERSION = "3.11"
    case (3, 12):
        PYTHON_VERSION = "3.12"
    case (3, 13):
        PYTHON_VERSION = "3.13"
    case _:
        PYTHON_VERSION = "3.11"

NODEPS = Path(".tools/requirements/nodeps.in").as_posix()
DEV = Path(".tools/requirements/dev.in").as_posix()
LOCK = Path(".lock") / RUNNER
"""Path to the lock directory."""
LOCK.mkdir(exist_ok=True, parents=True)


@app.command()
def lock(highest: bool = False):
    """Lock the requirements for the given environment.

    Args:
        highest: Whether to lock the highest dependencies.
    """
    lock_result = run(
        args=split(
            " ".join([
                f"{Path(executable).as_posix()} -m uv",
                f"pip compile --python-version {PYTHON_VERSION}",
                f"--resolution {'highest' if highest else 'lowest-direct'}",
                f"--exclude-newer {datetime.now(UTC).isoformat().replace('+00:00', 'Z')}",
                "--extra cv" if highest else "--all-extras",
                PYPROJECT,
                DEV,
            ])
        ),
        capture_output=True,
        check=False,
        text=True,
    )
    if lock_result.returncode:
        raise RuntimeError(lock_result.stderr)
    path = LOCK / Path(
        "_".join([
            "requirements",
            RUNNER,
            PYTHON_VERSION.replace(".", ""),
            *([] if highest else ["dev"]),
        ])
    ).with_suffix(".txt")
    print("welp2", path.as_posix())  # noqa: T201
    path.write_text(
        encoding="utf-8",
        data="\n".join([
            r.strip()
            for r in [lock_result.stdout, Path(NODEPS).read_text(encoding="utf-8")]
        ])
        + "\n",
    )


LOCKFILE = Path(".tools/lock.json")


@app.command()
def combine_locks():
    LOCKFILE.write_text(
        encoding="utf-8",
        data=json.dumps({
            lock.stem: lock.read_text(encoding="utf-8") for lock in LOCK.iterdir()
        })
        + "\n",
    )


@app.command()
def get_lock():
    name = "_".join(["requirements", RUNNER, PYTHON_VERSION.replace(".", ""), "dev"])
    (LOCK / RUNNER / Path(name).with_suffix(".txt")).write_text(
        encoding="utf-8", data=json.loads(LOCKFILE.read_text("utf-8"))[name]
    )


@dataclass
class Submodule:
    """Represents a git submodule."""

    _path: str | bytes
    """Submodule path as reported by the submodule source."""
    commit: str
    """Commit hash currently tracked by the submodule."""
    path: Path = Path()
    """Submodule path."""
    name: str = ""
    """Submodule name."""

    def __post_init__(self):
        """Handle byte strings reported by some submodule sources, like dulwich."""
        # dulwich.porcelain.submodule_list returns bytes
        self.path = Path(
            self._path.decode("utf-8") if isinstance(self._path, bytes) else self._path
        )
        self.name = self.path.name


def get_submodules() -> tuple[Submodule, Submodule, list[Submodule]]:
    """Get the special template and typings submodules, as well as the rest."""
    with closing(repo := Repo(str(Path.cwd()))):
        all_submodules = [Submodule(*item) for item in list(submodule_list(repo))]
    submodules: list[Submodule] = []
    template = typings = None
    for submodule in all_submodules:
        if submodule.name == "template":
            template = submodule
        elif submodule.name == "typings":
            typings = submodule
        else:
            submodules.append(submodule)
    if not template or not typings:
        raise ValueError("Could not find one of the template or typings submodules.")
    return template, typings, submodules


def sync_paired_dependency(deps: Array, src_name: str, dst_name: str):
    """Synchronize paired dependencies.

    Synchronize the `dst` dependency version from the `src` dependency version. This
    allows for certain complicated dependency relationships to be maintained, such as
    the one between `pandas` and `pandas-stubs`, in which `pandas-stubs` first three
    version numbers should match those of releases of `pandas`.
    """
    reqs = [Requirement(r) for r in deps]
    src_req = next(r for r in reqs if r.name == src_name)
    specs = src_req.specifier
    if len(specs) != 1:
        raise ValueError(f"Expected exactly one specifier in {src_req}.")
    src_ver = next(iter(specs)).version
    for i, dst_req in enumerate(reqs):
        if dst_req.name != dst_name:
            continue
        specs = dst_req.specifier
        if len(specs) != 1:
            raise ValueError(f"Expected exactly one specifier in {dst_req}.")
        dst_spec = next(iter(specs))
        deps[i] = str(Requirement(f"{dst_req.name}{dst_spec.operator}{src_ver}"))


def sync_submodule_dependency(deps: Array, sub: Submodule):
    """Synchronize commit-pinned dependencies to their respective submodule commit."""
    for i, req in enumerate(Requirement(r) for r in deps):
        if req.name != sub.name or not req.url:
            continue
        req.url = "@".join([req.url.split("@")[0], sub.commit])
        deps[i] = str(req).replace("@ git", " @ git")


if __name__ == "__main__":
    app()
