from typing import Dict


def _fill_percentage(value: float, minimum: float, maximum: float) -> int:
    if maximum <= minimum:
        return 0
    scaled = (value - minimum) / (maximum - minimum) * 100
    return max(0, min(100, int(round(scaled))))


def get_pressure_color(v: float, hot: bool) -> str:
    if hot:
        if v < 27.0:
            return "#E53935"
        elif v < 28.0:
            return "#FFD600"
        elif v <= 30.0:
            return "#00E676"
        else:
            return "#E53935"
    else:
        if v < 26.0:
            return "#E53935"
        elif v <= 27.5:
            return "#00E676"
        elif v <= 28.5:
            return "#FFD600"
        else:
            return "#FF6D00"


def _temperature_fill_color(value: float) -> str:
    if value < 75.0:
        return "#2196F3"
    if value <= 95.0:
        return "#00E676"
    if value <= 105.0:
        return "#FFD600"
    return "#E53935"


def _pressure_delta_text(value: float, target: float = 26.7) -> tuple[str, str]:
    delta = round(value - target, 1)
    delta_str = f"+{delta:.1f} PSI" if delta >= 0 else f"{delta:.1f} PSI"
    if delta == 0.0:
        color = "#00E676"
    elif delta < 0.0:
        color = "#E53935"
    elif delta > 0.5:
        color = "#FF6D00"
    else:
        color = "#FFD600"
    return delta_str, color


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
        "<div style='display:flex;flex-direction:column;align-items:center;gap:4px;'>"
        "<div style='width:36px;height:160px;background:#1a1a1a;border:1px solid #333;border-radius:18px;position:relative;overflow:hidden;'>"
        f"<div style='position:absolute;bottom:0;left:0;width:100%;height:{percent}%;background:{fill_color};border-radius:18px 18px 0 0;'></div>"
        "</div>"
        f"<span style='color:#fff;font-size:0.85rem;font-weight:700;letter-spacing:0.1em;'>{label}</span>"
        f"<span style='color:#fff;font-size:0.8rem;'>{value:.1f} {unit}</span>"
        f"{delta_html}"
        "</div>"
    )


def render_pressure_gauges(fl: float, fr: float, rl: float, rr: float, hot_mode: bool = False) -> str:
    ref_pressure = 28.8 if hot_mode else 26.7
    delta_fl, color_fl = _pressure_delta_text(fl, ref_pressure)
    delta_fr, color_fr = _pressure_delta_text(fr, ref_pressure)
    delta_rl, color_rl = _pressure_delta_text(rl, ref_pressure)
    delta_rr, color_rr = _pressure_delta_text(rr, ref_pressure)
    return (
        "<link href='https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap' rel='stylesheet'>"
        "<div style='background:#111;padding:16px;border-radius:8px;border:1px solid #333;font-family:&quot;Orbitron&quot;,monospace;overflow:visible;padding-bottom:20px;'>"
        "<div style='color:#fff;font-size:1rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:16px;'>🏁 PRESSIONI GOMME</div>"
        "<div style='display:flex;align-items:flex-end;justify-content:center;gap:12px;'>"
        "<div style='display:flex;flex-direction:row;gap:12px;'>"
        f"{_render_tire_gauge('FL', fl, 25.0, 29.0, get_pressure_color(fl, hot_mode), 'PSI', f'<span style=\'font-size:0.75rem;color:{color_fl};\'>{delta_fl}</span>')}"
        f"{_render_tire_gauge('FR', fr, 25.0, 29.0, get_pressure_color(fr, hot_mode), 'PSI', f'<span style=\'font-size:0.75rem;color:{color_fr};\'>{delta_fr}</span>')}"
        "</div>"
        "<div style='width:1px;background:#333;margin:0 12px;'></div>"
        "<div style='display:flex;flex-direction:row;gap:12px;'>"
        f"{_render_tire_gauge('RL', rl, 25.0, 29.0, get_pressure_color(rl, hot_mode), 'PSI', f'<span style=\'font-size:0.75rem;color:{color_rl};\'>{delta_rl}</span>')}"
        f"{_render_tire_gauge('RR', rr, 25.0, 29.0, get_pressure_color(rr, hot_mode), 'PSI', f'<span style=\'font-size:0.75rem;color:{color_rr};\'>{delta_rr}</span>')}"
        "</div>"
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
            "<p style='color:#8a8a8a;font-size:0.78rem;text-align:center;margin-top:8px;'>"
            "Dati CSV non caricati — valori di esempio</p>"
        )
    return (
        "<link href='https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap' rel='stylesheet'>"
        "<div style='background:#111;padding:16px;border-radius:8px;border:1px solid #333;font-family:&quot;Orbitron&quot;,monospace;overflow:visible;padding-bottom:20px;'>"
        "<div style='color:#fff;font-size:1rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:16px;'>🌡️ TEMPERATURE GOMME</div>"
        "<div style='display:flex;align-items:flex-end;justify-content:center;gap:12px;'>"
        "<div style='display:flex;flex-direction:row;gap:12px;'>"
        f"{_render_tire_gauge('FL', fl, 60.0, 120.0, _temperature_fill_color(fl), '°C')}"
        f"{_render_tire_gauge('FR', fr, 60.0, 120.0, _temperature_fill_color(fr), '°C')}"
        "</div>"
        "<div style='width:1px;background:#333;margin:0 12px;'></div>"
        "<div style='display:flex;flex-direction:row;gap:12px;'>"
        f"{_render_tire_gauge('RL', rl, 60.0, 120.0, _temperature_fill_color(rl), '°C')}"
        f"{_render_tire_gauge('RR', rr, 60.0, 120.0, _temperature_fill_color(rr), '°C')}"
        "</div>"
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
