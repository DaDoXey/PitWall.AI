import streamlit as st


def render_header(db_status: bool) -> None:
    """Renderizza l'header logo di PitWall.AI con design motorsport.

    Gradiente scuro, pattern bandiera a scacchi e gradiente testo.
    Mantiene il componente UI separato da logica e calcoli fisici.

    Args:
        db_status: True se il database SQLite è raggiungibile,
                   False altrimenti.
    """
    db_label = (
        '<span style="color:#00FF87;">● DB ONLINE</span>'
        if db_status
        else '<span style="color:#FF3131;">● DB OFFLINE</span>'
    )

    st.markdown(
        f"""
        <div class="pitwall-header-wrapper">
            <span class="pitwall-logo-badge">MVP</span>
            <h1 class="pitwall-logo-title">PITWALL.AI</h1>
            <p class="pitwall-logo-subtitle">
                Virtual Race Engineer &nbsp;·&nbsp; ACC v1.9+
            </p>
            <span class="pitwall-db-status">{db_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
