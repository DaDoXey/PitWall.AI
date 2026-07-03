# PitWall.AI

**Virtual Race Engineer** per Assetto Corsa Competizione (GT3). Carichi i dati di una
sessione, descrivi un problema di guida o di setup, e **Gigi** — l'ingegnere virtuale —
risponde con un'analisi tecnica strutturata in 4 sezioni (Diagnosi · Causa Meccanica ·
Correzione Setup · Note), vincolata ai range reali di ACC.

Stack: **Python + Streamlit**, LLM **Claude** (Anthropic). Deploy su Streamlit Community
Cloud: <https://pitwall-ai-dado.streamlit.app>.

## Architettura

L'app è una **shell + router** (`app.py`) che, dopo il gate di autenticazione, instrada
le quattro pagine via `st.session_state`:

```
app.py                 # entry point: auth gate + design system + router
ui/                    # package di presentazione (restyle UI/UX)
  router.py            #   dispatch pagine (Dashboard · Engineer Console · Telemetria · Setup)
  sidebar.py / nav.py  #   navigazione
  dashboard.py         #   hero + card metriche (sorgente: demo_data)
  telemetry.py         #   line chart temp (toggle °C/°F, raw/smoothed) + 4 gauge + heatmap;
                       #   tabella giro-per-giro, proiezione giri, feed cross-check (Plotly/SVG)
  console.py           #   Engineer Console "Gigi": analisi 4 card + chat + demo-mode
  setup_view.py        #   5 tab setup ACC (slider funzionali)
  demo_data.py         #   SORGENTE DATI DEMO UNICA (coerenza tra le schermate)
  flags.py             #   feature-flag (demo-mode, input sessione, screenshot)
  components.py        #   builder SVG/HTML inline + token colore
  catalog.py           #   liste auto/piste/condizioni
pages/login.py         # schermata di login (SQLite + OAuth Google predisposto)
agent.py               # client LLM Claude + system prompt v4 (file protetto)
modules/
  setup_params.py      #   range/default/unit dei parametri setup ACC (fonte di verità)
  vision_parser.py     #   lettura setup da screenshot (dietro feature-flag)
backend/
  parser/csv_parser.py #   parsing + validazione CSV di sessione (file protetto)
  database/manager.py  #   storico sessioni (SQLite)
  prompts/             #   prompt di sistema
prompts/               # system_prompt_v4.txt (protetto) + chat_system_prompt.txt
assets/                # design system: font self-hosted (woff2 base64) + CSS + SVG
styles/login.css       # stile cockpit della schermata di login
app_legacy.py          # monolite precedente, preservato VERBATIM (logica fuel/gauge)
```

### Design system
Tema dark "cockpit": palette accento `#E8002D`, font **Orbitron / Inter / JetBrains Mono**
self-hosted (woff2 base64, nessun fetch a Google Fonts). I componenti custom usano
`st.components.v1.html()` con stili **inline** e font base64 (affidabilità su Cloud);
nessun selettore interno di Streamlit, nessun wildcard.

### Demo-mode
La Engineer Console serve di default una **risposta-cache pre-validata** a 4 sezioni
(`ui/flags.demo_mode()` ON): la demo non dipende dalla rete e ricade sulla cache anche se
la chiamata LLM fallisce. Tutti i numeri della demo provengono da `ui/demo_data.py`
(sorgente unica → coerenza Dashboard ↔ Telemetria ↔ Heatmap).

## Avvio rapido

1. Crea un ambiente virtuale Python e attivalo.
2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
3. Copia `.env.example` in `.env` e inserisci la tua `ANTHROPIC_API_KEY`
   (in locale via `.env`; su Streamlit Cloud via *Secrets*).
4. Avvia l'app:
   ```bash
   streamlit run app.py
   ```

Per la modalità demo non è necessaria una chiave API: la console serve la risposta-cache.

## Variabili d'ambiente principali

| Variabile | Default | Effetto |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Chiave Claude (analisi "live" e lettura screenshot). |
| `LLM_MODEL` | `claude-haiku-4-5` | Modello usato da `agent.py`. |
| `PITWALL_DEMO_MODE` | `1` (ON) | Console serve sempre la cache (demo blindata). |
| `PITWALL_SHOW_INPUTS` | `0` (OFF) | Mostra selettori auto/pista + upload nel Setup. |
| `FEATURE_SCREENSHOT` | `0` (OFF) | Abilita la lettura setup da screenshot (altrimenti stub). |

## File protetti

`agent.py`, `backend/parser/csv_parser.py`, `prompts/system_prompt_v4.txt`,
`backend/prompts/system_prompt.txt` e la logica gauge/fuel **non vanno riscritti**:
sono la fonte di verità per i range ACC e i calcoli. Le viste UI li **chiamano**, non li
modificano. Le correzioni ai soli dati demo di presentazione sono tracciate in
`SPEC_ERRATA.md`; gli incidenti in `INCIDENTS.md`; lo storico di lavoro in `PROMPT_LOG.md`.
