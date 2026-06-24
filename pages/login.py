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

# SVG animation via components.html
gt3_svg_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; }
  body { background: transparent; overflow: hidden; }
  .track { position: relative; width: 100vw; height: 110px; overflow: hidden; }
  .car {
    position: absolute;
    bottom: 5px;
    right: -600px;
    opacity: 0.18;
    animation: drive 16s linear infinite;
  }
  @keyframes drive {
    0%   { right: -600px; }
    100% { right: 110%; }
  }
</style>
</head>
<body>
<div class="track">
  <svg class="car" width="480" height="110" viewBox="0 0 520 120" xmlns="http://www.w3.org/2000/svg">

    <!-- Rear diffuser -->
    <path d="M 25 82 L 15 78 L 8 80 L 5 88 L 12 95 L 30 95 L 35 88 Z" fill="#E8002D" opacity="0.7"/>
    <rect x="10" y="83" width="2" height="9" rx="0.5" fill="#0a0a0a" opacity="0.4"/>
    <rect x="15" y="82" width="2" height="10" rx="0.5" fill="#0a0a0a" opacity="0.4"/>
    <rect x="20" y="82" width="2" height="10" rx="0.5" fill="#0a0a0a" opacity="0.4"/>
    <rect x="25" y="83" width="2" height="9" rx="0.5" fill="#0a0a0a" opacity="0.4"/>

    <!-- Rear wing endplate left -->
    <rect x="38" y="30" width="6" height="32" rx="1" fill="#E8002D" opacity="0.85"/>
    <!-- Rear wing endplate right -->
    <rect x="88" y="30" width="6" height="32" rx="1" fill="#E8002D" opacity="0.85"/>
    <!-- Rear wing main plane -->
    <path d="M 35 33 L 95 33 L 95 40 L 35 40 Z" fill="#E8002D" opacity="0.9"/>
    <!-- Rear wing flap -->
    <path d="M 33 27 L 97 27 L 97 32 L 33 32 Z" fill="#cc0022" opacity="0.7"/>
    <!-- Wing gurney flap -->
    <rect x="33" y="25" width="64" height="2" rx="0.5" fill="#FFFFFF" opacity="0.5"/>
    <!-- Wing stay sx -->
    <rect x="52" y="40" width="4" height="22" rx="1" fill="#FFFFFF" opacity="0.55"/>
    <!-- Wing stay dx -->
    <rect x="76" y="40" width="4" height="22" rx="1" fill="#FFFFFF" opacity="0.55"/>

    <!-- Antenna 1 (short, L-shape) -->
    <rect x="215" y="16" width="2" height="16" rx="0.5" fill="#FFFFFF" opacity="0.6"/>
    <rect x="215" y="16" width="8" height="1.5" rx="0.5" fill="#FFFFFF" opacity="0.5"/>
    <!-- Antenna 2 (tall, straight) -->
    <rect x="248" y="4" width="1.5" height="28" rx="0.5" fill="#FFFFFF" opacity="0.65"/>

    <!-- Body silhouette — smooth GT3 profile -->
    <path d="
      M 35 82
      L 42 72
      L 55 64
      L 72 56
      L 95 50
      L 125 44
      L 160 39
      L 195 35
      L 225 33
      L 260 32
      L 300 32
      L 335 33
      L 360 35
      L 385 38
      L 405 42
      L 420 48
      L 432 55
      L 440 64
      L 445 72
      L 448 82
      Z
    " fill="#E8002D" opacity="0.92"/>

    <!-- Roof/cabin -->
    <path d="
      M 175 38
      L 185 26
      L 200 20
      L 235 17
      L 275 16
      L 305 17
      L 325 20
      L 340 26
      L 348 33
      L 300 32
      L 260 32
      L 225 33
      L 195 35
      Z
    " fill="#cc0022" opacity="0.88"/>

    <!-- Windshield -->
    <path d="
      M 190 37
      L 198 23
      L 210 19
      L 240 17
      L 270 17
      L 295 18
      L 310 22
      L 320 28
      L 330 33
      L 260 32
      L 225 33
      L 195 35
      Z
    " fill="#0a0a0a" opacity="0.7"/>

    <!-- Front splitter -->
    <path d="M 445 78 L 475 80 L 478 84 L 445 84 Z" fill="#E8002D" opacity="0.75"/>
    <path d="M 460 80 L 490 82 L 492 86 L 460 85 Z" fill="#cc0022" opacity="0.55"/>

    <!-- Side skirt -->
    <line x1="95" y1="82" x2="405" y2="82" stroke="#cc0022" stroke-width="1.5" opacity="0.35"/>

    <!-- Rear wheel arch -->
    <path d="M 55 60 Q 78 48 100 60 L 100 82 Q 78 98 55 82 Z" fill="none" stroke="#cc0022" stroke-width="1.5" opacity="0.4"/>
    <!-- Rear wheel -->
    <circle cx="78" cy="80" r="18" fill="#111" stroke="#444" stroke-width="2.5"/>
    <circle cx="78" cy="80" r="11" fill="#1a1a1a" stroke="#555" stroke-width="1.5"/>
    <line x1="78" y1="69" x2="78" y2="91" stroke="#666" stroke-width="1.5"/>
    <line x1="67" y1="80" x2="89" y2="80" stroke="#666" stroke-width="1.5"/>
    <line x1="70" y1="72" x2="86" y2="88" stroke="#666" stroke-width="1"/>
    <line x1="86" y1="72" x2="70" y2="88" stroke="#666" stroke-width="1"/>

    <!-- Front wheel arch -->
    <path d="M 400 56 Q 423 44 445 56 L 445 82 Q 423 98 400 82 Z" fill="none" stroke="#cc0022" stroke-width="1.5" opacity="0.4"/>
    <!-- Front wheel -->
    <circle cx="423" cy="80" r="18" fill="#111" stroke="#444" stroke-width="2.5"/>
    <circle cx="423" cy="80" r="11" fill="#1a1a1a" stroke="#555" stroke-width="1.5"/>
    <line x1="423" y1="69" x2="423" y2="91" stroke="#666" stroke-width="1.5"/>
    <line x1="412" y1="80" x2="434" y2="80" stroke="#666" stroke-width="1.5"/>
    <line x1="415" y1="72" x2="431" y2="88" stroke="#666" stroke-width="1"/>
    <line x1="431" y1="72" x2="415" y2="88" stroke="#666" stroke-width="1"/>

    <!-- Mirror -->
    <path d="M 170 37 L 162 34 L 160 38 L 170 39 Z" fill="#FFFFFF" opacity="0.5"/>

    <!-- Headlight -->
    <ellipse cx="442" cy="62" rx="6" ry="3" fill="#FFFFFF" opacity="0.5"/>

    <!-- Underbody line -->
    <line x1="100" y1="82" x2="400" y2="82" stroke="#E8002D" stroke-width="0.8" opacity="0.2"/>

  </svg>
</div>
</body>
</html>
"""
components.html(gt3_svg_html, height=110, scrolling=False)

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
