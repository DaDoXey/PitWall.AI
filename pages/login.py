import streamlit as st
import uuid
from auth_config import is_oauth_configured
from db_auth import init_db, create_or_update_user
from ui import demo_data as dd  # sorgente dati demo (modulo puro, nessuna dipendenza Streamlit)

init_db()

st.set_page_config(page_title="PitWall.AI — Login", page_icon="🏁", layout="centered")

# Design system: font self-hosted + token (senza gli stili dei componenti dell'app)
from assets.css_loader import inject_design_system
inject_design_system(include_app_css=False)

with open("styles/login.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Hide sidebar navigation
st.markdown("""
<style>
    section[data-testid="stSidebar"] { display: none; }
    div[data-testid="stSidebarNav"] { display: none; }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }
</style>
""", unsafe_allow_html=True)

# ── HERO cinematografico ──
st.markdown("""
<div class="pw-hero">
    <div class="pw-hero-title">PITWALL<span class="dot">●</span>AI</div>
</div>
<div class="pw-ruler"></div>
<div class="pw-hero" style="padding-top:0;">
    <div class="pw-hero-sub">Virtual Race Engineer · ACC GT3</div>
    <div class="pw-hero-tagline" style="font-family:'Inter',sans-serif;font-size:0.82rem;color:#999999;font-style:italic;margin-top:6px;">Il tuo ingegnere di pista, sempre al muretto</div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

oauth_ready = is_oauth_configured()

# ── Blocco autenticazione, centrato (effetto card) ──
_left, _mid, _right = st.columns([1, 2, 1])
with _mid:
    # Bottone "Accedi con Google" — sempre VISIBILE ma PREDISPOSTO (non attivo).
    # Elemento non interattivo: nessun href, nessuna chiamata OAuth.
    _google_tag = "" if oauth_ready else "· in arrivo ·"
    st.markdown(f"""
    <div class="pw-google-btn" title="Login Google in arrivo — per ora usa Quick Login">
        <svg class="pw-google-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        <span>Accedi con Google</span>
        <span class="pw-google-tag">{_google_tag}</span>
    </div>
    """, unsafe_allow_html=True)

    # TODO OAuth: quando is_oauth_configured() ritornerà True (GOOGLE_CLIENT_ID/SECRET
    # in Streamlit Secrets + redirect URI configurato), agganciare QUI il flusso reale —
    # sostituire il bottone statico sopra con il redirect/azione OAuth e gestire il callback.

    st.markdown('<div class="pw-divider">oppure</div>', unsafe_allow_html=True)
    st.markdown('<div class="pw-quick-label">Quick Login · DEV</div>', unsafe_allow_html=True)

    col_demo, col_custom = st.columns(2)
    with col_demo:
        if st.button("Demo Pilot", use_container_width=True, type="primary"):
            uid = "demo_pilot_001"
            create_or_update_user(uid, "demo@pitwall.ai", "Demo Pilot", "mock")
            st.session_state.authenticated = True
            st.session_state.user_id = uid
            st.session_state.user_email = "demo@pitwall.ai"
            st.session_state.user_name = "Demo Pilot"
            st.session_state["gigi_chat"] = []  # chat azzerata a ogni login (come il DB)
            # Coerenza demo: retrotreno a freddo SOTTO finestra (storia sovrasterzo).
            st.session_state["setup_tire_press_rl"] = dd.COLD_PRESSURES["rl"]
            st.session_state["setup_tire_press_rr"] = dd.COLD_PRESSURES["rr"]
            st.switch_page("app.py")

    with col_custom:
        if st.button("Custom User", use_container_width=True):
            st.session_state.show_custom_login = True

    if st.session_state.get("show_custom_login"):
        st.markdown("---")
        st.markdown("#### Custom User (Dev Only)")
        # st.form: invio con Enter da un campo testo + un solo rerun al submit
        with st.form("custom_login_form", clear_on_submit=False):
            email = st.text_input("Email", key="custom_email")
            name = st.text_input("Name", key="custom_name")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
        if submitted:
            if email and name:
                uid = str(uuid.uuid4())
                create_or_update_user(uid, email, name, "mock")
                st.session_state.authenticated = True
                st.session_state.user_id = uid
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.session_state["gigi_chat"] = []  # chat azzerata a ogni login (come il DB)
                # Coerenza demo: retrotreno a freddo SOTTO finestra (storia sovrasterzo).
                st.session_state["setup_tire_press_rl"] = dd.COLD_PRESSURES["rl"]
                st.session_state["setup_tire_press_rr"] = dd.COLD_PRESSURES["rr"]
                st.switch_page("app.py")
            else:
                st.error("Compila tutti i campi (email e nome).")

st.markdown("""
<div class="login-footer">
    PitWall.AI | AI-Powered Virtual Race Engineer<br>
    Built on <code>Claude</code> + <code>Streamlit</code>
</div>
""", unsafe_allow_html=True)

# ── Traccia telemetria decorativa in basso (FASE 4) ──
# Linea "giro di telemetria" tenue, full-width, dietro il contenuto. Polyline
# semplice inline (nessun selettore Streamlit, nessun asset esterno).
st.markdown("""
<div class="pw-telemetry-trace" aria-hidden="true">
  <svg viewBox="0 0 1200 80" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
    <polyline points="0,58 70,55 130,30 190,52 250,50 310,20 380,48 450,46 520,60 580,33 650,62 710,40 770,56 830,24 900,52 970,48 1040,64 1100,36 1200,58"
      fill="none" stroke="#E8002D" stroke-width="2" vector-effect="non-scaling-stroke"
      stroke-linejoin="round" stroke-linecap="round"/>
  </svg>
</div>
""", unsafe_allow_html=True)
