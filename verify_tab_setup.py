import streamlit as st

from components.sidebar import render_sidebar
from components.tab_setup import render_tab_setup


st.set_page_config(page_title="PitWall.AI Tab Setup Verify", layout="wide")

st.title("Verifica Tab Setup")

st.write("Questo script verifica l'interfaccia del tab Analisi Setup.")

sidebar_data = render_sidebar()
render_tab_setup(sidebar_data)
