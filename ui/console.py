"""ui/console.py — Engineer Console (Gigi): analisi a 4 card + chat + demo-mode.

- Header Gigi (avatar SVG) via components.html (stili inline + font base64).
- Parsing dell'output a 4 sezioni di agent.py → 4 card numerate stylate; la
  Correzione resa come box "SCHEDA SETUP" evidenziato. Parsing robusto: se una
  sezione manca, la card degrada con grazia (non va in errore).
- Quick-chips (st.button in colonne) + chat input nativo.
- DEMO-MODE (ui/flags): risposta CACHE pre-validata → la demo non dipende dalla
  rete. agent.py NON viene toccato: la cache vive QUI.

NB sul rendering: l'header Gigi (altezza fissa) usa components.html; le 4 card,
a contenuto di altezza variabile, usano st.markdown con HTML/stili INLINE e classi
proprie (nessun selettore interno Streamlit, nessun wildcard) — scelta robusta
contro il clipping degli iframe a contenuto dinamico su Cloud.
"""

import html
import os
import re

import streamlit as st
import streamlit.components.v1 as components

from ui import components as c
from ui import flags
from ui import demo_data as dd

# ─────────────────────────────────────────────
# PROMPT DEMO + RISPOSTA CACHE PRE-VALIDATA (4 sezioni canoniche)
# ─────────────────────────────────────────────
DEMO_PROMPT = "L'auto scivola dietro in accelerazione"

DEMO_RESPONSE = """## Diagnosi
L'auto perde il posteriore in uscita di curva, quando apri il gas. La telemetria conferma il quadro: le **pressioni posteriori sono sotto la finestra** (28.2 / 28.0 psi a caldo, finestra 28.5–30.0) e la **Post.DX tocca i 105°C**, oltre il limite di 95°C. Una posteriore sgonfia flette troppo: impronta instabile e poco grip proprio in trazione.

## Causa Meccanica Probabile
Causa primaria: **pressioni posteriori troppo basse** → la gomma lavora fuori finestra, scalda in modo anomalo (Post.DX) e perde aderenza quando carichi la trazione.
Causa secondaria: **precarico differenziale basso**, che rende il retrotreno nervoso in apertura gas.

## Correzione Setup Consigliata
Pressione gomme posteriori (a freddo) **+0.5 psi · 26.0 → 26.5**, per riportarle in finestra a caldo.
In subordine, alza il **precarico differenziale · 60 → 75 Nm** per stabilizzare la trazione.
Una modifica per volta: parti dalle pressioni.

## Note Aggiuntive
- Verifica dopo 2–3 giri che le posteriori entrino in finestra a caldo (28.5–30.0 psi).
- Controlla che la Post.DX scenda sotto i 100°C.
- Le pressioni nel setup ACC sono a freddo: a caldo salgono di ~2.5–3.5 psi.
"""

# Quick-chips (prompt preset) — come da brief.
CHIPS = ["Sottosterzo", "Calcola carburante", "Analizza gomme", "Bilanciamento freni"]

# (titolo canonico, regex header tollerante, icona). Ordine = ordine card.
_SECTIONS = [
    ("Diagnosi", r"##\s*Diagnosi", "🔍"),
    ("Causa Meccanica Probabile", r"##\s*Causa\s+Meccanica", "⚙"),
    ("Correzione Setup Consigliata", r"##\s*Correzione\s+Setup", "🔧"),
    ("Note Aggiuntive", r"##\s*Note\s+Aggiuntive", "📋"),
]


# ─────────────────────────────────────────────
# PARSING ROBUSTO 4 SEZIONI
# ─────────────────────────────────────────────
def parse_sections(text: str):
    """Ritorna [(titolo, icona, body), ...] per le 4 sezioni canoniche.
    Sezione mancante → body "" (degrada con grazia, mai errore)."""
    text = text or ""
    found = []  # (pos, section_index)
    for i, (_title, pat, _icon) in enumerate(_SECTIONS):
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            found.append((m.start(), i))
    found.sort()

    bodies = {i: "" for i in range(len(_SECTIONS))}
    for idx, (start, i) in enumerate(found):
        line_end = text.find("\n", start)
        body_start = (line_end + 1) if line_end != -1 else len(text)
        next_start = found[idx + 1][0] if idx + 1 < len(found) else len(text)
        bodies[i] = text[body_start:next_start].strip()

    return [(_SECTIONS[i][0], _SECTIONS[i][2], bodies[i]) for i in range(len(_SECTIONS))]


# ─────────────────────────────────────────────
# MARKDOWN-LITE → HTML (per il body delle card)
# ─────────────────────────────────────────────
def _inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def _md_lite(body: str) -> str:
    if not body.strip():
        return '<span style="color:#666;font-style:italic;">— sezione non disponibile</span>'
    out, para, items = [], [], []

    def flush_para():
        if para:
            out.append("<p style=\"margin:0 0 8px;\">" + "<br>".join(_inline(x) for x in para) + "</p>")
            para.clear()

    def flush_list():
        if items:
            lis = "".join(
                f'<li style="margin:3px 0;">{_inline(x)}</li>' for x in items
            )
            out.append(f'<ul style="margin:0 0 8px;padding-left:18px;">{lis}</ul>')
            items.clear()

    for ln in body.split("\n"):
        s = ln.strip()
        if not s:
            flush_para(); flush_list(); continue
        if re.match(r"(?:[-*]|\d+\.)\s+", s):
            flush_para()
            items.append(re.sub(r"^(?:[-*]|\d+\.)\s+", "", s))
        else:
            flush_list()
            para.append(s)
    flush_para(); flush_list()
    return "".join(out)


# ─────────────────────────────────────────────
# RECUPERO ANALISI (demo-mode / cache / API con fallback)
# ─────────────────────────────────────────────
def _api_key() -> str:
    try:
        return st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))
    except Exception:
        return os.getenv("ANTHROPIC_API_KEY", "")


def _is_demo_prompt(prompt: str) -> bool:
    norm = re.sub(r"[^a-z]", "", (prompt or "").lower())
    return re.sub(r"[^a-z]", "", DEMO_PROMPT.lower()) in norm or norm in re.sub(r"[^a-z]", "", DEMO_PROMPT.lower())


def get_console_analysis(prompt: str):
    """Ritorna (testo_4_sezioni, sorgente). sorgente ∈ {demo, cache, api, fallback}."""
    # 1) demo-mode attivo o prompt = scenario demo → cache (sempre, niente rete)
    if flags.demo_mode() or _is_demo_prompt(prompt):
        return DEMO_RESPONSE, ("demo" if flags.demo_mode() else "cache")

    # 2) tentativo API reale, con fallback alla cache
    api_key = _api_key()
    if not api_key:
        return DEMO_RESPONSE, "fallback"
    try:
        from agent import get_ai_response  # file protetto: solo chiamata
        context = (
            f"Auto: {dd.SESSION['car']}\nTracciato: {dd.SESSION['track']}\n"
            f"Condizioni: {dd.SESSION['stint']}\n\n"
            f"Telemetria (a caldo): temperature gomme max "
            f"FL {dd.TYRE_TEMP_MAX['fl']}°C, FR {dd.TYRE_TEMP_MAX['fr']}°C, "
            f"RL {dd.TYRE_TEMP_MAX['rl']}°C, RR {dd.TYRE_TEMP_MAX['rr']}°C; "
            f"pressioni a caldo {dd.HOT_PRESSURES}.\n\n"
            f"Feedback pilota: {prompt.strip()}"
        )
        resp = get_ai_response(user_input=context, api_key=api_key,
                               auto=dd.SESSION["car"], tracciato=dd.SESSION["track"])
        # validazione minima: deve contenere le 4 sezioni
        ok = all(re.search(pat, resp or "", re.IGNORECASE) for _t, pat, _i in _SECTIONS)
        return (resp, "api") if ok else (DEMO_RESPONSE, "fallback")
    except Exception:
        return DEMO_RESPONSE, "fallback"


# ─────────────────────────────────────────────
# RENDER — header Gigi
# ─────────────────────────────────────────────
def _gigi_header_html() -> str:
    fonts = c.iframe_fonts("Orbitron", "Inter", "JetBrains Mono")
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
{fonts}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'Inter',sans-serif;}}
.h{{display:flex;align-items:center;gap:14px;background:linear-gradient(135deg,{c.BG_SURFACE},{c.BG_RAISED});
   border:1px solid {c.BORDER};border-left:3px solid {c.ACCENT};border-radius:10px;padding:12px 16px;}}
.name{{font-family:'Orbitron',sans-serif;font-size:0.95rem;font-weight:700;color:#FFFFFF;letter-spacing:0.04em;}}
.role{{font-family:'JetBrains Mono',monospace;font-size:0.66rem;color:#666;letter-spacing:0.1em;
   text-transform:uppercase;margin-top:3px;}}
.status{{display:inline-flex;align-items:center;gap:5px;font-family:'JetBrains Mono',monospace;
   font-size:0.6rem;color:{c.STATUS_OK};letter-spacing:0.12em;text-transform:uppercase;}}
.dot{{width:7px;height:7px;border-radius:50%;background:{c.STATUS_OK};box-shadow:0 0 6px {c.STATUS_OK};}}
</style></head><body>
<div class="h">
  <div>{c.gigi_avatar_svg(48)}</div>
  <div style="flex:1;">
    <div class="name">Gigi</div>
    <div class="role">Race Engineer</div>
  </div>
  <div class="status"><span class="dot"></span>online</div>
</div></body></html>"""


# ─────────────────────────────────────────────
# RENDER — 4 card analisi (st.markdown inline, robusto su Cloud)
# ─────────────────────────────────────────────
def _card_html(index: int, title: str, icon: str, body_html: str, is_setup: bool) -> str:
    num = f"{index + 1:02d}"
    accent_border = c.ACCENT if is_setup else c.BORDER
    bg = "rgba(232,0,45,0.06)" if is_setup else c.BG_SURFACE
    setup_pill = (
        f'<span style="margin-left:auto;font-family:\'JetBrains Mono\',monospace;'
        f'font-size:0.58rem;letter-spacing:0.14em;color:{c.ACCENT};border:1px solid {c.ACCENT};'
        f'border-radius:4px;padding:2px 7px;text-transform:uppercase;">Scheda Setup</span>'
        if is_setup else ""
    )
    body_wrap = (
        f'<div style="background:{c.BG_INSET};border:1px solid {c.ACCENT};border-radius:8px;'
        f'padding:12px 14px;">{body_html}</div>'
        if is_setup else body_html
    )
    return (
        f'<div style="background:{bg};border:1px solid {accent_border};border-radius:10px;'
        f'padding:14px 16px;margin-bottom:12px;">'
        f'<div style="display:flex;align-items:center;gap:10px;border-bottom:1px solid {c.BORDER};'
        f'padding-bottom:9px;margin-bottom:10px;">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.95rem;color:{c.ACCENT};">{num}</span>'
        f'<span style="font-size:1rem;">{icon}</span>'
        f'<span style="font-family:\'Orbitron\',sans-serif;font-size:0.8rem;font-weight:700;'
        f'letter-spacing:0.06em;text-transform:uppercase;color:#FFFFFF;">{title}</span>'
        f'{setup_pill}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.86rem;line-height:1.6;color:#BBBBBB;">'
        f'{body_wrap}</div>'
        f'</div>'
    )


def _render_cards(text: str) -> None:
    sections = parse_sections(text)
    cards = "".join(
        _card_html(i, title, icon, _md_lite(body), is_setup=(i == 2))
        for i, (title, icon, body) in enumerate(sections)
    )
    st.markdown(cards, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RENDER PAGINA
# ─────────────────────────────────────────────
def render() -> None:
    st.markdown(
        c.page_header("Engineer Console", "Gigi · Race Engineer · online"),
        unsafe_allow_html=True,
    )

    components.html(_gigi_header_html(), height=92, scrolling=False)

    # Stato iniziale: console SEMPRE popolata con lo scenario demo (mai vuota).
    if "console_response" not in st.session_state:
        st.session_state["console_question"] = DEMO_PROMPT
        st.session_state["console_response"] = DEMO_RESPONSE
        st.session_state["console_source"] = "demo"

    # Toggle demo-mode + quick-chips
    top_l, top_r = st.columns([3, 1])
    with top_r:
        dm = st.toggle("Demo-mode", value=flags.demo_mode(), key="demo_mode_toggle",
                       help="Cache offline pre-validata: la demo non dipende dalla rete.")
        flags.set_demo_mode(dm)
    with top_l:
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.62rem;'
            'letter-spacing:0.12em;color:#666;text-transform:uppercase;margin-bottom:6px;">'
            'Scenari rapidi</div>',
            unsafe_allow_html=True,
        )
        chip_cols = st.columns(len(CHIPS))
        pending = None
        for col, chip in zip(chip_cols, CHIPS):
            if col.button(chip, key=f"chip_{chip}", use_container_width=True):
                pending = chip

    # Chat input nativo (send rosso dal theme primaryColor)
    user_msg = st.chat_input("Descrivi il problema in pista… (es. «L'auto scivola dietro in accelerazione»)")
    if user_msg:
        pending = user_msg

    if pending:
        resp, src = get_console_analysis(pending)
        st.session_state["console_question"] = pending
        st.session_state["console_response"] = resp
        st.session_state["console_source"] = src
        st.rerun()

    # Domanda corrente
    q = st.session_state.get("console_question", DEMO_PROMPT)
    src = st.session_state.get("console_source", "demo")
    src_label = {"demo": "demo-mode", "cache": "cache", "api": "live", "fallback": "fallback offline"}.get(src, src)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin:12px 0 14px;">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.6rem;color:#666;'
        f'text-transform:uppercase;letter-spacing:0.12em;">Analisi richiesta</span>'
        f'<span style="font-family:\'Inter\',sans-serif;font-size:0.82rem;color:#FFFFFF;'
        f'background:rgba(232,0,45,0.10);border:1px solid rgba(232,0,45,0.25);border-radius:6px;'
        f'padding:3px 10px;">{html.escape(q)}</span>'
        f'<span style="margin-left:auto;font-family:\'JetBrains Mono\',monospace;font-size:0.56rem;'
        f'color:#00C853;text-transform:uppercase;letter-spacing:0.1em;">● {src_label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    _render_cards(st.session_state["console_response"])
