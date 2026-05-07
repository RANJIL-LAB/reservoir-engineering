"""
MBE Solver - Material Balance Equation Math Engine

This module defines the General Material Balance Equation (MBE) using SymPy
symbolic mathematics. It provides a unified solver that can calculate any
missing variable (N, We, m, or deltaP) by substituting known values and
applying drive-mechanism constraints (forced zeros).

The solver handles both direct algebraic solutions (via sympy.solve) and
iterative numerical fallback (via sympy.nsolve) for non-linear cases.
"""

import sympy as sp
import numpy as np
from config import SYMBOLS, N, Np, Bt, Bti, Rp, Rsi, Bg, Bgi, We, Wp, Bw, m, Swi, cw, cf, deltaP

# =============================================================================
# 2. Define the General MBE equation components
# =============================================================================
# The General MBE (as written in the project specification):
#
#   N = (Np * [Bt + (Rp - Rsi) * Bg] - (We - Wp * Bw))
#       -------------------------------------------------
#       (Bt - Bti) + m * Bti * [Bg/Bgi - 1]
#                    + Bti * (1 + m) * [(Swi*cw + cf)/(1 - Swi)] * deltaP
#
# We decompose it into three parts:
#   - numerator        : net production (oil + evolved gas) minus net water influx
#   - base_denominator : oil shrinkage + gas-cap expansion
#   - expansion_term   : rock and connate-water expansion (depends on deltaP)

numerator = Np * (Bt + (Rp - Rsi) * Bg) - (We - Wp * Bw)
base_denominator = (Bt - Bti) + m * Bti * (Bg / Bgi - 1)
expansion_term = Bti * (1 + m) * ((Swi * cw + cf) / (1 - Swi)) * deltaP
denominator = base_denominator + expansion_term

# ------------------------------------------------------------------------------
# Implicit form:  N * denominator - numerator = 0
# ------------------------------------------------------------------------------
# By writing the equation as an implicit expression equal to zero, SymPy can
# uniformly solve for ANY variable, not just N.  For example, if we want to
# solve for We, SymPy will rearrange the implicit equation to isolate We.
# This avoids maintaining four separate explicit formulas.
MBE_IMPLICIT = N * denominator - numerator



def solve_mbe(target_var: str, known_values: dict, forced_zeros: list = None) -> dict:
    """
    Solve the General Material Balance Equation for a single target variable.

    The function substitutes all known numeric values (and forced zeros) into
    the implicit MBE, then uses SymPy to solve for the remaining unknown.

    Parameters
    ----------
    target_var : str
        Name of the variable to solve for.  Must be one of the keys in SYMBOLS
        (e.g. 'N', 'We', 'm', 'deltaP').
    known_values : dict
        Mapping of variable names (str) to float values.  These are the inputs
        provided by the user (either manually or from a file).
    forced_zeros : list, optional
        List of variable names that should be treated as 0 because the
        corresponding drive mechanism has been turned off in the UI
        (e.g. ['cw', 'cf'] when rock/fluid expansion is inactive).

    Returns
    -------
    dict
        {
            'success': bool,
            'result': float or None,       # The solved value of target_var
            'error_message': str or None,  # Human-readable error if failed
            'all_values': dict             # Every variable's final numeric value
        }
    """
    # ------------------------------------------------------------------
    # Validate target variable exists in our symbol table
    # ------------------------------------------------------------------
    if target_var not in SYMBOLS:
        return {
            'success': False,
            'result': None,
            'error_message': f"Unknown target variable: {target_var}",
            'all_values': {}
        }

    target_symbol = SYMBOLS[target_var]

    # ------------------------------------------------------------------
    # a. Build the substitutions dictionary.
    #    Start by forcing selected variables to 0 (drive-mechanism toggles).
    # ------------------------------------------------------------------
    substitutions = {}
    if forced_zeros:
        for var_name in forced_zeros:
            if var_name in SYMBOLS:
                substitutions[SYMBOLS[var_name]] = 0.0

    # ------------------------------------------------------------------
    # b. Overlay the user's known values on top of the forced zeros.
    #    If the user explicitly typed 0 for a variable, it will overwrite
    #    the forced-zero entry with the same value (no harm done).
    # ------------------------------------------------------------------
    for var_name, val in known_values.items():
        if var_name in SYMBOLS:
            substitutions[SYMBOLS[var_name]] = float(val)

    # ------------------------------------------------------------------
    # c. Remove the target variable from substitutions — it is the one
    #    unknown we want SymPy to solve for.
    # ------------------------------------------------------------------
    substitutions.pop(target_symbol, None)

    # ------------------------------------------------------------------
    # d. Verify that every NON-target variable now has a numeric value.
    #    If anything is still missing, we cannot solve the equation.
    # ------------------------------------------------------------------
    missing = []
    for name, sym in SYMBOLS.items():
        if name != target_var and sym not in substitutions:
            missing.append(name)

    if missing:
        return {
            'success': False,
            'result': None,
            'error_message': (
                f"Missing known values for variables: {', '.join(missing)}"
            ),
            'all_values': {}
        }

    # ------------------------------------------------------------------
    # Edge-case guard: Swi = 1 creates division by zero in the expansion
    # term because of the (1 - Swi) denominator.
    # If the numerator of the expansion term is ALSO zero, the whole term
    # vanishes in the physical limit and we can drop it safely.
    # Otherwise the inputs are physically impossible.
    # ------------------------------------------------------------------
    if Swi in substitutions and substitutions[Swi] == 1.0:
        swi_val = substitutions[Swi]
        cw_val = substitutions.get(cw, 0.0)
        cf_val = substitutions.get(cf, 0.0)
        if abs(swi_val * cw_val + cf_val) < 1e-12:
            # Expansion term is 0 in the limit; solve using the reduced
            # implicit equation that omits the expansion term entirely.
            expr_to_solve = (N * base_denominator - numerator).subs(substitutions)
        else:
            return {
                'success': False,
                'result': None,
                'error_message': (
                    "Division by zero: Swi=1 with non-zero rock/fluid "
                    "expansion term (Swi*cw + cf != 0)"
                ),
                'all_values': {}
            }
    else:
        # Standard path: substitute everything into the full implicit equation.
        expr_to_solve = MBE_IMPLICIT.subs(substitutions)

    # ------------------------------------------------------------------
    # Simplify the substituted expression and guard against symbolic
    # infinities or NaNs that can arise from division by zero.
    # ------------------------------------------------------------------
    expr_to_solve = sp.simplify(expr_to_solve)

    if expr_to_solve.has(sp.zoo, sp.oo, sp.nan, -sp.oo):
        return {
            'success': False,
            'result': None,
            'error_message': (
                "Division by zero or undefined expression after substitution"
            ),
            'all_values': {}
        }

    # ------------------------------------------------------------------
    # Check if the target variable has dropped out of the equation.
    # If the derivative with respect to the target is zero, the variable
    # does not appear in the simplified expression.
    #   - If the entire expression is 0 -> infinite solutions (any value works).
    #   - If the expression is non-zero   -> no solution exists (inconsistent).
    # ------------------------------------------------------------------
    derivative = sp.diff(expr_to_solve, target_symbol)
    if derivative == 0:
        if sp.simplify(expr_to_solve) == 0:
            return {
                'success': False,
                'result': None,
                'error_message': (
                    f"Target variable {target_var} cancels out; "
                    "infinite solutions exist"
                ),
                'all_values': {}
            }
        else:
            return {
                'success': False,
                'result': None,
                'error_message': (
                    f"Target variable {target_var} cancels out; "
                    "equation is inconsistent"
                ),
                'all_values': {}
            }

    # ------------------------------------------------------------------
    # e. Attempt direct algebraic solving with sympy.solve.
    #    This works well for linear and simple rational equations (N, We, m).
    # ------------------------------------------------------------------
    result = None
    solutions = []
    try:
        solutions = sp.solve(expr_to_solve, target_symbol)
    except Exception:
        pass

    if solutions:
        # sympy.solve can return a list, a dict, or a single expression.
        # Normalise everything to a list of candidate solutions.
        if isinstance(solutions, dict):
            solutions = [solutions.get(target_symbol)]

        for sol in solutions:
            if sol is None:
                continue
            try:
                # Prefer an explicit real solution
                if hasattr(sol, 'is_real') and sol.is_real:
                    result = float(sol)
                    break
                # Accept complex numbers with negligible imaginary part
                val = complex(sol.evalf())
                if abs(val.imag) < 1e-10 and not (
                    np.isnan(val.real) or np.isinf(val.real)
                ):
                    result = float(val.real)
                    break
            except Exception:
                continue

    # ------------------------------------------------------------------
    # f. Algebraic solving failed -> use iterative numerical solver.
    #    SymPy's nsolve is a Newton-Raphson implementation.  We try a
    #    range of initial guesses spanning many orders of magnitude
    #    because reservoir variables can be tiny (compressibilities) or
    #    huge (cumulative production).
    # ------------------------------------------------------------------
    if result is None:
        guesses = [
            1e-6, 1e-3, 0.1, 1.0, 10.0, 100.0,
            1e3, 1e4, 1e5, 1e6, 1e9
        ]
        for guess in guesses:
            try:
                candidate = float(
                    sp.nsolve(
                        expr_to_solve, target_symbol, guess,
                        tol=1e-10, maxsteps=100
                    )
                )
                # Verify the residual is small (equation actually balances)
                residual = float(
                    expr_to_solve.subs({target_symbol: candidate})
                )
                if abs(residual) < 1e-6:
                    result = candidate
                    break
            except Exception:
                continue

    # ------------------------------------------------------------------
    # Validate the final result before returning it to the caller.
    # ------------------------------------------------------------------
    if result is None or np.isnan(result) or np.isinf(result):
        return {
            'success': False,
            'result': None,
            'error_message': "No valid solution found",
            'all_values': {}
        }

    # ------------------------------------------------------------------
    # g. Build the all_values dictionary with every variable's final value.
    #    The target variable gets the solved result; everything else gets
    #    the substituted numeric value that was used during solving.
    # ------------------------------------------------------------------
    all_values = {}
    for name, sym in SYMBOLS.items():
        if name == target_var:
            all_values[name] = result
        else:
            all_values[name] = substitutions[sym]

    return {
        'success': True,
        'result': result,
        'error_message': None,
        'all_values': all_values
    }


def compute_drive_indices(all_values: dict) -> dict:
    """
    Compute approximate drive-index contributions for visualization.

    The MBE denominator contains three distinct physical mechanisms that
    provide the energy pushing oil out of the reservoir:

      1. Oil shrinkage / solution-gas drive :  (Bt - Bti)
      2. Gas-cap expansion                  :  m * Bti * (Bg/Bgi - 1)
      3. Rock & connate-water expansion     :  Bti*(1+m)*[(Swi*cw+cf)/(1-Swi)]*deltaP

    In addition, the net water influx (We - Wp*Bw) appears in the numerator
    and represents energy supplied from an aquifer.

    This function evaluates the absolute magnitude of each term using the
    final variable values, then normalises them to percentages so they can
    be plotted as a pie or bar chart.

    Parameters
    ----------
    all_values : dict
        Dictionary mapping variable names (str) to their final numeric values.
        Must contain at least the keys required by the MBE denominator.

    Returns
    -------
    dict
        {
            'labels':   list of str,
            'values':   list of float (percentages, sum to ~100),
            'raw':      list of float (absolute magnitudes of each term)
        }
    """
    # Extract numeric values; default to 0 if a key is missing.
    N_val = all_values.get('N', 0)
    m_val = all_values.get('m', 0)
    Bt_val = all_values.get('Bt', 0)
    Bti_val = all_values.get('Bti', 0)
    Bg_val = all_values.get('Bg', 0)
    Bgi_val = all_values.get('Bgi', 0)
    Swi_val = all_values.get('Swi', 0)
    cw_val = all_values.get('cw', 0)
    cf_val = all_values.get('cf', 0)
    deltaP_val = all_values.get('deltaP', 0)
    We_val = all_values.get('We', 0)
    Wp_val = all_values.get('Wp', 0)
    Bw_val = all_values.get('Bw', 0)

    # --- Compute absolute magnitudes of each drive term ---
    #
    # The denominator terms (oil shrinkage, gas-cap expansion, rock/water
    # expansion) are expressed in FVF units (bbl/STB).  To compare them
    # with the water-influx term (which is in bbl), we multiply each
    # denominator term by N [STB], yielding consistent bbl units.
    #
    # This gives the actual volume of fluid displaced by each mechanism.

    # 1. Oil shrinkage / solution-gas expansion energy [bbl]
    oil_term = abs(N_val * (Bt_val - Bti_val))

    # 2. Gas-cap expansion energy [bbl]
    gas_cap_term = abs(N_val * m_val * Bti_val * (Bg_val / Bgi_val - 1))

    # 3. Rock & connate-water expansion energy [bbl]
    #    Guard against division by zero when Swi == 1.
    if abs(1.0 - Swi_val) < 1e-12:
        rock_water_term = 0.0
    else:
        rock_water_term = abs(
            N_val * Bti_val * (1 + m_val)
            * ((Swi_val * cw_val + cf_val) / (1 - Swi_val))
            * deltaP_val
        )

    # 4. Net water influx energy [bbl]
    water_term = abs(We_val - Wp_val * Bw_val)

    # Collect labels and raw values for the caller
    labels = [
        "Oil Shrinkage / Solution Gas",
        "Gas Cap Expansion",
        "Rock & Water Expansion",
        "Net Water Influx"
    ]
    raw_values = [oil_term, gas_cap_term, rock_water_term, water_term]

    # Normalise to percentages.  If the total is zero, return equal shares
    # so the chart still renders gracefully.
    total = sum(raw_values)
    if total > 0:
        percentages = [100.0 * v / total for v in raw_values]
    else:
        percentages = [0.0, 0.0, 0.0, 0.0]

    return {
        'labels': labels,
        'values': percentages,
        'raw': raw_values
    }


# =============================================================================
# Stand-alone test (run with: python mbe_solver.py)
# =============================================================================
if __name__ == "__main__":
    # Test case: solve for N with expansion inactive (cw=cf=Swi=0).
    target = 'N'
    forced = ['cw', 'cf', 'Swi']
    known = {
        'Np': 5e6,
        'Rp': 1100,
        'Rsi': 600,
        'Bt': 1.48,
        'Bg': 0.0015,
        'We': 3e6,
        'Wp': 2e5,
        'Bw': 1.0,
        'Bti': 1.35,
        'm': 0.2,
        'Bgi': 0.0011,
        'deltaP': 500
    }
    expected = 36_590_000  # ~36.59 MMSTB (physically correct formula)

    result_dict = solve_mbe(target, known, forced)

    print("MBE Solver Test")
    print("=" * 40)
    print(f"Target variable : {target}")
    print(f"Forced zeros    : {forced}")
    print(f"Known values    : {known}")
    print("-" * 40)

    if result_dict['success']:
        calc = result_dict['result']
        print(f"Calculated N    : {calc:,.2f} STB")
        print(f"Expected N      : {expected:,.2f} STB")
        diff = abs(calc - expected)
        tol = 1e5  # ±100,000 STB tolerance
        print(f"Difference      : {diff:,.2f} STB")
        print(f"Within tolerance: {diff <= tol}")

        # Also print drive indices for quick visual verification
        indices = compute_drive_indices(result_dict['all_values'])
        print("\nDrive Indices:")
        for label, pct, raw in zip(indices['labels'], indices['values'], indices['raw']):
            print(f"  {label:35s} : {pct:6.2f}%  (raw = {raw:,.4f})")
    else:
        print("Solver failed!")
        print(f"Error message   : {result_dict['error_message']}")
