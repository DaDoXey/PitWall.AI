"""ui/dashboard.py — pagina Dashboard (hero + card modulari + card Gigi).

Tutti i numeri da ui/demo_data.py (sorgente unica → coerenza con Telemetria).
Visual via components.html (stili inline + font base64); i bottoni "Apri" sono
st.button nativi che navigano via ui.nav.
"""

import streamlit as st
import streamlit.components.v1 as components

from ui import components as c
from ui import nav
from ui import demo_data as dd


# ─────────────────────────────────────────────
# HERO — metriche sessione
# ─────────────────────────────────────────────
def _hero_html() -> str:
    fonts = c.iframe_fonts("Orbitron", "Inter", "JetBrains Mono")
    s = dd.SESSION

    def tile(label, value):
        return (
            f'<div style="flex:1;min-width:150px;">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.58rem;'
            f'letter-spacing:0.16em;color:#666;text-transform:uppercase;margin-bottom:5px;">{label}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.95rem;color:#FFFFFF;">{value}</div>'
            f'</div>'
        )

    tiles = (
        tile("Vettura", f"{s['car']} · {s['car_year']}")
        + tile("Giri completati", f"{s['laps']} · Best {s['best_lap']}")
        + tile("Consumo", f"{s['fuel_avg_per_lap']:.1f} L/giro · {s['fuel_total']:.1f} L tot")
    )
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{fonts}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'Inter',sans-serif;}}
.hero{{background:linear-gradient(135deg,{c.BG_SURFACE} 0%,{c.BG_RAISED} 100%);
   border:1px solid {c.BORDER};border-left:3px solid {c.ACCENT};border-radius:12px;padding:18px 22px;}}
.kick{{font-family:'JetBrains Mono',monospace;font-size:0.6rem;letter-spacing:0.2em;
   color:{c.ACCENT};text-transform:uppercase;margin-bottom:6px;}}
.title{{font-family:'Orbitron',sans-serif;font-size:1.6rem;font-weight:700;color:#FFFFFF;line-height:1.05;}}
.nick{{font-family:'Inter',sans-serif;font-size:0.78rem;color:#999;margin-top:3px;}}
.row{{display:flex;gap:24px;flex-wrap:wrap;margin-top:16px;padding-top:14px;border-top:1px solid {c.BORDER};}}
</style></head><body>
<div class="hero">
  <div class="kick">Ultima sessione</div>
  <div class="title">{s['track']}</div>
  <div class="nick">{s['track_nick']}</div>
  <div class="row">{tiles}</div>
</div></body></html>"""


# ─────────────────────────────────────────────
# CARD MODULARI — temp / pressione / consumo
# ─────────────────────────────────────────────
def _metric_card(label, value, unit, note, note_color, chart_svg) -> str:
    unit_html = f'<span style="font-size:0.8rem;color:#999;margin-left:3px;">{unit}</span>' if unit else ""
    return (
        f'<div style="flex:1;background:{c.BG_SURFACE};border:1px solid {c.BORDER};'
        f'border-radius:12px;padding:16px 18px;display:flex;flex-direction:column;gap:8px;">'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.6rem;letter-spacing:0.14em;'
        f'color:#666;text-transform:uppercase;">{label}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1.8rem;font-weight:500;'
        f'color:#FFFFFF;line-height:1;">{value}{unit_html}</div>'
        f'<div style="min-height:52px;">{chart_svg}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.68rem;color:{note_color};">{note}</div>'
        f'</div>'
    )


def _cards_html() -> str:
    fonts = c.iframe_fonts("JetBrains Mono", "Inter")

    temp_card = _metric_card(
        "Temperatura gomme", dd.TYRE_TEMP_MAX["rr"], "°C",
        "Post.DX sopra finestra (limite 95°C)", c.ACCENT,
        c.sparkline_svg(dd.TYRE_TEMP_SERIES["rr"], c.ACCENT,
                        limit=dd.TEMP_LIMIT, value_fmt="{:.0f}"),
    )
    press_card = _metric_card(
        "Pressione media", dd.PRESS_AVG_HOT, "psi",
        "Retrotreno sotto finestra (28.5–30.0)", c.ACCENT,
        c.window_bar_svg(dd.PRESS_AVG_HOT, 27.0, 30.5,
                         dd.HOT_PRESS_WINDOW[0], dd.HOT_PRESS_WINDOW[1], c.ACCENT,
                         value_fmt="{:.1f}"),
    )
    fuel_card = _metric_card(
        "Consumo medio", f"{dd.SESSION['fuel_avg_per_lap']:.1f}", "L/giro",
        f"Stabile · {dd.SESSION['fuel_total']:.1f} L totali", c.STATUS_OK,
        c.sparkline_svg(dd.FUEL_PER_LAP, c.STATUS_OK, value_fmt="{:.1f}"),
    )
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{fonts}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'Inter',sans-serif;}}
.grid{{display:flex;gap:14px;}}
@media(max-width:760px){{.grid{{flex-direction:column;}}}}
</style></head><body>
<div class="grid">{temp_card}{press_card}{fuel_card}</div>
</body></html>"""


# ─────────────────────────────────────────────
# CARD "CHIEDI A GIGI"
# ─────────────────────────────────────────────
def _gigi_card_html() -> str:
    fonts = c.iframe_fonts("Orbitron", "Inter", "JetBrains Mono")
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{fonts}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'Inter',sans-serif;}}
.card{{display:flex;align-items:center;gap:16px;background:linear-gradient(135deg,{c.BG_SURFACE},{c.BG_RAISED});
   border:1px solid {c.BORDER};border-left:3px solid {c.ACCENT};border-radius:12px;padding:16px 20px;}}
.name{{font-family:'Orbitron',sans-serif;font-size:0.9rem;font-weight:700;color:#FFFFFF;}}
.txt{{font-family:'Inter',sans-serif;font-size:0.82rem;color:#999;line-height:1.55;margin-top:4px;}}
</style></head><body>
<div class="card">
  <div>{c.gigi_avatar_svg(50)}</div>
  <div style="flex:1;">
    <div class="name">Chiedi a Gigi</div>
    <div class="txt">Hai un problema di guida o di setup? Descrivilo al tuo ingegnere
       e ricevi un'analisi tecnica in 4 punti — diagnosi, causa, correzione, note.</div>
  </div>
</div></body></html>"""


# ─────────────────────────────────────────────
# RENDER PAGINA
# ─────────────────────────────────────────────
def render() -> None:
    st.markdown(
        c.page_header("Dashboard", "Riepilogo ultima sessione"),
        unsafe_allow_html=True,
    )

    components.html(_hero_html(), height=192, scrolling=False)

    st.markdown(
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.62rem;'
        'letter-spacing:0.14em;color:#666;text-transform:uppercase;margin:14px 0 8px;">'
        'Metriche sessione</div>',
        unsafe_allow_html=True,
    )
    components.html(_cards_html(), height=230, scrolling=False)

    # Bottoni "Apri" sotto le 3 card → ognuno alla destinazione coerente con la card.
    # Temp → Telemetria · Pressione → Setup (regolazione) · Consumo → Gigi (strategia).
    b1, b2, b3 = st.columns(3)
    if b1.button("Apri Telemetria", key="open_temp", use_container_width=True):
        nav.go_to("Telemetria")
    if b2.button("Regola Setup", key="open_press", use_container_width=True):
        nav.go_to("Setup")
    if b3.button("Strategia carburante", key="open_fuel", use_container_width=True):
        nav.go_to("Engineer Console")

    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    components.html(_gigi_card_html(), height=120, scrolling=False)
    if st.button("Apri Engineer Console", key="open_gigi", type="primary", use_container_width=True):
        nav.go_to("Engineer Console")
