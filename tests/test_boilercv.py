from subprocess import run


def test_import():
    """Import test."""
    import boilercv  # noqa: F401


def test_repro_check_cv():
    """Run the basic OpenCV examples."""
    run(["pwsh", "-C", ".venv/Scripts/activate; dvc repro --pull --force check_cv"])
