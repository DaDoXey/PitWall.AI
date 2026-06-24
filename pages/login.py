import streamlit as st
import uuid
from auth_config import get_auth_method, ENVIRONMENT
from db_auth import init_db, create_or_update_user

init_db()

st.set_page_config(page_title="PitWall.AI — Login", page_icon="🏁", layout="centered")

with open("styles/login.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# GT3 Silhouette Animation
import streamlit.components.v1 as components

# Track line CSS
st.markdown("""
<style>
.ferrari-track {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #E8002D 30%, #E8002D 70%, transparent 100%);
    opacity: 0.25;
    pointer-events: none;
    z-index: 0;
}
</style>
""", unsafe_allow_html=True)

# SVG animation — clean GT3 silhouette matching reference
gt3_svg_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; }
  body { background: transparent; overflow: hidden; }
  .track { position: relative; width: 100vw; height: 100px; overflow: hidden; }
  .car {
    position: absolute;
    bottom: 2px;
    right: -550px;
    opacity: 0.2;
    animation: drive 16s linear infinite;
  }
  @keyframes drive {
    0%   { right: -550px; }
    100% { right: 110%; }
  }
</style>
</head>
<body>
<div class="track">
  <svg class="car" width="460" height="95" viewBox="0 0 500 100" xmlns="http://www.w3.org/2000/svg">

    <!-- REAR WING — large, prominent, defines the GT3 look -->
    <!-- Endplate sx -->
    <rect x="30" y="18" width="5" height="38" rx="1.5" fill="#E8002D" opacity="0.85"/>
    <!-- Endplate dx -->
    <rect x="100" y="18" width="5" height="38" rx="1.5" fill="#E8002D" opacity="0.85"/>
    <!-- Main plane -->
    <path d="M 28 22 L 108 22 L 108 30 L 28 30 Z" fill="#E8002D" opacity="0.9"/>
    <!-- Flap -->
    <path d="M 26 16 L 110 16 L 110 21 L 26 21 Z" fill="#cc0022" opacity="0.65"/>
    <!-- Gurney -->
    <rect x="26" y="14" width="84" height="2" rx="0.5" fill="#FFFFFF" opacity="0.4"/>
    <!-- Stays -->
    <rect x="48" y="30" width="3" height="24" rx="0.5" fill="#FFFFFF" opacity="0.45"/>
    <rect x="82" y="30" width="3" height="24" rx="0.5" fill="#FFFFFF" opacity="0.45"/>

    <!-- BODY — single smooth flowing silhouette -->
    <path d="
      M 30 72
      C 35 62, 48 52, 65 44
      C 82 36, 105 30, 135 26
      C 165 22, 200 20, 240 19
      C 280 18, 320 18, 355 19
      C 375 20, 395 22, 415 26
      C 430 30, 442 36, 450 44
      C 456 50, 460 58, 462 66
      L 462 72
      Z
    " fill="#E8002D" opacity="0.92"/>

    <!-- ROOF / CABIN — smooth dome -->
    <path d="
      M 185 24
      C 192 16, 210 10, 240 8
      C 270 7, 300 7, 325 9
      C 345 11, 358 16, 365 22
      L 355 19
      C 320 18, 280 18, 240 19
      C 200 20, 165 22, 135 26
      C 120 28, 110 30, 105 32
      Z
    " fill="#cc0022" opacity="0.85"/>

    <!-- WINDSHIELD — dark glass -->
    <path d="
      M 195 23
      C 200 16, 215 11, 240 9
      C 265 8, 290 8, 310 10
      C 325 12, 335 16, 342 22
      L 300 19
      C 270 18, 240 19, 210 21
      Z
    " fill="#0a0a0a" opacity="0.65"/>

    <!-- FRONT SPLITTER — low, wide -->
    <path d="M 458 68 L 485 70 L 488 74 L 458 74 Z" fill="#E8002D" opacity="0.7"/>

    <!-- SIDE SKIRT line -->
    <line x1="65" y1="72" x2="420" y2="72" stroke="#cc0022" stroke-width="1.2" opacity="0.3"/>

    <!-- REAR DIFFUSER — subtle -->
    <path d="M 28 66 L 18 64 L 12 68 L 10 74 L 18 78 L 32 78 L 35 72 Z" fill="#cc0022" opacity="0.6"/>

    <!-- REAR WHEEL -->
    <circle cx="72" cy="74" r="14" fill="#111" stroke="#444" stroke-width="2"/>
    <circle cx="72" cy="74" r="8" fill="#1a1a1a" stroke="#555" stroke-width="1"/>
    <!-- Spokes -->
    <line x1="72" y1="66" x2="72" y2="82" stroke="#555" stroke-width="1.2"/>
    <line x1="64" y1="74" x2="80" y2="74" stroke="#555" stroke-width="1.2"/>
    <line x1="66" y1="68" x2="78" y2="80" stroke="#555" stroke-width="0.8"/>
    <line x1="78" y1="68" x2="66" y2="80" stroke="#555" stroke-width="0.8"/>

    <!-- FRONT WHEEL -->
    <circle cx="418" cy="74" r="14" fill="#111" stroke="#444" stroke-width="2"/>
    <circle cx="418" cy="74" r="8" fill="#1a1a1a" stroke="#555" stroke-width="1"/>
    <!-- Spokes -->
    <line x1="418" y1="66" x2="418" y2="82" stroke="#555" stroke-width="1.2"/>
    <line x1="410" y1="74" x2="426" y2="74" stroke="#555" stroke-width="1.2"/>
    <line x1="412" y1="68" x2="424" y2="80" stroke="#555" stroke-width="0.8"/>
    <line x1="424" y1="68" x2="412" y2="80" stroke="#555" stroke-width="0.8"/>

    <!-- Antenna 1 — short L-shape -->
    <rect x="245" y="6" width="1.5" height="10" rx="0.5" fill="#FFFFFF" opacity="0.5"/>
    <rect x="245" y="6" width="6" height="1" rx="0.5" fill="#FFFFFF" opacity="0.4"/>
    <!-- Antenna 2 — tall straight -->
    <rect x="270" y="0" width="1" height="18" rx="0.5" fill="#FFFFFF" opacity="0.55"/>

    <!-- HEADLIGHT -->
    <ellipse cx="456" cy="50" rx="5" ry="2.5" fill="#FFFFFF" opacity="0.45"/>

    <!-- MIRROR -->
    <path d="M 178 23 L 170 20 L 168 24 L 178 25 Z" fill="#FFFFFF" opacity="0.4"/>

  </svg>
</div>
</body>
</html>
"""
components.html(gt3_svg_html, height=100, scrolling=False)

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
