"""
rp_sensitivity.py — Interactive Rp vs. RF sensitivity chart.

Displays a Plotly line graph showing how the Recovery Factor (RF)
varies with the Cumulative Produced GOR (Rp), using reservoir
parameters from the MBE solution.

The fractional recovery formula derives from the MBE (ignoring
rock/water expansion and assuming no net water influx):

    RF = numerator / (Bo + (Rp - Rs) * Bg) * 100

where numerator = (Bo - Boi) + (Rsi - Rs)*Bg + m*Boi*(Bg/Bgi - 1)
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go


def render_rp_sensitivity(all_vals: dict) -> None:
    Bo = all_vals.get('Bo') or 1.0
    Boi = all_vals.get('Boi') or 1.0
    Rsi = all_vals.get('Rsi') or 0.0
    Rs = all_vals.get('Rs') or 0.0
    Bg = all_vals.get('Bg') or 0.0
    Bgi = all_vals.get('Bgi') or 0.001
    m = all_vals.get('m') or 0.0

    actual_Rp = all_vals.get('Rp') if all_vals.get('Rp') is not None else 800.0

    gas_cap_term = 0.0
    if Bgi != 0:
        gas_cap_term = m * Boi * ((Bg / Bgi) - 1)

    numerator = (Bo - Boi) + (Rsi - Rs) * Bg + gas_cap_term

    rp_val = st.slider(
        "Cumulative Produced GOR (Rp)",
        min_value=0,
        max_value=3000,
        value=int(round(actual_Rp)),
        step=50,
        key="rp_sensitivity_slider",
    )

    denom_single = Bo + (rp_val - Rs) * Bg

    if numerator == 0 and denom_single == 0:
        rf_single = 0.0
    elif denom_single == 0:
        rf_single = float('nan')
    else:
        rf_single = (numerator / denom_single) * 100

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Selected Rp", f"{rp_val:,.2f} scf/STB")
    with col2:
        st.metric("Recovery Factor (RF)", f"{rf_single:.2f}%")

    rp_array = np.linspace(0, 3000, 301)
    denom_array = Bo + (rp_array - Rs) * Bg

    with np.errstate(divide='ignore', invalid='ignore'):
        rf_array = np.where(
            denom_array != 0,
            (numerator / denom_array) * 100,
            np.nan,
        )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=rp_array,
            y=rf_array,
            mode='lines',
            name='RF Curve',
            line=dict(color='#1f77b4', width=2),
            hovertemplate=(
                "Rp = %{x:,.0f} scf/STB<br>"
                "RF = %{y:.2f}%<extra></extra>"
            ),
        )
    )

    if not np.isnan(rf_single) and 0 <= rp_val <= 3000:
        fig.add_trace(
            go.Scatter(
                x=[rp_val],
                y=[rf_single],
                mode='markers',
                name='Current Rp',
                marker=dict(color='#d62728', size=12, symbol='circle'),
                hovertemplate=(
                    "Rp = %{x:,.0f} scf/STB<br>"
                    "RF = %{y:.2f}%<extra></extra>"
                ),
            )
        )

        fig.add_vline(
            x=rp_val,
            line=dict(color='#d62728', width=1, dash='dash'),
            annotation_text=f"Rp = {rp_val:,.0f}",
            annotation_position="top",
        )

    fig.update_layout(
        xaxis_title="Cumulative Produced GOR (Rp) [scf/STB]",
        yaxis_title="Recovery Factor (RF) [%]",
        showlegend=False,
        hovermode='x unified',
        margin=dict(l=60, r=20, t=20, b=60),
    )

    st.plotly_chart(fig, use_container_width=True)
