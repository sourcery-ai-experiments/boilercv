from subprocess import run


def test_repro():
    run(["dvc", "pull"])
    run(["dvc", "repro"])
