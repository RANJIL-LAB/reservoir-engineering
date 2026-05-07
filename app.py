"""
Reservoir Engineering MBE Tool — Streamlit Application

This application provides an interactive web interface for solving the
General Material Balance Equation (MBE).  Users can:

  1. Select a target variable to solve for (N, We, m, or deltaP).
  2. Configure reservoir state and active drive mechanisms.
  3. Enter data manually or upload a CSV/Excel file.
  4. View the calculated result, drive-mechanism analysis,
     execution timer, interactive drive-index chart, and a
     downloadable summary table.
  5. View time-series charts (Pressure vs Np, Havlena-Odeh F vs Et)
     when multi-row CSV data is uploaded.

The heavy lifting is delegated to `mbe_solver.py`, which uses SymPy to
symbolically solve the MBE for any missing variable.
"""

import time

import streamlit as st

from config import var_info, all_vars
from mbe_solver import solve_mbe
from ui.sidebar import render_sidebar
from ui.data_input import render_manual_input, render_file_upload
from ui.results import render_results
from ui.time_series import render_time_series

st.set_page_config(
    page_title="Reservoir Engineering MBE Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Reservoir Engineering: Material Balance Equation (MBE) Solver")
st.markdown("---")

config = render_sidebar()
target_var = config['target_var']
is_unsaturated = config['is_unsaturated']
forced_zeros = config['forced_zeros']

st.header("Data Input")

input_method = st.radio(
    "Input Method",
    options=["Manual Entry", "File Upload (CSV/Excel)"],
    horizontal=True
)

known_values = {}
df = None
col_map = {}

if input_method == "Manual Entry":
    manual_result = render_manual_input(var_info, target_var, forced_zeros, is_unsaturated)
    known_values = manual_result['known_values']
else:
    file_result = render_file_upload(var_info, target_var, forced_zeros, is_unsaturated)
    known_values = file_result['known_values']
    df = file_result['df']
    col_map = file_result['col_map']

st.markdown("---")
st.header("Results")

if st.button("Calculate", type="primary"):
    if not known_values:
        st.error("Please provide input values before calculating.")
        st.stop()

    for var in forced_zeros:
        known_values[var] = 0.0

    if is_unsaturated:
        if 'Rsi' in known_values:
            known_values['Rp'] = known_values['Rsi']
        elif 'Rp' in known_values:
            known_values['Rsi'] = known_values['Rp']
        else:
            st.error(
                "For an unsaturated reservoir, Rsi (and therefore Rp) "
                "must be provided."
            )
            st.stop()

    if target_var in known_values:
        del known_values[target_var]

    with st.spinner("Solving Material Balance Equation..."):
        t_start = time.perf_counter()
        result = solve_mbe(target_var, known_values, forced_zeros)
        t_elapsed = time.perf_counter() - t_start

    all_vals = result.get('all_values', {})
    render_results(result, target_var, forced_zeros, all_vals, t_elapsed, var_info, all_vars)

# Render time-series charts if multi-row data is available (rendered below results or on its own)
if df is not None and len(df) > 1:
    render_time_series(df, col_map)
