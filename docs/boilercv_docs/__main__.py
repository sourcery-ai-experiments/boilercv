"""Insert `hide-input` tag to all documentation notebooks."""

from pathlib import Path
from textwrap import dedent

from nbformat import NO_CONVERT, NotebookNode, read, write

EXCLUDE_THEBE = [
    Path(p) for p in ["docs/experiments/e230920_subcool/find_tracks_trackpy.ipynb"]
]
SRC = "source"
CODE = "code"
MD = "markdown"


def main():
    for path in Path("docs").rglob("*.ipynb"):
        nb: NotebookNode = read(path, NO_CONVERT)  # type: ignore  # pyright 1.1.348,  # nbformat: 5.9.2
        if path not in EXCLUDE_THEBE:
            # Patch the first Markdown cell
            i, first_md_cell = get_first(nb, MD)
            nb.cells[i][SRC] = patch(
                first_md_cell.get(SRC, ""),
                """
                ::::
                :::{thebe-button}
                :::
                ::::
                """,
            )
        i, first_code_cell = get_first(nb, CODE)
        if path not in EXCLUDE_THEBE:
            # Insert Thebe tags to the first code cell
            nb.cells[i] = insert_tag(first_code_cell, ["thebe-init"])
        # Patch the first code cell
        nb.cells[i][SRC] = patch(
            first_code_cell.get(SRC, ""),
            """
            from boilercv_docs.nbs import init

            paths = init()
            """,
        )
        # Insert tags to all code cells
        for i, cell in enumerate(nb.cells):
            if cell.cell_type != "code":
                continue
            nb.cells[i] = insert_tag(cell, ["hide-input", "parameters"])
        # Write the notebook back
        write(nb, path)


def insert_tag(cell: NotebookNode, tags_to_insert: list[str]) -> NotebookNode:
    """Insert tags to a notebook cell.

    See: https://jupyterbook.org/en/stable/content/metadata.html?highlight=python#add-tags-using-python-code
    """
    tags = cell.get("metadata", {}).get("tags", [])
    cell["metadata"]["tags"] = tags_to_insert + list(set(tags) - set(tags_to_insert))
    return cell


def get_first(nb: NotebookNode, cell_type: str) -> tuple[int, NotebookNode]:
    """Get the first cell of a given type."""
    return next((i, c) for i, c in enumerate(nb.cells) if c.cell_type == cell_type)


def patch(src: str, content: str, end: str = "\n\n") -> str:
    """Prepend source lines to cell source if not there already."""
    content = dedent(content).strip()
    return src if src.startswith(content) else f"{content}{end}{src}"


main()
