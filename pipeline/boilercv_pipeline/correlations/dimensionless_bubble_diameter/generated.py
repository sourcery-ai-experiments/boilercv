"""Generated equations."""

from boilercv_pipeline.equations import Equation, Forms

# fmt: off
equations = {
    "florschuetz_chao_1965": Equation(
        name="florschuetz_chao_1965",
        forms=Forms(
            latex=r"\beta = 1 - 4 \Ja \sqrt{\Fo_\o / \pi}",
            sympy=r"Eq(beta, 1 - 4 * Ja * sqrt(Fo_0 / pi))",
            python=r"1 - 4 * bubble_jakob * sqrt(bubble_fourier / pi)",
        ),
        expect=[1.000000, 0.946807, 0.924774, 0.907868, 0.893615, 0.881058, 0.869705, 0.859266, 0.849549, 0.840423],
    ),
    "isenberg_sideman_1970": Equation(
        name="isenberg_sideman_1970",
        forms=Forms(
            latex=r"\beta = \left(1 - \left(\frac{3}{\sqrt{\pi}}\right) \Re_\bo^{1/2} \Pr^{1/3} \Ja \Fo_\o \right)^{2/3}",
            sympy=r"Eq(beta, (1 - \frac{3}{\sqrt{\pi}} \Re_b0^{1/2} \Pr^{1/3} \Ja \Fo_0)^{2/3})",
            python=r"(1 - \frac{3}{\sqrt{\pi}} * bubble_initial_reynolds^{1/2} * liquid_prandtl^{1/3} * bubble_jakob * bubble_fourier)^{2/3}",
        ),
        expect=[1.000000, 0.993721, 0.987422, 0.981104, 0.974765, 0.968405, 0.962024, 0.955622, 0.949199, 0.942753],
    ),
    "akiyama_1973": Equation(
        name="akiyama_1973",
        forms=Forms(
            latex=r"\beta = (1 - 1.036 \Re_\bo^{1/2} \Pr^{1/3} \Ja \Fo_\o)^{0.714}",
            sympy=r"Eq(beta, (1 - 1.036 \Re_b0^{1/2} \Pr^{1/3} \Ja \Fo_0)^{0.714})",
            python=r"(1 - 1.036 * bubble_fourier * bubble_initial_reynolds^{1/2} * bubble_jakob * liquid_prandtl^{1/3})^{0.714}",
        ),
        expect=[1.000000, 0.995887, 0.991767, 0.987640, 0.983507, 0.979367, 0.975219, 0.971065, 0.966903, 0.962734],
    ),
    "yuan_et_al_2009": Equation(
        name="yuan_et_al_2009",
        forms=Forms(
            latex=r"\beta = \left(1 - 1.8 \Re_\bo^{0.5} \Pr^{1/3} \Ja \Fo_\o \left(1 - 0.5 \Ja^{0.1} \Fo_\o\right)\right)^{2/3}",
            sympy=r"Eq(beta, (1 - 1.8 \Re_b0^{0.5} \Pr^{1/3} \Ja \Fo_0 (1 - 0.5 \Ja^{0.1} \Fo_0))^{2/3})",
            python=r"(1 - 1.8 * bubble_initial_reynolds^0.5 * liquid_prandtl^{1/3} * bubble_jakob * bubble_fourier * (1 - 0.5 * bubble_jakob^{0.1} * bubble_fourier))^{2/3}",
        ),
        expect=[1.000000, 0.993324, 0.986629, 0.979915, 0.973182, 0.966429, 0.959656, 0.952864, 0.946050, 0.939216],
    ),
}
# fmt: on

# [[equation]]
# name = 'florschuetz_chao_1965'
# latex = '\beta = 1 - 4 \Ja \sqrt{\Fo_\o / \pi}'
# sympy = 'Eq(beta, 1 - 4 * Ja * sqrt(Fo_0 / pi))'
# python = '1 - 4 * bubble_jakob * sqrt(bubble_fourier / pi)'
# expect = [1.000000, 0.946807, 0.924774, 0.907868, 0.893615, 0.881058, 0.869705, 0.859266, 0.849549, 0.840423]

# [[equation]]
# name = 'isenberg_sideman_1970'
# latex = '''
# \beta =
# \left(1 - \left(3/\sqrt{\pi}\right) \Re_\bo^{1/2} \Pr^{1/3} Ja Fo_\o \right)^{2/3}
# '''
# sympy = 'Eq(beta, (1 - 3/sqrt(pi) * Re_b0**(1/2) * Pr**(1/3) * Ja * Fo_0)**(2/3))'
# python = '''
# (
#     1 - (3/sqrt(pi)) * bubble_initial_reynolds**(1/2) * liquid_prandtl**(1/3) *
#     bubble_jakob * bubble_fourier
# )**(2/3)
# '''
# expect = [1.000000, 0.993721, 0.987422, 0.981104, 0.974765, 0.968405, 0.962024, 0.955622, 0.949199, 0.942753]

# [[equation]]
# name = 'akiyama_1973'
# latex = '\beta=(1 - 1.036 Re_\bo^{1/2} Pr^{1/3} Ja Fo_\o)^{0.714}'
# sympy = 'Eq(beta, (1 - 1.036 * Re_b0**(1/2) * Pr**(1/3) * Ja * Fo_0)**0.714)'
# python = '''
# (
#     1 - 1.036 * bubble_fourier * bubble_initial_reynolds**(1/2) *
#     bubble_jakob * liquid_prandtl**(1/3)
# )**0.714
# '''
# expect = [1.000000, 0.995887, 0.991767, 0.987640, 0.983507, 0.979367, 0.975219, 0.971065, 0.966903, 0.962734]

# [[equation]]
# name = 'yuan_et_al_2009'
# latex = '''
# \beta =
# \left(
#     1 - 1.8 \Re_\bo^{0.5} \Pr^{1/3} \Ja \Fo_\o \left(1 - 0.5 \Ja^{0.1} \Fo_\o\right)
# \right)^{2/3}
# '''
# sympy = '''Eq(
# beta, (1 - 1.8 * Re_b0**0.5 * Pr**(1/3) * Ja * Fo_0 * (1 - 0.5 * Ja**0.1 * Fo_0))**(2/3)
# )'''
# python = '''
# (
#     1 - 1.8 * bubble_initial_reynolds**0.5 * liquid_prandtl**(1/3) *
#     bubble_jakob * bubble_fourier * (1 - 0.5 * bubble_jakob**0.1 * bubble_fourier)
# )**(2/3)
# '''
# expect = [1.000000, 0.993324, 0.986629, 0.979915, 0.973182, 0.966429, 0.959656, 0.952864, 0.946050, 0.939216]
