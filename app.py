"""
app.py — PitWall.AI · shell + router (restyle UI/UX)

Entry point Streamlit. Responsabilità:
  - gate di autenticazione (invariato rispetto al monolite precedente);
  - iniezione del design system (font self-hosted + token + tema dark);
  - dispatch delle pagine (Dashboard · Engineer Console · Telemetria · Setup)
    via st.session_state, gestito da ui/router.py.

Il monolite precedente è preservato VERBATIM in app_legacy.py (logica fuel/gauge,
upload CSV, setup tabs, storico): nessuna logica protetta è stata riscritta, solo
riorganizzata la presentazione attorno ad essa.
"""

import streamlit as st
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# CONFIGURAZIONE
# ─────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="PitWall.AI",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Design system — font self-hosted (base64) + token + tema dark (una sola volta).
from assets.css_loader import inject_design_system
inject_design_system()

# ─────────────────────────────────────────────
# GATE AUTENTICAZIONE (invariato)
# ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.switch_page("pages/login.py")
    st.stop()

# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
from ui.router import render_app

render_app()
