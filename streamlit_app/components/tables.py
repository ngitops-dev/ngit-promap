import streamlit as st
import pandas as pd

from utils.formatting import status_badge


def render_table(data: list[dict], columns: list[dict], key: str = None, on_select: str = None):
    if not data:
        st.info("No data available.")
        return

    df = pd.DataFrame(data)

    display_cols = [c["key"] for c in columns if c["key"] in df.columns]
    header = {c["key"]: c["label"] for c in columns if c["key"] in df.columns}

    st.dataframe(
        df[display_cols].rename(columns=header),
        use_container_width=True,
        key=key,
        on_select="rerun" if on_select else None,
        selection_mode="single-row" if on_select else None,
    )
