import streamlit as st

from components.tab_history import render_tab_history


def main() -> None:
    st.set_page_config(page_title="PitWall.AI History Tab Verify", layout="wide")
    st.title("Verifica Tab Storico")
    render_tab_history()


if __name__ == "__main__":
    main()
