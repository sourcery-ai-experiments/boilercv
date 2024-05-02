"""Generate expected results for the response of each correlation to `KWDS`."""

# TODO: Fix generation for new layout
# sourcery skip: dont-import-test-modules

from decimal import Decimal
from inspect import Signature
from pathlib import Path
from textwrap import dedent

from boilercv_pipeline.correlations import EXPECTED, KWDS

from boilercv import dimensionless_params

TMP = Path("tests") / "plots"
CORRELATIONS = TMP / "applied_correlations.py"


def main():  # noqa: D103
    TMP.mkdir(parents=True, exist_ok=True)
    CORRELATIONS.unlink(missing_ok=True)
    correlations: dict[str, str] = {
        name: getattr(dimensionless_params, name)(**{
            kwd: value
            for kwd, value in KWDS.items()
            if kwd
            in Signature.from_callable(getattr(dimensionless_params, name)).parameters
        })
        for name in EXPECTED
    }
    CORRELATIONS.write_text(
        encoding="utf-8",
        data=dedent("""
        from boilercv_pipeline.correlations import (
            dimensionless_bubble_diameter_akiyama_1973,
            dimensionless_bubble_diameter_al_issa_et_al_2014,
            dimensionless_bubble_diameter_chen_mayinger_1992,
            dimensionless_bubble_diameter_florschuetz_chao_1965,
            dimensionless_bubble_diameter_inaba_et_al_2013,
            dimensionless_bubble_diameter_isenberg_sideman_1970,
            dimensionless_bubble_diameter_kalman_mori_2002,
            dimensionless_bubble_diameter_kim_park_2011,
            dimensionless_bubble_diameter_lucic_mayinger_2010,
            dimensionless_bubble_diameter_tang_et_al_2016,
            dimensionless_bubble_diameter_yuan_et_al_2009,
        )

        EXPECTED = {
        """)
        + ",\n".join([
            corr
            + ": ["
            + ", ".join([str(Decimal(r).quantize(Decimal(10) ** -6)) for r in result])
            + "]"
            for corr, result in correlations.items()
        ])
        + "}\n",
    )


if __name__ == "__main__":
    main()
