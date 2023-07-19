"""Prepare to reproduce the pipeline with DVC."""

from contextlib import chdir
from pathlib import Path
from subprocess import run

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
        for md, docx in nbs.values():
            generate_report_from_notebook(md, docx)


def run_notebook(notebook: Path):
    """Run a notebook."""
    nb = notebook
    run(
        f".venv/scripts/jupyter nbconvert --execute --to notebook --inplace {nb}"  # noqa: S603
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
        run(f".venv/scripts/{command}")  # noqa: S603"


def export_notebook(notebook: Path):
    """Export a notebook to Markdown and HTML."""
    nb = notebook
    html = PARAMS.local_paths.html
    md = PARAMS.paths.md
    run(
        f".venv/scripts/jupyter nbconvert {nb} --to markdown --no-input --output-dir {md}"  # noqa: S603
    )
    run(
        f".venv/scripts/jupyter nbconvert {nb} --to html --no-input --output-dir {html}"  # noqa: S603
    )


def generate_report_from_notebook(md, docx):
    """Generate a DOCX report from a notebook.

    Requires changing the active directory to the Markdown folder outside of this
    asynchronous function, due to how Pandoc generates links inside the documents.
    """
    run(
        f"pandoc --standalone --from markdown-auto_identifiers --to docx --reference-doc scripts/template.dotx --lua-filter scripts/zotero.lua --metadata zotero_library:3 --metadata zotero_csl_style:scripts/international-journal-of-heat-and-mass-transfer.csl --output {docx} {md}"  # noqa: S603
    )


def get_modified_nbs(modified: list[Path]) -> dict[Path, tuple[str, str]]:
    """Get the modified notebooks and their corresponding report paths."""
    return {
        nb: (
            (PARAMS.paths.docx / nb.with_suffix(".docx").name).resolve(),
            (PARAMS.paths.md / nb.with_suffix(".md").name).resolve(),
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


if __name__ == "__main__":
    main()
