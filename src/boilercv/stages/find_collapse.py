"""Update DVC paths (implicitly through import of PARAMS) and build docs."""

import asyncio
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from concurrent.futures import ProcessPoolExecutor
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from shlex import quote, split
from subprocess import CalledProcessError
from sys import stdout

from dulwich.porcelain import status, submodule_list
from dulwich.repo import Repo
from loguru import logger  # type: ignore  # pyright: 1.1.311
from ploomber_engine import execute_notebook  # type: ignore  # pyright: 1.1.311

from boilercv.models.params import PARAMS

# Pipeline parameters
NB = PARAMS.paths.stages["find_collapse"].with_suffix(".ipynb")
TIMES = ["2023-09-20T16:52:06"]
DATA = Path("data/docs/study_the_fit_of_bubble_collapse_correlations/prove_the_concept")

# Logging
VERBOSE_LOG = True
REPLAY = LOG_TO_FILE = False
logger.remove()
for sink in (["pre_repro.log"] if LOG_TO_FILE else []) + ([] if REPLAY else [stdout]):
    logger.add(
        sink=sink, enqueue=True, format=("<green>{time:mm:ss}</green> | {message}")
    )
logger = logger.opt(colors=not REPLAY)


async def main():
    if nb := nb_if_modified():
        await clean(nb)
    else:
        return
    if nb := nb_if_modified():
        await execute(nb, times=TIMES)
    else:
        return


# * -------------------------------------------------------------------------------- * #
# * Notebook processing


def nb_if_modified() -> str | None:
    """Get all notebooks or just the modified ones."""
    return fold(NB) if NB in (change.resolve() for change in get_changes()) else None


async def execute(nb: str, times: list[str]):
    """Execute notebooks."""
    logger.info("<yellow>START</yellow> EXECUTE")
    with ProcessPoolExecutor() as executor:
        for time in times:
            executor.submit(
                execute_notebook,
                input_path=nb,
                output_path=nb,
                progress_bar=VERBOSE_LOG,
                remove_tagged_cells=["ploomber-engine-error-cell"],
                parameters={"TIME": time},
            )
    logger.info("<green>FINISH</green> EXECUTE")
    logger.info("<yellow>START</yellow> REMOVE EXECUTION METADATA")
    await clean(nb)
    logger.info("<green>FINISH</green> REMOVE EXECUTION METADATA")


async def clean(nb: str):
    """Clean a notebook."""
    logger.info("<yellow>START</yellow> CLEAN")
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
    logger.info("<green>FINISH</green> CLEAN")


# * -------------------------------------------------------------------------------- * #
# * Utilities

COLORS = {"nb-clean clean": "blue", "ruff --fix-only": "magenta", "ruff format": "cyan"}


async def run_process(command: str, venv: bool = True):
    """Run a subprocess asynchronously."""
    command, *args = split(command, posix=False)

    # Log start
    file = args[-1].split("/")[-1]
    key = f"{command} {args[0]}"
    colored_command = f"<{COLORS[key]}>{command}</{COLORS[key]}>"
    logger.info(f"    <yellow>Start </yellow> {colored_command} {file}")

    # Run process
    process = await create_subprocess_exec(
        f"{'.venv/scripts/' if venv else ''}{command}", *args, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = (msg.decode("utf-8") for msg in await process.communicate())
    message = (
        (f"{stdout}\n{stderr}" if stdout and stderr else stdout or stderr)
        .replace("\r\n", "\n")
        .strip()
    )

    # Handle exceptions
    if process.returncode:
        exception = CalledProcessError(
            returncode=process.returncode, cmd=command, output=stdout, stderr=stderr
        )
        exception.add_note(message)
        exception.add_note("Arguments:\n" + "    \n".join(args))
        raise exception

    # Log finish
    logger.info(
        f"    <green>Finish</green> {colored_command} {file}"
        + ((": " + message.replace("\n", ". ")[:30] + "...") if message else "")
    )


def fold(path: Path) -> str:
    """Resolve and normalize a path to a POSIX string path with forward slashes."""
    return quote(str(path.resolve()).replace("\\", "/"))


# * -------------------------------------------------------------------------------- * #
# * Changes


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


# * -------------------------------------------------------------------------------- * #

if __name__ == "__main__":
    logger.info("<yellow>START</yellow> find_collapse")
    if not VERBOSE_LOG:
        logger.disable("__main__")
    asyncio.run(main())
    logger.enable("__main__")
    logger.info("<green>FINISH</green> find_collapse")
