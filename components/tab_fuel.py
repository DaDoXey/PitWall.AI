import streamlit as st
from backend.core import calculate_fuel_load
from typing import Dict


def _parse_lap_time(value: str) -> float:
    """Converte un tempo giro in formato mm:ss in minuti float.

    Questo parsing è deterministico e non coinvolge l'LLM.
    """
    try:
        parts = value.strip().split(":")
        if len(parts) != 2:
            raise ValueError("Formato non valido")
        minutes = int(parts[0])
        seconds = int(parts[1])
        if seconds < 0 or seconds >= 60:
            raise ValueError("Secondi non validi")
        return minutes + seconds / 60.0
    except Exception as exc:
        raise ValueError(
            "Formato tempo giro non valido. Usa mm:ss, ad esempio 1:52."
        ) from exc


def render_tab_fuel() -> None:
    """Renderizza il tab carburante usando solo calcoli deterministici.

    Questo componente non invoca l'LLM: sfrutta esclusivamente la funzione
    `calculate_fuel_load` in backend/core/physics.py.
    """
    st.markdown(
        '<h2 style="font-family:\'Orbitron\',monospace;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:#fff;'
        'border-left:3px solid #E10600;padding-left:12px;margin-bottom:16px;">'
        'Strategia Carburante</h2>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        race_duration = st.number_input(
            "Durata Gara (min)",
            min_value=5,
            max_value=180,
            value=60,
            step=1,
        )
    with col2:
        lap_time_text = st.text_input(
            "Tempo Giro Medio (mm:ss)", value="1:52"
        )
    with col3:
        fuel_per_lap = st.number_input(
            "Consumo/Giro (L)",
            min_value=1.0,
            max_value=6.0,
            value=3.2,
            step=0.1,
        )

    compute_clicked = st.button("⛽ CALCOLA CARICO CARBURANTE")

    if compute_clicked:
        try:
            lap_time_min = _parse_lap_time(lap_time_text)
        except ValueError as exc:
            st.warning(str(exc))
            return

        try:
            result = calculate_fuel_load(
                race_duration_min=float(race_duration),
                lap_time_min=lap_time_min,
                fuel_cons_per_lap=float(fuel_per_lap),
            )
        except ValueError as exc:
            st.error(str(exc))
            return

        st.markdown("### Risultati")
        m1, m2, m3 = st.columns(3)
        m1.metric("Giri Totali Stimati", str(result["laps_needed"]))
        m2.metric("Carburante Base (L)", f"{result['fuel_needed_L']:.2f}")
        m3.metric(
            "Carico Consigliato +5% (L)",
            f"{result['fuel_recommended_L']:.2f}",
        )

        formula_text = (
            "ceil(durata_gara / tempo_giro) × consumo_per_giro × 1.05"
        )
        st.code(
            f"{formula_text}\n"
            f"= ceil({race_duration} / {lap_time_min:.3f}) × {fuel_per_lap:.1f} × 1.05\n"
            f"= {result['laps_needed']} × {fuel_per_lap:.1f} × 1.05\n"
            f"= {result['fuel_recommended_L']:.2f} L",
            language="python",
        )
