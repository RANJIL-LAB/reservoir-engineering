"""Havlena-Odeh material balance variables for time-series analysis."""


def compute_havlena_odeh_f_et(row_values: dict) -> dict:
    """Compute Havlena-Odeh F (total withdrawal) and Et (total expansion)
    from a single row of reservoir data.

    Parameters
    ----------
    row_values : dict
        Dictionary with keys: 'Np', 'Bt', 'Rp', 'Rsi', 'Bg', 'Wp', 'Bw',
        'Bti', 'm', 'Bgi', 'Swi', 'cw', 'cf', 'deltaP'.

    Returns
    -------
    dict
        {'F': float, 'Et': float}
    """
    Np = row_values.get("Np", 0.0)
    Bt = row_values.get("Bt", 0.0)
    Rp = row_values.get("Rp", 0.0)
    Rsi = row_values.get("Rsi", 0.0)
    Bg = row_values.get("Bg", 0.0)
    Wp = row_values.get("Wp", 0.0)
    Bw = row_values.get("Bw", 0.0)
    Bti = row_values.get("Bti", 0.0)
    m = row_values.get("m", 0.0)
    Bgi = row_values.get("Bgi", 0.0)
    Swi = row_values.get("Swi", 0.0)
    cw = row_values.get("cw", 0.0)
    cf = row_values.get("cf", 0.0)
    deltaP = row_values.get("deltaP", 0.0)

    F = Np * (Bt + (Rp - Rsi) * Bg) + Wp * Bw

    oil_shrinkage = Bt - Bti

    if abs(Bgi) > 0:
        gas_cap = m * Bti * (Bg / Bgi - 1.0)
    else:
        gas_cap = 0.0

    if abs(1.0 - Swi) < 1e-12:
        expansion = 0.0
    else:
        expansion = (
            Bti
            * (1.0 + m)
            * ((Swi * cw + cf) / (1.0 - Swi))
            * deltaP
        )

    Et = oil_shrinkage + gas_cap + expansion

    return {"F": float(F), "Et": float(Et)}
