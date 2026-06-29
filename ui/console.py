"""ui/console.py — pagina Engineer Console / Gigi (riempita in Fase 3)."""

import streamlit as st

from ui import components as c


def render() -> None:
    st.markdown(
        c.page_header("Engineer Console", "Gigi · Race Engineer"),
        unsafe_allow_html=True,
    )
    st.markdown(c.placeholder_panel("Engineer Console — in arrivo (Fase 3)"), unsafe_allow_html=True)
