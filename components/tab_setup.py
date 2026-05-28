import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Optional

from backend.core import (
    ACCPhysicsEngine,
    ClaudeEngine,
    validate_pressure,
    validate_temperature,
)
from backend.database.manager import SessionDatabase
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
    st.markdown("## Analisi Setup")

    st.markdown("#### A — Input Pressioni")

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

    row1 = st.columns([1, 1])
    with row1[0]:
        psi_fl = st.number_input(
            "Pressione FL (PSI)", min_value=20.0, max_value=35.0, value=26.7,
            step=0.1, format="%.1f"
        )
        psi_rl = st.number_input(
            "Pressione RL (PSI)", min_value=20.0, max_value=35.0, value=26.7,
            step=0.1, format="%.1f"
        )
    with row1[1]:
        psi_fr = st.number_input(
            "Pressione FR (PSI)", min_value=20.0, max_value=35.0, value=26.7,
            step=0.1, format="%.1f"
        )
        psi_rr = st.number_input(
            "Pressione RR (PSI)", min_value=20.0, max_value=35.0, value=26.7,
            step=0.1, format="%.1f"
        )

    pressures = {"fl": psi_fl, "fr": psi_fr, "rl": psi_rl, "rr": psi_rr}

    st.markdown("#### B — Input Temperature Gomme")
    row2 = st.columns([1, 1])
    with row2[0]:
        temp_fl = st.number_input(
            "Temp. FL (°C)", min_value=0, max_value=150, value=85, step=1
        )
        temp_rl = st.number_input(
            "Temp. RL (°C)", min_value=0, max_value=150, value=85, step=1
        )
    with row2[1]:
        temp_fr = st.number_input(
            "Temp. FR (°C)", min_value=0, max_value=150, value=85, step=1
        )
        temp_rr = st.number_input(
            "Temp. RR (°C)", min_value=0, max_value=150, value=85, step=1
        )

    temperatures = {"fl": temp_fl, "fr": temp_fr, "rl": temp_rl, "rr": temp_rr}
    csv_data = st.session_state.get("csv_data")

    st.markdown("#### B bis — Visualizzazione Live Gomme")
    pressure_values = (
        csv_data.get("pressures")
        if csv_data and csv_data.get("pressures")
        else pressures
    )
    temperature_values = (
        csv_data.get("temperatures")
        if csv_data and csv_data.get("temperatures")
        else None
    )

    pressure_html = render_pressure_gauges(
        pressure_values["fl"],
        pressure_values["fr"],
        pressure_values["rl"],
        pressure_values["rr"],
    )

    if temperature_values:
        temperature_html = render_temperature_gauges(
            temperature_values["fl"],
            temperature_values["fr"],
            temperature_values["rl"],
            temperature_values["rr"],
            csv_loaded=True,
        )
    else:
        temperature_html = render_temperature_gauges(
            88.0,
            90.0,
            95.0,
            102.0,
            csv_loaded=False,
        )

    st.markdown(
        "<div class='pitwall-live-gomme-card'>"
        "<div class='pitwall-live-gomme-header'>🏁 LIVE GOMME</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    gauge_columns = st.columns(2)
    with gauge_columns[0]:
        st.markdown(
            f"<div class='pitwall-live-gomme-panel'>{pressure_html}</div>",
            unsafe_allow_html=True,
        )
    with gauge_columns[1]:
        st.markdown(
            f"<div class='pitwall-live-gomme-panel'>{temperature_html}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("#### AVANZATA — Parametri Tweaker Mode")
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

    st.markdown("#### C — Feedback Pilota")
    pilot_feedback = st.text_area(
        "📻 Descrivi il problema in pista",
        placeholder=(
            "Es: 'Sovrasterzo in uscita dalle curve lente, "
            "specialmente al T1. La posteriore destra perde aderenza "
            "prima che io possa riaprire il gas.'"
        ),
        height=120,
    )

    st.markdown("#### D — Upload CSV (opzionale)")
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
            st.markdown("#### Andamento Temperature per Giro")
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
            
            # Salva la sessione nel database per lo storico
            db = SessionDatabase()
            try:
                db.init_db()
                db.save_session({
                    "timestamp": physics_data["timestamp"],
                    "car": sidebar_data.get("car"),
                    "track": sidebar_data.get("track"),
                    "psi_input": pressures,
                    "psi_suggested": None,  # MVP: non calcolato, aggiungere in futuro
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
