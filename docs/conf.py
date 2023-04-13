from datetime import date

from myst_parser import __version__

project = ""
html_title = "Contents"
copyright = f"{date.today().year}, Blake Naccarato, Kwang Jin Kim"  # noqa: A001
version = __version__
master_doc = "index"
language = "en"
extensions = ["myst_parser", "sphinx_design"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_book_theme"
