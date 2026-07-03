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


def _smooth_path(coords) -> str:
    """Path 'd' morbido (Catmull-Rom → cubiche di Bézier) per una lista di punti.

    Con <3 punti degrada a segmenti retti. Rende le sparkline meno spigolose senza
    dipendenze esterne. Solo presentazione.
    """
    if len(coords) < 3:
        return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in coords)
    d = [f"M{coords[0][0]:.1f} {coords[0][1]:.1f}"]
    for i in range(len(coords) - 1):
        p0 = coords[i - 1] if i > 0 else coords[i]
        p1, p2 = coords[i], coords[i + 1]
        p3 = coords[i + 2] if i + 2 < len(coords) else p2
        c1x = p1[0] + (p2[0] - p0[0]) / 6.0
        c1y = p1[1] + (p2[1] - p0[1]) / 6.0
        c2x = p2[0] - (p3[0] - p1[0]) / 6.0
        c2y = p2[1] - (p3[1] - p1[1]) / 6.0
        d.append(f"C{c1x:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return " ".join(d)


def sparkline_svg(series, color: str, w: int = 200, h: int = 52, *,
                  limit=None, fill: bool = True, show_minmax: bool = True,
                  value_fmt: str = "{:.0f}") -> str:
    """Mini-grafico a linea arricchito (area sfumata, curva morbida, min/max, limite).

    Ritorna un frammento HTML (div posizionato con SVG + etichette in overlay): le
    etichette sono HTML, non <text> SVG, così NON si distorcono con
    preserveAspectRatio="none" (lo stretch orizzontale rovinerebbe il testo).
    `limit` disegna una linea tratteggiata ambra (solo se cade dentro il range dati).
    Solo presentazione.
    """
    pts = [float(v) for v in series if v is not None]
    if len(pts) < 2:
        return ""
    lo, hi = min(pts), max(pts)
    span = (hi - lo) or 1.0
    pad = 5.0
    n = len(pts)

    def X(i):
        return pad + (w - 2 * pad) * (i / (n - 1))

    def Y(v):
        return pad + (h - 2 * pad) * (1 - (v - lo) / span)

    coords = [(X(i), Y(v)) for i, v in enumerate(pts)]
    line_d = _smooth_path(coords)
    gid = f"pwg{abs(hash((tuple(pts), color))) % 999983}"

    svg = [f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true" '
           f'style="position:absolute;inset:0;width:100%;height:100%;">']
    if fill:
        area_d = (f'{line_d} L{coords[-1][0]:.1f} {h - pad:.1f} '
                  f'L{coords[0][0]:.1f} {h - pad:.1f} Z')
        svg.append(
            f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{color}" stop-opacity="0.28"/>'
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/>'
            f'</linearGradient></defs><path d="{area_d}" fill="url(#{gid})"/>'
        )
    show_limit = limit is not None and lo < float(limit) < hi
    if show_limit:
        ly = Y(float(limit))
        svg.append(f'<line x1="{pad:.1f}" y1="{ly:.1f}" x2="{w - pad:.1f}" y2="{ly:.1f}" '
                   f'stroke="{STATUS_WARN}" stroke-width="1" stroke-dasharray="4 3" opacity="0.75"/>')
    svg.append(f'<path d="{line_d}" fill="none" stroke="{color}" stroke-width="2" '
               f'stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/>')
    svg.append('</svg>')

    mono = "font-family:'JetBrains Mono',monospace;"
    # chip: sfondo scuro semitrasparente → le etichette restano leggibili sopra la linea.
    chip = "background:rgba(10,10,10,0.55);padding:0 2px;border-radius:2px;"
    lx_pct = (coords[-1][0] / w) * 100
    ly_pct = (coords[-1][1] / h) * 100
    ov = [f'<span style="position:absolute;left:{lx_pct:.1f}%;top:{ly_pct:.1f}%;'
          f'width:6px;height:6px;margin:-3px 0 0 -3px;border-radius:50%;background:{color};"></span>']
    if show_minmax:
        ov.append(f'<span style="position:absolute;left:2px;top:0;{mono}{chip}font-size:0.55rem;'
                  f'color:#888;">{value_fmt.format(hi)}</span>')
        ov.append(f'<span style="position:absolute;left:2px;bottom:0;{mono}{chip}font-size:0.55rem;'
                  f'color:#888;">{value_fmt.format(lo)}</span>')
    if show_limit:
        lim_pct = (Y(float(limit)) / h) * 100
        ov.append(f'<span style="position:absolute;right:2px;top:{lim_pct:.1f}%;{mono}{chip}'
                  f'font-size:0.52rem;color:{STATUS_WARN};margin-top:-0.75rem;">'
                  f'lim {value_fmt.format(float(limit))}</span>')
    return (f'<div style="position:relative;width:100%;height:{h}px;">'
            + "".join(svg) + "".join(ov) + '</div>')


def window_bar_svg(value: float, vmin: float, vmax: float, win_lo: float, win_hi: float,
                   color: str, w: int = 200, h: int = 42, *,
                   value_fmt: str = "{:.1f}", unit: str = "") -> str:
    """Barra orizzontale con finestra ottimale (verde), marker sul valore, e
    etichette in overlay HTML: valore sopra il marker + range finestra sotto la
    banda verde. Solo presentazione."""
    pad = 5.0
    span = (vmax - vmin) or 1.0
    bar_y = h * 0.62

    def X(v):
        return pad + (w - 2 * pad) * (_clamp((v - vmin) / span))

    x_lo, x_hi, x_val = X(win_lo), X(win_hi), X(value)
    svg = (
        f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true" '
        f'style="position:absolute;inset:0;width:100%;height:100%;">'
        f'<rect x="{pad:.1f}" y="{bar_y - 3:.1f}" width="{w - 2 * pad:.1f}" height="6" rx="3" fill="{BG_RAISED}"/>'
        f'<rect x="{x_lo:.1f}" y="{bar_y - 3:.1f}" width="{max(2, x_hi - x_lo):.1f}" height="6" rx="3" '
        f'fill="{STATUS_OK}" opacity="0.5"/>'
        f'<line x1="{x_val:.1f}" y1="{bar_y - 9:.1f}" x2="{x_val:.1f}" y2="{bar_y + 9:.1f}" '
        f'stroke="{color}" stroke-width="2.4" vector-effect="non-scaling-stroke"/>'
        f'</svg>'
    )
    mono = "font-family:'JetBrains Mono',monospace;"
    val_pct = (x_val / w) * 100
    win_pct = ((x_lo + x_hi) / 2 / w) * 100
    ov = (
        f'<span style="position:absolute;left:{val_pct:.1f}%;top:0;transform:translateX(-50%);'
        f'{mono}font-size:0.62rem;font-weight:600;color:{color};white-space:nowrap;">'
        f'{value_fmt.format(value)}{unit}</span>'
        f'<span style="position:absolute;left:{win_pct:.1f}%;bottom:0;transform:translateX(-50%);'
        f'{mono}font-size:0.5rem;color:{STATUS_OK};white-space:nowrap;">'
        f'{value_fmt.format(win_lo)}–{value_fmt.format(win_hi)}</span>'
    )
    return f'<div style="position:relative;width:100%;height:{h}px;">{svg}{ov}</div>'


def gigi_avatar_svg(size: int = 44) -> str:
    """Icona di Gigi: headset minimale a contorno (archetto + padiglioni + mic).

    Line-art, sfondo trasparente (nessuna tile/anello): interamente bianca (archetto,
    padiglioni, braccetto e capsula mic). Pensata per rendere bene a 44–50px su
    superfici scure. Stringa SVG inseribile inline.
    """
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Gigi" '
        f'fill="none" stroke="#FFFFFF" stroke-width="3" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        # archetto (headband) agganciato al top dei padiglioni
        f'<path d="M13 29 C13 11 51 11 51 29"/>'
        # padiglioni (capsule a contorno)
        f'<rect x="7.5" y="29" width="11" height="18" rx="5.5"/>'
        f'<rect x="45.5" y="29" width="11" height="18" rx="5.5"/>'
        # braccetto microfono + capsula (tutto bianco)
        f'<path d="M51 47 C51 56 43 59 34 59"/>'
        f'<circle cx="33.5" cy="59" r="2.8" fill="#FFFFFF" stroke="none"/>'
        f'</svg>'
    )
