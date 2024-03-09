"""Update script to run after core dependencies are installed, but before others."""

from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from re import MULTILINE, VERBOSE, Pattern, compile, sub
from shlex import split
from subprocess import run
from sys import executable
from typing import Literal, TypeAlias

from cyclopts import App
from dulwich.porcelain import submodule_list
from dulwich.repo import Repo

app = App()

UV = next(Path(executable).parent.glob("uv*"))
"""Path to the `uv` executable."""
LOCK = Path(".lock")
"""Path to the lock directory."""
CV_REGEX = r"^opencv(?:-contrib)?-python(?:-headless)?(.*)$"
"""Pattern to match the various OpenCV options."""
CV_REQS = Path(".tools/requirements/cv.in")
"""Path to the `cv` requirements file."""

# * -------------------------------------------------------------------------------- * #


@app.command()
def sync():
    *_, submodule_deps = get_submodules()
    requirements_files = [
        Path("pyproject.toml"),
        *sorted(Path(".tools/requirements").glob("*.in")),
    ]
    for file in requirements_files:
        original_content = content = file.read_text("utf-8")
        content = sync_paired_dependency(content, "pandas", "pandas-stubs")
        for dep in submodule_deps:
            content = sync_submodule_dependency(content, dep)
        if content != original_content:
            file.write_text(encoding="utf-8", data=content)


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


def sync_paired_dependency(content: str, src_name: str, dst_name: str) -> str:
    """Synchronize paired dependencies.

    Synchronize the `dst` dependency version from the `src` dependency version. This
    allows for certain complicated dependency relationships to be maintained, such as
    the one between `pandas` and `pandas-stubs`, in which `pandas-stubs` first three
    version numbers should match those of releases of `pandas`.
    """
    if match := dependency(src_name).search(content):
        return dependency(dst_name).sub(
            repl=rf"\g<pre>{dst_name}\g<detail>{match['version']}\g<post>",
            string=content,
        )
    else:
        return content


def dependency(name: str) -> Pattern[str]:
    """Pattern for a dependency in 'requirements.txt' or 'pyproject.toml'."""
    return compile_dependency(
        rf"""
        {name}               # The dependency name
        (?P<detail>          # e.g. `~=` or `[hdf5,performance]~=`
            (\[[^\]]*\])?       # e.g. [hdf5,performance] (optional)
            [=~><]=             # ==, ~=, >=, <=
        )
        (?P<version>[^\n]+)  # e.g. 2.0.2
        """
    )


def sync_submodule_dependency(content: str, sub: Submodule) -> str:
    """Synchronize commit-pinned dependencies to their respective submodule commit."""
    return commit_dependency(sub.name, "https://github.com").sub(
        repl=rf"\g<before_commit>{sub.commit}\g<post>", string=content
    )


def commit_dependency(name: str, url: str) -> Pattern[str]:
    """Pattern for a commit-pinned dep in 'requirements.txt' or 'pyproject.toml'."""
    return compile_dependency(
        rf"""
        (?P<before_commit>      # Everything up to the commit hash
            {name}\s@\sgit\+{url}/      # e.g. name@git+https://github.com/
            (?P<org>[^/]+/)         # org/
            {name}@                 # name@
        )
        (?P<commit>[^\n]+)      # <commit-hash>
        """
    )


def compile_dependency(pattern: str) -> Pattern[str]:
    """Compile a regex pattern for dependencies in verbose, multiline mode.

    Supports specifications in both `pyproject.toml` and `requirements.txt`.
    """
    return compile(
        pattern=(
            rf"""
            ^                   # Start of line
            (?P<pre>\s*['"])?   # `"` if in pyproject.toml
            {pattern}
            (?P<post>\s*['"])?  # `",` if in pyproject.toml
            $                   # End of line
            """
        ),
        flags=VERBOSE | MULTILINE,
    )


# * -------------------------------------------------------------------------------- * #
# * Locks

System: TypeAlias = Literal["mac", "unix", "windows"]
PythonSystem: TypeAlias = Literal["macos", "linux", "windows"]
PythonVersion: TypeAlias = Literal["3.11", "3.12"]
ResolutionStrategy: TypeAlias = Literal["lower", "upper", "latest"]
CvFlavor: TypeAlias = Literal[
    "opencv-python",
    "opencv-contrib-python",
    "opencv-python-headless",
    "opencv-contrib-python-headless",
]


@dataclass
class Environment:
    """An environment.

    Args:
        system: Operating system.
        python_version: Python version.
        resolution_strategy: Resolution strategy.
        cv_contrib: Use `python_opencv_contrib`.
        cv_headless: Use `python_opencv_headless`.
    """

    system: System
    """Operating system."""
    python_version: PythonVersion
    """Python version."""
    resolution_strategy: ResolutionStrategy
    """Resolution strategy."""
    cv_flavor: CvFlavor
    """Flavor of OpenCV."""
    requirements: list[Path]
    """Requirements files."""


GitHubActionsRunner: TypeAlias = Literal["macos-12", "ubuntu-22.04", "windows-2022"]

RUNNERS: dict[GitHubActionsRunner, System] = {
    "macos-12": "mac",
    "ubuntu-22.04": "unix",
    "windows-2022": "windows",
}


@app.command()
def lock(
    runner: GitHubActionsRunner, python_version: PythonVersion, cv_flavor: CvFlavor
):
    env = Environment(
        system=RUNNERS[runner],
        python_version=python_version,
        resolution_strategy="lower",
        cv_flavor=cv_flavor,
        requirements=[Path(f".tools/requirements/{p}.in") for p in ["core", "cv"]],
    )
    reqs = env.requirements
    override = CV_REQS.with_stem(f"{CV_REQS.stem}_override")
    override.write_text(
        encoding="utf-8",
        data="\n".join([
            sub(CV_REGEX, rf"{env.cv_flavor}\1", line)
            for line in CV_REQS.read_text("utf-8").splitlines()
        ]),
    )
    reqs[reqs.index(CV_REQS)] = override
    resolution = "lowest-direct" if env.resolution_strategy == "lower" else "highest"
    lock_result = run(
        args=split(
            " ".join([
                f"{UV.as_posix()} pip compile --python-version {env.python_version}",
                f"--resolution {resolution}",
                *[r.as_posix() for r in reqs],
                f"--exclude-newer {datetime.now(UTC).isoformat().replace('+00:00', 'Z')}",
            ])
        ),
        capture_output=True,
        check=False,
        text=True,
    )
    if lock_result.returncode:
        raise RuntimeError(lock_result.stderr)
    LOCK.mkdir(exist_ok=True, parents=True)
    (LOCK / f"requirements_{runner}_{python_version}_{cv_flavor}.txt").write_text(
        encoding="utf-8", data=lock_result.stdout
    )


def lock_(env: Environment) -> str:
    reqs = env.requirements
    if CV_REQS in reqs:
        override = CV_REQS.with_stem(f"{CV_REQS.stem}_override")
        override.write_text(
            encoding="utf-8",
            data="\n".join([
                sub(CV_REGEX, rf"{env.cv_flavor}\1", line)
                for line in CV_REQS.read_text("utf-8").splitlines()
            ]),
        )
        reqs[reqs.index(CV_REQS)] = override
    resolution = "lowest-direct" if env.resolution_strategy == "lower" else "highest"
    result = run(
        args=split(
            " ".join([
                f"{UV.as_posix()} pip compile --python-version {env.python_version}",
                f"--resolution {resolution}",
                *[r.as_posix() for r in reqs],
                f"--exclude-newer {datetime.now(UTC).isoformat().replace('+00:00', 'Z')}",
            ])
        ),
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout


# * -------------------------------------------------------------------------------- * #


@app.command()
def dev():
    dev_envs = [  # noqa: F841
        Environment(
            system=sys,
            python_version="3.11",
            resolution_strategy="lower",
            cv_flavor="opencv-contrib-python",
            requirements=[Path(".tools/requirements/cv.in")],
        )
        for sys in ("mac", "unix", "windows")
    ]


# * -------------------------------------------------------------------------------- * #

if __name__ == "__main__":
    app()
