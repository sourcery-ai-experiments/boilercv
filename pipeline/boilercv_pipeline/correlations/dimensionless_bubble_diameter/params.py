"""Parameters."""

from boilercv_pipeline.equations import Forms, LinspaceKwds, Param, Param2

args = (
    Param(arg=True, name="bubble_initial_reynolds", sym="Fo_0", test=100.0),
    Param(arg=True, name="bubble_jakob", sym="Ja", test=1.0),
    Param(
        arg=True,
        name="bubble_fourier",
        sym="Fo_0",
        test=dict(start=0.0, stop=5.0e-3, num=10),  # type: ignore
    ),
    Param(arg=True, name="liquid_prandtl", sym="Pr", test=1.0),
)

args2 = (
    Param2(
        arg=True,
        name="bubble_initial_reynolds",
        forms=Forms(latex=r"\Re_\bo", sympy="Re_b0"),
        test=100.0,
    ),
    Param2(
        arg=True, name="bubble_jakob", forms=Forms(latex=r"\Ja", sympy="Ja"), test=1.0
    ),
    Param2(
        arg=True,
        name="bubble_fourier",
        forms=Forms(latex=r"\Fo_\o", sympy="Fo_0"),
        test=LinspaceKwds(start=0.0, stop=5.0e-3, num=10),
    ),
    Param2(
        arg=True, name="liquid_prandtl", forms=Forms(latex=r"\Pr", sympy="Pr"), test=1.0
    ),
    Param2("beta"),
    Param2("pi"),
)
