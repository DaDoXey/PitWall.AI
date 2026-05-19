import streamlit as st
from components.header import render_header


st.set_page_config(page_title="PitWall.AI Header Verify", layout="wide")

st.title("Verifica Header")

st.write("Questo script mostra lo stato DB online/offline per validare il badge.")

st.markdown("---")

st.header("DB Online")
render_header(db_status=True)

st.markdown("---")

st.header("DB Offline")
render_header(db_status=False)
