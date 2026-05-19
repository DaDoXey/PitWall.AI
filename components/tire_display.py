import streamlit as st
from typing import Dict


def render_tire_grid(pressures: Dict[str, float], status: Dict[str, str]) -> None:
    """Renderizza una griglia 2x2 di indicatori gomme in stile dashboard.

    Streamlit non fornisce un vero CSS grid layout come HTML puro. Per
    creare una vista posizionale usiamo righe di `st.columns` annidate e
    contenitori HTML, che sono sufficienti per un layout 2x2 ma non per
    griglie molto complesse o overlay precisi.
    """
    target_psi = 26.7

    def format_tire_card(position: str, label: str) -> None:
        current_pressure = pressures.get(position, 0.0)
        current_status = status.get(position, "warning")
        delta = current_pressure - target_psi
        abs_delta = abs(delta)

        if abs_delta <= 0.3:
            delta_color = "var(--accent-green)"
        elif abs_delta <= 0.7:
            delta_color = "var(--accent-yellow)"
        elif current_status == "hot":
            delta_color = "var(--accent-red)"
        elif current_status == "cold":
            delta_color = "var(--accent-blue)"
        else:
            delta_color = "var(--accent-red)"

        delta_sign = "−" if delta < 0 else "+"
        delta_value = f"{delta_sign}{abs_delta:.1f} PSI"
        status_class = f"tire-{current_status}"

        st.markdown(
            f"""
            <div class='pitwall-tire-indicator {status_class}'>
                <div class='data-label'>{label}</div>
                <div class='data-value'>{current_pressure:.1f}</div>
                <div style='color:{delta_color};margin-top:8px;font-weight:600;'>
                    {delta_value}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    row_top = st.columns([1, 0.25, 1])
    with row_top[0]:
        format_tire_card("fl", "FL")
    with row_top[1]:
        st.markdown(
            """
            <div style='height:100%;display:flex;align-items:center;justify-content:center;'>
                <span style='writing-mode: vertical-rl; transform: rotate(180deg);'
                      >VISTA DALL&apos;ALTO</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with row_top[2]:
        format_tire_card("fr", "FR")

    row_bottom = st.columns([1, 0.25, 1])
    with row_bottom[0]:
        format_tire_card("rl", "RL")
    with row_bottom[1]:
        st.write("")
    with row_bottom[2]:
        format_tire_card("rr", "RR")
