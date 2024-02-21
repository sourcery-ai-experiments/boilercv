"""Docs config."""

from datetime import date

from boilercv.docs import init_docs

init_docs()

# ! Basics
project = ""
copyright = f"{date.today().year}, Blake Naccarato, Kwang Jin Kim"  # noqa: A001
version = "0.0.1"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
extensions = [
    "autodoc2",
    "myst_nb",
    "sphinx_design",
    "sphinx_tippy",
    "sphinx_togglebutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinxcontrib.bibtex",
    "sphinxcontrib.mermaid",
]
# ! Theme
html_title = "boilercv"
html_favicon = "_static/favicon.ico"
html_logo = "_static/favicon.ico"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme = "sphinx_book_theme"
html_theme_options = {
    "path_to_docs": "docs",
    "repository_branch": "main",
    "repository_url": "https://github.com/blakeNaccarato/boilercv",
    "show_navbar_depth": 2,
    "show_toc_level": 4,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "use_repository_button": True,
}
# ! MyST
myst_enable_extensions = ["colon_fence", "dollarmath", "attrs_block", "linkify"]
myst_heading_anchors = 6
# ! Autodoc, intersphinx, tippy
# ? Autodoc
nitpicky = True
autodoc2_packages = ["../src/boilercv"]
autodoc2_render_plugin = "myst"
python_use_unqualified_type_names = True
# ? Tippy
# * Won't do anything until math is fixed
# * https://github.com/sphinx-extensions2/sphinx-tippy/pull/14
tippy_enable_mathjax = True
# * https://sphinx-tippy.readthedocs.io/en/latest/index.html#confval-tippy_anchor_parent_selector
tippy_anchor_parent_selector = "article.bd-article"
# * Mermaid tips don't work
tippy_skip_anchor_classes = ["mermaid"]
# * https://github.com/sphinx-extensions2/sphinx-tippy/issues/6#issuecomment-1627820276
tippy_tip_selector = """\
        aside,
        div.admonition,
        div.literal-block-wrapper,
        figure,
        img,
        div.math,
        p,
        table
        """
# ? All

tippy_rtd_urls = [
    "https://docs.opencv.org/2.4",
    "https://nbformat.readthedocs.io/en/stable",
    "https://numpy.org/doc/stable",
    "https://pyqtgraph.readthedocs.io/en/latest",
]
intersphinx_mapping = {
    "cv2": ("https://docs.opencv.org/2.4", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "nbformat": ("https://nbformat.readthedocs.io/en/stable", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "pyqtgraph": ("https://pyqtgraph.readthedocs.io/en/latest", None),
    "python": ("https://docs.python.org/3", None),
}
nitpick_ignore = [
    ("py:class", "cv2.LineSegmentDetector"),
    ("py:class", "boilercv.correlations.T"),
    ("py:class", "boilercv.data.sets.Stage"),
    ("py:class", "boilercv.experiments.e230920_subcool.NbProcess"),
]
nitpick_ignore_regex = [
    # ? Type aliases
    ("py:.*", r"boilercv\.types\..*"),
    ("py:.*", r"boilercv\.captivate\.previews\..*"),
    # ? Ignore until I'm using autodoc there, too
    ("py:.*", r"boilercore\..*"),
    # ? Typing portion not found
    ("py:.*", r"numpy\.typing\..*"),
    # ? Until we're done with Pydantic v1
    ("py:.*", r"pydantic\.v1\..*"),
    # ? https://bugreports.qt.io/browse/PYSIDE-2215
    ("py:.*", r"PySide6\..*"),
]
# ! BibTeX
bibtex_bibfiles = ["refs.bib"]
bibtex_reference_style = "label"
bibtex_default_style = "unsrt"
# ! NB
nb_execution_mode = "cache"
nb_execution_raise_on_error = True
# ! Other
mermaid_d3_zoom = False
