"""Prepare to reproduce the pipeline with DVC."""

import asyncio
from asyncio import Task, TaskGroup, create_subprocess_exec, gather
from asyncio.subprocess import PIPE
from contextlib import chdir
from pathlib import Path
from shlex import quote, split
from subprocess import CalledProcessError
from typing import TypedDict

from dulwich.porcelain import add
from dvc.repo import Repo
from loguru import logger

from boilercv.models.params import PARAMS


async def main():
    # Get modfied files
    repo = Repo()
    modified = get_dvc_modified(repo, granular=True)
    if PARAMS.paths.docs not in modified:
        return
    nbs = get_modified_nbs(modified)
    tasks: list[Task[str]] = []

    # Run stages that don't require changing the active directory
    for stage in [run_notebook, clean_notebook, export_notebook]:
        async with TaskGroup() as tg:
            tasks.extend(tg.create_task(stage(nb)) for nb in nbs)

    # Run the last stage, which requires changing the active directory
    with chdir(PARAMS.paths.md):
        async with TaskGroup() as tg:
            tasks.extend(
                [
                    tg.create_task(generate_report_from_notebook(**kwargs))
                    for kwargs in nbs.values()
                ]
            )

    # Log the results
    prefix = "\n  "
    for res in await gather(*tasks):
        logger.info((prefix + res.replace("\n", prefix)) if "\n" in res else res)

    # Commit the changes
    # docs_dvc_file = PARAMS.paths.docs.with_suffix(".dvc")
    # repo.commit(str(docs_dvc_file), force=True)
    # add(paths=str(docs_dvc_file))


async def run_notebook(notebook: Path) -> str:
    """Run a notebook."""
    nb = fold(notebook)
    return await run_process(
        f"jupyter nbconvert --execute --to notebook --inplace {nb}"
    )


async def clean_notebook(notebook: Path) -> str:
    """Clean a notebook."""
    nb = fold(notebook)
    return "\n".join(
        [
            await run_process(command)
            for command in [
                f"nbqa black {nb}",
                f"nbqa ruff --fix-only {nb}",
                (
                    " nb-clean clean --remove-empty-cells --preserve-cell-outputs"
                    "   --preserve-cell-metadata tags special"
                    f"  -- {nb}"
                ),
            ]
        ]
    )


async def export_notebook(notebook: Path) -> str:
    """Export a notebook to Markdown and HTML."""
    nb = fold(notebook)
    html = fold(PARAMS.local_paths.html)
    md = fold(PARAMS.paths.md)
    return "\n".join(
        [
            await run_process(command)
            for command in [
                f"jupyter nbconvert {nb} --to markdown --no-input --output-dir {md}",
                f"jupyter nbconvert {nb} --to html --no-input --output-dir {html}",
            ]
        ]
    )


async def generate_report_from_notebook(template, zotero, csl, docx, md) -> str:
    """Generate a DOCX report from a notebook.

    Requires changing the active directory to the Markdown folder outside of this
    asynchronous function, due to how Pandoc generates links inside the documents.
    """
    return await run_process(
        venv=False,
        command=(
            " pandoc"
            # Pandoc configuration
            "   --standalone"  # Don't produce a document fragment.
            "   --from markdown-auto_identifiers"  # Avoids bookmark pollution around Markdown headers
            "   --to docx"  # The output format
            f"  --reference-doc {template}"  # The template to export literature reviews to
            # Zotero Lua filter and metadata passed to it
            f"  --lua-filter {zotero}"  # Needs to be the one downloaded from the tutorial page https://retorque.re/zotero-better-bibtex/exporting/pandoc/#from-markdown-to-zotero-live-citations
            "   --metadata zotero_library:3"  # Corresponds to "Nucleate pool boiling [3]"
            f"  --metadata zotero_csl_style:{csl}"  # Must also be installed in Zotero
            # I/O
            f"  --output {docx}"
            f"  {md}"
        ),
    )


class ReportKwargs(TypedDict):
    """Keyword arguments for generating a report."""

    template: str
    zotero: str
    csl: str
    docx: str
    md: str


def get_modified_nbs(modified: list[Path]) -> dict[Path, ReportKwargs]:
    """Get the modified notebooks and their corresponding report paths."""
    return {
        nb: ReportKwargs(
            **{
                kwarg: fold(path)
                for kwarg, path in dict(
                    template=PARAMS.project_paths.template,
                    zotero=PARAMS.project_paths.zotero,
                    csl=PARAMS.project_paths.csl,
                    docx=PARAMS.paths.docx / nb.with_suffix(".docx").name,
                    md=PARAMS.paths.md / nb.with_suffix(".md").name,
                ).items()
            }
        )
        for nb in sorted(
            [
                path
                for path in modified
                if path.is_relative_to(PARAMS.paths.docs) and path.suffix == ".ipynb"
            ]
        )
    }


def get_dvc_modified(
    repo: Repo, granular: bool = False, committed: bool = False
) -> list[Path]:
    """Get a list of modified files tracked by DVC."""
    status = repo.data_status(granular=granular)
    modified: list[Path] = []
    for key in ["modified", "added"]:
        if paths := status["committed" if committed else "uncommitted"].get(key):
            modified.extend([Path(path) for path in paths])
    return modified


async def run_process(command: str, venv: bool = True) -> str:
    """Run a subprocess asynchronously."""
    command, *args = split(command, posix=False)
    process = await create_subprocess_exec(
        f"{'.venv/scripts/' if venv else ''}{command}", *args, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = (msg.decode("utf-8") for msg in await process.communicate())
    message = f"{stdout}\n{stderr}" if stdout and stderr else stdout or stderr
    if process.returncode:
        exception = CalledProcessError(
            returncode=process.returncode,
            cmd=command,
            output=stdout,
            stderr=stderr,
        )
        exception.add_note(message)
        exception.add_note("Arguments:\n" + "  \n".join(args))
        raise exception
    return message


def fold(path: Path):
    """Resolve and normalize a path to a POSIX string path with forward slashes."""
    return quote(str(path.resolve()).replace("\\", "/"))


if __name__ == "__main__":
    asyncio.run(main())
