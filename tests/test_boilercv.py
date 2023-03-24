from subprocess import run


def test_repro():
    """Test that the pipeline can be reproduced."""
    run(["dvc", "repro"])
