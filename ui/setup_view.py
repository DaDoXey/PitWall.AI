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

import os

import streamlit as st

from ui import components as c
from ui import demo_data as dd
from ui import flags, catalog
from modules.setup_params import get_params_for_car, get_all_params_flat


# ─────────────────────────────────────────────
# SLIDER (presentazionale) — legge i range dal modulo dati, scrive in session_state
# ─────────────────────────────────────────────
def _pressure_status_color(value: float) -> str:
    """Colore stato di una pressione a freddo (psi) vs finestra ottimale.

    Verde se in finestra, ambra entro il margine dal bordo, rosso oltre. Soglie
    da demo_data (COLD_PRESS_WINDOW / COLD_PRESS_AMBER_MARGIN), tunable in un punto.
    """
    lo, hi = dd.COLD_PRESS_WINDOW
    m = dd.COLD_PRESS_AMBER_MARGIN
    if lo <= value <= hi:
        return c.STATUS_OK
    if (lo - m) <= value <= (hi + m):
        return c.STATUS_WARN
    return c.STATUS_ERROR


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
    if is_float:
        # 1 decimale per pressioni/camber/caster/brake-bias (step ≥ 0.1);
        # 2 decimali solo dove serve davvero (toe, step 0.01).
        decimals = 1 if p_step >= 0.1 else 2
        disp = f"{current:.{decimals}f}"
    else:
        disp = str(int(current))

    # Colore del valore:
    #  - pressioni (tire_press_*) → colore di STATO vs finestra ottimale a freddo
    #    (verde/ambra/rosso) + pallino ● dello stesso colore accanto al numero;
    #  - altri parametri → bianco di default, rosso SOLO se suggerito da Gigi (FASE 6.2).
    is_pressure = key.startswith("tire_press_")
    if is_pressure:
        val_color = _pressure_status_color(current)
        dot = ' <span style="font-size:0.7rem;">●</span>'
    else:
        val_color = "#E8002D" if key in dd.SUGGESTED_PARAMS else "#FFFFFF"
        dot = ""

    # Riga nome (mono, muted) + valore — stili inline, nessun selettore interno.
    target.markdown(
        '<div style="display:flex;justify-content:space-between;align-items:baseline;'
        'margin:0.7rem 0 0.15rem 0;">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.66rem;'
        f'letter-spacing:0.08em;color:#999;text-transform:uppercase;">{p["label"]}</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.82rem;'
        f'font-weight:600;color:{val_color};">{disp}{unit}{dot}</span>'
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
    # Legenda colore (finestra ottimale a freddo, soglie da demo_data).
    _lo, _hi = dd.COLD_PRESS_WINDOW
    st.markdown(
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.6rem;'
        'letter-spacing:0.04em;color:#666;margin:-0.15rem 0 0.25rem 0;">'
        f'<span style="color:{c.STATUS_OK};">●</span> ottimale {_lo:.1f}–{_hi:.1f} psi&emsp;'
        f'<span style="color:{c.STATUS_WARN};">●</span> limite&emsp;'
        f'<span style="color:{c.STATUS_ERROR};">●</span> fuori finestra</div>',
        unsafe_allow_html=True,
    )
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
# INPUT SESSIONE (Fase 7) — dietro feature-flag, OFF in demo
# ─────────────────────────────────────────────
def _apply_vision_to_sliders(vision_params: dict) -> int:
    """Applica i parametri letti da screenshot agli slider (clamp nei range).

    Imposta le chiavi `setup_<param>` in session_state; ritorna quanti applicati.
    """
    flat = get_all_params_flat()
    applied = 0
    for key, val in (vision_params or {}).items():
        if key not in flat:
            continue
        p = flat[key]
        try:
            num = float(val)
        except (TypeError, ValueError):
            continue
        is_float = isinstance(p["step"], float) or isinstance(p["min"], float)
        num = num if is_float else int(round(num))
        num = min(max(num, p["min"]), p["max"])
        st.session_state[f"setup_{key}"] = float(num) if is_float else int(num)
        applied += 1
    return applied


def _csv_upload() -> None:
    st.markdown('<div class="pw-field-label">Carica CSV sessione</div>', unsafe_allow_html=True)
    f = st.file_uploader("Carica CSV sessione", type=["csv"], key="setup_csv",
                         label_visibility="collapsed")
    if not f:
        return
    try:
        from backend.parser.csv_parser import parse_session_csv, CSVParseError
    except Exception as e:  # import difensivo: la demo non deve mai rompersi
        st.error(f"Parser CSV non disponibile: {e}")
        return
    try:
        res = parse_session_csv(f)
    except CSVParseError as e:
        st.warning(f"CSV non valido: {e}")
        return
    except Exception as e:
        st.warning(f"Impossibile leggere il CSV: {e}")
        return
    st.session_state["csv_parsed_result"] = res
    laps = res.get("laps_count", 0)
    fuel = res.get("fuel_cons_avg", 0) or 0.0
    st.success(f"CSV letto: {laps} giri · consumo medio {fuel:.2f} L/giro")


def _screenshot_upload() -> None:
    st.markdown('<div class="pw-field-label">Screenshot setup ACC</div>', unsafe_allow_html=True)

    # FASE 2.3 — stub "Prossimamente": la lettura da screenshot resta dietro
    # feature-flag (OFF di default), non cancellata. In demo si mostra disattivata.
    if not flags.feature_screenshot():
        st.file_uploader("Screenshot setup (non attivo)", type=["jpg", "jpeg", "png", "webp"],
                         key="setup_shot_stub", label_visibility="collapsed", disabled=True)
        st.caption("🔒 Prossimamente — lettura automatica del setup da screenshot ACC.")
        return

    img = st.file_uploader("Screenshot setup", type=["jpg", "jpeg", "png", "webp"],
                           key="setup_shot", label_visibility="collapsed")
    if img is not None and st.button("Leggi parametri dallo screenshot",
                                     use_container_width=True, key="btn_vision"):
        # st.secrets solleva se manca secrets.toml (locale): fallback su .env.
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))
        except Exception:
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            st.error("ANTHROPIC_API_KEY non trovata — verifica .env (locale) o Streamlit Secrets (cloud)")
        else:
            try:
                from modules.vision_parser import parse_setup_from_image, summarize_parsed_setup
                with st.spinner("Analisi screenshot in corso…"):
                    result = parse_setup_from_image(img.getvalue(), api_key=api_key,
                                                    media_type=img.type)
                st.session_state["vision_params"] = result.get("params", {})
                st.session_state["vision_summary"] = summarize_parsed_setup(result)
                st.success(f"Riconosciuti {len(result.get('params', {}))} parametri.")
            except Exception as e:
                st.error(f"Lettura screenshot fallita: {e}")

    if st.session_state.get("vision_summary"):
        st.markdown(st.session_state["vision_summary"])
        if st.button("Usa questi parametri negli slider", use_container_width=True,
                     key="btn_apply_vision"):
            n = _apply_vision_to_sliders(st.session_state.get("vision_params", {}))
            st.success(f"{n} parametri applicati agli slider.")
            st.rerun()


def _session_inputs() -> tuple[str, str]:
    """Selettori auto/pista/condizioni + temperature + upload. Ritorna (car, track)."""
    _group("CONFIGURAZIONE SESSIONE")
    c1, c2, c3 = st.columns(3)
    car = c1.selectbox("Auto", options=catalog.CAR_LIST, key="setup_car")
    track = c2.selectbox("Tracciato", options=catalog.TRACK_LIST, key="setup_track")
    c3.selectbox("Condizioni", options=catalog.CONDITIONS, key="setup_conditions")

    t1, t2 = st.columns(2)
    t1.slider("Temp. Ambiente (°C)", 0, 50, 20, key="setup_temp_amb")
    t2.slider("Temp. Pista (°C)", 0, 60, 30, key="setup_temp_track")

    with st.expander("Dati sessione — CSV / screenshot setup", expanded=False):
        _csv_upload()
        st.markdown('<div class="section-separator"></div>', unsafe_allow_html=True)
        _screenshot_upload()

    return car, track


# ─────────────────────────────────────────────
# RENDER PAGINA
# ─────────────────────────────────────────────
def render() -> None:
    # Sottotitolo coerente con la selezione corrente (o default demo).
    car_sub = st.session_state.get("setup_car", dd.SESSION["car"])
    track_sub = st.session_state.get("setup_track", dd.SESSION["track"])
    st.markdown(
        c.page_header("Setup", f"{car_sub} · {track_sub} · range ACC"),
        unsafe_allow_html=True,
    )

    # Feature-flag (Fase 7): default OFF → demo pulita. Toggle = override runtime.
    st.session_state.setdefault("inputs_enabled", flags.inputs_enabled())
    show_inputs = st.toggle(
        "Input sessione (selettori auto/pista · upload CSV/screenshot)",
        key="inputs_enabled",
    )

    if show_inputs:
        car, track = _session_inputs()
        st.markdown('<div class="section-separator"></div>', unsafe_allow_html=True)
    else:
        car = st.session_state.get("setup_car", dd.SESSION["car"])
        track = st.session_state.get("setup_track", dd.SESSION["track"])

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
