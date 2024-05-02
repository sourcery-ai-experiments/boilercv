"""Parameters"""

from boilercv_pipeline.equations import Param

args = (
    Param(arg=True, name="bubble_initial_reynolds", sym="Fo_0", test=100.0),
    Param(arg=True, name="bubble_jakob", sym="Ja", test=1.0),
    Param(
        arg=True,
        name="bubble_fourier",
        sym="Fo_0",
        test=dict(start=0.0, stop=5e-3, num=10),  # type: ignore
    ),
    Param(arg=True, name="liquid_prandtl", sym="Pr", test=1.0),
)
# beta = Param(name="beta")
# pi = Param(name="pi")
