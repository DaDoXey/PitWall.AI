import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Optional

from backend.core import (
    ACCPhysicsEngine,
    ClaudeEngine,
    validate_pressure,
    validate_temperature,
)
from backend.database.manager import SessionDatabase, extract_suggested_psi, backfill_suggested_psi
from backend.parser.csv_parser import CSVParseError, parse_session_csv
from components.tire_display import (
    render_pressure_gauges,
    render_temperature_gauges,
)
from components.temp_chart import render_temperature_chart


def render_tab_setup(sidebar_data: Dict[str, Any]) -> None:
    """Renderizza il tab di analisi setup mantenendo app.py solo come orchestratore.

    Questo componente gestisce i controlli di input, la validazione fisica tramite
    backend/core/physics.py e la chiamata all'LLM tramite backend/core/ai_logic.py.
    """
    st.markdown(
        '<h2 style="font-family:\'Orbitron\',monospace;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:#fff;'
        'border-left:3px solid #E10600;padding-left:12px;margin-bottom:16px;">'
        'Analisi Setup</h2>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<h3 style="font-family:\'Orbitron\',monospace;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:#fff;'
        'border-left:3px solid #E10600;padding-left:12px;margin-bottom:16px;">'
        'A — Input Pressioni</h3>',
        unsafe_allow_html=True
    )

    pressure_context = st.radio(
        "I valori PSI che stai inserendo sono:",
        options=[
            "A freddo (impostati in garage prima della sessione)",
            "A caldo (letti dal MFD mentre sei in pista — tasto N)",
        ],
        horizontal=True,
        help=(
            "A freddo → target 26.7 PSI | range 26.0–27.0 PSI\n"
            "A caldo  → target 29.0 PSI | range 28.5–30.0 PSI"
        ),
    )

    # Converti la selezione nel formato atteso da physics.py
    ctx = "cold" if "freddo" in pressure_context else "hot"
    hot_mode = ctx == "hot"

    row1 = st.columns([1, 1])
    with row1[0]:
        psi_fl = st.number_input(
            "Pressione FL (PSI)", min_value=20.0, max_value=35.0, value=26.7,
            step=0.1, format="%.1f", key="press_fl"
        )
        psi_rl = st.number_input(
            "Pressione RL (PSI)", min_value=20.0, max_value=35.0, value=26.7,
            step=0.1, format="%.1f", key="press_rl"
        )
    with row1[1]:
        psi_fr = st.number_input(
            "Pressione FR (PSI)", min_value=20.0, max_value=35.0, value=26.7,
            step=0.1, format="%.1f", key="press_fr"
        )
        psi_rr = st.number_input(
            "Pressione RR (PSI)", min_value=20.0, max_value=35.0, value=26.7,
            step=0.1, format="%.1f", key="press_rr"
        )

    pressures = {"fl": psi_fl, "fr": psi_fr, "rl": psi_rl, "rr": psi_rr}

    st.markdown(
        '<h3 style="font-family:\'Orbitron\',monospace;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:#fff;'
        'border-left:3px solid #E10600;padding-left:12px;margin-bottom:16px;">'
        'B — Input Temperature Gomme</h3>',
        unsafe_allow_html=True
    )
    row2 = st.columns([1, 1])
    with row2[0]:
        temp_fl = st.number_input(
            "Temp. FL (°C)", min_value=0, max_value=150, value=85, step=1, key="temp_fl"
        )
        temp_rl = st.number_input(
            "Temp. RL (°C)", min_value=0, max_value=150, value=85, step=1, key="temp_rl"
        )
    with row2[1]:
        temp_fr = st.number_input(
            "Temp. FR (°C)", min_value=0, max_value=150, value=85, step=1, key="temp_fr"
        )
        temp_rr = st.number_input(
            "Temp. RR (°C)", min_value=0, max_value=150, value=85, step=1, key="temp_rr"
        )

    temperatures = {"fl": temp_fl, "fr": temp_fr, "rl": temp_rl, "rr": temp_rr}
    csv_data = st.session_state.get("csv_data")

    st.markdown(
        '<h3 style="font-family:\'Orbitron\',monospace;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:#fff;'
        'border-left:3px solid #E10600;padding-left:12px;margin-bottom:16px;">'
        'B bis — Visualizzazione Live Gomme</h3>',
        unsafe_allow_html=True
    )

    # FIX 2: Estrai pressioni dal CSV se disponibile, altrimenti usa input manuale
    def _pressure_value(key: str, csv_key: str, default: float) -> float:
        current = float(st.session_state.get(key, default))
        if (
            current == default
            and csv_data is not None
            and csv_data.get("pressures")
        ):
            csv_val = csv_data["pressures"].get(csv_key)
            if isinstance(csv_val, dict) and "avg" in csv_val:
                return float(csv_val["avg"])
            if isinstance(csv_val, (int, float)):
                return float(csv_val)
        return current

    def _temperature_value(key: str, csv_key: str, default: float) -> float:
        current = float(st.session_state.get(key, default))
        if (
            current == default
            and csv_data is not None
            and csv_data.get("temperatures")
        ):
            csv_val = csv_data["temperatures"].get(csv_key)
            if isinstance(csv_val, dict) and "avg" in csv_val:
                return float(csv_val["avg"])
            if isinstance(csv_val, (int, float)):
                return float(csv_val)
        return current

    fl_p = _pressure_value("press_fl", "fl", 26.7)
    fr_p = _pressure_value("press_fr", "fr", 26.7)
    rl_p = _pressure_value("press_rl", "rl", 26.7)
    rr_p = _pressure_value("press_rr", "rr", 26.7)

    tfl = _temperature_value("temp_fl", "fl", 88.0)
    tfr = _temperature_value("temp_fr", "fr", 90.0)
    trl = _temperature_value("temp_rl", "rl", 95.0)
    trr = _temperature_value("temp_rr", "rr", 102.0)

    # Renderizza HTML pressioni e temperature
    pressure_html = render_pressure_gauges(fl_p, fr_p, rl_p, rr_p, hot_mode=hot_mode)
    temperature_html = render_temperature_gauges(
        float(tfl),
        float(tfr),
        float(trl),
        float(trr),
        csv_loaded=(csv_data is not None and csv_data.get("temperatures") is not None),
    )

    # FIX 4: Card LIVE GOMME strutturata con header e footer visivi
    st.markdown(
        """<div style="background:#0f0f0f;border:1px solid #333;border-radius:8px;
        padding:16px 16px 4px 16px;margin-bottom:18px;">
            <div style="font-family:'Orbitron',monospace;font-size:1rem;
            font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
            color:#fff;margin-bottom:12px;">🏁 LIVE GOMME</div>
        </div>""",
        unsafe_allow_html=True
    )

    # I due widget affiancati dentro st.columns
    gauge_columns = st.columns(2)
    with gauge_columns[0]:
        components.html(pressure_html, height=340)
    with gauge_columns[1]:
        components.html(temperature_html, height=320)

    # Chiusura visiva della card (sottile linea inferiore)
    st.markdown(
        '<div style="border-top:1px solid #222;margin-top:4px;'
        'margin-bottom:18px;"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<h3 style="font-family:\'Orbitron\',monospace;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:#fff;'
        'border-left:3px solid #E10600;padding-left:12px;margin-bottom:16px;">'
        'AVANZATA — Parametri Tweaker Mode</h3>',
        unsafe_allow_html=True
    )
    with st.expander("⚙️ Parametri Avanzati — Tweaker Mode", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            camber_front = st.number_input(
                "Camber Ant. (°)", min_value=-4.0, max_value=-1.0, value=-2.0, step=0.1
            )
            camber_rear = st.number_input(
                "Camber Post. (°)", min_value=-3.5, max_value=-0.5, value=-1.8, step=0.1
            )
        with col2:
            brake_bias = st.slider("Brake Bias (%)", 50, 70, 56, step=1)
            diff_preload = st.number_input(
                "Precarico Diff. (Nm)", min_value=20, max_value=100, value=65, step=5
            )
        with col3:
            tc1 = st.select_slider("TC1", options=list(range(0, 12)), value=3)
            tc2 = st.select_slider("TC2", options=list(range(0, 12)), value=2)
            abs_level = st.select_slider("ABS", options=list(range(0, 12)), value=4)

        st.caption(
            "Questi parametri vengono raccolti per lo storico, ma non vengono inviati "
            "all'LLM nell'MVP. In una versione successiva possono essere persistiti "
            "nella tabella sessions del database."
        )

    st.markdown(
        '<h3 style="font-family:\'Orbitron\',monospace;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:#fff;'
        'border-left:3px solid #E10600;padding-left:12px;margin-bottom:16px;">'
        'C — Feedback Pilota</h3>',
        unsafe_allow_html=True
    )
    pilot_feedback = st.text_area(
        "📻 Descrivi il problema in pista",
        placeholder=(
            "Es: 'Sovrasterzo in uscita dalle curve lente, "
            "specialmente al T1. La posteriore destra perde aderenza "
            "prima che io possa riaprire il gas.'"
        ),
        height=120,
    )

    st.markdown(
        '<h3 style="font-family:\'Orbitron\',monospace;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:#fff;'
        'border-left:3px solid #E10600;padding-left:12px;margin-bottom:16px;">'
        'D — Upload CSV (opzionale)</h3>',
        unsafe_allow_html=True
    )
    csv_file = st.file_uploader("📂 Carica CSV Sessione ACC (opzionale)", type=["csv"])
    csv_data = st.session_state.get("csv_data")

    if csv_file is not None:
        try:
            raw_bytes = csv_file.read()
            csv_data = parse_session_csv(BytesIO(raw_bytes))
            st.session_state["csv_data"] = csv_data
            st.dataframe(
                pd.read_csv(BytesIO(raw_bytes)).head(5),
                height=150,
            )
            st.markdown(
                '<h3 style="font-family:\'Orbitron\',monospace;font-weight:700;'
                'letter-spacing:0.08em;text-transform:uppercase;color:#fff;'
                'border-left:3px solid #E10600;padding-left:12px;margin-bottom:16px;">'
                'Andamento Temperature per Giro</h3>',
                unsafe_allow_html=True
            )
            render_temperature_chart(csv_data)
        except CSVParseError as exc:
            st.warning(f"CSV non valido: {exc}")
        except Exception:
            st.warning("Impossibile leggere il CSV. Verifica il formato e riprova.")

    st.divider()

    analyze_clicked = st.button("🔍 ANALIZZA SESSIONE", use_container_width=True)
    if analyze_clicked:
        invalid_pressure = [
            p for p in pressures.values()
            if not ACCPhysicsEngine.validate_pressure_context(p, ctx)
        ]
        invalid_temp = [t for t in temperatures.values() if not validate_temperature(t)]

        if invalid_pressure:
            range_name = "freddo" if ctx == "cold" else "caldo"
            st.error(
                f"Verifica le pressioni: alcuni valori non rientrano nel range "
                f"consentito per la pressione a {range_name}."
            )
            return
        if invalid_temp:
            st.error(
                "Verifica le temperature: alcuni valori non rientrano nel range "
                "operativo previsto per le gomme."
            )
            return
        if not pilot_feedback.strip():
            st.error("Inserisci il feedback del pilota prima di avviare l'analisi.")
            return

        with st.spinner("Analisi in corso — Race Engineer al lavoro..."):
            session_payload = {
                "car": sidebar_data.get("car"),
                "track": sidebar_data.get("track"),
                "conditions": sidebar_data.get("conditions"),
                "ambient_temp": sidebar_data.get("ambient_temp"),
                "track_temp": sidebar_data.get("track_temp"),
                "pressures": pressures,
                "temperatures": temperatures,
            }
            engine = ClaudeEngine()
            try:
                markdown_response = engine.generate_commentary(session_payload, pilot_feedback)
            except Exception as exc:
                st.error(f"Errore durante la chiamata AI: {exc}")
                return

        target = (
            ACCPhysicsEngine.CONSTANTS.TARGET_PRESSURE_COLD
            if ctx == "cold"
            else ACCPhysicsEngine.CONSTANTS.HOT_PRESSURE_TARGET
        )
        delta_target = sum(p - target for p in pressures.values()) / 4
        max_delta = max(abs(p - target) for p in pressures.values())
        status = (
            "OTTIMALE"
            if max_delta <= 0.3
            else "ATTENZIONE"
            if max_delta <= 0.7
            else "CRITICO"
        )

        physics_data = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "car": sidebar_data.get("car"),
            "track": sidebar_data.get("track"),
            "psi_media": round(sum(pressures.values()) / 4, 2),
            "delta_target": round(delta_target, 2),
            "temp_media": round(sum(temperatures.values()) / 4, 1),
            "status": status,
        }

        try:
            from components.engineer_report import render_engineer_report

            render_engineer_report(markdown_response, physics_data)
            suggested_psi = extract_suggested_psi(markdown_response)

            # Salva la sessione nel database per lo storico
            db = SessionDatabase()
            try:
                db.init_db()
                db.save_session({
                    "timestamp": physics_data["timestamp"],
                    "car": sidebar_data.get("car"),
                    "track": sidebar_data.get("track"),
                    "psi_input": pressures,
                    "psi_suggested": suggested_psi,
                    "temp_ambient": sidebar_data.get("ambient_temp"),
                    "temp_track": sidebar_data.get("track_temp"),
                    "feedback_text": pilot_feedback,
                    "llm_response": markdown_response,
                })
            except Exception as exc:
                st.warning(f"Impossibile salvare la sessione nello storico: {exc}")
            finally:
                db.close()
        except ImportError:
            st.error(
                "Componente report non disponibile. Verificare che components/engineer_report.py "
                "sia presente e importabile nel progetto."
            )
