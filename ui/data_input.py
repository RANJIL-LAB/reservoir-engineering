import pandas as pd
import streamlit as st

from config import GAS_VARS, OIL_VARS


def _apply_unsaturated_overrides(known_values, is_unsaturated):
    if not is_unsaturated:
        return
    if "Rsi" in known_values:
        known_values["Rp"] = known_values["Rsi"]
        known_values["Rs"] = known_values["Rsi"]
    elif "Rp" in known_values:
        known_values["Rsi"] = known_values["Rp"]
        known_values["Rs"] = known_values["Rp"]


def _clear_calculated():
    st.session_state["calculated"] = False


def render_manual_time_series_table(
    var_info, known_values, fluid_type="oil", is_unsaturated=False
):
    """Render an editable table for manual time-series data entry.

    Returns a dict with 'df' (DataFrame or None) and 'col_map' (dict),
    analogous to the previous file-upload path, so the calling code can pass
    the result directly into render_time_series.
    """
    if fluid_type == "gas":
        return _render_gas_time_series_table(var_info)

    with st.expander(
        "📊 Optional: Time-Series Data for Havlena-Odeh & Pressure Plots",
        expanded=False,
    ):
        st.caption(
            "Enter multiple rows of time-varying data below. Each row represents "
            "a different time step or pressure point. Constants (Boi, Bgi, Rsi, "
            "Bw, Swi, cw, cf, m) are taken from your manual inputs above.\n\n"
            "Add at least **2 rows** to unlock: Pressure Decline, Havlena-Odeh "
            "F vs. Et, and drive-mechanism-specific plots."
        )

        if is_unsaturated:
            ts_columns = ["Np", "deltaP", "Bo", "Bg", "Wp"]
        else:
            ts_columns = ["Np", "deltaP", "Rp", "Bo", "Rs", "Bg", "Wp"]

        initial_data = {}
        for var in ts_columns:
            default_val = float(var_info[var].get("default", 0.0))
            initial_data[var] = [default_val] * 3

        initial_df = pd.DataFrame(initial_data)

        column_config = {}
        for var in ts_columns:
            info = var_info[var]
            column_config[var] = st.column_config.NumberColumn(
                info["label"],
                help=info["label"],
                format=info["format"],
                min_value=0.0 if var != "deltaP" else None,
            )

        edited_df = st.data_editor(
            initial_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config=column_config,
            key=f"manual_ts_editor_{fluid_type}_{is_unsaturated}",
        )

        if edited_df is not None and len(edited_df) > 1:
            col_map = {var: var for var in ts_columns}
            return {"df": edited_df, "col_map": col_map}

        return {"df": None, "col_map": {}}


def _render_gas_time_series_table(var_info):
    ts_columns = ["p", "Gp", "Bg", "Wp", "Z"]
    initial_data = {}
    for var in ts_columns:
        default_val = float(var_info.get(var, {}).get("default", 0.0))
        initial_data[var] = [default_val] * 3
    initial_df = pd.DataFrame(initial_data)
    column_config = {}
    for var in ts_columns:
        info = var_info.get(var, {})
        label = info.get("label", var)
        fmt = info.get("format", "%.2f")
        column_config[var] = st.column_config.NumberColumn(
            label,
            help=label,
            format=fmt,
            min_value=0.0,
        )
    with st.expander(
        "📊 Optional: Time-Series Data for Gas Plots",
        expanded=False,
    ):
        st.caption(
            "Enter multiple rows of time-varying gas data below. Each row "
            "represents a different time step. Add at least 2 rows to unlock "
            "p/Z vs Gp, F vs Eg, and Roach plots."
        )
        edited_df = st.data_editor(
            initial_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config=column_config,
            key="manual_ts_editor_gas",
        )
        if edited_df is not None and len(edited_df) > 1:
            col_map = {var: var for var in ts_columns}
            return {"df": edited_df, "col_map": col_map}
        return {"df": None, "col_map": {}}


def render_manual_input(
    var_info, target_var, forced_zeros, is_unsaturated, fluid_type="oil"
):
    st.subheader("Enter Known Variables")

    col_left, col_right = st.columns(2)
    display_order = GAS_VARS if fluid_type == "gas" else OIL_VARS

    known_values = {}
    for idx, var in enumerate(display_order):
        if var == target_var:
            continue
        if var in forced_zeros:
            continue
        if fluid_type != "gas" and is_unsaturated and var in ("Rp", "Rs"):
            continue

        info = var_info[var]
        container = col_left if idx % 2 == 0 else col_right
        min_val = 0.0 if var not in ("deltaP",) else None

        default_for_widget = st.session_state.get(f"manual_{var}", info["default"])
        val = container.number_input(
            info["label"],
            value=default_for_widget,
            format=info["format"],
            min_value=min_val,
            key=f"manual_{var}",
            on_change=_clear_calculated,
        )
        known_values[var] = val

    _apply_unsaturated_overrides(known_values, is_unsaturated)

    return {"known_values": known_values}
