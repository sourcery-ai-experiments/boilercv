"""Documentation setup."""

from glob import glob

import nbformat as nbf


def main():
    hide_input_cells()


def hide_input_cells():
    """Hide input cells in all example notebooks.

    See: https://jupyterbook.org/en/stable/content/metadata.html?highlight=python#add-tags-using-python-code
    """
    notebooks = glob("docs/examples/**.ipynb")
    tag = "hide-input"
    for notebook in notebooks:
        contents = nbf.read(notebook, nbf.NO_CONVERT)
        for cell in contents.cells:  # type: ignore
            cell_tags = cell.get("metadata", {}).get("tags", [])
            if tag not in cell_tags:
                cell_tags.append(tag)
            if len(cell_tags) > 0:
                cell["metadata"]["tags"] = cell_tags
        nbf.write(contents, notebook)


if __name__ == "__main__":
    main()
