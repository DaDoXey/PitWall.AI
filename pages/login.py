import streamlit as st
import uuid
from auth_config import get_auth_method, ENVIRONMENT
from db_auth import init_db, create_or_update_user

init_db()

st.set_page_config(page_title="PitWall.AI — Login", page_icon="🏁", layout="centered")

with open("styles/login.css") as f:
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
