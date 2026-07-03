"""ui/telemetry.py — pagina Telemetria (cuore visivo della demo).

Tre visualizzazioni, tutte alimentate da ui/demo_data.py (sorgente unica):
  1. Line chart Plotly  — temperatura 4 gomme su 8 giri + limite finestra 95°C;
  2. 4 gauge Plotly     — pressioni a CALDO, finestra 28.5–30.0 psi;
  3. Heatmap SVG        — schema auto vista dall'alto (components.html, inline).

COERENZA pressioni (vedi SPEC_ERRATA.md): i gauge mostrano le pressioni a CALDO
(display in pista), distinte da quelle a FREDDO del CSV/garage. Nessuna
trasformazione viene applicata qui: i valori a caldo sono dati demo dedicati.
"""

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

from ui import components as c
from ui import demo_data as dd
from ui import console  # riuso della diagnosi di Gigi nel feed cross-check (no LLM)


# ─────────────────────────────────────────────
# HELPER — unità (°C/°F) e smoothing (media mobile leggera)
# ─────────────────────────────────────────────
def _to_unit(v: float, unit: str) -> float:
    """Converte una temperatura in °C a °F se richiesto; altrimenti invariata."""
    return round(v * 9 / 5 + 32, 1) if unit == "F" else v


def _smooth_series(vals):
    """Media mobile a 3 punti (bordi inclusi): leviga la curva senza spostare i picchi troppo."""
    out = []
    for i in range(len(vals)):
        lo, hi = max(0, i - 1), min(len(vals), i + 2)
        out.append(round(sum(vals[lo:hi]) / (hi - lo), 1))
    return out

# Ordine canonico gomme + etichette legenda + colore linea (solo colori consentiti).
_SERIES = [
    ("fl", "Ant.SX", "#3B82F6"),   # blu
    ("fr", "Ant.DX", c.STATUS_OK),  # verde
    ("rl", "Post.SX", c.STATUS_WARN),  # ambra
    ("rr", "Post.DX", c.ACCENT),    # rosso brand — gomma critica
]


# ─────────────────────────────────────────────
# 1) LINE CHART — temperatura gomme · 8 giri
# ─────────────────────────────────────────────
def _temp_line_fig(unit: str = "C", smoothed: bool = False) -> go.Figure:
    laps = dd.lap_axis()
    fig = go.Figure()
    for pos, label, color in _SERIES:
        y = dd.TYRE_TEMP_SERIES[pos]
        if smoothed:
            y = _smooth_series(y)
        y = [_to_unit(v, unit) for v in y]
        fig.add_trace(go.Scatter(
            x=laps, y=y,
            mode="lines+markers", name=label,
            line=dict(color=color, width=2.4),
            marker=dict(size=5),
            hovertemplate=f"{label}: %{{y:.0f}}°{unit}<extra></extra>",
        ))
    # Limite finestra (tratteggiata) — anche in legenda. Convertito nell'unità scelta.
    limit = _to_unit(dd.TEMP_LIMIT, unit)
    fig.add_trace(go.Scatter(
        x=laps, y=[limit] * len(laps),
        mode="lines", name="Limite finestra",
        line=dict(color=c.TEXT_SECONDARY, width=1.6, dash="dash"),
        hoverinfo="skip",
    ))
    fig.update_layout(
        # Titolo NON in figura: reso come markdown sopra il grafico (vedi render()).
        # Così la legenda torna in alto senza sovrapporsi al titolo e l'asse "Giro"
        # resta libero in basso (niente più legenda a ridosso di "Giro").
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=c.TEXT_SECONDARY, size=11),
        # Top ridotto (niente legenda in alto) + bottom ampliato per ospitare
        # asse "Giro" e legenda su righe separate.
        margin=dict(l=46, r=20, t=16, b=88), height=410,
        hovermode="x unified",
        # Legenda SOTTO il grafico: il box tooltip "x unified" viene ancorato in alto,
        # vicino ai punti; tenendo la legenda sotto l'asse i due non si sovrappongono
        # mai (fix bug overlap tooltip/legenda). L'asse "Giro" resta comunque leggibile
        # grazie al title_standoff che lo distanzia dalla legenda.
        legend=dict(orientation="h", yanchor="top", y=-0.20, xanchor="center", x=0.5,
                    font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(title_text="Giro", title_standoff=6, gridcolor=c.BORDER,
                     zeroline=False, color=c.TEXT_MUTED, linecolor=c.BORDER, dtick=1)
    # Unità come SUFFISSO dei tick dell'asse Y ("88°C", "95°C"…): orizzontale, non può
    # sovrapporsi (niente più titolo asse ruotato né etichetta flottante). Suffisso
    # "°C"/"°F" completo per uniformità con annotazione soglia e tooltip.
    fig.update_yaxes(ticksuffix=f"°{unit}", title_text="", gridcolor=c.BORDER, zeroline=False,
                     color=c.TEXT_MUTED, linecolor=c.BORDER,
                     range=[_to_unit(74, unit), _to_unit(110, unit)])
    # Annotazione sul limite finestra (nell'unità scelta).
    fig.add_annotation(x=laps[0], y=limit, text=f"{limit:.0f}°{unit}",
                       showarrow=False, yshift=10, xshift=4,
                       font=dict(family="JetBrains Mono, monospace", size=9, color=c.TEXT_SECONDARY))
    return fig


# ─────────────────────────────────────────────
# 2) GAUGE PRESSIONI (a caldo) — finestra 28.5–30.0 psi
# ─────────────────────────────────────────────
def _pressure_gauge_fig(value: float, in_window: bool) -> go.Figure:
    color = c.STATUS_OK if in_window else c.STATUS_ERROR
    lo, hi = dd.HOT_PRESS_WINDOW
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"font": {"family": "JetBrains Mono, monospace", "size": 24, "color": color},
                "suffix": " psi", "valueformat": ".1f"},
        gauge={
            "axis": {"range": [27.0, 30.5], "tickwidth": 1, "tickcolor": c.BORDER_STRONG,
                     "tickfont": {"size": 8, "color": c.TEXT_MUTED}, "dtick": 0.5},
            "bar": {"color": color, "thickness": 0.30},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [{"range": [lo, hi], "color": "rgba(0,200,83,0.20)"}],
            "threshold": {"line": {"color": "#FFFFFF", "width": 2}, "thickness": 0.8, "value": value},
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=180,
                      margin=dict(l=18, r=18, t=18, b=6),
                      font=dict(color=c.TEXT_SECONDARY))
    return fig


# ─────────────────────────────────────────────
# 3) HEATMAP — schema auto vista dall'alto (SVG inline, components.html)
# ─────────────────────────────────────────────
# Geometria della scocca — DEVE combaciare col <path> della silhouette in
# _heatmap_html(). I 4 riquadri-gomma sono ancorati a QUESTI punti (fianchi dritti
# + linee-assali), non a coordinate slegate: così i valori restano attaccati alle
# ruote della sagoma anche se il layout cambia (fix disallineamento heatmap).
_BODY_LEFT_X, _BODY_RIGHT_X = 78, 162     # fianchi dritti della scocca
_FRONT_AXLE_Y, _REAR_AXLE_Y = 96, 230     # assale anteriore / posteriore (curve del path)
_WHEEL_W, _WHEEL_H = 40, 74               # dimensioni del riquadro-gomma


def _heat_corner_svg(cx: int, cy: int, pos: str) -> str:
    """Riquadro-gomma + valore centrati sul punto-ruota (cx, cy) della sagoma."""
    val = dd.TYRE_TEMP_MAX[pos]
    fill = c.temp_to_color(val, dd.TEMP_SCALE)
    label = dd.TYRE_LABELS[pos]
    x = cx - _WHEEL_W // 2
    y = cy - _WHEEL_H // 2
    return (
        f'<g>'
        f'<rect x="{x}" y="{y}" width="{_WHEEL_W}" height="{_WHEEL_H}" rx="12" fill="{fill}" '
        f'stroke="#000000" stroke-opacity="0.35" stroke-width="1"/>'
        f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" '
        f'font-family="JetBrains Mono, monospace" font-size="14" font-weight="700" '
        f'fill="#FFFFFF">{val}°</text>'
        f'<text x="{cx}" y="{cy + 20}" text-anchor="middle" '
        f'font-family="JetBrains Mono, monospace" font-size="8" '
        f'fill="#FFFFFF" opacity="0.85">{label}</text>'
        f'</g>'
    )


def _heatmap_html() -> str:
    fonts = c.iframe_fonts("JetBrains Mono", "Inter", "Orbitron")
    lo, hi = dd.TEMP_SCALE
    # Centri-ruota derivati dalla geometria della scocca: le ruote sinistre/destre
    # affiancano i fianchi dritti (BODY_LEFT/RIGHT), quelle ant./post. si allineano
    # alle linee-assali (FRONT/REAR_AXLE_Y) del <path>. Nessuna coordinata slegata.
    lx = _BODY_LEFT_X - _WHEEL_W // 2      # centro-X ruote sinistre
    rx = _BODY_RIGHT_X + _WHEEL_W // 2     # centro-X ruote destre
    corners = (
        _heat_corner_svg(lx, _FRONT_AXLE_Y, "fl")
        + _heat_corner_svg(rx, _FRONT_AXLE_Y, "fr")
        + _heat_corner_svg(lx, _REAR_AXLE_Y, "rl")
        + _heat_corner_svg(rx, _REAR_AXLE_Y, "rr")
    )
    grad_lo = c.temp_to_color(lo, dd.TEMP_SCALE)
    grad_hi = c.temp_to_color(hi, dd.TEMP_SCALE)
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{fonts}
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{height:100%;}}
body{{background:transparent;font-family:'Inter',sans-serif;}}
/* Il contenitore RIEMPIE l'iframe (height:100%) invece di un'altezza fissa che
   poteva eccederlo → niente clipping/scroll al primo render. */
.wrap{{background:{c.BG_INSET};border:1px solid {c.BORDER};border-radius:10px;
       padding:14px 16px;height:100%;display:flex;flex-direction:column;}}
.t{{font-family:'JetBrains Mono',monospace;font-size:0.72rem;letter-spacing:0.14em;
    text-transform:uppercase;color:{c.TEXT_SECONDARY};margin-bottom:6px;}}
.svgbox{{flex:1;display:flex;align-items:center;justify-content:center;min-height:0;}}
.legend{{display:flex;align-items:center;gap:8px;margin-top:10px;}}
.legend .bar{{flex:1;height:8px;border-radius:4px;
   background:linear-gradient(90deg,{grad_lo} 0%,{grad_hi} 100%);}}
.legend .end{{font-family:'JetBrains Mono',monospace;font-size:9px;color:{c.TEXT_MUTED};}}
svg{{display:block;margin:0 auto;}}
</style></head><body>
<div class="wrap">
  <div class="t">Heatmap gomme · max stint</div>
  <div class="svgbox">
  <svg viewBox="0 0 240 290" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
    <!-- scocca auto -->
    <path d="M120 24 C150 24 162 50 162 96 L162 230 C162 256 146 268 120 268
             C94 268 78 256 78 230 L78 96 C78 50 90 24 120 24 Z"
          fill="#161616" stroke="{c.BORDER_STRONG}" stroke-width="2"/>
    <!-- abitacolo / parabrezza -->
    <path d="M98 118 L142 118 L134 150 L106 150 Z" fill="#0e0e0e" stroke="{c.BORDER}" stroke-width="1"/>
    <rect x="104" y="158" width="32" height="46" rx="6" fill="#0e0e0e" stroke="{c.BORDER}" stroke-width="1"/>
    {corners}
  </svg>
  </div>
  <div class="legend">
    <span class="end">{lo}°</span>
    <span class="bar"></span>
    <span class="end">{hi}°</span>
  </div>
</div></body></html>"""


# ─────────────────────────────────────────────
# 4) TABELLA GIRO-PER-GIRO (numeri grezzi, ordinabile)
# ─────────────────────────────────────────────
def _laps_table_df() -> pd.DataFrame:
    """DataFrame lap · consumo · 4 temperature · 4 pressioni a caldo (sorgente: demo_data)."""
    data = {"Giro": dd.lap_axis(), "Consumo (L)": dd.FUEL_PER_LAP}
    for pos, label, _ in _SERIES:
        data[f"Temp {label} (°C)"] = dd.TYRE_TEMP_SERIES[pos]
    for pos, label, _ in _SERIES:
        data[f"Press {label} (psi)"] = dd.HOT_PRESS_SERIES[pos]
    return pd.DataFrame(data)


# ─────────────────────────────────────────────
# 5) PROIEZIONE GIRI RIMANENTI (sola lettura — FUORI dalla logica fuel protetta)
# ─────────────────────────────────────────────
def project_remaining_laps(fuel_residual: float, avg_per_lap: float) -> float:
    """Stima giri percorribili = carburante residuo / consumo medio. Sola lettura,
    indipendente dalla strategia carburante protetta (nessun import di quella logica)."""
    if avg_per_lap <= 0:
        return 0.0
    return round(fuel_residual / avg_per_lap, 1)


# ─────────────────────────────────────────────
# 6) FEED INCONGRUENZE / CROSS-CHECK (deterministico + riuso diagnosi Gigi, no LLM)
# ─────────────────────────────────────────────
def _cross_check_items():
    """Incongruenze rilevate dal cross-check dei dati demo (temperature vs limite,
    pressioni a caldo vs finestra, stabilità consumo). Ritorna [(livello, testo)]."""
    items = []
    for pos, label, _ in _SERIES:
        mx = dd.TYRE_TEMP_MAX[pos]
        if mx > dd.TEMP_LIMIT:
            items.append(("crit", f"{label}: {mx}°C oltre il limite finestra ({dd.TEMP_LIMIT}°C)"))
    lo, hi = dd.HOT_PRESS_WINDOW
    for pos, label, _ in _SERIES:
        v = dd.HOT_PRESSURES[pos]
        if v < lo:
            items.append(("warn", f"{label}: {v} psi sotto la finestra a caldo ({lo}–{hi} psi)"))
        elif v > hi:
            items.append(("warn", f"{label}: {v} psi oltre la finestra a caldo ({lo}–{hi} psi)"))
    spread = max(dd.FUEL_PER_LAP) - min(dd.FUEL_PER_LAP)
    if spread <= 0.4:
        items.append(("ok", f"Consumo stabile (variazione {spread:.1f} L/giro su {dd.SESSION['laps']} giri)"))
    if not items:
        items.append(("ok", "Nessuna incongruenza rilevata"))
    return items


def _gigi_diagnosi_summary() -> str:
    """Riusa la diagnosi già generata da Gigi (session_state) senza richiamare l'LLM;
    fallback allo scenario demo di default se la Console non è ancora stata usata."""
    text = st.session_state.get("console_response", console.DEMO_RESPONSE)
    for title, _icon, body in console.parse_sections(text):
        if title == "Diagnosi":
            return body
    return ""


# ─────────────────────────────────────────────
# RENDER PAGINA
# ─────────────────────────────────────────────
def render() -> None:
    st.markdown(
        c.page_header("Telemetria", "Monza · BMW M4 GT3 · 8 giri · stint asciutto"),
        unsafe_allow_html=True,
    )

    # Riga 1: line chart (2/3) + heatmap (1/3)
    col_line, col_heat = st.columns([2, 1], gap="medium")
    with col_line:
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.8rem;'
            'letter-spacing:0.05em;color:#FFFFFF;margin:2px 0 0 4px;">'
            'Temperatura gomme · 8 giri</div>',
            unsafe_allow_html=True,
        )
        # Toggle di visualizzazione (solo presentazione: non toccano i dati).
        t_unit, t_smooth, _sp = st.columns([1.1, 1.3, 3])
        with t_unit:
            unit = "F" if st.toggle("°F", value=False, key="tele_unit_f",
                                    help="Mostra le temperature in Fahrenheit") else "C"
        with t_smooth:
            smoothed = st.toggle("Smoothed", value=False, key="tele_smooth",
                                 help="Curva lisciata (media mobile a 3 giri)")
        st.plotly_chart(_temp_line_fig(unit, smoothed), use_container_width=True,
                        config={"displayModeBar": False})
    with col_heat:
        components.html(_heatmap_html(), height=410, scrolling=False)

    # Riga 2: gauge pressioni a caldo
    st.markdown(
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;'
        'letter-spacing:0.14em;text-transform:uppercase;color:#999;margin:6px 0 2px 0;">'
        'Pressioni gomme · a caldo (display)</div>'
        '<div style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#666;'
        'margin-bottom:10px;">Finestra ottimale 28.5–30.0 psi · valori a freddo (garage) '
        'distinti, vedi CSV</div>',
        unsafe_allow_html=True,
    )
    lo, hi = dd.HOT_PRESS_WINDOW
    cols = st.columns(4, gap="small")
    for col, (pos, label, _) in zip(cols, _SERIES):
        value = dd.HOT_PRESSURES[pos]
        in_window = lo <= value <= hi
        with col:
            st.markdown(
                f'<div style="text-align:center;font-family:\'JetBrains Mono\',monospace;'
                f'font-size:0.7rem;letter-spacing:0.1em;color:#999;text-transform:uppercase;">'
                f'{label}</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(_pressure_gauge_fig(value, in_window), use_container_width=True,
                            config={"displayModeBar": False})
            badge = (
                '<div style="text-align:center;font-family:\'JetBrains Mono\',monospace;'
                'font-size:0.62rem;letter-spacing:0.12em;color:#00C853;text-transform:uppercase;">'
                '● IN FINESTRA</div>'
                if in_window else
                '<div style="text-align:center;font-family:\'JetBrains Mono\',monospace;'
                'font-size:0.62rem;letter-spacing:0.12em;color:#E8002D;text-transform:uppercase;">'
                '▼ BASSA</div>'
            )
            st.markdown(badge, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # Riga 3 — Tabella giro-per-giro (numeri grezzi, ordinabile)
    # ─────────────────────────────────────────────
    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
    with st.expander("📊  Dati giro-per-giro · tabella ordinabile", expanded=False):
        st.dataframe(_laps_table_df(), use_container_width=True, hide_index=True)
        st.caption("Clicca l'intestazione di una colonna per ordinare. Pressioni a caldo: "
                   "l'ultimo giro coincide con i valori dei gauge qui sopra.")

    # ─────────────────────────────────────────────
    # Riga 4 — Proiezione giri rimanenti (sola lettura)
    # ─────────────────────────────────────────────
    st.markdown(
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;'
        'letter-spacing:0.14em;text-transform:uppercase;color:#999;margin:18px 0 2px 0;">'
        'Proiezione giri rimanenti</div>'
        '<div style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#666;'
        'margin-bottom:10px;">Stima di sola lettura · indipendente dalla logica strategia '
        'carburante</div>',
        unsafe_allow_html=True,
    )
    avg = round(sum(dd.FUEL_PER_LAP) / len(dd.FUEL_PER_LAP), 2)
    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        residual = st.number_input("Carburante residuo (L)", min_value=0.0, max_value=200.0,
                                   value=20.0, step=0.5, key="tele_fuel_residual")
    with pc2:
        st.metric("Consumo medio", f"{avg} L/giro")
    with pc3:
        st.metric("Giri rimanenti (stima)", f"{project_remaining_laps(residual, avg):.1f}")

    # ─────────────────────────────────────────────
    # Riga 5 — Feed incongruenze / cross-check (riuso diagnosi Gigi, no LLM)
    # ─────────────────────────────────────────────
    with st.expander("⚠  Cross-check dati & sintesi Gigi", expanded=False):
        _dot = {"crit": c.STATUS_ERROR, "warn": c.STATUS_WARN, "ok": c.STATUS_OK}
        rows = "".join(
            f'<div style="display:flex;align-items:center;gap:9px;padding:4px 0;'
            f'font-family:\'Inter\',sans-serif;font-size:0.82rem;color:#CCCCCC;">'
            f'<span style="width:8px;height:8px;border-radius:50%;background:{_dot[lvl]};'
            f'flex:0 0 auto;"></span>{msg}</div>'
            for lvl, msg in _cross_check_items()
        )
        st.markdown(rows, unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.62rem;'
            'letter-spacing:0.12em;text-transform:uppercase;color:#666;margin:12px 0 4px;">'
            'Sintesi diagnosi Gigi (riuso, nessuna nuova chiamata)</div>',
            unsafe_allow_html=True,
        )
        st.markdown(_gigi_diagnosi_summary() or "—")
