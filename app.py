import streamlit as st

from assets.css_loader import inject_css
from backend.database.manager import SessionDatabase
from components.sidebar import render_sidebar
from components.tab_fuel import render_tab_fuel
from components.tab_history import render_tab_history
from components.tab_setup import render_tab_setup


st.set_page_config(
    page_title="PitWall.AI",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()


def main() -> None:
    """Orchestra l'app Streamlit mantenendo la logica nei componenti.

    app.py resta leggero: carica i componenti, verifica il DB e gestisce
    il layout principale. Tutta la fisica e le chiamate AI sono delegate.
    """
    db_status = True
    db = SessionDatabase()
    try:
        db.init_db()
    except Exception:
        db_status = False
    finally:
        db.close()

    page_status = (
        '<span style="color:#00FF87;">● DB ONLINE</span>'
        if db_status
        else '<span style="color:#FF3131;">● DB OFFLINE</span>'
    )

    st.markdown(
        f"""
        <div class="pitwall-logo-header">
            <span class="logo-flag">🏁</span>
            <div>
                <div class="logo-text">PitWall<span class="logo-accent">.AI</span></div>
                <div class="logo-subtitle">Virtual Race Engineer — ACC GT3</div>
            </div>
            <span class="pitwall-db-status">{page_status}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sidebar_data = render_sidebar()

    tab1, tab2, tab3 = st.tabs(
        ["🔧 Analisi Setup", "⛽ Strategia Carburante", "📋 Storico Sessioni"]
    )

    with tab1:
        render_tab_setup(sidebar_data)
    with tab2:
        render_tab_fuel()
    with tab3:
        render_tab_history()


if __name__ == "__main__":
    main()
