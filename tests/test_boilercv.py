from subprocess import run


def test_repro():
    run(["dvc", "repro", "--pull"])
