import streamlit as st


def inject_css() -> None:
    """Inietta style.css nell'app Streamlit.

    Streamlit non fornisce un metodo nativo per includere file CSS esterni
    nell'interfaccia. Per questo motivo usiamo st.markdown con HTML inline.
    `unsafe_allow_html=True` abilita l'interpretazione del tag <style>.
    """
    with open("assets/style.css", "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
