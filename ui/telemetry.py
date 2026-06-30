"""ui/telemetry.py — pagina Telemetria (cuore visivo della demo).

Tre visualizzazioni, tutte alimentate da ui/demo_data.py (sorgente unica):
  1. Line chart Plotly  — temperatura 4 gomme su 8 giri + limite finestra 95°C;
  2. 4 gauge Plotly     — pressioni a CALDO, finestra 28.5–30.0 psi;
  3. Heatmap SVG        — schema auto vista dall'alto (components.html, inline).

COERENZA pressioni (vedi SPEC_ERRATA.md): i gauge mostrano le pressioni a CALDO
(display in pista), distinte da quelle a FREDDO del CSV/garage. Nessuna
trasformazione viene applicata qui: i valori a caldo sono dati demo dedicati.
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

from ui import components as c
from ui import demo_data as dd

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
def _temp_line_fig() -> go.Figure:
    laps = dd.lap_axis()
    fig = go.Figure()
    for pos, label, color in _SERIES:
        fig.add_trace(go.Scatter(
            x=laps, y=dd.TYRE_TEMP_SERIES[pos],
            mode="lines+markers", name=label,
            line=dict(color=color, width=2.4),
            marker=dict(size=5),
            hovertemplate=f"{label}: %{{y:.0f}}°C<extra></extra>",
        ))
    # Limite finestra (tratteggiata) — anche in legenda.
    fig.add_trace(go.Scatter(
        x=laps, y=[dd.TEMP_LIMIT] * len(laps),
        mode="lines", name="Limite finestra",
        line=dict(color=c.TEXT_SECONDARY, width=1.6, dash="dash"),
        hoverinfo="skip",
    ))
    fig.update_layout(
        title=dict(text="Temperatura gomme · 8 giri",
                   font=dict(family="JetBrains Mono, monospace", size=14, color=c.TEXT_PRIMARY)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=c.TEXT_SECONDARY, size=11),
        margin=dict(l=52, r=20, t=48, b=44), height=320,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(title_text="Giro", gridcolor=c.BORDER, zeroline=False,
                     color=c.TEXT_MUTED, linecolor=c.BORDER, dtick=1)
    fig.update_yaxes(title_text="°C", gridcolor=c.BORDER, zeroline=False,
                     color=c.TEXT_MUTED, linecolor=c.BORDER, range=[74, 110])
    # Annotazione sul limite.
    fig.add_annotation(x=dd.lap_axis()[0], y=dd.TEMP_LIMIT, text="95°C",
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
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=170,
                      margin=dict(l=18, r=18, t=8, b=4),
                      font=dict(color=c.TEXT_SECONDARY))
    return fig


# ─────────────────────────────────────────────
# 3) HEATMAP — schema auto vista dall'alto (SVG inline, components.html)
# ─────────────────────────────────────────────
def _heat_corner_svg(x: int, y: int, pos: str) -> str:
    val = dd.TYRE_TEMP_MAX[pos]
    fill = c.temp_to_color(val, dd.TEMP_SCALE)
    label = dd.TYRE_LABELS[pos]
    return (
        f'<g>'
        f'<rect x="{x}" y="{y}" width="34" height="74" rx="11" fill="{fill}" '
        f'stroke="#000000" stroke-opacity="0.35" stroke-width="1"/>'
        f'<text x="{x + 17}" y="{y + 34}" text-anchor="middle" '
        f'font-family="JetBrains Mono, monospace" font-size="17" font-weight="700" '
        f'fill="#FFFFFF">{val}°</text>'
        f'<text x="{x + 17}" y="{y + 52}" text-anchor="middle" '
        f'font-family="JetBrains Mono, monospace" font-size="8.5" '
        f'fill="#FFFFFF" opacity="0.85">{label}</text>'
        f'</g>'
    )


def _heatmap_html() -> str:
    fonts = c.iframe_fonts("JetBrains Mono", "Inter", "Orbitron")
    lo, hi = dd.TEMP_SCALE
    # Posizioni angoli: FL/FR in alto (musata), RL/RR in basso.
    corners = (
        _heat_corner_svg(40, 70, "fl")
        + _heat_corner_svg(166, 70, "fr")
        + _heat_corner_svg(40, 196, "rl")
        + _heat_corner_svg(166, 196, "rr")
    )
    grad_lo = c.temp_to_color(lo, dd.TEMP_SCALE)
    grad_hi = c.temp_to_color(hi, dd.TEMP_SCALE)
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{fonts}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'Inter',sans-serif;}}
.wrap{{background:{c.BG_INSET};border:1px solid {c.BORDER};border-radius:10px;
       padding:14px 16px;height:392px;display:flex;flex-direction:column;}}
.t{{font-family:'JetBrains Mono',monospace;font-size:0.72rem;letter-spacing:0.14em;
    text-transform:uppercase;color:{c.TEXT_SECONDARY};margin-bottom:6px;}}
.legend{{display:flex;align-items:center;gap:8px;margin-top:10px;}}
.legend .bar{{flex:1;height:8px;border-radius:4px;
   background:linear-gradient(90deg,{grad_lo} 0%,{grad_hi} 100%);}}
.legend .end{{font-family:'JetBrains Mono',monospace;font-size:9px;color:{c.TEXT_MUTED};}}
svg{{display:block;margin:0 auto;}}
</style></head><body>
<div class="wrap">
  <div class="t">Heatmap gomme · max stint</div>
  <svg viewBox="0 0 240 290" width="100%" height="250" preserveAspectRatio="xMidYMid meet">
    <!-- scocca auto -->
    <path d="M120 24 C150 24 162 50 162 96 L162 230 C162 256 146 268 120 268
             C94 268 78 256 78 230 L78 96 C78 50 90 24 120 24 Z"
          fill="#161616" stroke="{c.BORDER_STRONG}" stroke-width="2"/>
    <!-- abitacolo / parabrezza -->
    <path d="M98 118 L142 118 L134 150 L106 150 Z" fill="#0e0e0e" stroke="{c.BORDER}" stroke-width="1"/>
    <rect x="104" y="158" width="32" height="46" rx="6" fill="#0e0e0e" stroke="{c.BORDER}" stroke-width="1"/>
    {corners}
  </svg>
  <div class="legend">
    <span class="end">{lo}°</span>
    <span class="bar"></span>
    <span class="end">{hi}°</span>
  </div>
</div></body></html>"""


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
        st.plotly_chart(_temp_line_fig(), use_container_width=True,
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
