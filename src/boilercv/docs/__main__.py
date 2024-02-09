"""Insert `hide-input` tag to all documentation notebooks."""

from pathlib import Path

from nbformat import NO_CONVERT, NotebookNode, read, write

from boilercv.docs.nbs import foo, insert_tags

for path in Path("docs").rglob("*.ipynb"):
    nb: NotebookNode = read(path, NO_CONVERT)  # type: ignore  # pyright 1.1.348,  # nbformat: 5.9.2
    nb = foo(nb)
    nb = insert_tags(nb, ["hide-input"])
    write(nb, path)
