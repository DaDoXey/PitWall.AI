import streamlit as st
from typing import Dict, Any


def render_sidebar() -> Dict[str, Any]:
    """Renderizza la sidebar e restituisce le selezioni dell'utente.

    Separando la sidebar in un componente dedicato manteniamo app.py come
    orchestratore e riduciamo il coupling con la logica di configurazione.
    """
    st.sidebar.markdown(
        """
        <div style='font-size:1.1rem;font-weight:700;letter-spacing:-0.02em;'>
            PITWALL.AI SESSIONE
        </div>
        """,
        unsafe_allow_html=True,
    )

    car_choice = st.sidebar.selectbox(
        "🏎 Auto",
        [
            "BMW M4 GT3",
            "Ferrari 296 GT3",
            "Porsche 992 GT3-R",
            "Lamborghini Huracán GT3 EVO2",
            "McLaren 720S GT3",
        ],
    )

    track_choice = st.sidebar.selectbox(
        "🏁 Tracciato",
        [
            "Monza",
            "Spa-Francorchamps",
            "Nürburgring GP",
            "Silverstone",
            "Misano",
            "Zandvoort",
            "Barcelona",
        ],
    )

    conditions_choice = st.sidebar.selectbox(
        "🌤 Condizioni",
        ["Asciutto", "Bagnato", "In Asciugamento"],
    )

    st.sidebar.divider()

    ambient_temp = st.sidebar.number_input(
        "Temp. Ambiente (°C)", min_value=0, max_value=45, value=20, step=1
    )
    track_temp = st.sidebar.number_input(
        "Temp. Pista (°C)", min_value=0, max_value=65, value=30, step=1
    )

    st.sidebar.divider()

    st.sidebar.markdown(
        """
        <div style='color:var(--text-secondary);font-size:0.85rem;line-height:1.6;'>
            Versione app: 0.1.0<br>
            <a href='https://github.com/' style='color:var(--accent-blue);'
               target='_blank'>GitHub</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return {
        "car": car_choice,
        "track": track_choice,
        "conditions": conditions_choice,
        "ambient_temp": ambient_temp,
        "track_temp": track_temp,
    }
