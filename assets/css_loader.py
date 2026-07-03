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
_APP_CSS = _ASSETS / "app.css"

# (family, weight, file) — i pesi effettivamente usati
_FONTS = [
    ("Orbitron", 700, "orbitron-700.woff2"),
    ("Inter", 400, "inter-400.woff2"),
    ("Inter", 500, "inter-500.woff2"),
    ("Inter", 600, "inter-600.woff2"),
    ("JetBrains Mono", 400, "jetbrainsmono-400.woff2"),
    ("JetBrains Mono", 500, "jetbrainsmono-500.woff2"),
]


@functools.lru_cache(maxsize=4)
def _base_style_cached(_mtime: float) -> str:
    """Font self-hosted (base64) + token del design system.

    Cache keyed sull'mtime di design_system.css: se il file cambia, l'mtime cambia
    e viene riletto (niente più CSS stantio servito da cache-a-vita-processo).
    """
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

    return "".join(faces) + css


def _base_style() -> str:
    return _base_style_cached(_DESIGN_SYSTEM.stat().st_mtime)


@functools.lru_cache(maxsize=8)
def font_faces_css(*families: str) -> str:
    """@font-face base64 per le sole famiglie richieste.

    Pensato per gli iframe di st.components.v1.html(): un iframe è un documento
    isolato, non eredita né i token né i font del parent, quindi va reso
    autosufficiente. Embeddando i woff2 in base64 si evita il <link> a Google
    Fonts (niente fetch a runtime, niente flash, affidabile su Cloud).
    """
    wanted = set(families) or {f[0] for f in _FONTS}
    faces = []
    for family, weight, filename in _FONTS:
        if family not in wanted:
            continue
        data = (_FONTS_DIR / filename).read_bytes()
        b64 = base64.b64encode(data).decode("ascii")
        faces.append(
            f"@font-face{{font-family:'{family}';font-style:normal;"
            f"font-weight:{weight};font-display:swap;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "".join(faces)


@functools.lru_cache(maxsize=4)
def _app_style_cached(_mtime: float) -> str:
    """Stile principale dell'app (estratto da app.py in Lotto 2).

    Cache keyed sull'mtime di app.css: modificando il CSS basta un rerun/refresh
    per vederlo aggiornato, senza riavviare il server (Streamlit non sorveglia i .css).
    """
    return _APP_CSS.read_text(encoding="utf-8")


def _app_style() -> str:
    return _app_style_cached(_APP_CSS.stat().st_mtime) if _APP_CSS.exists() else ""


def inject_design_system(include_app_css: bool = True) -> None:
    """Inietta font self-hosted + token + tema dark. Da chiamare una volta per pagina.

    include_app_css: True per l'app principale; False per pagine leggere (es. login)
    che vogliono solo font+token senza gli stili dei componenti dell'app.
    """
    style = _base_style() + (_app_style() if include_app_css else "")
    st.markdown("<style>" + style + "</style>", unsafe_allow_html=True)
    st.markdown(
        "<script>document.documentElement.setAttribute('data-theme','dark');</script>",
        unsafe_allow_html=True,
    )
