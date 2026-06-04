"""
app.py — PitWall.AI v2
Entry point Streamlit con:
  - 5 tab setup completi (Tyres, Electronics, Mechanical Grip, Dampers, Aero)
  - Input da screenshot tramite Claude Vision
  - Input manuale con slider per ogni parametro
  - Compatibile con agent.py e parser.py esistenti
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Import moduli PitWall
from agent import get_ai_response
from parser import parse_csv
from modules.setup_params import SETUP_SECTIONS, get_all_params_flat, format_setup_for_prompt
from modules.vision_parser import parse_setup_from_image, summarize_parsed_setup

# ─────────────────────────────────────────────
# CONFIGURAZIONE
# ─────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="PitWall.AI",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# STILE CSS — coerente con MVP (dark, rosso ACC)
# ─────────────────────────────────────────────
st.markdown("""
<style>
  /* Font e colori base */
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;700&display=swap');

  :root {
    --red:     #E8002D;
    --red-dim: #9B0020;
    --bg:      #0D0D0D;
    --surface: #1A1A1A;
    --border:  #2E2E2E;
    --text:    #F0F0F0;
    --muted:   #888888;
  }

  html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
  }

  /* Header tabs */
  [data-testid="stTabs"] > div > div > button {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    color: var(--muted);
    border-bottom: 2px solid transparent;
    padding: 0.5rem 1rem;
  }
  [data-testid="stTabs"] > div > div > button[aria-selected="true"] {
    color: var(--red);
    border-bottom: 2px solid var(--red);
  }

  /* Slider — accent rosso */
  [data-testid="stSlider"] > div > div > div > div {
    background: var(--red) !important;
  }

  /* Sezioni parametri */
  .param-group {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--red);
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
  }
  .param-group-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.8rem;
  }

  /* Output AI */
  .ai-output {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--red);
    border-radius: 6px;
    padding: 1.5rem;
    font-size: 0.95rem;
    line-height: 1.7;
  }

  /* Bottone principale */
  [data-testid="stButton"] > button[kind="primary"] {
    background: var(--red);
    border: none;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    letter-spacing: 0.08em;
    font-weight: 700;
    color: white;
    padding: 0.6rem 2rem;
    border-radius: 4px;
  }
  [data-testid="stButton"] > button[kind="primary"]:hover {
    background: var(--red-dim);
  }

  /* Tooltip info */
  .tip-text {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: -0.4rem;
    margin-bottom: 0.6rem;
    font-style: italic;
  }

  /* Badge sezione */
  .section-badge {
    display: inline-block;
    background: var(--red-dim);
    color: white;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    margin-bottom: 0.5rem;
    letter-spacing: 0.08em;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.markdown("# 🏁")
with col_title:
    st.markdown("## PitWall.AI")
    st.caption("Virtual Race Engineer — Assetto Corsa Competizione GT3")

st.divider()


# ─────────────────────────────────────────────
# SIDEBAR — Auto + CSV + Screenshot
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🚗 Configurazione Sessione")

    selected_car = st.selectbox(
        "Auto",
        options=[
            "BMW M4 GT3",
            "Ferrari 296 GT3",
            "Ferrari 488 GT3 Evo",
            "Porsche 992 GT3 R",
            "Porsche 991 II GT3 R",
            "Mercedes-AMG GT3 Evo",
            "Audi R8 LMS Evo II GT3",
            "Lamborghini Huracán GT3 EVO2",
            "McLaren 720S GT3 Evo",
            "Bentley Continental GT3",
            "Honda NSX GT3 Evo",
            "Nissan GT-R Nismo GT3",
            "Lexus RC F GT3",
            "Ford Mustang GT3",
            "Aston Martin V8 Vantage GT3",
        ],
        help="Seleziona l'auto in uso. Alcuni range parametri variano per modello.",
    )

    st.markdown("---")
    st.markdown("### 📊 Dati Sessione (opzionale)")

    csv_file = st.file_uploader(
        "Carica CSV sessione",
        type=["csv"],
        help="CSV con colonne: lap, fuel_cons, tire_press_*, tire_temp_*",
    )

    st.markdown("---")
    st.markdown("### 📸 Screenshot Setup ACC")
    st.caption("Carica una foto del menu setup dal gioco. L'AI leggerà automaticamente tutti i parametri.")

    screenshot_file = st.file_uploader(
        "Screenshot setup (JPG/PNG)",
        type=["jpg", "jpeg", "png", "webp"],
        key="screenshot_uploader",
        help="Schermata di qualsiasi tab del menu setup in ACC.",
    )

    # Bottone lettura screenshot
    if screenshot_file is not None:
        if st.button("🔍 Leggi Parametri da Screenshot", type="secondary", use_container_width=True):
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            if not api_key:
                st.error("ANTHROPIC_API_KEY non trovata nel file .env")
            else:
                with st.spinner("Analisi screenshot in corso..."):
                    result = parse_setup_from_image(
                        screenshot_file.getvalue(),
                        api_key=api_key,
                    )
                st.session_state["vision_params"] = result.get("params", {})
                st.session_state["vision_summary"] = summarize_parsed_setup(result)
                st.success(f"Riconosciuti {len(result['params'])} parametri.")

    # Mostra sommario lettura
    if "vision_summary" in st.session_state:
        with st.expander("📋 Parametri riconosciuti", expanded=True):
            st.markdown(st.session_state["vision_summary"])
        if st.button("✅ Usa questi parametri nel form", use_container_width=True):
            st.session_state["load_vision_params"] = True
            st.rerun()

    st.markdown("---")
    st.caption("PitWall.AI v2 — ITS ICT Academy Roma")


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_default_or_vision(key: str, default_val):
    """
    Se sono stati caricati parametri da Vision e l'utente ha confermato,
    usa il valore riconosciuto come default dello slider. Altrimenti usa
    il default standard del parametro.
    """
    if st.session_state.get("load_vision_params"):
        vision = st.session_state.get("vision_params", {})
        if key in vision:
            return vision[key]
    return default_val


def render_param_slider(key: str, param: dict, col=None) -> float | int:
    """
    Renderizza uno slider per un parametro di setup.
    Supporta float e int in modo automatico.
    """
    default = get_default_or_vision(key, param["default"])
    label = param["label"]
    unit_str = f" ({param['unit']})" if param["unit"] else ""
    full_label = f"{label}{unit_str}"

    is_float = isinstance(param["step"], float) or isinstance(param["min"], float)

    target = col if col else st

    value = target.slider(
        full_label,
        min_value=float(param["min"]) if is_float else int(param["min"]),
        max_value=float(param["max"]) if is_float else int(param["max"]),
        value=float(default) if is_float else int(default),
        step=float(param["step"]) if is_float else int(param["step"]),
        key=f"slider_{key}",
    )

    target.markdown(
        f'<p class="tip-text">💡 {param["tip"]}</p>',
        unsafe_allow_html=True,
    )

    return value


# ─────────────────────────────────────────────
# AREA PRINCIPALE — 2 colonne: feedback + setup
# ─────────────────────────────────────────────

col_left, col_right = st.columns([5, 4], gap="large")

# ══ COLONNA SINISTRA — Feedback + Output ══
with col_left:
    st.markdown("### 🎙 Feedback Pilota")
    feedback = st.text_area(
        "Descrivi il problema che stai riscontrando in pista",
        height=140,
        placeholder=(
            "Es: 'Ho troppo sottosterzo a centro curva sulle curve lente. "
            "L'auto non ruota e devo aprire il volante. "
            "Accade soprattutto nelle curve a destra, principalmente nel settore 2.'"
        ),
        help="Più sei specifico (fase della curva, tipo di curva, condizioni), migliore sarà l'analisi.",
    )

    btn_analizza = st.button("🔍 ANALIZZA", type="primary", use_container_width=True)

    st.markdown("---")

    # Area output
    if "last_response" in st.session_state:
        st.markdown("### 📋 Analisi Race Engineer")
        st.markdown(
            f'<div class="ai-output">{st.session_state["last_response"]}</div>',
            unsafe_allow_html=True,
        )


# ══ COLONNA DESTRA — Tab Setup ══
with col_right:
    st.markdown("### ⚙️ Setup Corrente")
    st.caption("Inserisci i valori del tuo setup attuale. L'AI li userà come riferimento per le modifiche incrementali.")

    # Dizionario per raccogliere tutti i valori del setup
    current_setup = {}

    # Render dei 5 tab — stessa struttura del gioco ACC
    tab_keys = list(SETUP_SECTIONS.keys())
    tab_labels = [SETUP_SECTIONS[k]["label"] for k in tab_keys]
    tabs = st.tabs(tab_labels)

    for tab, section_key in zip(tabs, tab_keys):
        with tab:
            section = SETUP_SECTIONS[section_key]
            params = section["params"]

            # ── TYRES: griglia 2×2 per le 4 ruote ──
            if section_key == "tyres":
                # Pressioni
                st.markdown('<div class="param-group-title">PRESSIONI</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                current_setup["tire_press_fl"] = render_param_slider("tire_press_fl", params["tire_press_fl"], c1)
                current_setup["tire_press_fr"] = render_param_slider("tire_press_fr", params["tire_press_fr"], c2)
                c3, c4 = st.columns(2)
                current_setup["tire_press_rl"] = render_param_slider("tire_press_rl", params["tire_press_rl"], c3)
                current_setup["tire_press_rr"] = render_param_slider("tire_press_rr", params["tire_press_rr"], c4)

                # Camber
                st.markdown('<div class="param-group-title" style="margin-top:1rem">CAMBER</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                current_setup["camber_fl"] = render_param_slider("camber_fl", params["camber_fl"], c1)
                current_setup["camber_fr"] = render_param_slider("camber_fr", params["camber_fr"], c2)
                c3, c4 = st.columns(2)
                current_setup["camber_rl"] = render_param_slider("camber_rl", params["camber_rl"], c3)
                current_setup["camber_rr"] = render_param_slider("camber_rr", params["camber_rr"], c4)

                # Toe
                st.markdown('<div class="param-group-title" style="margin-top:1rem">TOE</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                current_setup["toe_fl"] = render_param_slider("toe_fl", params["toe_fl"], c1)
                current_setup["toe_fr"] = render_param_slider("toe_fr", params["toe_fr"], c2)
                c3, c4 = st.columns(2)
                current_setup["toe_rl"] = render_param_slider("toe_rl", params["toe_rl"], c3)
                current_setup["toe_rr"] = render_param_slider("toe_rr", params["toe_rr"], c4)

                # Caster
                st.markdown('<div class="param-group-title" style="margin-top:1rem">CASTER</div>', unsafe_allow_html=True)
                current_setup["caster"] = render_param_slider("caster", params["caster"])

            # ── ELECTRONICS: lista verticale ──
            elif section_key == "electronics":
                for key, param in params.items():
                    current_setup[key] = render_param_slider(key, param)

            # ── MECHANICAL GRIP: due colonne ant/post ──
            elif section_key == "mechanical_grip":
                st.markdown('<div class="param-group-title">BARRE ANTIROLLIO</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                current_setup["arb_front"] = render_param_slider("arb_front", params["arb_front"], c1)
                current_setup["arb_rear"] = render_param_slider("arb_rear", params["arb_rear"], c2)

                st.markdown('<div class="param-group-title" style="margin-top:1rem">WHEEL RATE</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                current_setup["wheel_rate_front"] = render_param_slider("wheel_rate_front", params["wheel_rate_front"], c1)
                current_setup["wheel_rate_rear"] = render_param_slider("wheel_rate_rear", params["wheel_rate_rear"], c2)

                st.markdown('<div class="param-group-title" style="margin-top:1rem">BUMPSTOP RATE</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                current_setup["bumpstop_rate_front"] = render_param_slider("bumpstop_rate_front", params["bumpstop_rate_front"], c1)
                current_setup["bumpstop_rate_rear"] = render_param_slider("bumpstop_rate_rear", params["bumpstop_rate_rear"], c2)

                st.markdown('<div class="param-group-title" style="margin-top:1rem">BUMPSTOP RANGE</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                current_setup["bumpstop_range_front"] = render_param_slider("bumpstop_range_front", params["bumpstop_range_front"], c1)
                current_setup["bumpstop_range_rear"] = render_param_slider("bumpstop_range_rear", params["bumpstop_range_rear"], c2)

                st.markdown('<div class="param-group-title" style="margin-top:1rem">DIFFERENZIALE</div>', unsafe_allow_html=True)
                current_setup["preload"] = render_param_slider("preload", params["preload"])

            # ── DAMPERS: griglia 4 ruote × 4 parametri ──
            elif section_key == "dampers":
                damper_corners = [
                    ("FL", "Anteriore Sinistra"),
                    ("FR", "Anteriore Destra"),
                    ("RL", "Posteriore Sinistra"),
                    ("RR", "Posteriore Destra"),
                ]
                for suffix, corner_label in damper_corners:
                    st.markdown(
                        f'<div class="param-group-title" style="margin-top:0.8rem">{corner_label.upper()}</div>',
                        unsafe_allow_html=True,
                    )
                    c1, c2, c3, c4 = st.columns(4)
                    cols = [c1, c2, c3, c4]
                    damper_params = [
                        f"bump_{suffix.lower()}",
                        f"fast_bump_{suffix.lower()}",
                        f"rebound_{suffix.lower()}",
                        f"fast_rebound_{suffix.lower()}",
                    ]
                    for param_key, col in zip(damper_params, cols):
                        current_setup[param_key] = render_param_slider(
                            param_key, params[param_key], col
                        )

            # ── AERO: due blocchi ant/post ──
            elif section_key == "aero":
                st.markdown('<div class="param-group-title">RIDE HEIGHT & DEPORTANZA</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                current_setup["ride_height_front"] = render_param_slider("ride_height_front", params["ride_height_front"], c1)
                current_setup["ride_height_rear"] = render_param_slider("ride_height_rear", params["ride_height_rear"], c2)

                # Rake display
                rake = current_setup["ride_height_rear"] - current_setup["ride_height_front"]
                rake_color = "#E8002D" if rake < 10 or rake > 35 else "#4CAF50"
                st.markdown(
                    f'<p style="font-family:JetBrains Mono,monospace;font-size:0.85rem;color:{rake_color};">'
                    f'📐 Rake attuale: {rake:.0f} mm</p>',
                    unsafe_allow_html=True,
                )

                st.markdown('<div class="param-group-title" style="margin-top:1rem">CARICO AERODINAMICO</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                current_setup["splitter"] = render_param_slider("splitter", params["splitter"], c1)
                current_setup["wing"] = render_param_slider("wing", params["wing"], c2)

                st.markdown('<div class="param-group-title" style="margin-top:1rem">BRAKE DUCTS</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                current_setup["brake_duct_front"] = render_param_slider("brake_duct_front", params["brake_duct_front"], c1)
                current_setup["brake_duct_rear"] = render_param_slider("brake_duct_rear", params["brake_duct_rear"], c2)


# ─────────────────────────────────────────────
# ELABORAZIONE — bottone Analizza
# ─────────────────────────────────────────────

if btn_analizza:
    if not feedback.strip():
        st.warning("⚠️ Descrivi il problema riscontrato in pista prima di procedere.")
        st.stop()

    # Recupera API key
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY non trovata nel file .env")
        st.stop()

    # Parsing CSV (se presente)
    csv_context = ""
    if csv_file is not None:
        csv_result = parse_csv(csv_file)
        if csv_result.get("error"):
            st.warning(f"⚠️ CSV non valido: {csv_result['error']}")
        else:
            csv_context = csv_result.get("formatted", "")

    # Formattazione setup
    setup_context = format_setup_for_prompt(current_setup)

    # Costruzione contesto completo
    full_context = f"Auto: {selected_car}\n\n{setup_context}"
    if csv_context:
        full_context += f"\n\n{csv_context}"

    full_context += f"\n\nFeedback pilota: {feedback.strip()}"

    # Chiamata LLM
    with st.spinner("🔄 Race Engineer in analisi..."):
        response = get_ai_response(
            user_input=full_context,
            api_key=api_key,
        )

    st.session_state["last_response"] = response

    # Reset caricamento vision params
    if st.session_state.get("load_vision_params"):
        st.session_state["load_vision_params"] = False

    st.rerun()
