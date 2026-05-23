"""Gas stabilization time calculations for tight gas reservoirs.

Ch 13 p.888.
tpss = minimum shut-in time to reach pseudosteady-state.
"""

import numpy as np


def stabilization_time_radial(porosity, mu_g, ct, k, A_ft2=None, A_acres=None):
    """Minimum shut-in time for radial flow (days).

    Ch 13: tpss = 15.8 * phi * mu_g * ct * A / k

    Parameters
    ----------
    porosity : float
        Porosity (fraction).
    mu_g : float
        Gas viscosity (cp).
    ct : float
        Total compressibility = Swi*cwi + Sg*cgi + cf (psi^-1).
    A_ft2 : float, optional
        Drainage area in ft^2. Provide A_ft2 or A_acres.
    k : float
        Permeability (md).
    A_acres : float, optional
        Drainage area in acres. 1 acre = 43560 ft^2.

    Returns
    -------
    float
        Stabilization time (days).
    """
    if A_acres is not None:
        A_ft2 = A_acres * 43560.0

    if A_ft2 <= 0 or k <= 0:
        return 0.0

    return 15.8 * porosity * mu_g * ct * A_ft2 / k


def stabilization_time_fractured(porosity, mu_g, ct, xf, k):
    """Minimum shut-in time for fractured gas well (days).

    Earlougher: tpss = 474 * phi * mu_g * ct * xf^2 / k

    Parameters
    ----------
    porosity : float
        Porosity (fraction).
    mu_g : float
        Gas viscosity (cp).
    ct : float
        Total compressibility (psi^-1).
    xf : float
        Fracture half-length (ft).
    k : float
        Permeability (md).

    Returns
    -------
    float
        Stabilization time (days).
    """
    if xf <= 0 or k <= 0:
        return 0.0

    return 474.0 * porosity * mu_g * ct * xf**2 / k


def example_13_5():
    """Example 13-5: 40-acre fractured well.
    phi=0.14, mu_gi=0.016 cp, cti=0.0008 psi^-1, A=40 acres, k=0.1 md.
    """
    A_ft2 = 40 * 43560
    t_radial = stabilization_time_radial(
        porosity=0.14, mu_g=0.016, ct=0.0008, A_ft2=A_ft2, k=0.1
    )
    return t_radial
