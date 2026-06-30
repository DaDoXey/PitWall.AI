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

## Fase 4 — Dashboard

**Data:** 30/06/2026 · branch `restyle-ui`

**Modifiche:** `ui/dashboard.py` + 2 helper mini-grafico in `ui/components.py`
(`sparkline_svg`, `window_bar_svg`).
- **Hero metrics** (components.html): "Ultima sessione · Monza · Tempio della
  Velocità", "BMW M4 GT3 · 2024", "Giri completati 8 · Best 1:47.812", "Consumo
  medio 3.2 L/giro · 25.6 L totali".
- **3 card modulari** con mini-grafici: Temperatura gomme (sparkline RR + "105°C
  sopra finestra"), Pressione media (window-bar + "26.8 psi · retrotreno sotto
  finestra"), Consumo (sparkline + "stabile · 25.6 L totali"). Ogni card ha un
  bottone **"Apri Telemetria"** (st.button) che naviga.
- **Card "Chiedi a Gigi"** (avatar + testo) con bottone **"Apri Engineer Console"**.

**Coerenza (checklist):** cross-check automatico PASS — temp RR 105°C identica su
Dashboard/Telemetria/Heatmap; heatmap 88/90/95/105 = max delle serie; pressione
media 26.8 = media dei 4 gauge; finestra 27.0–27.8 / limite 95 uniformi; la cache
console cita gli stessi numeri.

**Nota dati:** la card Pressione media mostra **26.8 psi** (media dei 4 valori a
caldo) anziché il 26.6 del brief, per coerenza con i gauge della Telemetria —
vedi `SPEC_ERRATA.md` ERR-04.

**Verifica:** import di tutti i moduli `ui/*` OK; builder HTML costruiti coi
numeri attesi; `py_compile` OK; bottoni "Apri" mappati su `nav.go_to`.

**Decisione:** mantenuto. Commit "fase 4: dashboard". STOP CRITICO — core
Login → Dashboard → Telemetria → Gigi DEMO-READY.

## Fase 5 — Setup (5 tab ACC funzionali)

**Data:** 30/06/2026 · branch `restyle-ui` + `main`

**Scelta committente:** Setup **funzionale** (non solo demo) — ricollego la logica
reale; ritmo **una fase alla volta con verifica online**.

**Modifiche:** `ui/setup_view.py` da placeholder a pagina funzionale:
- 5 tab orizzontali (`st.tabs`, stile cockpit da `app.css`): Tyres / Electronics /
  Mechanical Grip / Dampers / Aero, **stessa struttura del menu setup ACC**.
- Slider alimentati da `modules.setup_params.get_params_for_car(car, track)`
  (modulo dati protetto: **chiamato, non riscritto**) → range/step/default/unit e
  override per vettura+circuito vengono dalla fonte di verità.
- Renderer presentazionale `_slider()`: riga nome (mono) + valore (accent) +
  slider nativo con label nascosta; clamp del valore salvato se fuori range
  (pattern del legacy). Tip ACC come `help`. Raggruppamenti fedeli al legacy
  (tyres 2×2 pressioni/camber/toe + caster; mechanical a gruppi; dampers 4 corner
  ×4 col; aero con readout rake informativo).
- Valori raccolti in `st.session_state["setup_current"]` per le fasi successive.
- Auto/pista da `session_state` (`setup_car`/`setup_track`) con **fallback ai
  default demo** (BMW M4 GT3 · Monza): i selettori e l'upload restano per la
  Fase 7 (dietro feature-flag) e si innesteranno senza riscrivere qui.

**File protetti:** nessuno toccato. `agent.py`, parser, prompt, logica fuel/gauge
invariati; `setup_params.py` solo chiamato.

**Verifica:** `py_compile` OK; import del modulo pagina + API OK; tutte le 5
sezioni hanno un renderer; **tutti i `param_key` referenziati esistono** e nessun
parametro del modulo resta non renderizzato (test di coerenza chiavi PASS).

**Decisione:** mantenuto. Commit "fase 5: setup". Attesa verifica online prima
della Fase 6 (restyle Login).

## Fase 6 — Restyle Login

**Data:** 30/06/2026 · branch `restyle-ui` + `main`

**Contesto:** il login carica solo font+token (`inject_design_system(include_app_css=False)`),
quindi i widget (bottoni/input) restavano con lo stile Streamlit di default —
incoerenti col cockpit. Hero/ruler/badge erano già allineati.

**Modifiche:** solo `styles/login.css` (nessuna riga di logica auth toccata):
- **Bottoni** (Demo Pilot / Custom User / submit form) in stile cockpit: mono
  uppercase, radius, primary = accento rosso (testo bianco), secondary =
  superficie scura con bordo, hover rosso. Selettori robusti che coprono sia
  l'attributo `kind` sia i `data-testid` (`stBaseButton-*`, `primaryFormSubmit`)
  delle versioni recenti. `button p { color: inherit }` → label sempre visibile.
- **Input testo** (form Custom User): superficie scura, mono, focus rosso; label
  mono uppercase muted.

**Garanzie:** `login.py` invariato → flusso Demo Pilot / Custom User / switch_page
identico (priorità #1 "login sempre funzionante" salva). Nessun file protetto
toccato. `login.css` caricato dopo i token → regole vincenti.

**Decisione:** mantenuto. Commit "fase 6: restyle login". Attesa verifica online
prima della Fase 7 (selettori auto/pista + upload dietro feature-flag).

## Fase 7 — Selettori auto/pista + upload dietro feature-flag

**Data:** 30/06/2026 · branch `restyle-ui` + `main`

**Obiettivo:** re-introdurre i controlli funzionali (selettori vettura/circuito,
upload CSV/screenshot) **dietro feature-flag**, OFF in demo (priorità #1: demo
pulita e che non si rompe).

**Modifiche:**
- `ui/flags.py`: nuovo flag `inputs_enabled()` / `set_inputs_enabled()` — default
  OFF, override via env `PITWALL_SHOW_INPUTS` o toggle a runtime.
- `ui/catalog.py` (NUOVO): `CAR_LIST` (15), `TRACK_LIST` (15), `CONDITIONS` —
  liste statiche importabili **senza importare `app_legacy.py`** (che all'import
  eseguirebbe l'intera app Streamlit).
- `ui/setup_view.py`: toggle "Input sessione" in cima (default = flag). Quando ON:
  - selettori **Auto / Tracciato / Condizioni** (scrivono `setup_car`/`setup_track`
    → i 5 tab si ricostruiscono coi range della vettura via `get_params_for_car`),
    + slider Temp. Ambiente/Pista;
  - expander upload: **CSV** (parser reale `backend.parser.parse_session_csv`,
    import difensivo + gestione `CSVParseError`, salva `csv_parsed_result` e mostra
    giri/consumo) e **screenshot** (`modules.vision_parser.parse_setup_from_image`,
    richiede `ANTHROPIC_API_KEY`; "Usa negli slider" applica i parametri letti via
    `get_all_params_flat`, con clamp nei range).
  Quando OFF: car/track = default demo (BMW M4 GT3 · Monza), nessun controllo.

**File protetti:** nessuno toccato. Parser/vision/setup_params solo **chiamati**;
logica fuel/gauge invariata. Gli import dei parser sono **lazy** (dentro gli
handler) per non appesantire/rischiare l'import della pagina.

**Verifica:** `py_compile` OK (setup_view/flags/catalog); import dell'intera catena
OK; flag default OFF; catalogo 15/15; 49 parametri flat; chiavi vision presenti nel
flat; tutte le helper presenti.

**Decisione:** mantenuto. Commit "fase 7: selettori + upload dietro flag". Restyle
fasi 1–7 completo. TODO post-fasi: rivedere stile tasti login (vedi richiesta utente).

---

# PUNCH-LIST v2 — Fix Gigi online + correzioni (branch `main`)

**Data:** 30/06/2026 · branch `main` (restyle già merged, `origin/main == origin/restyle-ui`)

## Prompt ricevuti (catalogo messaggi)
1. Standby ("aspetta che ti dia delle istruzioni").
2. Incollato il **Prompt v2** ("Gigi non risponde + Correzioni Restyle", FASE 0–7).
3. "procedi seguendo le fasi e con tutto quello che è necessario".

## Ricognizione (FASE 0) — discrepanze prompt v2 ↔ repo reale
- Branch reale `main` (non `restyle-ui`); file reali `backend/parser/csv_parser.py`,
  `prompts/system_prompt_v4.txt`, font in `assets/fonts/` (non `static/`). `plotly` OK.
- **FASE 1 (Gigi non risponde): già risolta in `main`.** Input = `st.chat_input`
  (mai `disabled`), demo-mode ON di default → cache 4 sezioni sempre servita,
  fallback su errore API. Sintomo presente solo sul **deploy stale** → vedi INC-003.

## Interventi eseguiti (file presentazione/dati, ZERO file protetti)
- **2.1** Tab Setup in italiano (`modules/setup_params.py`): Gomme / Elettronica /
  Meccanica / Ammortizzatori / Aerodinamica (solo label visibili; chiavi invariate).
- **2.2** Precarico differenziale → **20–300 Nm step 10** (`setup_params.py`).
  ⚠️ Divergenza col prompt protetto (20–200) **documentata in SPEC_ERRATA ERR-05**;
  il file protetto NON è stato toccato. (Il brief diceva "prompt a 20–100": verificato,
  è 20–200.)
- **2.3** Screenshot upload → **stub "Prossimamente"** dietro flag `FEATURE_SCREENSHOT`
  (OFF di default) in `ui/flags.py` + `ui/setup_view._screenshot_upload` (uploader
  `disabled=True`, funzione reale gated non cancellata).
- **3.1 / ERR-01/02/04** Pressioni a caldo riallineate alla finestra ACC reale/protetta
  **28.5–30.0 psi** (`ui/demo_data.py`): HOT `{fl 29.0, fr 29.2, rl 28.2, rr 28.0}`,
  media **28.6**. Ora a caldo > a freddo (prima 26.2/26.0 a caldo era < a freddo:
  impossibile). Caso didattico "retrotreno sotto finestra → sovrasterzo" preservato.
  Risincronizzati: `ui/telemetry.py` (gauge axis [27.0, 30.5], testi), `ui/dashboard.py`
  (window-bar + nota), `ui/console.DEMO_RESPONSE` (numeri di Gigi).
- **3.2** Tooltip giro 8 Post.DX = 105 (no 103 vagante): già coerente da `TYRE_TEMP_SERIES`.
- **4.1** Toggle "Input sessione" OFF di default: già a posto.
- **4.2** 3 bottoni Dashboard differenziati (`ui/dashboard.py`): Temp → Telemetria ·
  Pressione → **Regola Setup** · Consumo → **Strategia carburante** (Engineer Console).
  Consumo non punta più a Telemetria.
- **5** Login: aggiunta tagline **"Il tuo ingegnere di pista, sempre al muretto"**
  (`pages/login.py`); SVG auto animata + ruler già presenti.
- **6.1** Label upload CSV → "Carica CSV sessione" (`ui/setup_view.py`).
- **6.2** Slider Setup: valore **bianco**, **1 decimale** (2 solo per toe, step 0.01);
  **rosso solo sui parametri suggeriti da Gigi** (`ui/demo_data.SUGGESTED_PARAMS` =
  {tire_press_rl, tire_press_rr, preload}).
- **6.3** Slider Temp: valore sul cursore già nativo (st.slider).

## Verifica
`py_compile` OK su tutti i file editati; check dati: HOT > COLD per ogni gomma,
anteriori in finestra / posteriori sotto, media 28.6, tab IT, preload 20–300 step 10,
nessun override BMW nel DB (il generico vale per la demo). File protetti invariati.

## Azione fuori-codice
- **Ri-deploy** `pitwall-ai-dado.streamlit.app` per allinearlo a `main` (chiude INC-003).

**Stato:** punch-list v2 completata lato codice. In attesa di "ok push" per commit
su `main` (regola git: nessun commit/push senza conferma esplicita).
