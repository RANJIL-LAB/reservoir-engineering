"""Linear aquifer water influx for gas reservoirs.

Ch 13 Eq 13-24, Example 13-4.
We = C * sum(Delta_p * sqrt(t - tn)) via superposition.
"""

import numpy as np


def linear_aquifer_we_gas(p_history, t_history, C):
    """Compute cumulative water influx via linear aquifer model.

    Parameters
    ----------
    p_history : array-like
        Pressures at each time step (psi).
    t_history : array-like
        Cumulative times (same units as t, e.g., days or months).
    C : float
        Water influx constant (ft3/psi, or consistent units).

    Returns
    -------
    np.ndarray
        Cumulative We (same unit as C * psi) at each time step.
    """
    p = np.asarray(p_history, dtype=float)
    t = np.asarray(t_history, dtype=float)
    n = len(t)

    we = np.zeros(n)

    dp_drops = np.zeros(n)
    dp_drops[0] = 0.0
    for i in range(1, n):
        dp_drops[i] = p[i - 1] - p[i]

    for i in range(1, n):
        we_super = 0.0
        for j in range(1, i + 1):
            delta_t = t[i] - t[j - 1]
            if delta_t > 0:
                we_super += dp_drops[j] * np.sqrt(delta_t)
        we[i] = C * we_super

    return we


def gas_linear_aquifer_diagnostic(F, Eg, p_history, t_history, C):
    """Compute F/Eg and We/Eg for Havlena-Odeh linear aquifer diagnostic.

    Returns dict with x=We/Eg, y=F/Eg arrays.
    """
    we = linear_aquifer_we_gas(p_history, t_history, C)

    F_arr = np.asarray(F, dtype=float)
    Eg_arr = np.asarray(Eg, dtype=float)
    We_arr = np.asarray(we, dtype=float)

    valid = np.abs(Eg_arr) > 1e-15
    x = np.divide(We_arr[valid], Eg_arr[valid])
    y = np.divide(F_arr[valid], Eg_arr[valid])

    return {"x": x, "y": y, "we": we}
