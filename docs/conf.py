from datetime import date
from os import chdir
from pathlib import Path
from shutil import copytree, rmtree

if Path.cwd().name != "docs":
    chdir("docs")

DOCS_DATA = Path("../tests/root/data").resolve()

for dst in [
    (p / "data").resolve()
    for p in Path().rglob("")
    if p.is_dir() and p.name != "_static" and "data" not in p.parts
]:
    rmtree(dst, ignore_errors=True)
    copytree(src=DOCS_DATA, dst=dst)

project = ""
html_title = "boilercv"
copyright = f"{date.today().year}, Blake Naccarato, Kwang Jin Kim"  # noqa: A001
version = "0.0.1"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_favicon = "_static/favicon.ico"
html_theme = "sphinx_book_theme"
extensions = [
    "myst_nb",
    "sphinx_design",
    "sphinx_togglebutton",
    "sphinxcontrib.mermaid",
]
html_theme_options = {
    "path_to_docs": "docs",
    "repository_branch": "main",
    "repository_url": "https://github.com/blakeNaccarato/boilercv",
    "show_navbar_depth": 4,
    "show_toc_level": 4,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "use_repository_button": True,
}
bibtex_default_style = "unsrt"
bibtex_reference_style = "label"
html_context = {"default_mode": "light"}
mermaid_d3_zoom = False
myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 6
nb_execution_mode = "auto"
