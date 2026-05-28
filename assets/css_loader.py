import streamlit as st


def inject_css() -> None:
    """Inietta style.css nell'app Streamlit.

    Streamlit non fornisce un metodo nativo per includere file CSS esterni
    nell'interfaccia. Per questo motivo usiamo st.markdown con HTML inline.
    `unsafe_allow_html=True` abilita l'interpretazione del tag <style>.
    """
    with open("assets/style.css", "r", encoding="utf-8") as f:
        css = f.read()
    font_link = (
        '<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;500;600&display=swap" '
        'rel="stylesheet">'
    )
    st.markdown(f"{font_link}<style>{css}</style>", unsafe_allow_html=True)
