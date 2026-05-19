import streamlit as st

from assets.css_loader import inject_css
from backend.database.manager import SessionDatabase
from components.header import render_header
from components.sidebar import render_sidebar
from components.tab_fuel import render_tab_fuel
from components.tab_history import render_tab_history
from components.tab_setup import render_tab_setup


st.set_page_config(
    page_title="PitWall.AI",
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

    render_header(db_status)
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
