import time

import pandas as pd
import streamlit as st

from config import var_info, all_vars
from mbe_solver import solve_mbe
from ui.sidebar import render_sidebar
from ui.data_input import render_manual_input, render_file_upload
from ui.results import render_results
from ui.rp_sensitivity import render_rp_sensitivity
from ui.time_series import render_time_series

st.set_page_config(
    page_title="Reservoir Engineering MBE Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

FLOAT_VARS = set(var_info.keys())


def _hydrate_from_query_params():
    params = st.query_params.to_dict()
    if not params:
        return False

    hydrated = st.session_state.get('_url_hydrated', False)
    if hydrated:
        return params.get('auto_calculate') == 'true'

    sidebar_map = {
        'fluid_type': 'sidebar_fluid_type',
        'target_var': 'sidebar_target_var',
        'reservoir_state': 'sidebar_reservoir_state',
        'water_drive_active': 'sidebar_water_drive',
        'gas_cap_active': 'sidebar_gas_cap',
        'expansion_active': 'sidebar_expansion',
    }
    sidebar_bool = {'sidebar_water_drive', 'sidebar_gas_cap', 'sidebar_expansion'}

    sidebar_fluid_map = {
        'oil': 'Oil Reservoir', 'Oil': 'Oil Reservoir', 'Oil Reservoir': 'Oil Reservoir',
        'gas': 'Gas Reservoir', 'Gas': 'Gas Reservoir', 'Gas Reservoir': 'Gas Reservoir',
    }
    sidebar_state_map = {
        'saturated': 'Saturated Reservoir (p ≤ pb)',
        'Saturated': 'Saturated Reservoir (p ≤ pb)',
        'unsaturated': 'Unsaturated Reservoir (p > pb)',
        'Unsaturated': 'Unsaturated Reservoir (p > pb)',
    }

    for param_key, param_val_list in params.items():
        val = param_val_list[0] if isinstance(param_val_list, list) else param_val_list

        if param_key == 'auto_calculate':
            continue

        if param_key in sidebar_map:
            ss_key = sidebar_map[param_key]
            if ss_key == 'sidebar_fluid_type':
                st.session_state[ss_key] = sidebar_fluid_map.get(val, 'Oil Reservoir')
            elif ss_key == 'sidebar_reservoir_state':
                st.session_state[ss_key] = sidebar_state_map.get(val, 'Saturated Reservoir (p ≤ pb)')
            elif ss_key in sidebar_bool:
                st.session_state[ss_key] = (val.lower() == 'true')
            else:
                st.session_state[ss_key] = val
            continue

        if param_key in FLOAT_VARS:
            parsed_val = pd.to_numeric(val, errors='coerce')
            if pd.notna(parsed_val):
                st.session_state[f"manual_{param_key}"] = float(parsed_val)
            continue

    st.session_state['_url_hydrated'] = True

    try:
        st.query_params.clear()
    except Exception:
        pass

    return params.get('auto_calculate') == 'true'


auto_calculate = _hydrate_from_query_params()

st.title("Reservoir Engineering: Material Balance Equation (MBE) Solver")
st.markdown("---")

config = render_sidebar()
target_var = config['target_var']
fluid_type = config['fluid_type']
is_unsaturated = config['is_unsaturated']
forced_zeros = config['forced_zeros']

st.header("Data Input")

input_method = st.radio(
    "Input Method",
    options=["Manual Entry", "File Upload (CSV/Excel)"],
    horizontal=True,
    key="app_input_method",
)

known_values = {}
df = None
col_map = {}

if input_method == "Manual Entry":
    manual_result = render_manual_input(var_info, target_var, forced_zeros, is_unsaturated, fluid_type)
    known_values = manual_result['known_values']
else:
    file_result = render_file_upload(var_info, target_var, forced_zeros, is_unsaturated, fluid_type)
    known_values = file_result['known_values']
    df = file_result['df']
    col_map = file_result['col_map']

st.markdown("---")
st.header("Results")

trigger_calc = st.button("Calculate", type="primary") or auto_calculate

cfg_fingerprint = (
    config['target_var'],
    config['fluid_type'],
    config['is_unsaturated'],
    tuple(sorted(config['forced_zeros'])),
)
if cfg_fingerprint != st.session_state.get('_prev_cfg_fp'):
    st.session_state['calculated'] = False

input_fingerprint = (
    input_method,
    tuple(sorted((k, v) for k, v in known_values.items())),
)
if input_fingerprint != st.session_state.get('_prev_inp_fp'):
    st.session_state['calculated'] = False

if trigger_calc:
    if not known_values and not auto_calculate:
        st.error("Please provide input values before calculating.")
        st.stop()

    for var in forced_zeros:
        known_values[var] = 0.0

    if fluid_type != 'gas' and is_unsaturated:
        if 'Rsi' in known_values:
            known_values['Rp'] = known_values['Rsi']
            known_values['Rs'] = known_values['Rsi']
        elif 'Rp' in known_values:
            known_values['Rsi'] = known_values['Rp']
            known_values['Rs'] = known_values['Rp']
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
        result = solve_mbe(target_var, known_values, forced_zeros, fluid_type)
        t_elapsed = time.perf_counter() - t_start

    all_vals = result.get('all_values', {})

    st.session_state['calculated'] = True
    st.session_state['_result'] = result
    st.session_state['_target_var'] = target_var
    st.session_state['_forced_zeros'] = forced_zeros
    st.session_state['_all_vals'] = all_vals
    st.session_state['_t_elapsed'] = t_elapsed
    st.session_state['_fluid_type'] = fluid_type
    st.session_state['_is_unsaturated'] = is_unsaturated
    st.session_state['_df'] = df
    st.session_state['_col_map'] = col_map
    st.session_state['_prev_cfg_fp'] = cfg_fingerprint
    st.session_state['_prev_inp_fp'] = input_fingerprint

    if auto_calculate:
        auto_calculate = False

if st.session_state.get('calculated', False):
    render_results(
        st.session_state['_result'],
        st.session_state['_target_var'],
        st.session_state['_forced_zeros'],
        st.session_state['_all_vals'],
        st.session_state['_t_elapsed'],
        var_info,
        all_vars,
        st.session_state['_fluid_type'],
    )

    _df = st.session_state.get('_df')
    _col_map = st.session_state.get('_col_map', {})
    if _df is not None and len(_df) > 1:
        render_time_series(_df, _col_map)

    if (
        st.session_state['_fluid_type'] == 'oil'
        and not st.session_state['_is_unsaturated']
    ):
        st.markdown("---")
        st.subheader("Rp Sensitivity Analysis")
        st.caption(
            "Explore how the Cumulative Produced GOR (Rp) affects the "
            "predicted Recovery Factor (RF) based on current reservoir conditions."
        )
        render_rp_sensitivity(st.session_state['_all_vals'])
