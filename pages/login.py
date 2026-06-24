import streamlit as st
import uuid
from auth_config import get_auth_method, ENVIRONMENT
from db_auth import init_db, create_or_update_user

init_db()

st.set_page_config(page_title="PitWall.AI — Login", page_icon="🏁", layout="centered")

with open("styles/login.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# GT3 Car Animation
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

/* GT3 Car Animation Container */
.gt3-track {
    position: fixed;
    bottom: 80px;
    left: 0;
    width: 100%;
    height: 60px;
    overflow: hidden;
    pointer-events: none;
    z-index: 0;
    opacity: 0.18;
}

.gt3-car {
    position: absolute;
    right: -300px;
    bottom: 0;
    animation: carDrive 12s linear infinite;
}

@keyframes carDrive {
    0%   { right: -300px; }
    100% { right: 110%; }
}

/* Track line */
.gt3-track::before {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, #E8002D, transparent);
    opacity: 0.4;
}
</style>

<div class="gt3-track">
    <svg class="gt3-car" width="260" height="55" viewBox="0 0 260 55" xmlns="http://www.w3.org/2000/svg">
        <!-- GT3 silhouette stilizzata -->
        <!-- Corpo principale -->
        <path d="M20 38 L30 22 L55 16 L90 12 L140 11 L185 13 L215 20 L235 28 L240 38 Z" 
              fill="#E8002D" opacity="0.9"/>
        <!-- Tetto/abitacolo -->
        <path d="M70 12 L85 4 L155 3 L175 10 L185 13 L140 11 L90 12 Z" 
              fill="#FFFFFF" opacity="0.7"/>
        <!-- Ala posteriore -->
        <rect x="10" y="26" width="25" height="3" rx="1" fill="#FFFFFF" opacity="0.8"/>
        <rect x="18" y="22" width="2" height="6" fill="#FFFFFF" opacity="0.8"/>
        <!-- Ruota anteriore -->
        <circle cx="195" cy="40" r="10" fill="#111" stroke="#999" stroke-width="2"/>
        <circle cx="195" cy="40" r="5" fill="#333"/>
        <!-- Ruota posteriore -->
        <circle cx="60" cy="40" r="10" fill="#111" stroke="#999" stroke-width="2"/>
        <circle cx="60" cy="40" r="5" fill="#333"/>
        <!-- Splitter anteriore -->
        <path d="M235 32 L248 33 L248 36 L232 36 Z" fill="#E8002D" opacity="0.7"/>
        <!-- Dettagli finestrino -->
        <path d="M95 12 L100 5 L150 4 L160 11 Z" fill="#0a0a0a" opacity="0.6"/>
    </svg>
</div>
""", unsafe_allow_html=True)

# Hide sidebar navigation
st.markdown("""
<style>
    section[data-testid="stSidebar"] { display: none; }
    div[data-testid="stSidebarNav"] { display: none; }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }
</style>
""", unsafe_allow_html=True)

# Header
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown("""
    <div style="padding-top: 20px;">
        <div class="login-title">PITWALL<span style="color:#E8002D;">.AI</span></div>
        <div class="login-subtitle">Virtual Race Engineer — ACC GT3</div>
    </div>
    """, unsafe_allow_html=True)
with col_badge:
    st.markdown("""
    <div style="text-align: right; padding-top: 28px;">
        <span class="badge-mvp">MVP v2.0</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown('<div style="height:1px;background:#222;"></div>', unsafe_allow_html=True)
st.markdown("")

auth_method = get_auth_method()

if auth_method["type"] == "mock":
    st.markdown(f"""
    <div class="dev-banner">
        DEV MODE — Mock Authentication<br>
        <span style="color:#666;">Environment: <code style="color:#E8002D;">{ENVIRONMENT}</code></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Quick Login")

    col_demo, col_custom = st.columns(2)
    with col_demo:
        if st.button("Demo Pilot", use_container_width=True, type="primary"):
            uid = "demo_pilot_001"
            create_or_update_user(uid, "demo@pitwall.ai", "Demo Pilot", "mock")
            st.session_state.authenticated = True
            st.session_state.user_id = uid
            st.session_state.user_email = "demo@pitwall.ai"
            st.session_state.user_name = "Demo Pilot"
            st.switch_page("app.py")

    with col_custom:
        if st.button("Custom User", use_container_width=True):
            st.session_state.show_custom_login = True

    if st.session_state.get("show_custom_login"):
        st.markdown("---")
        st.markdown("#### Custom User (Dev Only)")
        email = st.text_input("Email", key="custom_email")
        name = st.text_input("Name", key="custom_name")
        if st.button("Login", use_container_width=True, type="primary"):
            if email and name:
                uid = str(uuid.uuid4())
                create_or_update_user(uid, email, name, "mock")
                st.session_state.authenticated = True
                st.session_state.user_id = uid
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.switch_page("app.py")
            else:
                st.error("Compila tutti i campi.")

else:
    st.markdown("### Login with Google")
    st.markdown("Accedi con il tuo account Google per continuare.")
    st.warning("""
    **Placeholder PROD:** Google OAuth richiede:
    - Google Cloud Project creato
    - Client ID e Secret in Streamlit Secrets
    - Redirect URI configurato
    """)
    if st.button("Login with Google", use_container_width=True, type="primary"):
        st.info("Redirect a Google OAuth... (da implementare con credentials)")

st.markdown("""
<div class="login-footer">
    PitWall.AI | AI-Powered Virtual Race Engineer<br>
    Built on <code>Claude Sonnet</code> + <code>Streamlit</code>
</div>
""", unsafe_allow_html=True)
