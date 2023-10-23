"""Find collapsing bubbles."""

import asyncio
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from concurrent.futures import ProcessPoolExecutor
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from shlex import quote, split
from subprocess import CalledProcessError

from dulwich.porcelain import status, submodule_list
from dulwich.repo import Repo
from ploomber_engine import execute_notebook  # type: ignore  # pyright: 1.1.311

from boilercv.models.params import PARAMS

# Pipeline parameters
NB = quote(
    str(PARAMS.paths.stages["find_collapse"].with_suffix(".ipynb").resolve()).replace(
        "\\", "/"
    )
)
TIMES = [
    "2023-09-20T16:52:06",
    "2023-09-20T16:52:06",
    "2023-09-20T17:01:04",
    "2023-09-20T17:05:15",
    "2023-09-20T17:14:18",
    "2023-09-20T17:26:15",
    "2023-09-20T17:34:38",
    "2023-09-20T17:42:19",
    "2023-09-20T17:47:49",
]


async def main():
    if not modified(NB):
        return
    await clean(NB)
    if not modified(NB):
        return
    await execute(NB, times=TIMES)


def modified(nb: str) -> bool:
    """Get modified notebook."""
    return Path(nb) in (change.resolve() for change in get_changes())


async def clean(nb: str):
    """Clean a notebook."""
    commands = [
        f"ruff --fix-only {nb}",
        f"ruff format {nb}",
         "   nb-clean clean --remove-empty-cells"
         "     --preserve-cell-outputs"
         "     --preserve-cell-metadata special tags"
        f"    -- {nb}",
    ]  # fmt: skip
    for command in commands:
        await run_process(command)


async def execute(nb: str, times: list[str]):
    """Execute notebooks."""
    with ProcessPoolExecutor() as executor:
        for time in times:
            executor.submit(
                execute_notebook,
                input_path=nb,
                output_path=None,
                parameters={"TIME": time},
            )


async def run_process(command: str, venv: bool = True):
    """Run a subprocess asynchronously."""
    command, *args = split(command, posix=False)
    process = await create_subprocess_exec(
        f"{'.venv/scripts/' if venv else ''}{command}", *args, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = (msg.decode("utf-8") for msg in await process.communicate())
    message = (
        (f"{stdout}\n{stderr}" if stdout and stderr else stdout or stderr)
        .replace("\r\n", "\n")
        .strip()
    )
    if process.returncode:
        exception = CalledProcessError(
            returncode=process.returncode, cmd=command, output=stdout, stderr=stderr
        )
        exception.add_note(message)
        exception.add_note("Arguments:\n" + "    \n".join(args))
        raise exception


def get_changes() -> list[Path]:
    """Get pending changes."""
    staged, unstaged, _ = status(untracked_files="no")
    changes = {
        # Many dulwich functions return bytes for legacy reasons
        Path(path.decode("utf-8")) if isinstance(path, bytes) else path
        for change in (*staged.values(), unstaged)
        for path in change
    }
    # Exclude submodules from the changeset (submodules are considered always changed)
    return sorted(
        change
        for change in changes
        if change not in {submodule.path for submodule in get_submodules()}
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
        # Many dulwich functions return bytes for legacy reasons
        self.path = Path(
            self._path.decode("utf-8") if isinstance(self._path, bytes) else self._path
        )
        self.name = self.path.name


def get_submodules() -> list[Submodule]:
    """Get the special template and typings submodules, as well as the rest."""
    with closing(repo := Repo(str(Path.cwd()))):
        return [Submodule(*item) for item in list(submodule_list(repo))]


if __name__ == "__main__":
    asyncio.run(main())
