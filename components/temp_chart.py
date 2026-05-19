import pandas as pd
import plotly.express as px
import streamlit as st
from typing import Any, Dict, Optional


def render_temperature_chart(csv_data: Optional[Dict[str, Any]]) -> None:
    """Renderizza un grafico temperature gomme da un dataset ACC.

    Plotly Express è preferito in Streamlit perché offre integrazione
    diretta con `st.plotly_chart`, interattività nativa e stile dark-ready
    senza richiedere un layer di configurazione aggiuntiva come in Matplotlib.
    """
    if csv_data is None:
        st.info("Carica un CSV per visualizzare l'andamento temperature.")
        return

    if not csv_data.get("lap") or not csv_data.get("temperature_series"):
        st.warning(
            "I dati CSV non contengono la serie di temperature necessaria."
        )
        return

    lap_values = csv_data["lap"]
    temp_series = csv_data["temperature_series"]
    data = {
        "lap": lap_values,
        "FL": temp_series.get("fl", []),
        "FR": temp_series.get("fr", []),
        "RL": temp_series.get("rl", []),
        "RR": temp_series.get("rr", []),
    }
    df_plot = pd.DataFrame(data)

    fig = px.line(
        df_plot,
        x="lap",
        y=["FL", "FR", "RL", "RR"],
        labels={
            "lap": "Giro",
            "value": "Temperature (°C)",
            "variable": "Pneumatico",
        },
        title="Andamento Temperature Gomma per Giro",
        color_discrete_map={
            "FL": "#00FF87",
            "FR": "#00A3FF",
            "RL": "#FFD600",
            "RR": "#FF3131",
        },
    )

    fig.update_layout(
        paper_bgcolor="#1A1A1A",
        plot_bgcolor="#0D0D0D",
        font=dict(color="#F0F0F0"),
        legend=dict(bgcolor="#1A1A1A"),
        margin=dict(t=60, b=40, l=40, r=40),
    )
    fig.update_xaxes(gridcolor="#2E2E2E", showgrid=True)
    fig.update_yaxes(gridcolor="#2E2E2E", showgrid=True)

    fig.add_hline(
        y=75,
        line_dash="dash",
        line_color="#8A8A8A",
        annotation_text="Min Operativa",
        annotation_position="bottom left",
        annotation_font_color="#F0F0F0",
    )
    fig.add_hline(
        y=95,
        line_dash="dash",
        line_color="#FF3131",
        annotation_text="Max Operativa",
        annotation_position="bottom left",
        annotation_font_color="#FF3131",
    )

    st.plotly_chart(fig, use_container_width=True)
