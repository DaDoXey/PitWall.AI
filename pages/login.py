import streamlit as st
import uuid
from auth_config import get_auth_method, ENVIRONMENT
from db_auth import init_db, create_or_update_user

init_db()

st.set_page_config(page_title="PitWall.AI — Login", page_icon="🏁", layout="centered")

with open("styles/login.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Ferrari 296 GT3 Animation
import streamlit.components.v1 as components

# CSS animation via st.markdown
st.markdown("""
<style>
.ferrari-track {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 90px;
    overflow: hidden;
    pointer-events: none;
    z-index: 0;
}
.ferrari-track::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #E8002D 30%, #E8002D 70%, transparent 100%);
    opacity: 0.25;
}
</style>
""", unsafe_allow_html=True)

# SVG animation via components.html (renderizza correttamente in iframe)
ferrari_svg_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; }
  body { background: transparent; overflow: hidden; }
  .track { position: relative; width: 100vw; height: 90px; overflow: hidden; }
  .car {
    position: absolute;
    bottom: 8px;
    right: -500px;
    opacity: 0.25;
    animation: drive 14s linear infinite;
    filter: drop-shadow(0 0 6px rgba(232, 0, 45, 0.3));
  }
  @keyframes drive {
    0%   { right: -500px; }
    100% { right: 110%; }
  }
</style>
</head>
<body>
<div class="track">
  <svg class="car" width="380" height="78" viewBox="0 0 420 85" xmlns="http://www.w3.org/2000/svg">
    <path d="M 45 62 L 52 52 L 60 44 L 75 36 L 95 30 L 130 25 L 175 22 L 220 21 L 265 22 L 295 24 L 318 28 L 330 34 L 335 42 L 338 52 L 340 62 Z" fill="#E8002D" opacity="0.95"/>
    <path d="M 115 25 L 122 13 L 135 7 L 200 5 L 250 6 L 268 10 L 280 18 L 290 24 L 265 22 L 220 21 L 175 22 L 130 25 Z" fill="#cc0022" opacity="0.9"/>
    <path d="M 128 24 L 135 10 L 145 7 L 200 6 L 245 7 L 260 12 L 268 20 L 250 22 L 175 22 Z" fill="#0a0a0a" opacity="0.75"/>
    <rect x="148" y="4" width="4" height="22" rx="1" fill="#FFFFFF" opacity="0.7"/>
    <rect x="195" y="0" width="2" height="22" rx="1" fill="#FFFFFF" opacity="0.8"/>
    <path d="M 118 25 L 110 22 L 108 26 L 118 27 Z" fill="#FFFFFF" opacity="0.6"/>
    <path d="M 338 58 L 370 60 L 370 64 L 338 64 Z" fill="#E8002D" opacity="0.8"/>
    <path d="M 355 60 L 380 62 L 380 65 L 355 64 Z" fill="#cc0022" opacity="0.6"/>
    <path d="M 42 52 L 30 50 L 20 53 L 18 60 L 25 65 L 42 65 Z" fill="#cc0022" opacity="0.85"/>
    <rect x="22" y="54" width="2" height="8" rx="0.5" fill="#0a0a0a" opacity="0.5"/>
    <rect x="26" y="53" width="2" height="9" rx="0.5" fill="#0a0a0a" opacity="0.5"/>
    <rect x="30" y="53" width="2" height="9" rx="0.5" fill="#0a0a0a" opacity="0.5"/>
    <rect x="34" y="54" width="2" height="8" rx="0.5" fill="#0a0a0a" opacity="0.5"/>
    <rect x="58" y="24" width="5" height="16" rx="1" fill="#FFFFFF" opacity="0.75"/>
    <rect x="80" y="24" width="5" height="16" rx="1" fill="#FFFFFF" opacity="0.75"/>
    <path d="M 50 22 L 98 22 L 98 26 L 50 26 Z" fill="#FFFFFF" opacity="0.9"/>
    <path d="M 48 18 L 100 18 L 100 21 L 48 21 Z" fill="#FFFFFF" opacity="0.7"/>
    <rect x="68" y="18" width="3" height="8" rx="0.5" fill="#FFFFFF" opacity="0.6"/>
    <circle cx="308" cy="65" r="17" fill="#111" stroke="#444" stroke-width="2.5"/>
    <circle cx="308" cy="65" r="10" fill="#1a1a1a" stroke="#555" stroke-width="1.5"/>
    <line x1="308" y1="55" x2="308" y2="75" stroke="#666" stroke-width="1.5"/>
    <line x1="298" y1="65" x2="318" y2="65" stroke="#666" stroke-width="1.5"/>
    <line x1="301" y1="58" x2="315" y2="72" stroke="#666" stroke-width="1"/>
    <line x1="315" y1="58" x2="301" y2="72" stroke="#666" stroke-width="1"/>
    <path d="M 290 48 Q 308 44 326 48 L 326 64 Q 308 82 290 64 Z" fill="none" stroke="#cc0022" stroke-width="1.5" opacity="0.5"/>
    <circle cx="85" cy="65" r="17" fill="#111" stroke="#444" stroke-width="2.5"/>
    <circle cx="85" cy="65" r="10" fill="#1a1a1a" stroke="#555" stroke-width="1.5"/>
    <line x1="85" y1="55" x2="85" y2="75" stroke="#666" stroke-width="1.5"/>
    <line x1="75" y1="65" x2="95" y2="65" stroke="#666" stroke-width="1.5"/>
    <line x1="78" y1="58" x2="92" y2="72" stroke="#666" stroke-width="1"/>
    <line x1="92" y1="58" x2="78" y2="72" stroke="#666" stroke-width="1"/>
    <path d="M 67 48 Q 85 44 103 48 L 103 64 Q 85 82 67 64 Z" fill="none" stroke="#cc0022" stroke-width="1.5" opacity="0.5"/>
    <line x1="103" y1="64" x2="290" y2="64" stroke="#cc0022" stroke-width="1" opacity="0.4"/>
  </svg>
</div>
</body>
</html>
"""
components.html(ferrari_svg_html, height=90, scrolling=False)

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

    # Separatore
    st.markdown("<hr style='border: none; border-top: 1px solid #222; margin: 16px 0;'>", unsafe_allow_html=True)

    # Bottone Google OAuth stilizzato
    import streamlit.components.v1 as components
    google_btn_html = """
<style>
.google-login-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    padding: 11px 20px;
    background: #ffffff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: #1a1a1a;
    transition: background 0.2s, box-shadow 0.2s;
    text-decoration: none;
}
.google-login-btn:hover {
    background: #f0f0f0;
    box-shadow: 0 2px 8px rgba(255,255,255,0.15);
}
.google-icon {
    width: 18px;
    height: 18px;
}
</style>

<a class="google-login-btn" href="/oauth/google" id="google-btn">
  <svg class="google-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
  </svg>
  Accedi con Google
</a>
"""
    components.html(google_btn_html, height=55)

    # TODO: implementare Google OAuth callback
    # Per ora mostra info se la pagina OAuth non è configurata
    st.info("Google OAuth in arrivo. Usa 'Demo Pilot' per testare.")

st.markdown("""
<div class="login-footer">
    PitWall.AI | AI-Powered Virtual Race Engineer<br>
    Built on <code>Claude Sonnet</code> + <code>Streamlit</code>
</div>
""", unsafe_allow_html=True)
