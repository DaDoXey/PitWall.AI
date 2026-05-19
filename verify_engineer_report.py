import streamlit as st

from components.engineer_report import render_engineer_report


def main() -> None:
    st.set_page_config(page_title="PitWall.AI Report Verify", layout="wide")
    st.title("Verifica Engineer Report")

    markdown_response = (
        "# Analisi Sessione\n"
        "## Correzione Setup Consigliata\n"
        "Aumenta la pressione anteriore di 0.3 PSI e abbassa il retro di 0.2 PSI. "
        "Controlla il bilanciamento delle sospensioni e mantieni la temperatura tra 85-95°C.\n"
        "## Note\n"
        "Il pilota ha segnalato sovrasterzo in uscita dalle curve veloci."
    )

    physics_data = {
        "timestamp": "2026-05-14 12:00:00 UTC",
        "car": "Ferrari 296 GT3",
        "track": "Monza",
        "psi_media": 26.4,
        "delta_target": -0.3,
        "temp_media": 88.5,
        "status": "ATTENZIONE",
    }

    render_engineer_report(markdown_response, physics_data)


if __name__ == "__main__":
    main()
