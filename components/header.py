import streamlit as st


def render_header(db_status: bool) -> None:
    """Renderizza l'header principale dell'app con stato del DB.

    Separare i componenti UI in file distinti mantiene app.py snella e
    facilita il testing e la manutenzione. Qui non ci sono calcoli fisici
    né chiamate AI, solo rendering dell'interfaccia.
    """
    col_left, col_right = st.columns([3, 1])

    with col_left:
        st.markdown(
            """
            <div style='display:flex;flex-direction:column;gap:6px;'>
                <span style='font-size:1.8rem;font-weight:700;letter-spacing:-0.02em;'
                      >PITWALL.AI</span>
                <span style='color:var(--text-secondary);font-size:0.95rem;'
                      >Virtual Race Engineer — ACC v1.9+</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    status_class = "status-online" if db_status else "status-offline"
    status_label = "● DB ONLINE" if db_status else "● DB OFFLINE"

    with col_right:
        st.markdown(
            f"""
            <div style='display:flex;justify-content:flex-end;'>
                <span class='status-badge {status_class}'>
                    {status_label}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
