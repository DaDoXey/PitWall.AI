import streamlit as st

from components.temp_chart import render_temperature_chart


def main() -> None:
    st.set_page_config(page_title="PitWall.AI Temp Chart Verify", layout="wide")
    st.title("Verifica Grafico Temperature")

    sample_data = {
        "lap": [1, 2, 3, 4, 5],
        "temperature_series": {
            "fl": [83, 85, 86, 88, 87],
            "fr": [82, 84, 85, 87, 86],
            "rl": [78, 80, 82, 83, 84],
            "rr": [88, 89, 91, 93, 94],
        },
    }

    render_temperature_chart(sample_data)


if __name__ == "__main__":
    main()
