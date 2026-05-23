"""Gas reservoir Havlena-Odeh analysis.

Ch 13 Eq 13-11, 13-23.
p/Z vs Gp and F vs Eg plots for gas reservoir diagnostics.
"""

import numpy as np


def pz_vs_gp(p_values, z_values, gp_values):
    """Compute p/Z values for plotting against Gp.

    Parameters
    ----------
    p_values : array-like
        Pressures (psi).
    z_values : array-like
        Gas deviation factors (dimensionless).
    gp_values : array-like
        Cumulative gas production (Mscf or scf).

    Returns
    -------
    dict with pz (p/Z), gp (same units as input), pi_zi (initial p/Z).
    """
    p = np.asarray(p_values, dtype=float)
    z = np.asarray(z_values, dtype=float)
    gp = np.asarray(gp_values, dtype=float)

    pz = np.divide(p, z, out=np.zeros_like(p), where=z != 0)
    return {
        "pz": pz,
        "gp": gp,
        "pi_zi": float(pz[0]) if len(pz) > 0 else 0.0,
    }


def gas_f_vs_eg(pv, Bg_values, Bgi, Gp_values, Wp_values, Bw):
    """Compute F and Eg for gas Havlena-Odeh plot.

    Parameters
    ----------
    * This function accepts individual arrays or can take a DataFrame.
    Bg_values : array-like
        Gas FVF at each time step (bbl/scf or ft3/scf).
    Bgi : float
        Initial gas FVF.
    Gp_values : array-like
        Cumulative gas production (Mscf or consistent units).
    Wp_values : array-like
        Cumulative water production (bbl).
    Bw : float
        Water FVF (bbl/STB).

    Returns
    -------
    dict with F, Eg arrays.
    """
    bg = np.asarray(Bg_values, dtype=float)
    gp = np.asarray(Gp_values, dtype=float)
    wp = np.asarray(Wp_values, dtype=float)

    F = gp * bg + wp * Bw
    Eg = bg - Bgi

    return {"F": F, "Eg": Eg}


def gas_hod_parameterized(F, Eg, We):
    """F/Eg vs We/Eg plot data for water-drive gas diagnostic.

    Returns dict with x=F/Eg, y=We/Eg.
    """
    F_arr = np.asarray(F, dtype=float)
    Eg_arr = np.asarray(Eg, dtype=float)
    We_arr = np.asarray(We, dtype=float)

    valid = np.abs(Eg_arr) > 1e-15
    x = np.divide(F_arr[valid], Eg_arr[valid])
    y = np.divide(We_arr[valid], Eg_arr[valid])

    return {"x": x, "y": y}


def detect_water_drive_from_pz(pz_values, gp_values):
    """Detect water influx from p/Z vs Gp curvature.

    Simple heuristic: compute linear residual with and without
    the last data point. If including the last point increases
    residual by > 10%, water drive is likely present.

    Returns dict with is_water_drive (bool), curvature (float).
    """
    pz = np.asarray(pz_values, dtype=float)
    gp = np.asarray(gp_values, dtype=float)

    if len(pz) < 3:
        return {"is_water_drive": False, "curvature": 0.0}

    coeffs_all = np.polyfit(gp, pz, 1)
    trend_all = np.polyval(coeffs_all, gp)
    residual_all = np.sum((pz - trend_all) ** 2)

    coeffs_early = np.polyfit(gp[:-1], pz[:-1], 1)
    trend_early = np.polyval(coeffs_early, gp)
    residual_early = np.sum((pz - trend_early) ** 2)

    curvature = (residual_all - residual_early) / (residual_early + 1e-15)
    return {
        "is_water_drive": curvature > 0.1,
        "curvature": curvature,
    }


def bt_to_bo_rs(Bt_values, Bg_values, Rsi, p_values=None):
    """Estimate Bo and Rs from two-phase FVF (Bt) data.

    The two-phase FVF is defined as Bt = Bo + (Rsi - Rs)*Bg.
    This function estimates separate Bo and Rs when only Bt is available.

    Parameters
    ----------
    Bt_values : array-like
        Two-phase formation volume factor at each pressure (bbl/STB).
    Bg_values : array-like
        Gas FVF at each pressure (bbl/scf).
    Rsi : float
        Initial solution GOR (scf/STB).
    p_values : array-like, optional
        Pressures (psi). If provided, Rs is estimated by linear scaling.
        If None, Rs decline is estimated from Bt - Boi relationship.

    Returns
    -------
    tuple of (Bo_est, Rs_est) numpy arrays.
    """
    Bt = np.asarray(Bt_values, dtype=float)
    Bg = np.asarray(Bg_values, dtype=float)
    n = len(Bt)

    Boi = float(Bt[0])

    if p_values is not None:
        p = np.asarray(p_values, dtype=float)
        Rs_est = Rsi * p / p[0]
    else:
        ratio = np.linspace(1.0, 0.6, n)
        Rs_est = Rsi * ratio

    Bo_est = Bt - (Rsi - Rs_est) * Bg

    bad = (Bo_est < 1.0) | (np.abs(Rsi - Rs_est) < 1e-10)
    for _ in range(5):
        if not np.any(bad):
            break
        for i in range(1, n):
            if bad[i] and not bad[i - 1]:
                Bo_est[i] = max(Bo_est[i - 1] * 0.95, 1.0)
                diff = Bt[i] - Bo_est[i]
                if Bg[i] > 0:
                    Rs_est[i] = Rsi - diff / Bg[i]
                bad[i] = False

    return Bo_est, Rs_est
