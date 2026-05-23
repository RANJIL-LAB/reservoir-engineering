import sys, os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from models.gas_hod import pz_vs_gp, gas_f_vs_eg, detect_water_drive_from_pz
from models.gas_aquifer import linear_aquifer_we_gas
from models.roach import roach_alpha_beta, roach_fit
from models.gas_tight import stabilization_time_radial, stabilization_time_fractured


def approx(a, b, rt=0.02):
    if abs(b) < 1e-15:
        return abs(a) < 1e-10
    return abs(a - b) / max(abs(b), 1e-15) <= rt


def test_pz_vs_gp_basic():
    r = pz_vs_gp([3000, 2500, 2000], [0.8, 0.78, 0.82], [0, 1e6, 2e6])
    assert len(r["pz"]) == 3
    assert r["pz"][0] == 3000 / 0.8


def test_pz_vs_gp_zero_z():
    r = pz_vs_gp([3000, 2500], [0.0, 0.78], [0, 1e6])
    assert r["pz"][0] == 0.0


def test_pz_detect_water_drive_volumetric():
    G, pi, zi = 10e9, 3000, 0.8
    gp = np.linspace(0, 5e9, 10)
    pz = (pi / zi) * (1 - gp / G) + np.random.normal(0, 1, 10)
    r = detect_water_drive_from_pz(pz, gp)
    assert not r["is_water_drive"]


def test_pz_detect_water_drive_upward():
    gp = np.array([0, 1, 2, 3, 4, 5])
    pz = np.array([3750, 3400, 3150, 2950, 2820, 2750])
    r = detect_water_drive_from_pz(pz, gp)
    assert abs(r["curvature"]) > 0.01


def test_gas_f_vs_eg():
    Bg = np.array([0.001, 0.0012, 0.0015])
    r = gas_f_vs_eg(None, Bg, 0.001, np.array([0, 1e6, 2e6]), np.zeros(3), 1.0)
    assert len(r["F"]) == 3
    assert r["Eg"][1] > 0


def test_linear_aquifer_no_pressure():
    assert all(w == 0 for w in linear_aquifer_we_gas([3000, 3000], [0, 30], 100))


def test_linear_aquifer_single_step():
    we = linear_aquifer_we_gas([3000, 2900], [0, 30], 100)
    expected = 100 * 100 * np.sqrt(30)
    assert approx(we[1], expected)


def test_linear_aquifer_example_13_4():
    p = np.array(
        [
            2883,
            2881,
            2874,
            2866,
            2857,
            2849,
            2841,
            2826,
            2808,
            2794,
            2782,
            2767,
            2755,
            2741,
            2726,
            2712,
            2699,
            2688,
            2667,
        ]
    )
    we = linear_aquifer_we_gas(p, np.arange(len(p)) * 2, 1000)
    assert we[0] == 0 and we[-1] > we[1]


def test_roach_no_pressure_change():
    r = roach_alpha_beta([5000, 5000], [1.0, 1.0], 5000, 1.0)
    assert r["alpha"][1] == 0.0 and r["beta"][1] == 0.0


def test_roach_known():
    r = roach_alpha_beta([9507, 9000, 8500, 8000], [1.5, 1.45, 1.40, 1.36], 9507, 1.5)
    assert np.any(np.abs(r["alpha"][1:]) > 0)
    fit = roach_fit(r["alpha"], r["beta"])
    assert fit["G"] > 0 and fit["r_squared"] > 0


def test_roach_fit():
    fit = roach_fit([0, 1e-5, 2e-5], [0, 2e-5, 4e-5])
    assert fit["G"] > 0 and fit["r_squared"] > 0.9


def test_tpss_radial():
    t = stabilization_time_radial(
        porosity=0.14, mu_g=0.016, ct=0.0008, A_acres=40, k=0.1
    )
    assert 400 < t < 500


def test_tpss_radial_zero_k():
    t = stabilization_time_radial(porosity=0.14, mu_g=0.016, ct=0.0008, A_acres=40, k=0)
    assert t == 0.0


def test_tpss_fractured():
    t = stabilization_time_fractured(
        porosity=0.14, mu_g=0.016, ct=0.0008, xf=100, k=0.1
    )
    assert t > 0


def test_tpss_fractured_zero():
    assert (
        stabilization_time_fractured(porosity=0.14, mu_g=0.016, ct=0.0008, xf=0, k=0.1)
        == 0.0
    )


def test_example_13_5():
    from models.gas_tight import example_13_5

    assert approx(example_13_5(), 493, 0.02)


if __name__ == "__main__":
    for name, func in sorted(
        [(n, f) for n, f in list(globals().items()) if n.startswith("test_")]
    ):
        func()
        print(f"  {name} OK")
    print("All Ch 13 gas tests passed!")
