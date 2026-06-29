"""ui/nav.py — navigazione tra pagine via st.session_state.

Modulo SENZA dipendenze dalle pagine (per evitare import circolari):
sidebar e pagine importano questo, il router importa le pagine.
"""

import streamlit as st

# Ordine = ordine di visualizzazione nella sidebar.
PAGES = ["Dashboard", "Engineer Console", "Telemetria", "Setup"]

# Icona per ogni voce (resa inline nei bottoni nav).
PAGE_ICONS = {
    "Dashboard": "▦",
    "Engineer Console": "🎧",
    "Telemetria": "📈",
    "Setup": "🔧",
}

DEFAULT_PAGE = "Dashboard"


def current_page() -> str:
    return st.session_state.get("page", DEFAULT_PAGE)


def go_to(page: str) -> None:
    """Imposta la pagina attiva e forza un rerun pulito."""
    if page not in PAGES:
        page = DEFAULT_PAGE
    st.session_state["page"] = page
    st.rerun()
