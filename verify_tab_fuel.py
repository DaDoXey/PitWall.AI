import streamlit as st

from components.tab_fuel import render_tab_fuel


def main() -> None:
    st.set_page_config(page_title="PitWall.AI Fuel Tab Verify", layout="wide")
    st.title("Verifica Tab Fuel")
    render_tab_fuel()


if __name__ == "__main__":
    main()
