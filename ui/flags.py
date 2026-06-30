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


# ─────────────────────────────────────────────
# INPUT SESSIONE (Fase 7): selettori auto/pista + upload CSV/screenshot.
# Default OFF: la demo resta pulita (niente controlli funzionali a video).
# Attivabile a runtime (toggle in Setup) o via env PITWALL_SHOW_INPUTS.
# ─────────────────────────────────────────────
_INPUTS_ENV_DEFAULT = os.getenv("PITWALL_SHOW_INPUTS", "0").strip().lower() in ("1", "true", "yes", "on")


def inputs_enabled() -> bool:
    """True se i controlli di input sessione (selettori/upload) sono attivi."""
    return bool(st.session_state.get("inputs_enabled", _INPUTS_ENV_DEFAULT))


def set_inputs_enabled(value: bool) -> None:
    st.session_state["inputs_enabled"] = bool(value)


# ─────────────────────────────────────────────
# SCREENSHOT SETUP (vision, Fase 2.3): lettura automatica del setup da immagine.
# Non pronta per la demo → stub "Prossimamente". Funzione reale dietro flag,
# OFF di default; attivabile via env FEATURE_SCREENSHOT.
# ─────────────────────────────────────────────
_FEATURE_SCREENSHOT_DEFAULT = os.getenv("FEATURE_SCREENSHOT", "0").strip().lower() in ("1", "true", "yes", "on")


def feature_screenshot() -> bool:
    """True se la lettura setup da screenshot è abilitata (default False = stub)."""
    return bool(st.session_state.get("feature_screenshot", _FEATURE_SCREENSHOT_DEFAULT))
