import streamlit as st

from utils.formatting import format_currency, format_number


def render_kpi_card(label: str, value, delta: str = "", delta_color: str = "normal"):
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def render_kpi_row(kpis: list[dict]):
    cols = st.columns(len(kpis))
    for col, kpi in zip(cols, kpis):
        with col:
            render_kpi_card(
                kpi["label"],
                kpi["value"],
                kpi.get("delta", ""),
                kpi.get("delta_color", "normal"),
            )
