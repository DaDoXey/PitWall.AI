import streamlit as st
import streamlit.components.v1 as components

from backend.database.manager import SessionDatabase, backfill_suggested_psi
from components.sidebar import render_sidebar
from components.tab_fuel import render_tab_fuel
from components.tab_history import render_tab_history
from components.tab_setup import render_tab_setup


st.set_page_config(
    page_title="PitWall.AI",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded",
)

css = """<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;500;600&display=swap');

:root {
  --bg-primary: #0D0D0D;
  --bg-secondary: #141414;
  --bg-tertiary: #1A1A1A;
  --sidebar-bg: #0A0A0A;
  --panel-bg: #141414;
  --accent-primary: #E10600;
  --accent-secondary: #FFD700;
  --accent-green: #00FF87;
  --accent-red: #FF3131;
  --accent-blue: #00A3FF;
  --accent-yellow: #FFD600;
  --text-primary: #F0F0F0;
  --text-secondary: #8A8A8A;
  --border-color: #2A2A2A;
  --font-main: 'Exo 2', sans-serif;
  --font-heading: 'Orbitron', monospace;
  --color-ok: #00FF87;
  --color-critical: #FF3131;
}

body,
p,
label,
textarea,
select,
input,
button,
.stTextArea,
.stSelectbox,
.stButton,
.stFileUploader {
  font-family: var(--font-main) !important;
}

h1,
h2,
h3,
.section-title,
.tire-value,
.metric-number,
.tire-widget-title {
  font-family: var(--font-heading) !important;
}

body,
.block-container,
.main,
.stApp {
  background: var(--bg-primary) !important;
  color: var(--text-primary) !important;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
  color: #FFFFFF;
}

[data-testid="stSidebar"] {
  background: var(--sidebar-bg) !important;
  border-right: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] .stTextInput>div>div>input,
[data-testid="stSidebar"] .stNumberInput>div>div>input,
[data-testid="stSidebar"] .stSelectbox>button,
[data-testid="stSidebar"] .stFileUploader>div,
[data-testid="stSidebar"] .stRadio>div>label,
[data-testid="stSidebar"] .stSlider>div>input {
  background: #1A1A1A !important;
  color: var(--text-primary) !important;
  border: 1px solid #333333 !important;
  border-radius: 4px !important;
}

[data-testid="stSidebar"] .stSelectbox>button:focus-visible,
[data-testid="stSidebar"] .stNumberInput>div>div>input:focus-visible,
[data-testid="stSidebar"] .stTextInput>div>div>input:focus-visible,
[data-testid="stSidebar"] .stFileUploader>div:focus-visible {
  outline: 1px solid var(--accent-primary) !important;
  box-shadow: 0 0 0 3px rgba(225, 6, 0, 0.12) !important;
}

.stButton>button {
  background: var(--accent-primary);
  color: #FFFFFF;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border: none;
  border-radius: 2px;
  padding: 0.75rem 1rem;
  transition: background 0.2s ease, box-shadow 0.2s ease,
    transform 0.2s ease;
}

.stButton>button:hover,
.stButton>button:focus-visible {
  background: #FF1800;
  box-shadow: 0 0 12px rgba(225, 6, 0, 0.5);
}

.stButton>button:active {
  transform: translateY(1px);
}

.stButton>button[disabled] {
  opacity: 0.65;
  cursor: not-allowed;
}

[data-testid="stMetric"],
[data-testid="stExpander"] {
  background: var(--panel-bg) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 2px !important;
  padding: 18px !important;
}

[data-testid="stExpander"] {
  margin-bottom: 16px !important;
}

[data-testid="stExpander"] .streamlit-expanderHeader,
[data-testid="stExpander"] .streamlit-expanderContent {
  background: var(--panel-bg) !important;
}

/* Sidebar header custom */
[data-testid="stSidebar"] {
  background: #0A0A0A !important;
  border-right: 1px solid #2A2A2A !important;
}

/* Titolo sessione nel sidebar */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown h3 {
  font-family: 'Orbitron', monospace !important;
  font-size: 0.85rem !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  color: #E10600 !important;
  border-bottom: 1px solid #2A2A2A;
  padding-bottom: 8px;
  margin-bottom: 16px !important;
}

/* Label dei widget sidebar */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label {
  font-family: 'Exo 2', sans-serif !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: #8A8A8A !important;
}

/* Separatore visivo nel sidebar */
[data-testid="stSidebar"] hr {
  border-color: #2A2A2A !important;
  margin: 16px 0 !important;
}

/* Numero input +/- buttons */
[data-testid="stSidebar"] .stNumberInput button {
  background: #1A1A1A !important;
  border: 1px solid #333 !important;
  color: #E10600 !important;
  font-weight: 700 !important;
}

[data-testid="stSidebar"] .stNumberInput button:hover {
  background: #E10600 !important;
  color: #fff !important;
}

/* Titoli di sezione custom Orbitron */
.section-title-custom {
  font-family: 'Orbitron', monospace !important;
  font-weight: 700 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  color: #fff !important;
  border-left: 3px solid #E10600 !important;
  padding-left: 12px !important;
  margin-bottom: 16px !important;
}

/* Header wrapper con badge MVP, logo e status DB */
.pitwall-header-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #0D0D0D;
  border: 1px solid #2A2A2A;
  border-radius: 4px;
}

.pitwall-logo-badge {
  background: #E10600;
  color: #fff;
  font-family: 'Orbitron', monospace;
  font-weight: 700;
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 4px 8px;
  border-radius: 2px;
  white-space: nowrap;
}

.pitwall-logo-header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.logo-flag {
  font-size: 1.5rem;
}

.logo-text {
  font-family: 'Orbitron', monospace;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #fff;
}

.logo-accent {
  color: #E10600;
}

.logo-subtitle {
  display: block;
  font-family: 'Exo 2', sans-serif;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #8A8A8A;
}

.pitwall-db-status {
  display: flex;
  align-items: center;
  font-family: 'Exo 2', sans-serif;
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

.pitwall-card {
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  border-top: 2px solid var(--accent-primary);
  border-radius: 2px;
  padding: 22px 24px;
  margin-bottom: 18px;
}

.pitwall-live-gomme-card {
  background: #111;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 18px;
}

.pitwall-live-gomme-header {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #FFFFFF;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.pitwall-live-gomme-panel {
  background: transparent;
  border-radius: 8px;
  padding: 0;
}

.pitwall-gauge-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
  width: 100%;
}

.pitwall-gauge-stack {
  display: flex;
  justify-content: center;
  gap: 20px;
  align-items: flex-end;
  padding: 12px 0 8px 0;
}

.pitwall-gauge {
  width: 36px;
  height: 160px;
  background: #1A1A1A;
  border: 1px solid #333;
  border-radius: 18px;
  position: relative;
  overflow: hidden;
}

.pitwall-pressure-layout,
.pitwall-temperature-layout {
  display: flex;
  gap: 16px;
  justify-content: center;
  align-items: flex-end;
  flex-wrap: wrap;
  width: 100%;
}

.pitwall-pressure-side {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.pitwall-gauge-fill {
  width: 100%;
  position: absolute;
  bottom: 0;
  left: 0;
  border-radius: 18px 18px 0 0;
}

.pitwall-gauge-label {
  margin-top: 10px;
  font-family: var(--font-heading);
  font-size: 0.95rem;
  color: #FFFFFF;
}

.pitwall-gauge-value {
  margin-top: 6px;
  font-family: var(--font-heading);
  font-size: 0.85rem;
  color: #FFFFFF;
}

.pitwall-gauge-delta {
  margin-top: 4px;
  font-family: var(--font-heading);
  font-size: 0.8rem;
}

.pitwall-divider {
  width: 1px;
  background: #333;
  display: flex;
  justify-content: center;
}

.pitwall-divider-text {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  color: #8A8A8A;
  font-size: 0.75rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
</style>"""
st.markdown(css, unsafe_allow_html=True)


def main() -> None:
    """Orchestra l'app Streamlit mantenendo la logica nei componenti.

    app.py resta leggero: carica i componenti, verifica il DB e gestisce
    il layout principale. Tutta la fisica e le chiamate AI sono delegate.
    """
    db_status = True
    db = SessionDatabase()
    try:
        db.init_db()
        backfill_suggested_psi(db.connection)
    except Exception:
        db_status = False
    finally:
        db.close()

    page_status = (
        '<span style="color:#00FF87;">● DB ONLINE</span>'
        if db_status
        else '<span style="color:#FF3131;">● DB OFFLINE</span>'
    )

    st.markdown(
        f"""
        <div class="pitwall-header-wrapper">
            <div class="pitwall-logo-badge">MVP v1.0</div>
            <div class="pitwall-logo-header">
                <span class="logo-flag">🏁</span>
                <span class="logo-text">PITWALL<span class="logo-accent">.AI</span></span>
                <span class="logo-subtitle">Virtual Race Engineer — ACC GT3</span>
            </div>
            <div class="pitwall-db-status">{page_status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sidebar_data = render_sidebar()

    tab1, tab2, tab3 = st.tabs(
        ["🔧 Analisi Setup", "⛽ Strategia Carburante", "📋 Storico Sessioni"]
    )

    with tab1:
        render_tab_setup(sidebar_data)
    with tab2:
        render_tab_fuel()
    with tab3:
        render_tab_history()


if __name__ == "__main__":
    main()
