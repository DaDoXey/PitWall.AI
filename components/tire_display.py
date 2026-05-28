from typing import Dict


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _fill_percentage(value: float, minimum: float, maximum: float) -> int:
    if maximum <= minimum:
        return 0
    scaled = (value - minimum) / (maximum - minimum) * 100
    return max(0, min(100, int(round(scaled))))


def _pressure_fill_color(value: float) -> str:
    if value < 26.0:
        return "#E53935"
    if value <= 27.5:
        return "#00E676"
    if value <= 28.5:
        return "#FFD600"
    return "#FF6D00"


def _temperature_fill_color(value: float) -> str:
    if value < 75.0:
        return "#2196F3"
    if value <= 95.0:
        return "#00E676"
    if value <= 105.0:
        return "#FFD600"
    return "#E53935"


def _pressure_delta_html(value: float, target: float = 26.7) -> str:
    delta = round(value - target, 1)
    delta_text = f"{delta:+.1f} PSI"
    if delta == 0.0:
        color = "#00E676"
    elif delta < 0.0:
        color = "#E53935"
    elif delta > 0.5:
        color = "#FF6D00"
    else:
        color = "#00E676"
    return f"<div class='pitwall-gauge-delta' style='color:{color};'>{delta_text}</div>"


def _render_tire_gauge(
    label: str,
    value: float,
    minimum: float,
    maximum: float,
    fill_color: str,
    unit: str,
    delta_html: str = "",
) -> str:
    percent = _fill_percentage(value, minimum, maximum)
    return (
        "<div class='pitwall-gauge-column'>"
        "<div class='pitwall-gauge'>"
        f"<div class='pitwall-gauge-fill' style='height:{percent}%;background:{fill_color};'></div>"
        "</div>"
        f"<div class='pitwall-gauge-label'>{label}</div>"
        f"<div class='pitwall-gauge-value'>{value:.1f} {unit}</div>"
        f"{delta_html}"
        "</div>"
    )


def render_pressure_gauges(fl: float, fr: float, rl: float, rr: float) -> str:
    return (
        "<div class='pitwall-gauge-title'>PRESSIONE GOMME</div>"
        "<div class='pitwall-pressure-layout'>"
        "<div class='pitwall-pressure-side'>"
        f"{_render_tire_gauge('FL', fl, 25.0, 29.0, _pressure_fill_color(fl), 'PSI', _pressure_delta_html(fl))}"
        f"{_render_tire_gauge('RL', rl, 25.0, 29.0, _pressure_fill_color(rl), 'PSI', _pressure_delta_html(rl))}"
        "</div>"
        "<div class='pitwall-divider'><span class='pitwall-divider-text'>VISTA DALL&apos;ALTO</span></div>"
        "<div class='pitwall-pressure-side'>"
        f"{_render_tire_gauge('FR', fr, 25.0, 29.0, _pressure_fill_color(fr), 'PSI', _pressure_delta_html(fr))}"
        f"{_render_tire_gauge('RR', rr, 25.0, 29.0, _pressure_fill_color(rr), 'PSI', _pressure_delta_html(rr))}"
        "</div>"
        "</div>"
    )


def render_temperature_gauges(
    fl: float,
    fr: float,
    rl: float,
    rr: float,
    csv_loaded: bool = False,
) -> str:
    note_html = ""
    if not csv_loaded:
        note_html = (
            "<div class='pitwall-widget-note'>"
            "Dati CSV non caricati — valori di esempio"
            "</div>"
        )
    return (
        "<div class='pitwall-gauge-title'>🌡️ TEMPERATURE GOMME</div>"
        "<div class='pitwall-temperature-layout'>"
        "<div class='pitwall-pressure-side'>"
        f"{_render_tire_gauge('FL', fl, 60.0, 120.0, _temperature_fill_color(fl), '°C')}"
        f"{_render_tire_gauge('RL', rl, 60.0, 120.0, _temperature_fill_color(rl), '°C')}"
        "</div>"
        "<div class='pitwall-divider'><span class='pitwall-divider-text'>VISTA DALL&apos;ALTO</span></div>"
        "<div class='pitwall-pressure-side'>"
        f"{_render_tire_gauge('FR', fr, 60.0, 120.0, _temperature_fill_color(fr), '°C')}"
        f"{_render_tire_gauge('RR', rr, 60.0, 120.0, _temperature_fill_color(rr), '°C')}"
        "</div>"
        "</div>"
        f"{note_html}"
    )


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
