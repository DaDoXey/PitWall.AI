"""Caricamento centralizzato del design system PitWall.AI.

Inietta UNA sola volta:
  - i font self-hosted (woff2) come @font-face base64 → nessuna chiamata a
    Google Fonts a runtime (niente flash/latenza), affidabile su Streamlit Cloud;
  - i token del design system (assets/design_system.css);
  - l'attributo data-theme="dark" sul documento.

Streamlit non serve i file in assets/ come static affidabili in deploy, quindi
i woff2 vengono embeddati in base64: l'unico approccio che regge su Cloud.
"""

import base64
import functools
from pathlib import Path

import streamlit as st

_ASSETS = Path(__file__).parent
_FONTS_DIR = _ASSETS / "fonts"
_DESIGN_SYSTEM = _ASSETS / "design_system.css"

# (family, weight, file) — i pesi effettivamente usati
_FONTS = [
    ("Orbitron", 700, "orbitron-700.woff2"),
    ("Inter", 400, "inter-400.woff2"),
    ("Inter", 500, "inter-500.woff2"),
    ("Inter", 600, "inter-600.woff2"),
    ("JetBrains Mono", 400, "jetbrainsmono-400.woff2"),
    ("JetBrains Mono", 500, "jetbrainsmono-500.woff2"),
]


@functools.lru_cache(maxsize=1)
def _build_style() -> str:
    """Costruisce il blocco <style> completo (font base64 + token). Cache: 1 lettura."""
    faces = []
    for family, weight, filename in _FONTS:
        data = (_FONTS_DIR / filename).read_bytes()
        b64 = base64.b64encode(data).decode("ascii")
        faces.append(
            f"@font-face{{font-family:'{family}';font-style:normal;"
            f"font-weight:{weight};font-display:swap;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )

    css = _DESIGN_SYSTEM.read_text(encoding="utf-8")
    # Scarta i @font-face url()-based del file (non risolvibili via injection):
    # usiamo solo i token dal marcatore in poi.
    marker = "/* ===== TOKENS_START ====="
    if marker in css:
        css = css[css.index(marker):]

    return "<style>" + "".join(faces) + css + "</style>"


def inject_design_system() -> None:
    """Inietta font self-hosted + token + tema dark. Da chiamare una volta all'avvio."""
    st.markdown(_build_style(), unsafe_allow_html=True)
    st.markdown(
        "<script>document.documentElement.setAttribute('data-theme','dark');</script>",
        unsafe_allow_html=True,
    )
