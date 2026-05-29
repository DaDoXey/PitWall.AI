import streamlit as st
from typing import Any, Dict, List, Optional

from backend.database.manager import SessionDatabase


@st.cache_data(ttl=30)
def fetch_sessions() -> List[Dict[str, Any]]:
    """Recupera le sessioni dal database con cache a breve termine.

    ttl=30 secondi è appropriato perché lo storico cambia poco spesso ma
    vogliamo comunque un refresh rapido dopo modifiche manuali o inserimenti.
    """
    db = SessionDatabase()
    db.init_db()
    sessions = db.get_recent_sessions(limit=100)
    db.close()
    return sessions


def _average_pressure(pressure_data: Optional[Dict[str, Any] | float]) -> Optional[float]:
    if pressure_data is None:
        return None
    if isinstance(pressure_data, (int, float)):
        return float(pressure_data)
    values = [v for v in pressure_data.values() if isinstance(v, (int, float))]
    if not values:
        return None
    return sum(values) / len(values)


def render_tab_history() -> None:
    """Renderizza il tab storico sessioni con filtri e dettaglio espandibile.

    La query al database è memorizzata con @st.cache_data(ttl=30) per evitare
    chiamate ripetute su reload rapido, ma può essere invalidata manualmente.
    """
    st.markdown(
        '<h2 style="font-family:\'Orbitron\',monospace;font-weight:700;'
        'letter-spacing:0.08em;text-transform:uppercase;color:#fff;'
        'border-left:3px solid #E10600;padding-left:12px;margin-bottom:16px;">'
        'Storico Sessioni</h2>',
        unsafe_allow_html=True
    )

    refresh_button = st.button("🔄 Aggiorna")
    if refresh_button:
        fetch_sessions.clear()

    sessions = fetch_sessions()
    cars = ["Tutte"] + sorted(
        {session["car"] for session in sessions if session.get("car") is not None}
    )
    tracks = ["Tutti"] + sorted(
        {session["track"] for session in sessions if session.get("track") is not None}
    )

    filter_cols = st.columns(3)
    with filter_cols[0]:
        selected_car = st.selectbox("Filtra per Auto", cars)
    with filter_cols[1]:
        selected_track = st.selectbox("Filtra per Tracciato", tracks)
    with filter_cols[2]:
        st.write("")

    filtered_sessions = [
        session
        for session in sessions
        if (selected_car == "Tutte" or session.get("car") == selected_car)
        and (selected_track == "Tutti" or session.get("track") == selected_track)
    ]

    if not filtered_sessions:
        st.info("Nessuna sessione trovata per i filtri selezionati.")
        return

    table_rows = []
    for session in filtered_sessions:
        psi_input_avg = _average_pressure(session.get("psi_input"))
        psi_suggested_avg = _average_pressure(session.get("psi_suggested"))
        table_rows.append(
            {
                "Timestamp": session.get("timestamp"),
                "Auto": session.get("car"),
                "Tracciato": session.get("track"),
                "PSI Input Media": f"{psi_input_avg:.2f}" if psi_input_avg is not None else "N/A",
                "PSI Suggerita Media": f"{psi_suggested_avg:.2f}" if psi_suggested_avg is not None else "N/A",
                "Problema Dichiarato": session.get("feedback_text") or "",
                "Session ID": session.get("session_id"),
            }
        )

    st.dataframe(table_rows, use_container_width=True, height=400)

    session_ids = [row["Session ID"] for row in table_rows]
    selected_session_id = st.selectbox(
        "Seleziona sessione", [""] + session_ids
    )

    if selected_session_id:
        selected_session = next(
            (session for session in filtered_sessions if session.get("session_id") == selected_session_id),
            None,
        )
        if selected_session:
            with st.expander("Dettaglio sessione selezionata", expanded=True):
                st.markdown(f"**Timestamp:** {selected_session.get('timestamp')}")
                st.markdown(f"**Auto:** {selected_session.get('car')}")
                st.markdown(f"**Tracciato:** {selected_session.get('track')}")
                st.markdown(f"**Feedback:** {selected_session.get('feedback_text')}")
                st.markdown("### Report completo")
                st.markdown(selected_session.get("llm_response") or "Nessun report disponibile.")
