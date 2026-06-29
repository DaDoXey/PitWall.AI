"""ui/components.py — builder condivisi per i componenti custom (SVG/HTML inline).

Regole di rendering (vincoli Streamlit Cloud):
  - componenti custom → st.components.v1.html() con stili INLINE e font base64;
  - nessun selettore CSS wildcard (*), nessun selettore interno di Streamlit.
Qui vivono: token colore (hex letterali), helper colore heatmap, avatar Gigi,
e un wrapper per iniettare i @font-face base64 dentro gli iframe isolati.
"""

from assets.css_loader import font_faces_css

# ─────────────────────────────────────────────
# TOKEN COLORE (hex letterali — gli iframe non leggono le CSS var del parent)
# Allineati a assets/design_system.css. SOLO questi colori.
# ─────────────────────────────────────────────
BG_BASE = "#0a0a0a"
BG_SURFACE = "#111111"
BG_RAISED = "#1a1a1a"
BG_INSET = "#141414"
ACCENT = "#E8002D"
ACCENT_HOVER = "#CC0028"
STATUS_OK = "#00C853"
STATUS_WARN = "#FFB300"
STATUS_ERROR = "#E8002D"
BORDER = "#222222"
BORDER_STRONG = "#333333"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#999999"
TEXT_MUTED = "#666666"

FONT_DISPLAY = "'Orbitron', sans-serif"
FONT_BODY = "'Inter', sans-serif"
FONT_MONO = "'JetBrains Mono', monospace"


def iframe_fonts(*families: str) -> str:
    """@font-face base64 per gli iframe di components.html (documenti isolati)."""
    return font_faces_css(*families)


# ─────────────────────────────────────────────
# COLORE TEMPERATURA — gradiente blu → rosso su una scala [lo, hi]
# ─────────────────────────────────────────────
_COLD_RGB = (59, 130, 246)   # blu (#3B82F6) — colore consentito (non vietato)
_HOT_RGB = (232, 0, 45)      # rosso brand (#E8002D)


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def temp_to_color(value: float, scale=(80, 105)) -> str:
    """Mappa una temperatura sulla rampa blu→rosso. Ritorna un hex #RRGGBB."""
    lo, hi = scale
    t = _clamp((value - lo) / (hi - lo)) if hi > lo else 0.0
    r = round(_COLD_RGB[0] + (_HOT_RGB[0] - _COLD_RGB[0]) * t)
    g = round(_COLD_RGB[1] + (_HOT_RGB[1] - _COLD_RGB[1]) * t)
    b = round(_COLD_RGB[2] + (_HOT_RGB[2] - _COLD_RGB[2]) * t)
    return f"#{r:02X}{g:02X}{b:02X}"


# ─────────────────────────────────────────────
# AVATAR GIGI — silhouette casco/ingegnere, minimale (SVG inline)
# ─────────────────────────────────────────────
def page_header(title: str, subtitle: str = "") -> str:
    """Intestazione di pagina (titolo Orbitron + sottotitolo mono). HTML inline."""
    sub = (
        f'<div style="font-family:{FONT_MONO};font-size:0.7rem;letter-spacing:0.14em;'
        f'color:{TEXT_MUTED};text-transform:uppercase;margin-top:4px;">{subtitle}</div>'
        if subtitle else ""
    )
    return (
        '<div style="margin:0.2rem 0 1.2rem 0;border-left:4px solid '
        f'{ACCENT};padding-left:0.9rem;">'
        f'<div style="font-family:{FONT_DISPLAY};font-size:1.4rem;font-weight:700;'
        f'letter-spacing:0.04em;color:{TEXT_PRIMARY};line-height:1.1;">{title}</div>'
        f'{sub}</div>'
    )


def placeholder_panel(message: str) -> str:
    """Pannello vuoto per pagine non ancora implementate (Fase 1)."""
    return (
        f'<div style="background:{BG_SURFACE};border:1px dashed {BORDER_STRONG};'
        'border-radius:10px;padding:48px 24px;text-align:center;">'
        f'<div style="font-family:{FONT_MONO};font-size:0.8rem;letter-spacing:0.12em;'
        f'color:{TEXT_MUTED};text-transform:uppercase;">{message}</div></div>'
    )


def sparkline_svg(series, color: str, w: int = 200, h: int = 46) -> str:
    """Mini-grafico a linea (SVG inline) da una serie numerica. Solo presentazione."""
    pts = [float(v) for v in series if v is not None]
    if len(pts) < 2:
        return ""
    lo, hi = min(pts), max(pts)
    span = (hi - lo) or 1.0
    pad = 4.0
    n = len(pts)
    coords = []
    for i, v in enumerate(pts):
        x = pad + (w - 2 * pad) * (i / (n - 1))
        y = pad + (h - 2 * pad) * (1 - (v - lo) / span)
        coords.append((x, y))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    lx, ly = coords[-1]
    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" '
        f'preserveAspectRatio="none" aria-hidden="true">'
        f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="2.6" fill="{color}"/></svg>'
    )


def window_bar_svg(value: float, vmin: float, vmax: float, win_lo: float, win_hi: float,
                   color: str, w: int = 200, h: int = 30) -> str:
    """Barra orizzontale con finestra ottimale (verde) e marker sul valore."""
    pad = 4.0
    span = (vmax - vmin) or 1.0

    def x(v):
        return pad + (w - 2 * pad) * (_clamp((v - vmin) / span))

    x_lo, x_hi, x_val = x(win_lo), x(win_hi), x(value)
    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" preserveAspectRatio="none">'
        f'<rect x="{pad}" y="{h/2-3:.0f}" width="{w-2*pad:.0f}" height="6" rx="3" fill="{BG_RAISED}"/>'
        f'<rect x="{x_lo:.1f}" y="{h/2-3:.0f}" width="{max(2,x_hi-x_lo):.1f}" height="6" rx="3" '
        f'fill="{STATUS_OK}" opacity="0.45"/>'
        f'<line x1="{x_val:.1f}" y1="3" x2="{x_val:.1f}" y2="{h-3}" stroke="{color}" stroke-width="2.4"/>'
        f'<circle cx="{x_val:.1f}" cy="{h/2:.0f}" r="3.4" fill="{color}"/></svg>'
    )


def gigi_avatar_svg(size: int = 44) -> str:
    """SVG dell'avatar di Gigi (casco con cuffie). Stringa inseribile inline."""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Gigi">'
        f'<rect x="1.5" y="1.5" width="61" height="61" rx="16" fill="#0a0a0a" '
        f'stroke="#222222" stroke-width="1.5"/>'
        f'<circle cx="32" cy="32" r="25" fill="none" stroke="#E8002D" '
        f'stroke-width="1.5" opacity="0.45"/>'
        f'<path d="M16 51c0-9 7.2-14.5 16-14.5S48 42 48 51z" fill="#FFFFFF"/>'
        f'<circle cx="32" cy="26" r="9.5" fill="#FFFFFF"/>'
        f'<path d="M20.5 26a11.5 11.5 0 0 1 23 0" fill="none" stroke="#FFFFFF" '
        f'stroke-width="2.6" stroke-linecap="round"/>'
        f'<rect x="18" y="24" width="4.6" height="7.5" rx="2.3" fill="#E8002D"/>'
        f'<rect x="41.4" y="24" width="4.6" height="7.5" rx="2.3" fill="#E8002D"/>'
        f'<path d="M20.3 30c-2.4 3.4-2.4 6.6-.4 9.4" fill="none" stroke="#E8002D" '
        f'stroke-width="2.2" stroke-linecap="round"/>'
        f'<circle cx="20" cy="40" r="2.3" fill="#E8002D"/>'
        f'</svg>'
    )
