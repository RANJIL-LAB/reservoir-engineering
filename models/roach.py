"""Roach's method for abnormally pressured gas reservoirs.

Ch 13 Eq 13-29 to 13-31.
Graphical method: plot alpha vs beta.
Slope = 1/G (G = initial gas-in-place).
Intercept = -ER (rock expansion term).
"""

import numpy as np


def roach_alpha_beta(p_values, z_values, pi, zi):
    """Compute Roach's alpha and beta functions (Eq 13-30, 13-31).

    Parameters
    ----------
    p_values : array-like
        Pressures (psi).
    z_values : array-like
        Gas deviation factors at each pressure.
    pi : float
        Initial reservoir pressure (psi).
    zi : float
        Initial gas deviation factor.

    Returns
    -------
    dict with alpha, beta arrays (same length as input, first entry = 0).
    """
    p = np.asarray(p_values, dtype=float)
    z = np.asarray(z_values, dtype=float)
    n = len(p)

    alpha = np.zeros(n)
    beta = np.zeros(n)
    pz_i = pi / zi

    for i in range(1, n):
        dp = pi - p[i]
        if dp <= 0:
            continue
        pz_current = p[i] / z[i] if z[i] != 0 else 0.0
        if pz_current <= 0:
            continue
        alpha[i] = (1.0 - pz_current / pz_i) / dp
        beta[i] = (pz_i / pz_current - 1.0) / dp

    return {"alpha": alpha, "beta": beta}


def roach_fit(alpha, beta):
    """Fit Roach's method to estimate G and ER.

    Parameters
    ----------
    alpha : array-like
    beta : array-like

    Returns
    -------
    dict with G (scf), ER (psi^-1), r_squared.
    """
    a = np.asarray(alpha, dtype=float)
    b = np.asarray(beta, dtype=float)

    valid = np.isfinite(a) & np.isfinite(b) & (np.abs(a) > 1e-15) & (np.abs(b) > 1e-15)
    a_clean = a[valid]
    b_clean = b[valid]

    if len(a_clean) < 2:
        return {"G": 0.0, "ER": 0.0, "r_squared": 0.0}

    coeffs = np.polyfit(a_clean, b_clean, 1)
    slope, intercept = coeffs[0], coeffs[1]

    G = 1.0 / slope if abs(slope) > 1e-15 else 0.0
    ER = -intercept

    b_pred = slope * a_clean + intercept
    ss_res = np.sum((b_clean - b_pred) ** 2)
    ss_tot = np.sum((b_clean - np.mean(b_clean)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return {"G": G, "ER": ER, "r_squared": r2}
