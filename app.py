"""
app.py — PitWall.AI v2
Entry point Streamlit con:
  - 5 tab setup completi (Tyres, Electronics, Mechanical Grip, Dampers, Aero)
  - Input da screenshot tramite Claude Vision
  - Input manuale con slider per ogni parametro
  - Compatibile con agent.py e parser.py esistenti
"""

import os
import streamlit as st
from datetime import datetime, timezone
from dotenv import load_dotenv
import pandas as pd

# Import moduli PitWall
from agent import get_ai_response, log_incident
from backend.parser.csv_parser import parse_session_csv
from backend.database.manager import SessionDatabase
from modules.setup_params import SETUP_SECTIONS, get_all_params_flat, format_setup_for_prompt
from modules.vision_parser import parse_setup_from_image, summarize_parsed_setup

# ─────────────────────────────────────────────
# CONFIGURAZIONE
# ─────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="PitWall.AI",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# AUTENTICAZIONE GATE
# ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.switch_page("pages/login.py")
    st.stop()

user_id = st.session_state.get("user_id")
user_name = st.session_state.get("user_name")
user_email = st.session_state.get("user_email")

# Benvenuto Gigi — mostra solo al primo accesso della sessione
if not st.session_state.get("gigi_welcomed", False):
    import streamlit.components.v1 as components
    user_name_display = user_name if user_name else "Pilota"

    gigi_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: transparent; font-family: 'Inter', sans-serif; padding: 0; }}

  .gigi-card {{
    background: linear-gradient(135deg, #111111 0%, #1a1a1a 100%);
    border: 1px solid #2a2a2a;
    border-left: 3px solid #E8002D;
    border-radius: 8px;
    padding: 20px 24px;
    display: flex;
    align-items: flex-start;
    gap: 20px;
    animation: fadeInDown 0.4s ease;
  }}

  @keyframes fadeInDown {{
    from {{ opacity: 0; transform: translateY(-8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}

  .gigi-avatar {{ flex-shrink: 0; margin-top: 4px; }}

  .gigi-body {{ flex: 1; }}

  .gigi-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }}

  .gigi-name {{
    font-family: 'Orbitron', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #E8002D;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }}

  .gigi-role {{
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: #555;
    letter-spacing: 0.04em;
  }}

  .gigi-message {{
    font-size: 13.5px;
    color: #BBBBBB;
    line-height: 1.65;
    margin-bottom: 14px;
  }}

  .gigi-message strong {{ color: #FFFFFF; }}

  .gigi-tags {{
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
  }}

  .tag {{
    background: rgba(232, 0, 45, 0.08);
    border: 1px solid rgba(232, 0, 45, 0.2);
    border-radius: 4px;
    padding: 3px 9px;
    font-size: 11px;
    color: #E8002D;
    letter-spacing: 0.04em;
  }}
</style>
</head>
<body>
<div class="gigi-card">

  <!-- Avatar SVG Gigi -->
  <div class="gigi-avatar">
    <svg width="58" height="74" viewBox="0 0 58 74" xmlns="http://www.w3.org/2000/svg">
      <!-- Corpo uniforme -->
      <rect x="13" y="40" width="32" height="28" rx="4" fill="#1e1e1e" stroke="#2a2a2a" stroke-width="1.5"/>
      <!-- Banda rossa uniforme -->
      <rect x="13" y="40" width="32" height="5" rx="2" fill="#E8002D"/>
      <!-- Numero pettorale -->
      <text x="29" y="58" text-anchor="middle" fill="#666" font-size="8" font-family="Inter">31</text>
      <!-- Testa -->
      <circle cx="29" cy="27" r="13.5" fill="#252525" stroke="#333" stroke-width="1.5"/>
      <!-- Archetto cuffie -->
      <path d="M16.5 25 Q16.5 11 29 11 Q41.5 11 41.5 25" fill="none" stroke="#E8002D" stroke-width="3" stroke-linecap="round"/>
      <!-- Padiglione sx -->
      <rect x="11" y="22" width="7" height="10" rx="3.5" fill="#E8002D"/>
      <!-- Padiglione dx -->
      <rect x="40" y="22" width="7" height="10" rx="3.5" fill="#E8002D"/>
      <!-- Braccetto microfono -->
      <path d="M40 29 Q47 31 49 35" fill="none" stroke="#555" stroke-width="1.5" stroke-linecap="round"/>
      <circle cx="49.5" cy="35.5" r="2.5" fill="#888"/>
      <!-- Occhi -->
      <circle cx="23.5" cy="27" r="2" fill="#E8002D" opacity="0.85"/>
      <circle cx="34.5" cy="27" r="2" fill="#E8002D" opacity="0.85"/>
      <!-- Sorriso -->
      <path d="M23 33 Q29 37 35 33" fill="none" stroke="#555" stroke-width="1.5" stroke-linecap="round"/>
      <!-- Tablet -->
      <rect x="18" y="48" width="18" height="13" rx="2" fill="#0d0d0d" stroke="#E8002D" stroke-width="0.8"/>
      <rect x="20" y="50" width="14" height="2" rx="1" fill="#E8002D" opacity="0.5"/>
      <rect x="20" y="53.5" width="9" height="1.5" rx="0.5" fill="#2a2a2a"/>
      <rect x="20" y="56" width="11" height="1.5" rx="0.5" fill="#2a2a2a"/>
    </svg>
  </div>

  <div class="gigi-body">
    <div class="gigi-header">
      <span class="gigi-name">GIGI</span>
      <span class="gigi-role">// Race Engineer Virtuale</span>
    </div>
    <div class="gigi-message">
      Bentornato nel box, <strong>{user_name_display}</strong>! Sono Gigi, il tuo ingegnere di pista.<br><br>
      Carica i <strong>dati CSV di sessione</strong>, dimmi cosa provi in curva e ti restituisco
      un'analisi tecnica precisa — bilanciamento, gomme, differenziale, carburante.
      Tutto quello che serve per uscire dal box pi&ugrave; veloci di prima.
    </div>
    <div class="gigi-tags">
      <span class="tag">📊 Telemetria CSV</span>
      <span class="tag">🔧 Setup GT3</span>
      <span class="tag">⛽ Strategia Carburante</span>
      <span class="tag">🌡️ Monitor Gomme</span>
    </div>
  </div>
</div>
</body>
</html>
"""
    components.html(gigi_html, height=175, scrolling=False)
    st.session_state["gigi_welcomed"] = True

# Inizializza database sessioni (non cachato per evitare threading issues con SQLite)
def get_session_db():
    db = SessionDatabase()
    db.init_db()
    return db

# Ottieni istanza DB per questa esecuzione
db = get_session_db()

# Verifica status DB
def check_db_status() -> bool:
    try:
        db.connection.execute("SELECT 1")
        return True
    except Exception:
        return False

# ─────────────────────────────────────────────
# STILE CSS — coerente con MVP (dark, rosso ACC)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');

:root {
    --red:      #E8002D;
    --red-dim:  #9B0020;
    --bg:       #0A0A0A;
    --surface:  #141414;
    --surface2: #1E1E1E;
    --border:   #2A2A2A;
    --text:     #F0F0F0;
    --muted:    #7A7A7A;
    --green:    #00C853;
    --yellow:   #FFD600;
}

header[data-testid="stHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    overflow: visible !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}
/* Nasconde toolbar Streamlit (Deploy, hamburger, status) ma NON il toggle sidebar */
header[data-testid="stHeader"] button:not([data-testid="stExpandSidebarButton"]),
header[data-testid="stHeader"] [data-testid="stStatusWidget"],
header[data-testid="stHeader"] [data-testid="stDecoration"],
header[data-testid="stHeader"] [data-testid="headerActionElements"],
header[data-testid="stHeader"] [data-testid="stHeaderActionElements"] {
    display: none !important;
    visibility: hidden !important;
}
footer {
    display: none !important;
}

/* ── SIDEBAR TOGGLE — visibile in entrambi gli stati ── */
/* Bottone per CHIUDERE la sidebar (quando è aperta) */
[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background-color: transparent !important;
    border: 1px solid #333 !important;
    border-radius: 6px !important;
    z-index: 9999 !important;
    color: #999999 !important;
    min-width: 36px !important;
    min-height: 36px !important;
}
[data-testid="stSidebarCollapseButton"]:hover {
    border-color: #E8002D !important;
    color: #ffffff !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    fill: #999999 !important;
}
[data-testid="stSidebarCollapseButton"]:hover svg {
    fill: #ffffff !important;
}

/* Bottone per RIAPRIRE la sidebar (quando è chiusa) */
[data-testid="stExpandSidebarButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background-color: #1a1a1a !important;
    border: 1px solid #333 !important;
    border-radius: 6px !important;
    z-index: 9999 !important;
    color: #999999 !important;
    width: 36px !important;
    height: 36px !important;
    padding: 0 !important;
    margin: 0 !important;
    position: fixed !important;
    top: 50px !important;
    left: 4px !important;
}
[data-testid="stExpandSidebarButton"]:hover {
    border-color: #E8002D !important;
    color: #ffffff !important;
}
[data-testid="stExpandSidebarButton"] svg {
    fill: #999999 !important;
}
[data-testid="stExpandSidebarButton"]:hover svg {
    fill: #ffffff !important;
}

/* Fix icone file uploader sidebar — centratura assoluta */
[data-testid="stFileUploaderDropzone"] button {
    position: relative !important;
    width: 40px !important;
    height: 40px !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}
[data-testid="stFileUploaderDropzone"] button span[data-testid="stIconMaterial"] {
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    color: #999999 !important;
    visibility: visible !important;
    opacity: 1 !important;
    font-size: 1.2rem !important;
}
[data-testid="stFileUploaderDropzone"] button:hover span[data-testid="stIconMaterial"] {
    color: #ffffff !important;
}
.block-container {
    padding-top: 1rem !important;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: #0f0f0f !important;
    border-right: 1px solid #222 !important;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
}
.sidebar-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: var(--text) !important;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}
.sidebar-section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 2.5px;
    color: #444444 !important;
    text-transform: uppercase;
    margin-bottom: 8px;
    margin-top: 4px;
}
.sidebar-control-label {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: #888888;
    margin-bottom: 4px;
}
.sidebar-divider {
    height: 1px;
    background-color: #1e1e1e;
    margin: 1rem 0;
    border: none;
}

/* ── HEADER ── */
.pw-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1.2rem;
}
.pw-header-left {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.pw-badge {
    background: var(--red);
    color: white;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
}
.pw-logo-text {
    font-family: 'Orbitron', monospace;
    font-size: 1.3rem;
    font-weight: 900;
    letter-spacing: 0.05em;
    color: var(--text) !important;
}
.pw-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted) !important;
    letter-spacing: 0.12em;
}
.pw-db-online {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--green) !important;
    letter-spacing: 0.1em;
}
.pw-db-offline {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--red) !important;
    letter-spacing: 0.1em;
}

/* ── SECTION TITLES ── */
.section-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text) !important;
    border-left: 4px solid var(--red);
    padding-left: 0.8rem;
    margin: 1.5rem 0 1rem 0;
}

/* ── TABS ── */
[data-testid="stTabs"] > div > div > button {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    letter-spacing: 0.08em;
    color: var(--muted) !important;
    border-bottom: 2px solid transparent;
    padding: 0.5rem 1.2rem;
    background: transparent;
}
[data-testid="stTabs"] > div > div > button[aria-selected="true"] {
    color: var(--red) !important;
    border-bottom: 2px solid var(--red) !important;
}

/* ── SLIDERS ── */
[data-testid="stSlider"] > div > div > div > div {
    background: var(--red) !important;
}
[data-baseweb="slider"] [role="slider"] {
    background-color: #E8002D !important;
    border-color: #E8002D !important;
}
[data-baseweb="slider"] [data-testid="stSliderTrackFill"] {
    background-color: #E8002D !important;
}

/* ── BUTTONS ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: var(--red) !important;
    border: none !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    color: white !important;
    border-radius: 4px !important;
    padding: 0.6rem 2rem !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: var(--red-dim) !important;
}
[data-testid="stButton"] > button[kind="secondary"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    color: var(--text) !important;
    border-radius: 4px !important;
}

/* ── PARAMETRI GROUPS ── */
.param-group-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 600;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    margin-bottom: 0.3rem;
    margin-top: 0.6rem;
}
.tip-text {
    font-size: 0.65rem;
    color: var(--muted);
    margin-top: -0.25rem;
    margin-bottom: 0.25rem;
    font-style: italic;
}

/* ── SLIDER VALUE DISPLAY ── */
.slider-value-display {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text);
    text-align: center;
    padding: 0.15rem 0.4rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 3px;
    margin-bottom: 0.2rem;
}

/* ── SECTION SEPARATOR ── */
.section-separator {
    height: 1px;
    background: var(--border);
    margin: 0.8rem 0;
}
/* Sidebar divider — duplicate kept for safety */

/* ── SIDEBAR — background e bordo ── */
section[data-testid="stSidebar"] {
    background-color: #0f0f0f !important;
    border-right: 1px solid #222 !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 1rem 1rem 1.5rem 1rem !important;
}

/* ── SIDEBAR — testo generico (ESCLUDI icone materiali e bottone collapse) ── */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span:not([data-testid="stIconMaterial"]),
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
    color: #999999 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── SIDEBAR — nasconde il testo dell'icona collapse (keyboard_double_arrow_left) ── */
section[data-testid="stSidebar"] span[data-testid="stIconMaterial"] {
    color: transparent !important;
    font-size: 1.2rem !important;
}
/* Riattiva icone nei file uploader */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span[data-testid="stIconMaterial"] {
    color: #999999 !important;
}
/* Riattiva icona bottone collapse sidebar */
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] span[data-testid="stIconMaterial"] {
    color: #999999 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover span[data-testid="stIconMaterial"] {
    color: #ffffff !important;
}

/* ── SIDEBAR — titolo PITWALL.AI SESSIONE ── */
section[data-testid="stSidebar"] h1 {
    color: #FFFFFF !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

/* ── SIDEBAR — label widget ── */
section[data-testid="stSidebar"] label {
    color: #666666 !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.10em !important;
    text-transform: uppercase !important;
}

/* ── SIDEBAR — selectbox ── */
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #1a1a1a !important;
    border: 1px solid #333333 !important;
    border-radius: 4px !important;
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
    border-color: #E8002D !important;
}

/* ── SIDEBAR — number input ── */
section[data-testid="stSidebar"] .stNumberInput input {
    background-color: #1a1a1a !important;
    border: 1px solid #333333 !important;
    border-radius: 4px !important;
    color: #FFFFFF !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-align: center !important;
}

section[data-testid="stSidebar"] .stNumberInput input:focus {
    border-color: #E8002D !important;
    box-shadow: 0 0 0 1px #E8002D !important;
}

section[data-testid="stSidebar"] .stNumberInput button {
    background-color: #1a1a1a !important;
    border: 1px solid #333333 !important;
    color: #999999 !important;
}

section[data-testid="stSidebar"] .stNumberInput button:hover {
    border-color: #E8002D !important;
    color: #E8002D !important;
}

/* ── SIDEBAR — file uploader: nasconde il <p>Upload</p> duplicato ── */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    display: none !important;
}

/* ── SIDEBAR — file uploader dropzone ── */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background-color: #141414 !important;
    border: 1px dashed #333 !important;
    border-radius: 6px !important;
    padding: 0.75rem !important;
    transition: border-color 0.2s ease !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {
    border-color: #E8002D !important;
    background-color: #1a1010 !important;
}

/* ── SIDEBAR — istruzioni dropzone ── */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] {
    color: #666666 !important;
    font-size: 0.72rem !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── SIDEBAR — icona upload ── */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] svg {
    width: 20px !important;
    height: 20px !important;
    color: #666666 !important;
}

/* ── SIDEBAR — label file uploader ── */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label {
    font-size: 0.75rem !important;
    font-family: 'Orbitron', sans-serif !important;
    color: #999999 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    margin-bottom: 0.25rem !important;
}

/* ── SIDEBAR — divider ── */
section[data-testid="stSidebar"] hr {
    border-color: #222222 !important;
    margin: 0.75rem 0 !important;
}

/* ── SIDEBAR — link GitHub ── */
section[data-testid="stSidebar"] a {
    color: #E8002D !important;
    text-decoration: none !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] a:hover {
    color: #CC0028 !important;
    text-decoration: underline !important;
}

/* ── TYRE VISUALIZER ── */
.tyre-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
}
.tyre-bar-outer {
    width: 52px;
    height: 140px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 26px;
    display: flex;
    align-items: flex-end;
    overflow: hidden;
}
.tyre-bar-inner {
    width: 100%;
    border-radius: 26px;
    transition: height 0.3s ease;
}
.tyre-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.08em;
}
.tyre-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--text);
}
.tyre-delta-pos {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--green);
}
.tyre-delta-neg {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--red);
}
.tyre-delta-zero {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--muted);
}
.tyre-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.2rem;
}
.tyre-panel-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 1rem;
}

/* ── TABLE ── */
.session-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Inter', sans-serif;
    font-size: 0.82rem;
}
.session-table th {
    background: var(--surface2);
    color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.6rem 0.8rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
}
.session-table td {
    padding: 0.5rem 0.8rem;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    vertical-align: middle;
}
.session-table tr:hover td {
    background: var(--surface2);
}

/* ── AI OUTPUT ── */
.ai-output {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--red);
    border-radius: 6px;
    padding: 1.5rem;
    font-size: 0.93rem;
    line-height: 1.75;
}

/* ── INPUT NUMERICO +/- ── */
.num-input-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER (restored visual)
# ─────────────────────────────────────────────
db_status = "● DB ONLINE" if check_db_status() else "● DB OFFLINE"
db_class = "pw-db-online" if check_db_status() else "pw-db-offline"

st.markdown(
    f"""
    <div class="pw-header">
        <div class="pw-header-left">
            <span class="pw-badge">MVP V2.0</span>
            <span style="font-size:1.4rem;">♟</span>
            <div>
                <div class="pw-logo-text">PITWALL<span style="color:#E8002D;">.AI</span></div>
                <div class="pw-subtitle">VIRTUAL RACE ENGINEER — ACC GT3</div>
            </div>
        </div>
        <div class="{db_class}">{db_status}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("")


# ─────────────────────────────────────────────
# SIDEBAR — ristaurato stile e sezioni precedenti
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.25rem 0 0.75rem 0; border-bottom: 1px solid #1e1e1e; margin-bottom: 1rem;">
        <div style="font-family: 'Orbitron', sans-serif; font-size: 0.7rem; 
                    letter-spacing: 0.15em; color: #666666; text-transform: uppercase; 
                    margin-bottom: 0.2rem;">Sessione</div>
        <div style="font-family: 'Orbitron', sans-serif; font-size: 1rem; 
                    color: #FFFFFF; letter-spacing: 0.08em;">PITWALL<span style="color:#E8002D;">.</span>AI</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-family: 'Orbitron', sans-serif; font-size: 0.65rem; 
                letter-spacing: 0.12em; color: #444444; text-transform: uppercase; 
                margin-bottom: 0.75rem;">Dati Sessione</div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.85rem;color:#CCC;">📊 CSV Sessione</div>', unsafe_allow_html=True)
    csv_file = st.file_uploader(
        "Carica CSV",
        type=["csv"],
        key="csv_uploader",
        label_visibility="collapsed",
    )
    if csv_file:
        st.caption(f"📄 {csv_file.name}")
    st.markdown("")

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.85rem;color:#CCC;">📸 Screenshot Setup ACC</div>', unsafe_allow_html=True)
    st.caption("Carica foto del menu setup.")
    screenshot_file = st.file_uploader(
        "Screenshot (JPG/PNG)",
        type=["jpg", "jpeg", "png", "webp"],
        key="screenshot_uploader",
        label_visibility="collapsed",
    )
    if screenshot_file is not None:
        if st.button("🔍 Leggi Parametri da Screenshot", type="secondary", use_container_width=True):
            api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))
            if not api_key:
                st.error("ANTHROPIC_API_KEY non trovata — verifica .env (locale) o Streamlit Secrets (cloud)")
            else:
                with st.spinner("Analisi screenshot in corso..."):
                    result = parse_setup_from_image(screenshot_file.getvalue(), api_key=api_key)
                st.session_state["vision_params"] = result.get("params", {})
                st.session_state["vision_summary"] = summarize_parsed_setup(result)
                st.success(f"Riconosciuti {len(result['params'])} parametri.")
    if "vision_summary" in st.session_state:
        with st.expander("📋 Parametri riconosciuti", expanded=True):
            st.markdown(st.session_state["vision_summary"])
        if st.button("✅ Usa questi parametri nel form", use_container_width=True):
            st.session_state["load_vision_params"] = True
            st.rerun()

    # ── USER INFO + LOGOUT ──
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #666; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px;">Logged in as</div>
    <div style="font-family: 'Inter', sans-serif; font-size: 0.85rem; color: #fff; margin-bottom: 2px;">{user_name}</div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888;">{user_email}</div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("""
    <style>
    /* Logout button fix — targeting Streamlit secondary button via data-testid */
    [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        color: #888888 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        width: 100% !important;
        padding: 6px 12px !important;
        border-radius: 4px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
        border-color: #E8002D !important;
        color: #FFFFFF !important;
        background-color: rgba(232, 0, 45, 0.07) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True, key="btn_logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.user_email = None
        st.switch_page("pages/login.py")

    # ── FOOTER ──
    st.markdown("")
    st.markdown("""
    <div style="position: fixed; bottom: 1.5rem; left: 0; width: 240px; 
                padding: 0 1rem; box-sizing: border-box;">
        <div style="border-top: 1px solid #1e1e1e; padding-top: 0.75rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; 
                             color: #444444;">v0.2.0 — MVP</span>
                <a href="https://github.com/DaDoXey/PitWall.AI" target="_blank"
                   style="font-family: 'Orbitron', sans-serif; font-size: 0.6rem; 
                          color: #E8002D; text-decoration: none; letter-spacing: 0.08em;
                          text-transform: uppercase;">GitHub ↗</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CSV — PARSING IMMEDIATO + PREVIEW
# ─────────────────────────────────────────────
csv_filename = csv_file.name if csv_file else None
if csv_file is not None and st.session_state.get("csv_filename") != csv_filename:
    try:
        from backend.parser.csv_parser import CSVParseError
        st.session_state["csv_parsed_result"] = parse_session_csv(csv_file)
        st.session_state["csv_filename"] = csv_filename
        csv_result = st.session_state["csv_parsed_result"]
        press = csv_result.get("pressures") or {}
        temp = csv_result.get("temperatures") or {}
        if press:
            st.session_state["csv_pressures"] = {
                k: press[k]["avg"] for k in ["fl", "fr", "rl", "rr"] if k in press
            }
        if temp:
            st.session_state["csv_temps"] = {
                k: temp[k]["avg"] for k in ["fl", "fr", "rl", "rr"] if k in temp
            }
    except CSVParseError as e:
        st.warning(f"⚠️ CSV non valido: {str(e)}")

if "csv_parsed_result" in st.session_state:
    csv_result = st.session_state["csv_parsed_result"]

    st.markdown('<div class="section-title">📊 Anteprima Dati Sessione</div>', unsafe_allow_html=True)

    # 2a — Metriche aggregate
    temp_stats = csv_result.get("temperatures", {})
    press_stats = csv_result.get("pressures", {})

    def _get_stat(stats_dict, pos, key):
        if stats_dict and pos in stats_dict:
            return stats_dict[pos].get(key, 0.0)
        return 0.0

    temp_vals = [_get_stat(temp_stats, p, "max") for p in ["fl", "fr", "rl", "rr"]]
    temp_max = max(temp_vals) if temp_vals else 0.0
    press_vals = [_get_stat(press_stats, p, "avg") for p in ["fl", "fr", "rl", "rr"]]
    press_avg_rr = _get_stat(press_stats, "rr", "avg")

    metric_cols = st.columns(5)
    with metric_cols[0]:
        st.metric("🏁 Giri registrati", csv_result.get("laps_count", 0))
    with metric_cols[1]:
        st.metric("⛽ Consumo medio", f"{csv_result.get('fuel_cons_avg', 0):.2f} L/giro")
    with metric_cols[2]:
        st.metric("🌡 Temp max RR", f"{_get_stat(temp_stats, 'rr', 'max'):.1f}°C")
    with metric_cols[3]:
        st.metric("🔧 Press avg RR", f"{press_avg_rr:.1f} psi")
    with metric_cols[4]:
        st.metric("🔥 Temp max generale", f"{temp_max:.1f}°C")

    # 2c — Alert visivo automatico
    if temp_max > 100:
        st.warning(f"⚠️ Temperatura critica rilevata: {temp_max:.1f}°C — analisi prioritaria raccomandata.")
    elif temp_max > 95:
        st.info(f"ℹ️ Temperature elevate: {temp_max:.1f}°C — monitorare in analisi.")

    # 2b — Tabella dati grezzi (collassabile)
    try:
        csv_file.seek(0)
        df_preview = pd.read_csv(csv_file)
        with st.expander("📊 Dati grezzi sessione", expanded=False):
            st.dataframe(df_preview, use_container_width=True)
    except Exception:
        pass

    st.markdown("---")


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_default_or_vision(key: str, default_val):
    """
    Se sono stati caricati parametri da Vision e l'utente ha confermato,
    usa il valore riconosciuto come default dello slider. Altrimenti usa
    il default standard del parametro.
    """
    if st.session_state.get("load_vision_params"):
        vision = st.session_state.get("vision_params", {})
        if key in vision:
            return vision[key]
    return default_val


def render_param_slider(key: str, param: dict, col=None) -> float | int:
    """
    Renderizza uno slider per un parametro di setup.
    Supporta float e int in modo automatico.
    Mostra il valore corrente in evidenza sopra lo slider.
    """
    default = get_default_or_vision(key, param["default"])
    label = param["label"]
    unit_str = f" ({param['unit']})" if param["unit"] else ""
    full_label = f"{label}{unit_str}"

    is_float = isinstance(param["step"], float) or isinstance(param["min"], float)

    target = col if col else st

    # Recupera il valore corrente dallo session_state (se esiste)
    current_val = st.session_state.get(f"slider_{key}", float(default) if is_float else int(default))
    
    # Formatta il valore per display
    if is_float:
        formatted_val = f"{current_val:.2f}"
    else:
        formatted_val = str(int(current_val))
    
    target.markdown(
        f'<div class="slider-value-display" style="font-size:0.8rem;padding:0.1rem 0.3rem;margin-bottom:0.15rem;">{formatted_val}</div>',
        unsafe_allow_html=True,
    )

    value = target.slider(
        full_label,
        min_value=float(param["min"]) if is_float else int(param["min"]),
        max_value=float(param["max"]) if is_float else int(param["max"]),
        value=float(default) if is_float else int(default),
        step=float(param["step"]) if is_float else int(param["step"]),
        key=f"slider_{key}",
        label_visibility="collapsed",
    )

    return value


# ─────────────────────────────────────────────
# AREA PRINCIPALE — 2 colonne: feedback + setup
# ─────────────────────────────────────────────

tab_analisi, tab_carburante, tab_storico = st.tabs([
    "✂ Analisi Setup",
    "🗒 Strategia Carburante",
    "🗒 Storico Sessioni",
])

with tab_analisi:
    col1, col2, col3 = st.columns([1, 1.2, 1.5], gap="medium")

    # ══ COLONNA 1 — Configurazione Sessione ══
    with col1:
        st.markdown('<div class="section-title">1 — Configurazione Sessione</div>', unsafe_allow_html=True)
        st.caption("Parametri ambientali e di pista")
        st.divider()

        selected_car = st.selectbox(
            "🏎 Auto",
            options=[
                "BMW M4 GT3",
                "Ferrari 296 GT3",
                "Ferrari 488 GT3 Evo",
                "Porsche 992 GT3 R",
                "Porsche 991 II GT3 R",
                "Mercedes-AMG GT3 Evo",
                "Audi R8 LMS Evo II GT3",
                "Lamborghini Huracán GT3 EVO2",
                "McLaren 720S GT3 Evo",
                "Bentley Continental GT3",
                "Honda NSX GT3 Evo",
                "Nissan GT-R Nismo GT3",
                "Lexus RC F GT3",
                "Ford Mustang GT3",
                "Aston Martin V8 Vantage GT3",
            ],
            key="sel_car",
        )

        selected_track = st.selectbox(
            "🏁 Tracciato",
            options=[
                "Monza", "Spa-Francorchamps", "Nürburgring GP", "Silverstone",
                "Misano", "Barcelona", "Hungaroring", "Zandvoort", "Imola",
                "Kyalami", "Mount Panorama", "Suzuka", "Zolder",
                "Paul Ricard", "Brands Hatch",
            ],
            key="sel_track",
        )

        selected_conditions = st.selectbox(
            "☁ Condizioni",
            options=["Asciutto", "Umido", "Bagnato"],
            key="sel_conditions",
        )

        st.markdown('<div style="margin-top:0.8rem;font-size:0.85rem;color:#CCC;">🌡 Temperature</div>', unsafe_allow_html=True)
        ambient_temp = st.slider("Temp. Ambiente", 0, 50, 20, key="temp_amb")
        track_temp = st.slider("Temp. Pista", 0, 60, 30, key="temp_pista")

    # ══ COLONNA 2 — Feedback Pilota ══
    with col2:
        st.markdown('<div class="section-title">2 — Feedback Pilota</div>', unsafe_allow_html=True)
        st.caption("Descrivi il comportamento della vettura in pista")
        st.divider()

        feedback = st.text_area(
            "📻 Descrivi il problema riscontrato in pista",
            height=200,
            placeholder=(
                "Es: 'Ho troppo sottosterzo a centro curva sulle curve lente. "
                "L'auto non ruota e devo aprire il volante. "
                "Accade soprattutto nelle curve a destra, principalmente nel settore 2.'"
            ),
            help="Più sei specifico (fase della curva, tipo di curva, condizioni), migliore sarà l'analisi.",
            key="feedback_text_area",
        )

        btn_analizza = st.button("🔍 ANALIZZA SESSIONE", type="primary", use_container_width=True)

    # ══ COLONNA 3 — Setup Corrente ══
    with col3:
        st.markdown('<div class="section-title">3 — Setup Corrente</div>', unsafe_allow_html=True)
        st.caption("Contesto numerico di partenza per l'analisi")
        st.divider()

        # Dizionario per raccogliere tutti i valori del setup
        current_setup = {}

        # Render dei 5 tab — stessa struttura del gioco ACC
        tab_keys = list(SETUP_SECTIONS.keys())
        tab_labels = [SETUP_SECTIONS[k]["label"] for k in tab_keys]
        tabs = st.tabs(tab_labels)

        for tab, section_key in zip(tabs, tab_keys):
            with tab:
                section = SETUP_SECTIONS[section_key]
                params = section["params"]

                # ── TYRES: griglia 2×2 per le 4 ruote ──
                if section_key == "tyres":
                    st.markdown('<div class="param-group-title">PRESSIONI</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    current_setup["tire_press_fl"] = render_param_slider("tire_press_fl", params["tire_press_fl"], c1)
                    current_setup["tire_press_fr"] = render_param_slider("tire_press_fr", params["tire_press_fr"], c2)
                    c3, c4 = st.columns(2)
                    current_setup["tire_press_rl"] = render_param_slider("tire_press_rl", params["tire_press_rl"], c3)
                    current_setup["tire_press_rr"] = render_param_slider("tire_press_rr", params["tire_press_rr"], c4)

                    st.markdown('<div class="param-group-title" style="margin-top:1rem">CAMBER</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    current_setup["camber_fl"] = render_param_slider("camber_fl", params["camber_fl"], c1)
                    current_setup["camber_fr"] = render_param_slider("camber_fr", params["camber_fr"], c2)
                    c3, c4 = st.columns(2)
                    current_setup["camber_rl"] = render_param_slider("camber_rl", params["camber_rl"], c3)
                    current_setup["camber_rr"] = render_param_slider("camber_rr", params["camber_rr"], c4)

                    st.markdown('<div class="param-group-title" style="margin-top:1rem">TOE</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    current_setup["toe_fl"] = render_param_slider("toe_fl", params["toe_fl"], c1)
                    current_setup["toe_fr"] = render_param_slider("toe_fr", params["toe_fr"], c2)
                    c3, c4 = st.columns(2)
                    current_setup["toe_rl"] = render_param_slider("toe_rl", params["toe_rl"], c3)
                    current_setup["toe_rr"] = render_param_slider("toe_rr", params["toe_rr"], c4)

                    st.markdown('<div class="param-group-title" style="margin-top:1rem">CASTER</div>', unsafe_allow_html=True)
                    current_setup["caster"] = render_param_slider("caster", params["caster"])

                elif section_key == "electronics":
                    for key, param in params.items():
                        current_setup[key] = render_param_slider(key, param)

                elif section_key == "mechanical_grip":
                    st.markdown('<div class="param-group-title">BARRE ANTIROLLIO</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    current_setup["arb_front"] = render_param_slider("arb_front", params["arb_front"], c1)
                    current_setup["arb_rear"] = render_param_slider("arb_rear", params["arb_rear"], c2)

                    st.markdown('<div class="param-group-title" style="margin-top:1rem">WHEEL RATE</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    current_setup["wheel_rate_front"] = render_param_slider("wheel_rate_front", params["wheel_rate_front"], c1)
                    current_setup["wheel_rate_rear"] = render_param_slider("wheel_rate_rear", params["wheel_rate_rear"], c2)

                    st.markdown('<div class="param-group-title" style="margin-top:1rem">BUMPSTOP RATE</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    current_setup["bumpstop_rate_front"] = render_param_slider("bumpstop_rate_front", params["bumpstop_rate_front"], c1)
                    current_setup["bumpstop_rate_rear"] = render_param_slider("bumpstop_rate_rear", params["bumpstop_rate_rear"], c2)

                    st.markdown('<div class="param-group-title" style="margin-top:1rem">BUMPSTOP RANGE</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    current_setup["bumpstop_range_front"] = render_param_slider("bumpstop_range_front", params["bumpstop_range_front"], c1)
                    current_setup["bumpstop_range_rear"] = render_param_slider("bumpstop_range_rear", params["bumpstop_range_rear"], c2)

                    st.markdown('<div class="param-group-title" style="margin-top:1rem">DIFFERENZIALE</div>', unsafe_allow_html=True)
                    current_setup["preload"] = render_param_slider("preload", params["preload"])

                elif section_key == "dampers":
                    damper_corners = [
                        ("FL", "Anteriore Sinistra"),
                        ("FR", "Anteriore Destra"),
                        ("RL", "Posteriore Sinistra"),
                        ("RR", "Posteriore Destra"),
                    ]
                    for suffix, corner_label in damper_corners:
                        st.markdown(
                            f'<div class="param-group-title" style="margin-top:0.8rem">{corner_label.upper()}</div>',
                            unsafe_allow_html=True,
                        )
                        c1, c2, c3, c4 = st.columns(4)
                        cols = [c1, c2, c3, c4]
                        damper_params = [
                            f"bump_{suffix.lower()}",
                            f"fast_bump_{suffix.lower()}",
                            f"rebound_{suffix.lower()}",
                            f"fast_rebound_{suffix.lower()}",
                        ]
                        for param_key, col in zip(damper_params, cols):
                            current_setup[param_key] = render_param_slider(
                                param_key, params[param_key], col
                            )

                elif section_key == "aero":
                    st.markdown('<div class="param-group-title">RIDE HEIGHT & DEPORTANZA</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    current_setup["ride_height_front"] = render_param_slider("ride_height_front", params["ride_height_front"], c1)
                    current_setup["ride_height_rear"] = render_param_slider("ride_height_rear", params["ride_height_rear"], c2)

                    rake = current_setup["ride_height_rear"] - current_setup["ride_height_front"]
                    rake_color = "#E8002D" if rake < 10 or rake > 35 else "#4CAF50"
                    st.markdown(
                        f'<p style="font-family:JetBrains Mono,monospace;font-size:0.85rem;color:{rake_color};">'
                        f'📐 Rake attuale: {rake:.0f} mm</p>',
                        unsafe_allow_html=True,
                    )

                    st.markdown('<div class="param-group-title" style="margin-top:1rem">CARICO AERODINAMICO</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    current_setup["splitter"] = render_param_slider("splitter", params["splitter"], c1)
                    current_setup["wing"] = render_param_slider("wing", params["wing"], c2)

                    st.markdown('<div class="param-group-title" style="margin-top:1rem">BRAKE DUCTS</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    current_setup["brake_duct_front"] = render_param_slider("brake_duct_front", params["brake_duct_front"], c1)
                    current_setup["brake_duct_rear"] = render_param_slider("brake_duct_rear", params["brake_duct_rear"], c2)

    # ── Visualizzatore Live Gomme (full-width) ──
    st.markdown(
        '<div style="border-top:1px solid #2A2A2A;margin:0.5rem 0 1.2rem 0;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">Visualizzazione Live Gomme</div>', unsafe_allow_html=True)

    def _tyre_color(val: float, metric: str) -> str:
        if metric == "pressure":
            if 26.0 <= val <= 27.5:
                return "#00C853"
            if 25.0 <= val < 26.0 or 27.5 < val <= 28.5:
                return "#FFD600"
            return "#E8002D"
        if metric == "temp":
            if 85 <= val <= 95:
                return "#00C853"
            if 75 <= val < 85 or 95 < val <= 105:
                return "#FFD600"
            return "#E8002D"
        return "#7A7A7A"

    def _tyre_bar(label: str, val: float, delta: float, metric: str) -> str:
        color = _tyre_color(val, metric)
        pct = max(5, min(100, int((val - 25.0) / (30.0 - 25.0) * 100))) if metric == "pressure" else max(5, min(100, int((val - 50.0) / (120.0 - 50.0) * 100)))
        unit = "PSI" if metric == "pressure" else "°C"
        dsign = "+" if delta > 0 else ""
        dcol = "#00C853" if delta > 0 else "#E8002D" if delta < 0 else "#7A7A7A"
        return (
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:2px;min-width:60px;">'
            f'<div style="width:40px;height:120px;background:#1a1a1a;border:1px solid #333;border-radius:20px;display:flex;align-items:flex-end;overflow:hidden;">'
            f'<div style="width:100%;height:{pct}%;background:{color};border-radius:20px;"></div></div>'
            f'<div style="font-size:11px;font-weight:700;color:#fff;">{label}</div>'
            f'<div style="font-size:10px;color:#ccc;">{val:.1f} {unit}</div>'
            f'<div style="font-size:9px;color:{dcol};">{dsign}{delta:.1f} {unit}</div></div>'
        )

    slider_fl = st.session_state.get("slider_tire_press_fl")
    slider_fr = st.session_state.get("slider_tire_press_fr")
    slider_rl = st.session_state.get("slider_tire_press_rl")
    slider_rr = st.session_state.get("slider_tire_press_rr")
    csv_pressures = st.session_state.get("csv_pressures", {})
    live_press = {
        "fl": slider_fl if slider_fl is not None else csv_pressures.get("fl", 26.7),
        "fr": slider_fr if slider_fr is not None else csv_pressures.get("fr", 26.7),
        "rl": slider_rl if slider_rl is not None else csv_pressures.get("rl", 26.7),
        "rr": slider_rr if slider_rr is not None else csv_pressures.get("rr", 26.7),
    }
    csv_temps = st.session_state.get("csv_temps", {"fl": 85.0, "fr": 85.0, "rl": 85.0, "rr": 85.0})
    TARGET_PRESS_CENTER = 26.75
    CENTER_TEMP = 90.0

    col_press_panel, col_temp_panel = st.columns(2)

    with col_press_panel:
        fl_p, fr_p, rl_p, rr_p = (live_press.get(k, 26.7) for k in ("fl", "fr", "rl", "rr"))
        bars = "".join(_tyre_bar(l, v, v - TARGET_PRESS_CENTER, "pressure") for l, v in [("FL", fl_p), ("FR", fr_p), ("RL", rl_p), ("RR", rr_p)])
        st.markdown(
            f'<div style="background:#141414;border:1px solid #2A2A2A;border-radius:8px;padding:12px 8px;">'
            f'<div style="font-size:10px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:#fff;margin-bottom:8px;text-align:center;">♟ Pressioni Gomme</div>'
            f'<div style="display:flex;justify-content:center;gap:4px;">{bars}</div></div>',
            unsafe_allow_html=True,
        )

    with col_temp_panel:
        fl_t, fr_t, rl_t, rr_t = (csv_temps.get(k, 85.0) for k in ("fl", "fr", "rl", "rr"))
        bars_t = "".join(_tyre_bar(l, v, v - CENTER_TEMP, "temp") for l, v in [("FL", fl_t), ("FR", fr_t), ("RL", rl_t), ("RR", rr_t)])
        csv_note = "" if csv_file else '<div style="font-size:9px;color:#7A7A7A;text-align:center;margin-top:6px;">Dati CSV non caricati — valori di esempio</div>'
        st.markdown(
            f'<div style="background:#141414;border:1px solid #2A2A2A;border-radius:8px;padding:12px 8px;">'
            f'<div style="font-size:10px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:#fff;margin-bottom:8px;text-align:center;">🌡 Temperature Gomme</div>'
            f'<div style="display:flex;justify-content:center;gap:4px;">{bars_t}</div>'
            f'{csv_note}</div>',
            unsafe_allow_html=True,
        )

    # ── AI Output (full-width below) ──
    if "last_response" in st.session_state:
        st.markdown("---")
        st.markdown('<div class="section-title">▶ Analisi PitWall.AI</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ai-output">{st.session_state["last_response"]}</div>',
            unsafe_allow_html=True,
        )

    # ─────────────────────────────────────────────
    # TAB: Strategia Carburante
    # ─────────────────────────────────────────────
with tab_carburante:
    st.markdown('<div class="section-title">Strategia Carburante</div>', unsafe_allow_html=True)

    import math
    import re

    def parse_mm_ss(time_str: str) -> float | None:
        """
        Converte formato mm:ss in minuti decimali.
        Es: "1:52" -> 1.8667 minuti
        Ritorna None se il formato non è valido.
        """
        if not time_str or not isinstance(time_str, str):
            return None
        
        # Rimuovi spazi e prova a parsare
        time_str = time_str.strip()
        match = re.match(r'^(\d{1,2}):(\d{2})$', time_str)
        if not match:
            return None
        
        try:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            
            if seconds >= 60:
                return None
            
            return minutes + seconds / 60.0
        except (ValueError, IndexError):
            return None

    def parse_lap_time(lap_time_str: str) -> float | None:
        """
        Converte una stringa 'mm:ss' o 'm:ss' in minuti decimali.
        Restituisce None se il formato non è valido.
        """
        match = re.match(r'^(\d{1,2}):([0-5]\d)$', lap_time_str.strip())
        if not match:
            return None
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        return minutes + seconds / 60.0

    # Input fields in columns
    col_sc1, col_sc2, col_sc3 = st.columns(3)
    
    with col_sc1:
        st.markdown("**Durata Gara (min)**")
        if "fuel_durata" not in st.session_state:
            st.session_state["fuel_durata"] = 60
        
        st.markdown(
            f'<div class="slider-value-display">{st.session_state["fuel_durata"]}</div>',
            unsafe_allow_html=True,
        )
        
        cm1, cp1 = st.columns(2)
        with cm1:
            if st.button("−", key="fd_minus", use_container_width=True):
                st.session_state["fuel_durata"] = max(1, st.session_state["fuel_durata"] - 5)
                st.rerun()
        with cp1:
            if st.button("+", key="fd_plus", use_container_width=True):
                st.session_state["fuel_durata"] = min(300, st.session_state["fuel_durata"] + 5)
                st.rerun()

    with col_sc2:
        st.markdown("**Tempo Giro Medio**")
        st.markdown('<div style="font-size:0.75rem;color:#999;">Formato: mm:ss</div>', unsafe_allow_html=True)
        lap_time_str = st.text_input(
            "Tempo giro",
            value="1:52",
            key="fuel_laptime",
            label_visibility="collapsed",
            placeholder="Es. 1:52"
        )
        
        # Validazione formato
        parsed_time = parse_mm_ss(lap_time_str)
        if lap_time_str and not parsed_time:
            st.error("❌ Formato non valido. Usa mm:ss (es. 1:52)")

    with col_sc3:
        st.markdown("**Consumo/Giro (L)**")
        if "fuel_cons" not in st.session_state:
            st.session_state["fuel_cons"] = 3.20
        
        st.markdown(
            f'<div class="slider-value-display">{st.session_state["fuel_cons"]:.2f}</div>',
            unsafe_allow_html=True,
        )
        
        cm3, cp3 = st.columns(2)
        with cm3:
            if st.button("−", key="fc_minus", use_container_width=True):
                st.session_state["fuel_cons"] = max(0.1, round(st.session_state["fuel_cons"] - 0.1, 2))
                st.rerun()
        with cp3:
            if st.button("+", key="fc_plus", use_container_width=True):
                st.session_state["fuel_cons"] = min(10.0, round(st.session_state["fuel_cons"] + 0.1, 2))
                st.rerun()

    st.markdown("")
    
    # Bottone calcolo
    btn_col = st.columns([0.3])[0]
    with btn_col:
        calc_btn = st.button("⛽ CALCOLA", type="primary", use_container_width=True)

    if calc_btn:
        # Validazione
        if not lap_time_str or not parse_mm_ss(lap_time_str):
            st.error("⚠️ Formato tempo giro non valido. Usa mm:ss (es. 1:52).")
        else:
            try:
                lap_min = parse_mm_ss(lap_time_str)
                durata = st.session_state["fuel_durata"]
                cons = st.session_state["fuel_cons"]
                
                if lap_min <= 0:
                    st.error("⚠️ Tempo giro deve essere positivo.")
                else:
                    n_giri = math.ceil(durata / lap_min)
                    carb_necessario = n_giri * cons
                    carico_consigliato = carb_necessario * 1.05
                    
                    st.markdown("")
                    result_html = f"""
                    <div style="background:#111111;border:1px solid #E8002D;border-radius:8px;
                                padding:24px;margin-top:16px;text-align:center;">
                        <div style="font-family:JetBrains Mono,monospace;font-size:10px;
                                    letter-spacing:2px;color:#666;text-transform:uppercase;
                                    margin-bottom:12px;">⛽ CARICO CARBURANTE CONSIGLIATO</div>
                        <div style="font-family:JetBrains Mono,monospace;font-size:42px;
                                    font-weight:700;color:#FFFFFF;margin-bottom:12px;">
                            {carico_consigliato:.1f} <span style="font-size:20px;color:#999;">L</span>
                        </div>
                        <div style="font-family:Inter,sans-serif;font-size:13px;color:#666;
                                    border-top:1px solid #1e1e1e;padding-top:12px;">
                            Giri stimati: <span style="color:#999;">{n_giri}</span>
                            &nbsp;|&nbsp;
                            Consumo base: <span style="color:#999;">{carb_necessario:.1f} L</span>
                            &nbsp;|&nbsp;
                            Margine 5%: <span style="color:#999;">+{carico_consigliato - carb_necessario:.1f} L</span>
                        </div>
                    </div>
                    """
                    st.markdown(result_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Errore nel calcolo: {str(e)}")

    # ─────────────────────────────────────────────
    # TAB: Storico Sessioni
    # ─────────────────────────────────────────────
with tab_storico:
    st.markdown('<div class="section-title">Storico Sessioni</div>', unsafe_allow_html=True)

    # Pulsante aggiorna
    col_refresh = st.columns([1])[0]
    with col_refresh:
        if st.button("🔄 AGGIORNA", type="secondary", key="btn_aggiorna_storico"):
            st.rerun()

    st.markdown("")

    # Filtri
    col_fa, col_ft = st.columns(2)
    
    unique_cars = db.get_unique_cars()
    unique_tracks = db.get_unique_tracks()
    
    with col_fa:
        filtro_auto = st.selectbox(
            "Filtra per Auto",
            options=["Tutte"] + unique_cars,
            key="filtro_auto"
        )
    
    with col_ft:
        filtro_track = st.selectbox(
            "Filtra per Tracciato",
            options=["Tutti"] + unique_tracks,
            key="filtro_track"
        )

    # Recupera sessioni filtrate
    sessions = db.get_sessions_filtered(
        car=filtro_auto if filtro_auto != "Tutte" else None,
        track=filtro_track if filtro_track != "Tutti" else None,
        limit=100
    )

    if not sessions:
        st.info("📭 Nessuna sessione registrata con i filtri selezionati.")
    else:
        st.markdown(f"**Sessioni trovate:** {len(sessions)}")
        st.markdown("---")
        
        for idx, session in enumerate(sessions):
            with st.expander(
                f"🏎 {session['car']} @ {session['track']} — {session['timestamp']}"
                + (" 📊 CSV" if session.get('csv_present') else "")
                + (" 📸 SCR" if session.get('screenshot_presente') else ""),
                expanded=(idx == 0)
            ):
                # Dettagli sessione
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.caption("🌡 Ambiente")
                    st.markdown(f"**{session['temp_ambient']:.0f}°C**")
                with col2:
                    st.caption("🛣 Pista")
                    st.markdown(f"**{session['temp_track']:.0f}°C**")
                with col3:
                    st.caption("☁ Condizioni")
                    st.markdown(f"**{session['conditions']}**")
                with col4:
                    st.caption("♟ PSI Input")
                    st.markdown(f"**{session['psi_input']:.2f} psi**" if session['psi_input'] else "**N/D**")
                
                st.markdown("---")
                
                # Feedback pilota
                st.caption("📋 Feedback Pilota")
                st.markdown(f"> {session['feedback_text']}")
                
                st.markdown("---")
                
                # Risposta AI
                st.caption("🤖 Analisi Race Engineer")
                st.markdown(session['llm_response'], unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ELABORAZIONE — bottone Analizza
# ─────────────────────────────────────────────

if btn_analizza:
    if not feedback.strip():
        st.warning("⚠️ Descrivi il problema riscontrato in pista prima di procedere.")
        st.stop()

    # Recupera API key — compatibile con locale (.env) e Streamlit Cloud (Secrets)
    api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY non trovata — verifica .env (locale) o Streamlit Secrets (cloud)")
        st.stop()

    # Parsing CSV (usa risultato pre-parsed dalla preview)
    csv_context = ""
    if csv_file is not None and "csv_parsed_result" in st.session_state:
        csv_result = st.session_state["csv_parsed_result"]
        csv_context = f"""
### Dati Sessione CSV
- **Giri**: {csv_result.get('laps_count', 0)}
- **Consumo medio**: {csv_result.get('fuel_cons_avg', 0):.2f} L/giro
- **Pressioni gomme**: {csv_result.get('pressures', {})}
- **Temperature gomme**: {csv_result.get('temperatures', {})}
"""

    # Formattazione setup
    setup_context = format_setup_for_prompt(current_setup)

    # Costruzione contesto completo (include session state)
    full_context = (
        f"Auto: {selected_car}\n"
        f"Tracciato: {st.session_state.get('sel_track', 'N/D')}\n"
        f"Condizioni: {st.session_state.get('sel_conditions', 'Asciutto')}\n"
        f"Temp. Ambiente: {st.session_state.get('temp_amb', 20)}°C\n"
        f"Temp. Pista: {st.session_state.get('temp_pista', 30)}°C\n\n"
        f"{setup_context}"
    )
    if csv_context:
        full_context += f"\n\n{csv_context}"
    full_context += f"\n\nFeedback pilota: {feedback.strip()}"

    # Chiamata LLM
    with st.spinner("🔄 Race Engineer in analisi..."):
        response = get_ai_response(
            user_input=full_context,
            api_key=api_key,
            auto=selected_car,
            tracciato=selected_track,
        )

    st.session_state["last_response"] = response

    # Salva sessione nel DB usando SessionDatabase
    try:
        _press_vals = [
            current_setup.get("tire_press_fl", 0),
            current_setup.get("tire_press_fr", 0),
            current_setup.get("tire_press_rl", 0),
            current_setup.get("tire_press_rr", 0),
        ]
        _psi_in = round(sum(_press_vals) / len(_press_vals), 2) if _press_vals else None
        
        session_data = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "car": selected_car,
            "track": selected_track,
            "conditions": st.session_state.get("sel_conditions", "Asciutto"),
            "temp_ambient": st.session_state.get("temp_amb", 20),
            "temp_track": st.session_state.get("temp_pista", 30),
            "psi_input": _psi_in,
            "psi_suggested": None,
            "feedback_text": feedback.strip()[:500],
            "llm_response": response,
            "csv_present": csv_file is not None,
            "screenshot_presente": screenshot_file is not None,
        }
        db.save_session(session_data)
    except Exception as e:
        st.warning(f"⚠️ Sessione non salvata nel database: {str(e)}")
        log_incident(f"Errore salvataggio sessione DB: {e}")

    # Reset caricamento vision params
    if st.session_state.get("load_vision_params"):
        st.session_state["load_vision_params"] = False

    st.rerun()

