"""Export correlation plots for tracks."""

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from boilercore.notebooks.namespaces import Params, get_nb_ns

from boilercv.experiments.e230920_subcool import EXP_TIMES, read_exp_nb

PLOTS = Path("tests/plots/tracks")
PLOTS.mkdir(exist_ok=True)


def main():
    with ProcessPoolExecutor() as executor:
        for dt in EXP_TIMES:
            executor.submit(export_track_plot, params={"TIME": dt.isoformat()})


def export_track_plot(params: Params):
    """Export object centers and sizes."""
    ns = get_nb_ns(nb=read_exp_nb("find_tracks"), params=params)
    ns.figure.savefig(PLOTS / f"{params['TIME'].replace(':', '-')}.png")


if __name__ == "__main__":
    main()
