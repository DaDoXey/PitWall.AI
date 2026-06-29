"""ui/router.py — dispatch delle pagine in base a st.session_state["page"].

Importa le pagine (che NON importano il router → nessun ciclo). La sidebar e le
pagine usano ui.nav per cambiare pagina.
"""

import streamlit as st

from ui import nav, sidebar
from ui import dashboard, telemetry, console, setup_view

_RENDERERS = {
    "Dashboard": dashboard.render,
    "Engineer Console": console.render,
    "Telemetria": telemetry.render,
    "Setup": setup_view.render,
}


def render_app() -> None:
    st.session_state.setdefault("page", nav.DEFAULT_PAGE)
    sidebar.render_sidebar()
    page = nav.current_page()
    _RENDERERS.get(page, dashboard.render)()
