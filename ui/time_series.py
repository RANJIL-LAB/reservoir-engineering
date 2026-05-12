import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from mbe_solver import compute_mbe_derived_terms


def _parse_row_values(df, col_map, required_vars, row_index):
    row_values = {}
    for var_name in required_vars:
        col = col_map.get(var_name)
        if col is None:
            row_values[var_name] = 0.0
            continue
        val = pd.to_numeric(df[col].iloc[row_index], errors='coerce')
        if isinstance(val, (int, float)):
            row_values[var_name] = 0.0 if pd.isna(val) else float(val)
        else:
            row_values[var_name] = 0.0
    return row_values


def render_time_series(df, col_map):
    if df is None or len(df) <= 1:
        return

    st.markdown("---")
    st.header("Time-Series Analysis")

    delta_pressure_column = col_map.get('deltaP')
    cumulative_oil_column = col_map.get('Np')

    if delta_pressure_column is None or cumulative_oil_column is None:
        st.info("Pressure vs. Cumulative Production plot requires 'deltaP' and 'Np' columns.")
    else:
        delta_pressure_series = pd.Series(pd.to_numeric(df[delta_pressure_column], errors='coerce'))
        cumulative_oil_series = pd.Series(pd.to_numeric(df[cumulative_oil_column], errors='coerce'))

        mask = delta_pressure_series.notna() & cumulative_oil_series.notna()
        delta_pressure_values = delta_pressure_series[mask]
        cumulative_oil_values = cumulative_oil_series[mask]

        pressure_chart = go.Figure()
        pressure_chart.add_trace(go.Scatter(
            x=cumulative_oil_values, y=delta_pressure_values,
            mode='lines+markers',
            name='Pressure vs Np',
            line=dict(color='#d62728', width=2)
        ))
        pressure_chart.update_layout(
            title="Pressure Decline vs. Cumulative Oil Production",
            xaxis_title="Cumulative Oil Produced, Np (STB)",
            yaxis_title="Pressure Drop, ΔP (psi)",
            height=450
        )
        st.plotly_chart(pressure_chart, use_container_width=True)

    required_vars = ['Np', 'Bo', 'Rp', 'Rsi', 'Rs', 'Bg', 'Wp', 'Bw', 'Boi', 'm', 'Bgi', 'Swi', 'cw', 'cf', 'deltaP']
    if not all(c in col_map for c in required_vars):
        st.info("Havlena-Odeh plot requires: Np, Bo, Rp, Rsi, Rs, Bg, Wp, Bw, Boi, m, Bgi, Swi, cw, cf, deltaP columns.")
        return

    total_withdrawal_values = []
    total_expansion_values = []
    for i in range(len(df)):
        row_values = _parse_row_values(df, col_map, required_vars, i)
        terms = compute_mbe_derived_terms(row_values)
        total_withdrawal_values.append(terms['F'])
        total_expansion_values.append(terms['Et'])

    havlena_chart = go.Figure()
    havlena_chart.add_trace(go.Scatter(
        x=total_expansion_values, y=total_withdrawal_values,
        mode='markers',
        name='Data Points',
        marker=dict(color='#1f77b4', size=8)
    ))

    valid_points = [
        (et, f_val) for et, f_val in zip(total_expansion_values, total_withdrawal_values)
        if not (np.isnan(et) or np.isnan(f_val) or np.isinf(et) or np.isinf(f_val))
    ]
    if len(valid_points) >= 2:
        et_array = np.array([v[0] for v in valid_points])
        f_array = np.array([v[1] for v in valid_points])
        trend_coefficients = np.polyfit(et_array, f_array, 1)
        slope, intercept = trend_coefficients[0], trend_coefficients[1]
        trend_x = np.linspace(et_array.min(), et_array.max(), 100)
        trend_y = slope * trend_x + intercept
        r_squared = 1 - np.sum((f_array - (slope * et_array + intercept))**2) / np.sum((f_array - f_array.mean())**2)
        havlena_chart.add_trace(go.Scatter(
            x=trend_x, y=trend_y,
            mode='lines',
            name=f'Trendline (slope ≈ {slope:,.2f}, R² = {r_squared:.4f})',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))

    havlena_chart.update_layout(
        title="Havlena-Odeh Plot: F vs. Et",
        xaxis_title="Total Expansion, Et (bbl/STB)",
        yaxis_title="Total Withdrawal, F (bbl)",
        height=500
    )
    st.plotly_chart(havlena_chart, use_container_width=True)

    st.markdown("""
**Havlena-Odeh Straight-Line Interpretation**

In the Havlena-Odeh straight-line method, a linear trend in the F vs. Et plot confirms that the
assumed drive mechanisms are consistent with the production history. The slope of the best-fit
line represents the **Initial Oil-in-Place (N)**. Deviations from linearity suggest that additional
or different drive mechanisms may be active.
""")
