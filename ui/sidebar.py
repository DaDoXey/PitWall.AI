"""ui/sidebar.py — sidebar fissa: logo, navigazione, sessione attiva, logout.

Widget nativi Streamlit per i bottoni (stile da assets/app.css); chrome
(logo, box sessione) via st.markdown con stili inline / classi proprie.
Nessun selettore interno Streamlit, nessun wildcard.
"""

import streamlit as st

from ui import nav
from ui.demo_data import SESSION


def _logo() -> None:
    st.markdown(
        """
        <div style="padding:6px 2px 14px 2px;border-bottom:1px solid #222;margin-bottom:14px;">
          <div style="font-family:'Orbitron',sans-serif;font-size:1.15rem;font-weight:700;
                      letter-spacing:0.08em;color:#FFFFFF;line-height:1;">
            PITWALL<span style="color:#E8002D;">.AI</span>
          </div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                      letter-spacing:0.22em;color:#666;text-transform:uppercase;margin-top:6px;">
            Virtual Race Engineer
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _session_box() -> None:
    st.markdown(
        f"""
        <div style="margin-top:18px;background:#111111;border:1px solid #222;
                    border-left:3px solid #E8002D;border-radius:8px;padding:12px 14px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;
                      letter-spacing:0.2em;color:#00C853;text-transform:uppercase;
                      margin-bottom:10px;">● Sessione Attiva</div>
          <div style="display:flex;flex-direction:column;gap:7px;">
            <div style="display:flex;justify-content:space-between;">
              <span style="font-family:'Inter',sans-serif;font-size:0.62rem;
                           color:#666;text-transform:uppercase;letter-spacing:0.08em;">Circuito</span>
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                           color:#FFFFFF;">{SESSION['track']}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="font-family:'Inter',sans-serif;font-size:0.62rem;
                           color:#666;text-transform:uppercase;letter-spacing:0.08em;">Vettura</span>
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                           color:#FFFFFF;">{SESSION['car']}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="font-family:'Inter',sans-serif;font-size:0.62rem;
                           color:#666;text-transform:uppercase;letter-spacing:0.08em;">Giri</span>
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                           color:#FFFFFF;">{SESSION['laps']}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="font-family:'Inter',sans-serif;font-size:0.62rem;
                           color:#666;text-transform:uppercase;letter-spacing:0.08em;">Stint</span>
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                           color:#FFFFFF;">{SESSION['stint']}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _logout() -> None:
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_email = None
    st.session_state.gigi_welcomed = False
    st.switch_page("pages/login.py")


def render_sidebar() -> None:
    """Disegna la sidebar e gestisce i click di navigazione/logout."""
    active = nav.current_page()
    with st.sidebar:
        _logo()

        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.55rem;'
            'letter-spacing:0.2em;color:#444;text-transform:uppercase;margin-bottom:6px;">'
            'Navigazione</div>',
            unsafe_allow_html=True,
        )

        for page in nav.PAGES:
            icon = nav.PAGE_ICONS.get(page, "•")
            is_active = page == active
            if st.button(
                f"{icon}  {page}",
                key=f"nav_{page}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                if not is_active:
                    nav.go_to(page)

        _session_box()

        st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
        if st.button("⏻  Esci", key="btn_logout", use_container_width=True):
            _logout()
