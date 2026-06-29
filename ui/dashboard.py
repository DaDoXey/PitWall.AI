"""ui/dashboard.py — pagina Dashboard (riempita in Fase 4)."""

import streamlit as st

from ui import components as c


def render() -> None:
    st.markdown(
        c.page_header("Dashboard", "Ultima sessione · Monza"),
        unsafe_allow_html=True,
    )
    st.markdown(c.placeholder_panel("Dashboard — in arrivo (Fase 4)"), unsafe_allow_html=True)
