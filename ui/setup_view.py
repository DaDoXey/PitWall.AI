"""ui/setup_view.py — pagina Setup (placeholder; tab orizzontali in Fase 5)."""

import streamlit as st

from ui import components as c


def render() -> None:
    st.markdown(
        c.page_header("Setup", "Assetto BMW M4 GT3 · range ACC"),
        unsafe_allow_html=True,
    )
    st.markdown(c.placeholder_panel("Setup — in arrivo (Fase 5)"), unsafe_allow_html=True)
