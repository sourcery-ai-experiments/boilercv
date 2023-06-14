from datetime import date

project = ""
html_title = "boilercv"
copyright = f"{date.today().year}, Blake Naccarato, Kwang Jin Kim"  # noqa: A001
version = "0.0.1"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_book_theme"
extensions = [
    "sphinx_design",
    "myst_nb",
    "sphinxcontrib.bibtex",
    "sphinxcontrib.mermaid",
]
# https://sphinx-book-theme.readthedocs.io/en/stable/reference.html#reference-of-theme-options
html_context = {"default_mode": "light"}
html_theme_options = {
    "path_to_docs": "docs",
    "repository_url": "https://github.com/blakeNaccarato/boilercv",
    "repository_branch": "main",
    "use_download_button": True,
    "use_fullscreen_button": True,
    "use_repository_button": True,
}
bibtex_bibfiles = ["refs.bib"]
bibtex_reference_style = "label"
bibtex_default_style = "unsrt"
mermaid_d3_zoom = False
nb_execution_mode = "off"
nb_remove_code_source = True
