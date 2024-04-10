"""Patch notebooks."""

from pathlib import Path
from textwrap import dedent

from nbformat import NO_CONVERT, NotebookNode, read, write

EXCLUDE_THEBE = [
    Path(p) for p in ["docs/experiments/e230920_subcool/find_tracks_trackpy.ipynb"]
]
SRC = "source"
CODE = "code"
MD = "markdown"


def main():  # noqa: D103
    patch_nbs()


def patch_nbs():
    """Patch notebooks.

    Patch Thebe buttons in. Insert `parameters` and `thebe-init` tags to the first code
    cell. Insert `hide-input` tags to code cells.
    """
    for path in Path("docs").rglob("*.ipynb"):
        nb: NotebookNode = read(path, NO_CONVERT)  # type: ignore  # pyright 1.1.348,  # nbformat: 5.9.2
        if path not in EXCLUDE_THEBE:
            # ? Patch the first Markdown cell
            i, first = next(
                (i, c) for i, c in enumerate(nb.cells) if c.cell_type == "markdown"
            )
            nb.cells[i][SRC] = patch(
                first.get(SRC, ""),
                """
                ::::
                :::{thebe-button}
                :::
                ::::
                """,
            )
        # ? Patch the first code cell
        code_cells = ((i, c) for i, c in enumerate(nb.cells) if c.cell_type == "code")
        i, first = next(code_cells)
        nb.cells[i][SRC] = patch(
            first.get(SRC, ""),
            """
            from boilercv_docs.nbs import init

            paths = init()
            """,
        )
        # ? Insert tags to first code cell
        nb.cells[i] = insert_tag(
            first,
            [
                "hide-input",
                "parameters",
                *([] if path in EXCLUDE_THEBE else ["thebe-init"]),
            ],
        )
        # ? Insert tags to remaining code cells
        for i, cell in code_cells:
            nb.cells[i] = insert_tag(cell, ["hide-input"])
        # ? Write the notebook back
        write(nb, path)


def insert_tag(cell: NotebookNode, tags_to_insert: list[str]) -> NotebookNode:
    """Insert tags to a notebook cell.

    See: https://jupyterbook.org/en/stable/content/metadata.html?highlight=python#add-tags-using-python-code
    """
    tags = cell.get("metadata", {}).get("tags", [])
    cell["metadata"]["tags"] = sorted(set(tags) | set(tags_to_insert))
    return cell


def patch(src: str, content: str, end: str = "\n\n") -> str:
    """Prepend source lines to cell source if not there already."""
    content = dedent(content).strip()
    return src if src.startswith(content) else f"{content}{end}{src}"


if __name__ == "__main__":
    main()
