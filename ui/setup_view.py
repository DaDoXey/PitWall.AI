"""ui/setup_view.py — pagina Setup (Fase 5): 5 tab ACC con slider funzionali.

I parametri (range/default/unit per vettura+circuito) arrivano da
`modules.setup_params.get_params_for_car()` — modulo dati protetto, qui solo
CHIAMATO, mai riscritto. Il rendering degli slider è puramente presentazionale
(stile cockpit, classi di assets/app.css). I valori scelti restano in
st.session_state (chiavi `setup_<param>`) e vengono raccolti in
st.session_state["setup_current"] per le fasi successive.

Selettori auto/pista e upload (CSV/screenshot) → Fase 7 (dietro feature-flag).
Per ora car/track sono letti da session_state con fallback ai default demo
(BMW M4 GT3 · Monza), così la Fase 7 potrà valorizzarli senza riscrivere qui.
"""

import streamlit as st

from ui import components as c
from ui import demo_data as dd
from modules.setup_params import get_params_for_car


# ─────────────────────────────────────────────
# SLIDER (presentazionale) — legge i range dal modulo dati, scrive in session_state
# ─────────────────────────────────────────────
def _slider(params: dict, key: str, target=None):
    """Renderizza uno slider ACC: riga nome+valore + slider nativo (label nascosta).

    `params` è il dict `section["params"]`; `target` è una colonna o st.
    Supporta float e int automaticamente. Nessuna alterazione dei dati: i
    range/step/default provengono da modules.setup_params.
    """
    p = params[key]
    target = target if target is not None else st

    is_float = isinstance(p["step"], float) or isinstance(p["min"], float)
    p_min = float(p["min"]) if is_float else int(p["min"])
    p_max = float(p["max"]) if is_float else int(p["max"])
    p_step = float(p["step"]) if is_float else int(p["step"])
    default = float(p["default"]) if is_float else int(p["default"])

    skey = f"setup_{key}"
    current = st.session_state.get(skey, default)

    # Clamp se il valore salvato è fuori dal nuovo range (es. dopo cambio vettura):
    # va riscritto PRIMA dello slider, altrimenti st.slider con key= solleverebbe.
    if current < p_min or current > p_max:
        current = min(max(current, p_min), p_max)
        current = float(current) if is_float else int(current)
        st.session_state[skey] = current

    unit = f" {p['unit']}" if p["unit"] else ""
    disp = f"{current:.2f}" if is_float else str(int(current))

    # Riga nome (mono, muted) + valore (accent) — stili inline, nessun selettore interno.
    target.markdown(
        '<div style="display:flex;justify-content:space-between;align-items:baseline;'
        'margin:0.7rem 0 0.15rem 0;">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.66rem;'
        f'letter-spacing:0.08em;color:#999;text-transform:uppercase;">{p["label"]}</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.82rem;'
        f'font-weight:600;color:#E8002D;">{disp}{unit}</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    value = target.slider(
        p["label"],
        min_value=p_min,
        max_value=p_max,
        value=float(current) if is_float else int(current),
        step=p_step,
        key=skey,
        label_visibility="collapsed",
        help=p.get("tip") or None,
    )
    return value


def _group(title: str) -> None:
    st.markdown(f'<div class="param-group-title">{title}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RENDER DEI 5 TAB (stessa struttura del menu setup ACC)
# ─────────────────────────────────────────────
def _render_tyres(params: dict, setup: dict) -> None:
    _group("PRESSIONI")
    c1, c2 = st.columns(2)
    setup["tire_press_fl"] = _slider(params, "tire_press_fl", c1)
    setup["tire_press_fr"] = _slider(params, "tire_press_fr", c2)
    c3, c4 = st.columns(2)
    setup["tire_press_rl"] = _slider(params, "tire_press_rl", c3)
    setup["tire_press_rr"] = _slider(params, "tire_press_rr", c4)

    _group("CAMBER")
    c1, c2 = st.columns(2)
    setup["camber_fl"] = _slider(params, "camber_fl", c1)
    setup["camber_fr"] = _slider(params, "camber_fr", c2)
    c3, c4 = st.columns(2)
    setup["camber_rl"] = _slider(params, "camber_rl", c3)
    setup["camber_rr"] = _slider(params, "camber_rr", c4)

    _group("TOE")
    c1, c2 = st.columns(2)
    setup["toe_fl"] = _slider(params, "toe_fl", c1)
    setup["toe_fr"] = _slider(params, "toe_fr", c2)
    c3, c4 = st.columns(2)
    setup["toe_rl"] = _slider(params, "toe_rl", c3)
    setup["toe_rr"] = _slider(params, "toe_rr", c4)

    _group("CASTER")
    setup["caster"] = _slider(params, "caster")


def _render_electronics(params: dict, setup: dict) -> None:
    c1, c2 = st.columns(2)
    setup["tc1"] = _slider(params, "tc1", c1)
    setup["tc2"] = _slider(params, "tc2", c2)
    c3, c4 = st.columns(2)
    setup["abs"] = _slider(params, "abs", c3)
    setup["ecu_map"] = _slider(params, "ecu_map", c4)
    setup["brake_bias"] = _slider(params, "brake_bias")


def _render_mechanical(params: dict, setup: dict) -> None:
    _group("BARRE ANTIROLLIO")
    c1, c2 = st.columns(2)
    setup["arb_front"] = _slider(params, "arb_front", c1)
    setup["arb_rear"] = _slider(params, "arb_rear", c2)

    _group("WHEEL RATE")
    c1, c2 = st.columns(2)
    setup["wheel_rate_front"] = _slider(params, "wheel_rate_front", c1)
    setup["wheel_rate_rear"] = _slider(params, "wheel_rate_rear", c2)

    _group("BUMPSTOP RATE")
    c1, c2 = st.columns(2)
    setup["bumpstop_rate_front"] = _slider(params, "bumpstop_rate_front", c1)
    setup["bumpstop_rate_rear"] = _slider(params, "bumpstop_rate_rear", c2)

    _group("BUMPSTOP RANGE")
    c1, c2 = st.columns(2)
    setup["bumpstop_range_front"] = _slider(params, "bumpstop_range_front", c1)
    setup["bumpstop_range_rear"] = _slider(params, "bumpstop_range_rear", c2)

    _group("DIFFERENZIALE")
    setup["preload"] = _slider(params, "preload")


def _render_dampers(params: dict, setup: dict) -> None:
    corners = [
        ("fl", "Anteriore Sinistra"),
        ("fr", "Anteriore Destra"),
        ("rl", "Posteriore Sinistra"),
        ("rr", "Posteriore Destra"),
    ]
    for suffix, label in corners:
        _group(label.upper())
        cols = st.columns(4)
        for pkey, col in zip(
            (f"bump_{suffix}", f"fast_bump_{suffix}", f"rebound_{suffix}", f"fast_rebound_{suffix}"),
            cols,
        ):
            setup[pkey] = _slider(params, pkey, col)


def _render_aero(params: dict, setup: dict) -> None:
    _group("RIDE HEIGHT & DEPORTANZA")
    c1, c2 = st.columns(2)
    setup["ride_height_front"] = _slider(params, "ride_height_front", c1)
    setup["ride_height_rear"] = _slider(params, "ride_height_rear", c2)

    # Rake informativo (geometria, solo presentazione).
    rake = setup["ride_height_rear"] - setup["ride_height_front"]
    rake_color = c.ACCENT if (rake < 10 or rake > 35) else c.STATUS_OK
    st.markdown(
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.8rem;'
        f'color:{rake_color};margin:0.3rem 0 0.2rem 0;">Rake attuale: {rake:.0f} mm</div>',
        unsafe_allow_html=True,
    )

    _group("CARICO AERODINAMICO")
    c1, c2 = st.columns(2)
    setup["splitter"] = _slider(params, "splitter", c1)
    setup["wing"] = _slider(params, "wing", c2)

    _group("BRAKE DUCTS")
    c1, c2 = st.columns(2)
    setup["brake_duct_front"] = _slider(params, "brake_duct_front", c1)
    setup["brake_duct_rear"] = _slider(params, "brake_duct_rear", c2)


_RENDERERS = {
    "tyres": _render_tyres,
    "electronics": _render_electronics,
    "mechanical_grip": _render_mechanical,
    "dampers": _render_dampers,
    "aero": _render_aero,
}


# ─────────────────────────────────────────────
# RENDER PAGINA
# ─────────────────────────────────────────────
def render() -> None:
    # Auto/pista: da session_state (Fase 7 li valorizzerà coi selettori) o default demo.
    car = st.session_state.get("setup_car", dd.SESSION["car"])
    track = st.session_state.get("setup_track", dd.SESSION["track"])

    st.markdown(
        c.page_header("Setup", f"{car} · {track} · range ACC"),
        unsafe_allow_html=True,
    )

    # Override per vettura/circuito dal modulo dati (chiamato, non riscritto).
    sections = get_params_for_car(car, track)

    setup_current: dict = {}
    tab_keys = list(sections.keys())
    tab_labels = [sections[k]["label"] for k in tab_keys]
    tabs = st.tabs(tab_labels)

    for tab, section_key in zip(tabs, tab_keys):
        with tab:
            params = sections[section_key]["params"]
            renderer = _RENDERERS.get(section_key)
            if renderer:
                renderer(params, setup_current)

    # Setup raccolto, disponibile alle fasi successive (analisi, scheda, ecc.).
    st.session_state["setup_current"] = setup_current
