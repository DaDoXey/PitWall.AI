import re
import streamlit as st
from typing import Any, Dict, Optional


def _extract_recommended_action(markdown_response: str) -> Optional[str]:
    """Estrae la sezione '## Correzione Setup Consigliata' dal markdown.

    Non esegue una nuova chiamata LLM: usa solo il testo già fornito.
    """
    pattern = r"##\s+Correzione Setup Consigliata\s*(.*?)(?:\n##\s+|\Z)"
    match = re.search(pattern, markdown_response, flags=re.S | re.I)
    if not match:
        return None
    return match.group(1).strip()


def render_engineer_report(markdown_response: str, physics_data: Dict[str, Any]) -> None:
    """Renderizza il report del Race Engineer usando dati e testo restituiti.

    Il componente presenta metriche rapide, il corpo principale in stile
    foglio telemetria e una sezione di azione immediata estratta dal testo.
    """
    title = "◼ RACE ENGINEER REPORT"
    timestamp = physics_data.get("timestamp") or "Timestamp non disponibile"
    car = physics_data.get("car") or "Auto non disponibile"
    track = physics_data.get("track") or "Tracciato non disponibile"

    st.markdown(
        f"""
        <div style='margin-bottom:16px;'>
            <div style='color:var(--accent-green);font-size:1rem;font-weight:700;'
                 >{title}</div>
            <div style='color:var(--text-secondary);font-size:0.95rem;'
                 >{timestamp} · {car} · {track}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        label="PSI Media",
        value=f"{physics_data.get('psi_media', 0):.2f}",
    )
    col2.metric(
        label="Delta Target",
        value=f"{physics_data.get('delta_target', 0):+.2f} PSI",
    )
    col3.metric(
        label="Temp Media Gomme",
        value=f"{physics_data.get('temp_media', 0):.1f} °C",
    )
    col4.metric(
        label="Status",
        value=str(physics_data.get("status", "N/A")),
    )

    st.markdown(
        f"""
        <div class='pitwall-engineer-report' style='margin-top:20px;'>
            {markdown_response}
        </div>
        """,
        unsafe_allow_html=True,
    )

    recommendation = _extract_recommended_action(markdown_response)
    if recommendation:
        st.markdown(
            f"""
            <div style='background: rgba(0, 255, 135, 0.08); border: 1px solid var(--accent-green);'
                 >
                <div style='font-weight:700; color: var(--text-primary); margin-bottom: 8px;'>
                    ✅ COSA FARE ORA
                </div>
                <div style='color: var(--text-primary); line-height:1.6;'>
                    {recommendation}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
