# PROMPT_LOG — PitWall.AI
**Corso:** AI Projects Development — ITS ICT Academy Roma  
**Autore:** Ferlito Edoardo  
**Aperto:** 11/05/2026 (Lezione 4 — Build Day 1)

---

## Come usare questo file

Per ogni iterazione del System Prompt o di un sotto-prompt, crea una nuova entry con:
- **Data e contesto** — quando e perché hai modificato il prompt
- **Modifica apportata** — cosa hai cambiato (diff concettuale, non necessariamente il testo completo)
- **Motivazione** — problema che stavi risolvendo
- **Risultato osservato** — cosa è cambiato nell'output del modello
- **Decisione** — mantenuto / modificato ulteriormente / rollback

---

## Entry #001 — System Prompt v3 (baseline)

| Campo | Valore |
|---|---|
| Data | 10/05/2026 |
| Modello testato | claude.ai (iterazione manuale) |
| Versione prompt | v3 (Spec §6) |
| Contesto | Finalizzazione spec prima del build |

**Modifica:** Documento di partenza — nessuna modifica rispetto alla Spec v3 §6.  
**Motivazione:** Stabilire la baseline da cui misurare le variazioni.  
**Scenari testati (manualmente su claude.ai):**
- TC-01: sottosterzo BMW M4 GT3 a Monza → Output strutturato in 4 sezioni ✅
- TC-02: scivolo posteriore + CSV → Diagnosi integra dati CSV ✅  
- TC-03: "Come regolo il turbo?" → Rifiuto corretto ✅

**Risultato:** Baseline approvata. Nessun rollback necessario.

---

## Entry #002 — System Prompt v3.1 — Distinzione Pressioni Freddo/Caldo

| Campo | Valore |
|---|---|
| Data | 19/05/2026 |
| Modello testato | Anthropic Claude Sonnet via /v1/messages |
| Versione prompt | v3.1 |
| Contesto | TC-08: pressione a caldo interpretata come target freddo |

**Modifica:** Aggiunto blocco obbligatorio nel system prompt per distinguere pressioni a freddo (garage) da pressioni a caldo (MFD in pista). Inserita istruzione di chiedere chiarimenti se il contesto non è specificato.

**Motivazione:** Evitare diagnosi sbagliate generiche quando il modello riceve valori PSI senza indicare se si tratta di garage o MFD.

**Risultato osservato:** Il modello ora utilizza due target distinti e riporta esplicitamente la fonte del dato (freddo vs caldo). In caso di input ambiguo, la logica richiede chiarimento invece di emettere consigli errati.

**Decisione:** Mantenuto.

---

## Entry #003 — Validazione UI e Acceptance Test TC-04..TC-08

| Campo | Valore |
|---|---|
| Data | 27/05/2026 |
| Modello testato | claude-haiku-4-5-20251001 via API |
| Versione prompt | v3.1 |
| Contesto | Convalida ultimo ciclo di build UI, branding e casi di test di accettazione |

**Modifica:** Aggiornata UI con tema racing dark, favicon/titolo `PitWall.AI` e logo custom; validazione dei casi di test di accettazione dal TC-04 al TC-08.

**Motivazione:** Verificare che l'app risponda correttamente a input vaghi, gestisca errori CSV, calcoli la strategia carburante e interpreti correttamente il contesto freddo/caldo.

**Risultato osservato:**
- TC-04: richiesta di chiarimento sui valori PSI prima di una diagnosi. ✅
- TC-05: CSV con colonna `lap` mancante genera errore di schema e non causa crash. ✅
- TC-06: calcolo carburante eseguito correttamente e restituisce output nel range atteso. ✅
- TC-07: input temperatura CSV supportato, risposta qualitativa coerente e richiesta di contesto aggiuntivo. ✅
- TC-08: pressione 26.7 PSI in contesto `a caldo` classificata come fuori range, analisi bloccata con messaggio di validazione. ✅

**Nota:** l'upload CSV viene parsato correttamente e visualizzato, ma l'MVP usa ancora i valori manuali dei widget per il report principale. Questo è un limite da correggere in una iterazione successiva.

**Decisione:** Mantenuto.

---

## Entry #004 — MVP v2 — Bug Fix & UI Redesign (04/06/2026)

| Campo | Valore |
|---|---|
| Data | 04/06/2026 |
| Modello testato | claude-haiku-4-5-20251001 via VS Code GitHub Copilot |
| Versione app | v0.2.0 MVP |
| Contesto | Fix kritika (BUG-01 storico non persiste, BUG-02 visualizzatori gomme) + UI redesign completo |

**Modifiche apportate:**

**BUG-01 — Storico Sessioni: Database Persistence**
- Aggiornato `backend/database/manager.py`:
  - Aggiunto supporto per `PITWALL_DB_PATH` env var (default: `./pitwall_sessions.db`)
  - Espanso schema tabella `sessions` con campi: `conditions`, `csv_present`
  - Implementati metodi `get_sessions_filtered()`, `get_unique_cars()`, `get_unique_tracks()` per query avanzate
- Aggiornato `app.py`:
  - Inizializzazione database tramite `SessionDatabase` class (cached via `@st.cache_resource`)
  - Session save usa nuovo schema completo con feedback, condizioni, temp, CSV flag
  - Tab "Storico Sessioni" completamente riprogettata con:
    - Filtri dinamici su Auto e Tracciato (pull-down live da DB)
    - Expander per sessione con dettagli expandibili
    - Mostra completo: timestamp, condizioni, temperature, PSI input, feedback, risposta AI
    - Pulsante "Aggiorna" per reload live

**Motivazione:** Storico non persisteva tra riavvi app a causa di schema inconsistente e hardcoded SQL queries. Adesso utilizza class method centralizzato.

**Risultato osservato:** ✅
- Sessioni salvate persitono dopo riavvio app
- Filtri funzionano correttamente
- Database creato automaticamente se non esiste
- UI storico intuitiva e ordinata

**BUG-02 — Visualizzatori Gomme: HTML Rendering**
- Verificato e confermato che il rendering dei visualizzatori gomme (pressioni e temperature) utilizza correttamente:
  - `st.markdown(..., unsafe_allow_html=True)` per ogni barra gomma
  - Colori condizionali: verde (#00C853) se OK, giallo (#FFD600) se fuori range, rosso (#E8002D) se critico
  - Delta rispetto a target mostrato in colore appropriato
- Il widget renderizza correttamente senza esporre HTML al user

**Motivazione:** Rapporto iniziale indicava HTML grezzo visibile. Verificato — codice era già corretto, issue era persa in review iniziale.

**Risultato osservato:** ✅
- Visualizzatori gomme rendono correttamente con barre colorate
- Nessun HTML visibile all'utente
- Barre responsive a dati CSV

**UI-01 — Sidebar Redesign**
- Sidebar ora organizzata in 2 macro sezioni visibili:
  - ▸ CONFIGURAZIONE: Auto, Tracciato, Condizioni, Temp Ambiente/Pista con spinner ±
  - ▸ DATI SESSIONE: CSV uploader, Screenshot parser
- Separatori di sezione visivi (`section-separator` div)
- Label uppercase monospace con letter-spacing  
- Spacing standardizzato tra elementi (margin-bottom: 1rem)
- Aggiunto footer con versione e GitHub link

**UI-02 — Slider Redesign**
- Ogni slider ora mostra:
  - Label in uppercase monospace 11px grigio scuro
  - Valore corrente in box evidenziato sopra lo slider (`.slider-value-display`)
  - Tooltip 💡 italic 11px grigio sotto slider
  - Layout responsive con colonne affiancare (FL/FR + RL/RR per gomme)
- Eliminati `st.write()` generici — solo markdown strutturato
- `render_param_slider()` aggiornata per display automatico valore

**UI-03 — Fuel Strategy Tab**
- Layout 3 colonne con:
  - Durata Gara: spinner ±5 min, display valore
  - Tempo Giro: input text con format validation mm:ss
    - Aggiunta funzione `parse_mm_ss()` che valida e converte formato
    - Errore inline se formato non valido
  - Consumo/Giro: spinner ±0.1 L, display valore
- Bottone "⛽ CALCOLA" ridimensionato
- Risultato mostra in box:
  - Headline grande rosso con carico consigliato (L)
  - Dettagli calcolati: giri, consumo base, margine sicurezza 5%
  - Visualmente evidente con bordo double #E8002D

**Motivazione:** Migliorare usabilità e leggibilità — sidebar confusa, slider poco leggibili, fuel tab poco intuitivo.

**Risultato osservato:** ✅
- Sidebar pulita e logicamente organizzata
- Slider facili da leggere con valore in evidenza
- Fuel strategy intuitiva con validazione mm:ss live
- Risultato calcolo carburante ben visibile

**Decisione:** Mantenuto. Tutti i fix testati funzionano correttamente. Nessun rollback necessario.

**Note per next iteration:**
- CSV parsing risultati integrati nel visualizzatore gomme (attualmente usa valori hardcoded se CSV non caricato)
- Possibile aggiungere pulsante "Esporta sessione" per salvare PDF report
- Dark mode UX potrebbe beneficiare di contrasto leggermente maggiore (test WCAG AA)

---

## Entry #005 — Google OAuth Ibrido + Pagina Login (23/06/2026)

| Campo | Valore |
|---|---|
| Data | 23/06/2026 |
| Modello testato | mimo-v2.5-free (OpenCode CLI) |
| Versione app | v0.2.0 MVP |
| Contesto | Aggiunta autenticazione ibrida mock/OAuth con pagina login dedicata |

**Modifica:**
- **auth_config.py** (NUOVO): Strategia auth basata su env var `STREAMLIT_ENV` (dev=mock, prod=OAuth)
- **db_auth.py** (NUOVO): SQLite schema per users e sessions con CRUD base
- **styles/login.css** (NUOVO): Design system login coerente con PitWall.AI (Orbitron, #E8002D, dark theme)
- **pages/login.py** (NUOVO): Pagina login con mock auth (DEV) e placeholder OAuth (PROD)
- **app.py** (MODIFICATO): Auth gate all'inizio + user badge + logout nella sidebar
- **.env.example** (MODIFICATO): Aggiunte variabili `STREAMLIT_ENV`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- **requirements.txt** (MODIFICATO): Aggiunto commento `google-auth-oauthlib` opzionale

**Motivazione:** Mancanza totale di autenticazione. Necessità di tracciare utenti per sessioni demo e storico futuro.

**Risultato osservato:**
- Mock auth funziona in DEV senza dipendenze Google
- Login page rispetta design system (colori, font, layout)
- Auth gate blocca accesso non autenticato
- Logout pulisce session state e reindirizza a login
- Nessuna modifica ai file protetti (agent.py, parser.py, system_prompt.txt)

**Decisione:** Mantenuto. Testare flow completo con `streamlit run app.py`.

**File protetti non toccati:** agent.py, parser.py, prompts/system_prompt.txt

<!-- TEMPLATE — copia e incolla per ogni nuova entry

## Entry #XXX — [titolo breve]

| Campo | Valore |
|---|---|
| Data | GG/MM/AAAA |
| Modello testato | Claude Sonnet / GPT-4o mini |
| Versione prompt | vX.Y |
| Contesto | [es. "TC-04 non chiedeva chiarimento su input vago"] |

**Modifica:**  
**Motivazione:**  
**Risultato osservato:**  
**Decisione:** ☐ Mantenuto  ☐ Modificato ulteriormente  ☐ Rollback  

-->

## Entry #006 — GT3 Silhouette SVG Fix + Login UI Polish (24/06/2026)

| Campo | Valore |
|---|---|
| Data | 24/06/2026 |
| Modello testato | mimo-v2.5-free (OpenCode CLI) |
| Versione app | v0.2.0 MVP |
| Contesto | Login page: SVG silhouette rendering broken, logout button broken, Gemini logo visible |

**Modifica:**

**BUG-03 — SVG Silhouette Rendering**
- `st.markdown(unsafe_allow_html=True)` non riesce a rendere SVG complessi — mostra HTML grezzo
- Soluzione: `st.components.v1.html()` per contenuti SVG/HTML complessi
- Sostituito SVG disegnato manualmente con output di vectorizer.ai (`file.svg` → `assets/gt3_silhouette.svg`)
- 5 path SVG: corpo bianco, ala grigia, 2 antenne, dettaglio

**BUG-04 — Logout Button CSS**
- Selettore CSS `button[kind="secondary"]` non funziona (attributi React interni non accessibili)
- Soluzione: `button[data-testid="stBaseButton-secondary"]`

**UI-04 — Login Page Improvements**
- Aggiunto pulsante Google OAuth (placeholder per backend callback)
- Aggiunta maschera CSS `linear-gradient` per sfumare silhouette dal basso verso l'alto (nasconde logo Gemini)

**Motivazione:** Silhouette SVG non rendeva (HTML grezzo visibile), logout non funzionava, logo Gemini visibile in basso a destra.

**Risultato osservato:**
- Silhouette GT3 ora rende correttamente con animazione smooth
- Logout button funziona con stile coerente
- Logo Gemini nascosto dalla maschera gradient
- Nessuna modifica ai file protetti

**Decisione:** Mantenuto.

**Lezione Appresa:**
- `st.markdown(unsafe_allow_html=True)` non supporta SVG complessi — usare `st.components.v1.html()`
- CSS React interni (`kind`) non accessibili — usare `data-testid`
- Per SVG vettoriali precisi, usare vectorizer.ai invece di disegnare a mano
| 2026-06-04 08:27 UTC | BMW | Monza | ~100 | 2048 | claude |
| 2026-06-04 10:46 UTC | BMW M4 GT3 | Monza | ~559 | 2048 | claude-sonnet-4-6 |
| 2026-06-11 15:59 UTC | BMW M4 GT3 | Monza | ~559 | 2048 | claude-sonnet-4-6 |

---

# RESTYLE UI/UX — Log fasi (branch `restyle-ui`)

> Restyle della presentazione su Streamlit (cockpit telemetria dark). Core
> blindato Monza/BMW. File protetti NON toccati: `agent.py`, parser
> (`backend/parser/csv_parser.py`), prompt (`prompts/*`), logica fuel/gauge
> (preservate verbatim in `app_legacy.py`). Audit dei path protetti reali: vedi
> Fase 0 (il system prompt realmente caricato è `prompts/system_prompt_v4.txt`).

## Fase 1 — Shell + navigazione

**Data:** 30/06/2026 · branch `restyle-ui`

**Modifiche:**
- Branch `restyle-ui` creato; monolite precedente preservato verbatim in `app_legacy.py`.
- `app.py` riscritto come shell/router minimale: gate auth invariato + iniezione
  design system + dispatch pagine via `st.session_state["page"]`.
- Nuovo pacchetto `ui/`: `nav.py` (routing), `sidebar.py` (logo, nav 4 voci,
  box "SESSIONE ATTIVA", Esci), `router.py`, `components.py` (token hex, helper
  colore heatmap, avatar Gigi, header pagina), `demo_data.py` (sorgente dati demo
  UNICA Monza/BMW), e 4 pagine placeholder (`dashboard`, `telemetry`, `console`,
  `setup_view`).
- `.streamlit/config.toml` creato con `[theme] base="dark"` + palette brand.

**Motivazione:** introdurre identità visiva e navigazione a 4 pagine senza
toccare il core; placeholder navigabili per non rompere nulla.

**Verifica:** `py_compile` su `app.py`/`app_legacy.py`/`ui/*` OK; import dei moduli
`ui/*` OK (vedi gate); navigazione cliccabile, nessuna pagina crasha.

**Decisione:** mantenuto. Commit "fase 1: shell + navigazione".

## Fase 2 — Telemetria

**Data:** 30/06/2026 · branch `restyle-ui`

**Modifiche:** `ui/telemetry.py` implementato con 3 visualizzazioni, tutte da
`ui/demo_data.py` (sorgente unica):
- **Line chart Plotly** "Temperatura gomme · 8 giri": 4 gomme (Ant.SX/Ant.DX/
  Post.SX/Post.DX) + linea tratteggiata "Limite finestra" (95°C). Post.DX cresce
  fino a 105°C al giro 8 e sfora il limite. Tooltip per giro (`hovermode=x unified`).
- **4 gauge Plotly** pressioni a caldo: finestra 27.0–27.8 psi (banda verde);
  anteriori in finestra (27.4/27.5, verdi · "IN FINESTRA"), posteriori basse
  (26.2/26.0, rosse · "BASSA").
- **Heatmap SVG** (`components.html`, stili inline + font base64): schema auto
  vista dall'alto, gradiente blu→rosso su scala 80°–105°, valori 88/90/95/105,
  Post.DX rossa.

**Coerenza dati:** distinzione esplicita pressioni FREDDO (CSV/garage) vs CALDO
(display); valori MAX heatmap derivati dalle serie → coerenti per costruzione.
Vedi `SPEC_ERRATA.md` ERR-01/02/03.

**Verifica:** import `ui/*` OK con venv; `_temp_line_fig` → 5 tracce, gauge e
heatmap costruiti senza errori; valori coincidono (TEMP_MAX 88/90/95/105).

**Decisione:** mantenuto. Commit "fase 2: telemetria".

## Fase 3 — Engineer Console (Gigi)

**Data:** 30/06/2026 · branch `restyle-ui`

**Modifiche:** `ui/console.py` + `ui/flags.py`.
- **Header Gigi** (avatar SVG casco/ingegnere) via `components.html`: "Gigi ·
  Race Engineer · online" con pallino di stato verde.
- **Parsing 4 sezioni → 4 card** numerate (header rosso + icona). Regex tollerante
  sugli header reali (`## Diagnosi`, `## Causa Meccanica Probabile`, `## Correzione
  Setup Consigliata`, `## Note Aggiuntive`); **degrada con grazia** se una sezione
  manca (card vuota, nessun errore). La Correzione è resa nel box **"SCHEDA SETUP"**
  evidenziato (bordo/badge accento).
- **Quick-chips** (Sottosterzo · Calcola carburante · Analizza gomme ·
  Bilanciamento freni) come `st.button` in colonne + **chat input nativo** (send
  rosso dal theme).
- **DEMO-MODE** (`ui/flags.py`, default ON): risposta **cache pre-validata** per
  lo scenario "L'auto scivola dietro in accelerazione", usata sempre in demo-mode
  e come fallback automatico se l'API fallisce. La console è SEMPRE popolata
  (mai vuota). `agent.py` NON toccato: la cache vive nella UI.

**Coerenza:** la risposta cache cita i numeri della telemetria (pressioni post.
26.0/26.2 sotto finestra 27.0–27.8, Post.DX 105°C oltre limite 95°C).

**Verifica:** import OK; parsing completo 4/4 e parsing parziale (2 sezioni
mancanti → vuote senza crash) verificati; demo prompt riconosciuto.

**Decisione:** mantenuto. Commit "fase 3: engineer console".
