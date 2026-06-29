"""ui/flags.py — feature-flag centralizzati.

DEMO_MODE: quando attivo, la Engineer Console usa SEMPRE la risposta cache
pre-validata (nessuna dipendenza dalla rete) → la demo non può rompersi.
È anche il fallback automatico se la chiamata LLM fallisce.

Override a runtime via st.session_state["demo_mode"] (toggle nella console),
con default da variabile d'ambiente PITWALL_DEMO_MODE (default: ON).
"""

import os

import streamlit as st

# Default ON: priorità #1 = demo che non si rompe in diretta.
_ENV_DEFAULT = os.getenv("PITWALL_DEMO_MODE", "1").strip().lower() not in ("0", "false", "no", "off")


def demo_mode() -> bool:
    """True se la demo-mode è attiva (cache sempre, niente rete)."""
    return bool(st.session_state.get("demo_mode", _ENV_DEFAULT))


def set_demo_mode(value: bool) -> None:
    st.session_state["demo_mode"] = bool(value)
