"""Parameters."""

from numpy import linspace

from boilercv_pipeline.equations import Forms, Param

args = (
    Param(
        name="bubble_initial_reynolds",
        forms=Forms(latex=r"\Re_\bo", sympy="Re_b0"),
        test=100.0,
    ),
    Param(name="bubble_jakob", forms=Forms(latex=r"\Ja", sympy="Ja"), test=1.0),
    Param(
        name="bubble_fourier",
        forms=Forms(latex=r"\Fo_\o", sympy="Fo_0"),
        test=linspace(start=0.0, stop=5.0e-3, num=10),
    ),
    Param(name="liquid_prandtl", forms=Forms(latex=r"\Pr", sympy="Pr"), test=1.0),
)

params = tuple(Param(name=name) for name in ("beta", "pi"))
