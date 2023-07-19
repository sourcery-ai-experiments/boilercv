"""Prepare to reproduce the pipeline with DVC."""

from contextlib import chdir
from pathlib import Path
from shlex import join, quote, split
from subprocess import run
from typing import TypedDict

from dvc.repo import Repo

from boilercv.models.params import PARAMS

MAGIC = False


def main():
    # Get modfied files
    repo = Repo()
    modified = get_dvc_modified(repo, granular=True)
    if PARAMS.paths.docs not in modified:
        return
    nbs = get_modified_nbs(modified)

    # Run stages that don't require changing the active directory
    for stage in [run_notebook, clean_notebook, export_notebook]:
        for nb in nbs:
            stage(nb)

    # Run the last stage, which requires changing the active directory
    with chdir(PARAMS.paths.md):
        for kwargs in nbs.values():
            generate_report_from_notebook(**kwargs)


def run_notebook(notebook: Path):
    """Run a notebook."""
    nb = notebook
    run_process(
        f".venv/scripts/jupyter nbconvert --execute --to notebook --inplace {nb}"
    )


def clean_notebook(notebook: Path):
    """Clean a notebook."""
    nb = notebook
    for command in [
        f"nbqa black {nb}",
        f"nbqa ruff --fix-only {nb}",
        (
            "nb-clean clean --remove-empty-cells --preserve-cell-outputs"
            " --preserve-cell-metadata tags special"
            f" -- {nb}"
        ),
    ]:
        run_process(f".venv/scripts/{command}")  # "


def export_notebook(notebook: Path):
    """Export a notebook to Markdown and HTML."""
    nb = notebook
    html = PARAMS.local_paths.html
    md = PARAMS.paths.md
    run_process(
        f".venv/scripts/jupyter nbconvert {nb} --to markdown --no-input --output-dir {md}"
    )
    run_process(
        f".venv/scripts/jupyter nbconvert {nb} --to html --no-input --output-dir {html}"
    )


def generate_report_from_notebook(template, zotero, csl, docx, md):
    """Generate a DOCX report from a notebook.

    Requires changing the active directory to the Markdown folder outside of this
    asynchronous function, due to how Pandoc generates links inside the documents.
    """
    run_process(
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
        f"  {md}",
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


def run_process(cmd: str, venv: bool = True):
    """Normalize a command and run a script from the virtual environment by default."""
    run(f"{'.venv/scripts/' if venv else ''}{join(split(cmd))}")  # noqa: S603


def fold(path: Path):
    """Resolve and normalize a path to a POSIX string path with forward slashes."""
    return quote(str(path.resolve()).replace("\\", "/"))


if __name__ == "__main__":
    main()
