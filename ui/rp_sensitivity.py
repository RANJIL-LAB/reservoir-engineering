import streamlit as st
import numpy as np
import plotly.graph_objects as go


def render_rp_sensitivity(all_vals):
    st.subheader("Rp Sensitivity Analysis")
    st.caption(
        "Explore how the Cumulative Produced GOR (Rp) affects the "
        "predicted Recovery Factor (RF) based on current reservoir conditions."
    )

    Bo = all_vals.get('Bo') if all_vals.get('Bo') is not None else 1.0
    Boi = all_vals.get('Boi') if all_vals.get('Boi') is not None else 1.0
    Rsi = all_vals.get('Rsi') if all_vals.get('Rsi') is not None else 0.0
    Rs = all_vals.get('Rs') if all_vals.get('Rs') is not None else 0.0
    Bg = all_vals.get('Bg') if all_vals.get('Bg') is not None else 0.0
    Bgi = all_vals.get('Bgi') if all_vals.get('Bgi') is not None else 0.001
    m = all_vals.get('m') if all_vals.get('m') is not None else 0.0

    actual_produced_gor = all_vals.get('Rp') if all_vals.get('Rp') is not None else 800.0

    gas_cap_term = 0.0
    if Bgi != 0:
        gas_cap_term = m * Boi * ((Bg / Bgi) - 1)

    numerator = (Bo - Boi) + (Rsi - Rs) * Bg + gas_cap_term

    selected_produced_gor = st.slider(
        "Cumulative Produced GOR (Rp)",
        min_value=0,
        max_value=3000,
        value=int(round(actual_produced_gor)),
        step=50,
        key="rp_sensitivity_slider",
    )

    denominator_at_selected_rp = Bo + (selected_produced_gor - Rs) * Bg

    if numerator == 0 and denominator_at_selected_rp == 0:
        recovery_factor_at_selected_rp = 0.0
    elif denominator_at_selected_rp == 0:
        recovery_factor_at_selected_rp = float('nan')
    else:
        recovery_factor_at_selected_rp = (numerator / denominator_at_selected_rp) * 100

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Selected Rp", f"{selected_produced_gor:,.2f} scf/STB")
    with col2:
        st.metric("Recovery Factor (RF)", f"{recovery_factor_at_selected_rp:.2f}%")

    produced_gor_range = np.arange(0, 3050, 50)
    denominator_curve = Bo + (produced_gor_range - Rs) * Bg

    with np.errstate(divide='ignore', invalid='ignore'):
        recovery_factor_curve = np.where(
            denominator_curve != 0,
            (numerator / denominator_curve) * 100,
            np.nan,
        )

    sensitivity_chart = go.Figure()

    sensitivity_chart.add_trace(
        go.Scatter(
            x=produced_gor_range,
            y=recovery_factor_curve,
            mode='lines',
            name='RF Curve',
            line=dict(color='#1f77b4', width=2),
            hovertemplate=(
                "Rp = %{x:,.0f} scf/STB<br>"
                "RF = %{y:.2f}%<extra></extra>"
            ),
        )
    )

    if not np.isnan(recovery_factor_at_selected_rp) and 0 <= selected_produced_gor <= 3000:
        sensitivity_chart.add_trace(
            go.Scatter(
                x=[selected_produced_gor],
                y=[recovery_factor_at_selected_rp],
                mode='markers',
                name='Current Rp',
                marker=dict(color='#d62728', size=12, symbol='circle'),
                hovertemplate=(
                    "Rp = %{x:,.0f} scf/STB<br>"
                    "RF = %{y:.2f}%<extra></extra>"
                ),
            )
        )

        sensitivity_chart.add_vline(
            x=selected_produced_gor,
            line=dict(color='#d62728', width=1, dash='dash'),
            annotation_text=f"Rp = {selected_produced_gor:,.0f}",
            annotation_position="top",
        )

    sensitivity_chart.update_layout(
        xaxis_title="Cumulative Produced GOR (Rp) [scf/STB]",
        yaxis_title="Recovery Factor (RF) [%]",
        showlegend=False,
        hovermode='x unified',
        margin=dict(l=60, r=20, t=20, b=60),
    )

    st.plotly_chart(sensitivity_chart, use_container_width=True)
