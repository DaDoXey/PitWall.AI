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

**Stato:** punch-list v2 completata e **committata** (`dbcfb92`, poi pushata su
`origin/main`). Regola git rispettata: commit/push eseguiti dopo conferma utente.

### Addendum — fix post-verifica online (commit `dbcfb92` deployato)

Verifica visiva utente sul deploy → due problemi reali (vedi INC-004):
- **Engineer Console percepita statica / "non risponde":** in demo-mode tornava
  sempre la stessa analisi e l'input (`st.chat_input`) era ancorato in fondo,
  poco visibile. **Fix:** 5 risposte-cache per scenario (sottosterzo / sovrasterzo /
  carburante / gomme / freni) con router `_pick_demo_response()`; input sostituito
  da **campo + bottone «⚙ ANALIZZA»** in linea, con guardia anti ri-trigger.
- **Telemetria disallineata:** line chart `height=320 → 410` (= heatmap).

File toccati: `ui/console.py`, `ui/telemetry.py`, `INCIDENTS.md` (INC-004), questo log.
Verifica: `py_compile` OK; routing testato (ogni chip → scenario giusto); 5 risposte
con 4 sezioni piene. **Committato** come `e9115cb` (HEAD attuale = `origin/main`) e
deployato su Streamlit Cloud (chiude INC-003/INC-004).

> Nota manutenzione (02/07/2026): ref Git locale corrotta (`.git/refs/heads/main` +
> `refs/remotes/origin/main` azzerate da crash filesystem) — ripristinata a `e9115cb`
> senza perdita dati; working tree identico al commit, locale allineato a `origin/main`.

---

## Entry #007 — Manutenzione Git + Restyle Login "Marchio soft" (02/07/2026)

| Campo | Valore |
|---|---|
| Data | 02/07/2026 |
| Modello | claude-opus-4-8 (Claude Code) |
| Versione app | v0.2.0 MVP (branch `main`) |
| Contesto | Ripresa lavori: allineamento status, recupero Git, prossima task = login minimal |

### Catalogo messaggi di questa iterazione
1. **Setup/metodo (status):** leggere per intero prompt log + breakdown + progetto,
   verificare discordanze, controllare allineamento Git con `origin`, elaborare il
   prossimo passo, esporre il piano e attendere approvazione; non inventare/costruire
   senza ok. Subtask iniziale: nessuna, attendere comando.
2. **Utente:** «Approvo passo 1+2, poi procedi col login minimal, ricordati inoltre
   che dopo ti incollerò un prompt più massiccio.»
3. **Utente (scelta guidata):** grado di minimal per la login = **«Marchio soft»**
   (rimuovere solo auto animata + badge MVP; tenere hero, ruler, sottotitolo, tagline).
4. *(Atteso)* prompt più corposo in arrivo, da lavorare successivamente.

### Interventi eseguiti
- **Passo 1 — Recupero Git:** `.git/refs/heads/main` e `refs/remotes/origin/main`
  erano azzerate (null byte). Rimosse e ricreate: `update-ref` di `main` → `e9115cb`,
  `fetch origin` per rigenerare `origin/main`, upstream reimpostato. `git status` =
  `main...origin/main` allineato, `fsck` senza ref rotte. **Nessuna perdita dati**
  (working tree già identico a `e9115cb`).
- **Passo 2 — Allineamento log:** aggiornate le note stale di punch-list v2 (→ committata
  `dbcfb92`) e addendum INC-004 (→ committato `e9115cb`, deployato); aggiunta nota di
  manutenzione Git.
- **Passo 3 — Login "Marchio soft"** (solo presentazione, **logica auth invariata**):
  - `pages/login.py`: rimosso l'intero blocco SVG **auto GT3 animata** + track line CSS
    (e l'import `streamlit.components.v1` non più usato); rimosso il **badge `● MVP V2.0`**
    dall'hero. Restano wordmark, ruler rosso, sottotitolo e tagline.
  - `styles/login.css`: rimosse le regole ora inutili `.pw-badge-status`/`.pulse`;
    `.pw-hero` top padding `8px → 40px` per compensare l'auto rimossa e dare respiro.

### File protetti
Nessuno toccato. Flusso login (Demo Pilot / Custom User / `switch_page`) **identico**
→ priorità #1 "login sempre funzionante" preservata.

### Verifica
`py_compile pages/login.py` OK; grep senza residui (`components` / `pw-badge-status` /
`ferrari-track` / `gt3_svg`).

**Decisione:** ☑ Mantenuto. In attesa del prompt più corposo per la prossima iterazione.
Commit/push su `main` solo dopo tuo «ok push» esplicito (regola git).

### Addendum — Prompt "Correzione Punch-List Restyle" + FASE 4 sulla login (02/07/2026)

**Messaggi:**
1. Utente: «il prompt te lo incollerò alla prossima richiesta; controllami prima se la
   FASE 1 è stata eseguita, fammi un report sul prompt e poi ti dirò come proseguire».
2. Utente: incollato il prompt completo "Correzione Punch-List Restyle UI" (FASI 0–6).
3. Utente: «verifica anche le altre fasi (2–6) contro il codice».
4. Utente: «tieni il login minimal di oggi ed implementa anche le linee della FASE 4;
   voglio il logo minimal ma anche come richiesto — oppure gestiscila tu e proponi».

**Verifica prompt ↔ repo (sola lettura):** l'intero prompt risulta **già implementato**
dalla punch-list v2 (30/06). Note: branch reale `main` (non `restyle-ui`); path reali
`backend/parser/csv_parser.py`, `prompts/system_prompt_v4.txt`, font in `assets/fonts/`;
precarico system_prompt reale = **20–200** (non 20–100). Voce 2.1: caldo > freddo su tutte,
ma posteriori a +2.0 (non +2.5) **per scelta didattica** (retrotreno sotto finestra, ERR-01).

**FASE 4 su login (scelte utente: traccia telemetria + SVG ingegnere minimale):**
- `pages/login.py`: reintrodotti `import components` + `from ui import components as c`;
  **avatar ingegnere** (`c.gigi_avatar_svg(48)`, riuso, opacity 0.9) reso via
  `components.html` sotto la tagline; **traccia telemetria** decorativa (polyline inline
  full-width) come `<div class="pw-telemetry-trace">` in fondo.
- `styles/login.css`: nuova classe `.pw-telemetry-trace` (fixed bottom, tenue opacity 0.18,
  mask che sfuma ai bordi). Solo classi custom: nessun selettore interno Streamlit / wildcard.
- Login minimal di oggi **mantenuto** (niente auto animata, niente badge). Logica auth invariata.

**Verifica:** `py_compile pages/login.py` OK; import `ui.components` risolto da `pages/`.
Committato e pushato come `bf91a91`.

### Addendum 2 — Icona Gigi rifatta + avatar rimosso dalla login (02/07/2026)

**Messaggio utente:** verifica a schermo → l'avatar in mezzo alla login **non** era voluto;
voleva invece che rifacessi **l'icona dell'ingegnere** usata nell'Engineer Console e dove
appare Gigi nelle schermate. (Scelte: emblema **headset**, stile **linea minimale senza tile**.)

**Interventi:**
- `pages/login.py`: **rimosso** l'avatar `components.html` in mezzo alla pagina e i relativi
  import (`components`, `from ui import components as c`). La **traccia telemetria** resta.
- `ui/components.py` → `gigi_avatar_svg`: **ridisegnata** da "casco con cuffie in tile" a
  **headset line-art** (archetto + 2 padiglioni a contorno bianchi + braccetto/capsula mic in
  accento rosso), sfondo trasparente, niente tile/anello. Si aggiorna automaticamente in
  `ui/console.py:275` e `ui/dashboard.py:120` (unici usi).

**Verifica:** `py_compile` OK (components/login); icona senza tile (nessun `#0a0a0a`/`rx=16`).
Committato/pushato come `2ab0583`.

### Addendum 3 — Icona Gigi tutta bianca + pulizia geometria (02/07/2026)

**Messaggio utente:** «già meglio ma non abbastanza pulita: fai le cuffie totalmente bianche
e vedi se ci sono altri errori».

**Interventi (`ui/components.py → gigi_avatar_svg`):**
- Microfono (braccetto + capsula) da rosso `#E8002D` → **bianco**; colore/spessore unificati
  a livello di `<svg>` (ereditati) per uniformità garantita.
- Archetto riagganciato al top dei padiglioni (`y29`) → niente micro-gap.
- Padiglioni più compatti (h `20→18`), capsula mic riempita `stroke="none"` (non più ingrossata).

**Verifica:** `py_compile` OK; nessun `#E8002D` residuo nell'icona (headset 100% bianco).

### Entry #008 — Check generale repo + igiene codice (02/07/2026)

**Messaggio utente:** «vedi se ci sta della roba da fixare facendo un check generale su tutto
(file e repo) e dimmi cosa migliorare» → poi «procedi con tutto 1→4».

**Diagnosi (repo allineato `origin/main` 0/0, tree clean, tutti i moduli attivi compilano):**
- **Bug reale:** `frontend/__init__.py` non compilava — dentro c'era incollato il contenuto di
  `.env.example` (compresa API key placeholder) con la docstring appiccicata → `SyntaxError`.
  Nessun impatto in produzione perché il package `frontend` non è mai importato.
- **Zavorra tracciata da Git:** cartella `files/` (6 copie stantie del 10/06 di agent/app/
  setup_params/system_prompt_v4/vision_parser/README), `files.zip` (blob 18 KB),
  `assets/gt3_silhouette.svg` (orfano, era l'auto della login rimossa).
- **Doc:** docstring di `gigi_avatar_svg` diceva ancora "microfono in accento rosso" (ora bianco).

**Interventi:**
1. `frontend/__init__.py` → ridotto alla sola docstring pulita.
2. `ui/components.py` → docstring `gigi_avatar_svg` allineata (icona interamente bianca).
3. `git rm` di `files/`, `files.zip`, `assets/gt3_silhouette.svg`. **Tenuti** `assets/gigi.svg`
   (usato da `app_legacy.py`) e `app_legacy.py` (monolite di riferimento, mai importato).

**Verifica:** `py_compile frontend/__init__.py ui/components.py` OK; tree coerente. Committato/pushato.

### Entry #009 — Chiusura ERR-05: precarico UI allineato a 20–200 (02/07/2026)

**Messaggio utente:** «chiudiamo ERR-05 mettendo il precarico UI a 20-200».

**Intervento:** `modules/setup_params.py` riga 206 → slider Precarico Differenziale da
`max:300` a **`max:200`** (min 20, step 10, default 60 → in range). Unico punto con 300 nel
codice; `prompts/system_prompt_v4.txt` era già a 20–200 (file protetto non toccato). Aggiornato
`SPEC_ERRATA.md` ERR-05 → **RISOLTO**.

**Verifica:** `py_compile modules/setup_params.py` OK. Committato/pushato.

### Entry #010 — Chiusura FASE 2.1: delta pressioni retro a +2.5 (02/07/2026)

**Messaggio utente:** «chiudiamo anche la FASE 2.1 mettendo le pressioni a +2.5» →
«dimmi tu quale sarebbe la migliore e poi fai tu».

**Analisi:** il delta cold→hot davanti era già +2.5; solo il retrotreno era a +2.0. Due modi
opposti di portarlo a +2.5: (A) alzare il CALDO (28.7/28.5) → il retrotreno entra in finestra e
si rompe tutta la narrativa demo (SUGGESTED_PARAMS, console Gigi, nota Dashboard, ERR-02/04);
(B) abbassare il FREDDO (25.7/25.5) tenendo il caldo invariato → nessun visual cambia, storia
preservata, più realistico. **Scelta: B** (raccomandata).

**Interventi:**
- `ui/demo_data.py`: `COLD_PRESSURES` rl 26.2→25.7, rr 26.0→25.5 (delta +2.5; caldo invariato
  28.2/28.0). Commento aggiornato. `COLD_PRESSURES` non è renderizzato da nessun modulo.
- `ui/console.py`: advice cache di Gigi (2 punti) da "+0.5 · 26.0→26.5" a **"+1.0 · 25.5→26.5"**,
  coerente col nuovo freddo (a caldo → ~29.0, in finestra).
- `SPEC_ERRATA.md`: ERR-01 valori freddo aggiornati + nota "Rev. FASE 2.1" → **FASE 2.1 CHIUSA**.

**Verifica:** `py_compile ui/demo_data.py ui/console.py` OK; caldo/heatmap/media 28.6 invariati.
Committato/pushato.

---

## UI-FIX-2 — Bug visivi Telemetria/Setup + merge `restyle-ui` → `main` (02/07/2026)

**Data:** 02/07/2026 · branch `restyle-ui` (lavoro) → merge in `main` (deploy)

**Richiesta utente:** fix bug visivi (FASE 1 Telemetria, FASE 2 upload Setup, FASE 3
rosso RL/RR) su `restyle-ui`, poi "fai un merge" per portare tutto su `main`
(il branch effettivamente deployato), "attento a non cancellare/sovrascrivere".

**FASE 1 — `ui/telemetry.py` (solo presentazione):**
- "°C" da titolo asse ruotato → annotazione orizzontale in alto a sx.
- Legenda spostata SOTTO il grafico (`y=-0.15`) → niente overlap col titolo.
- Heatmap che riempie l'iframe (`.wrap`/`body height:100%`, svg in `.svgbox`) → no
  clipping; gauge `height 170→180`, `margin-top 8→18`.
- Riquadri gomma simmetrici al centro-scocca (ant. `y=52`, post. `y=166`).

**FASE 2 — `assets/app.css`:** regola dropzone `width:40px/overflow` scopata alla
sidebar (fix "Uplo…" nel Setup). Toggle "Input sessione" già OFF, nessuna modifica.

**FASE 3 — evidenziazione param suggeriti (RL/RR + precarico):** confermata
INTENZIONALE (`SUGGESTED_PARAMS`, rosso=suggeriti / bianco=resto). Già presente su
`main`; su `restyle-ui` era regredita e l'avevo ri-portata prima del merge.

**MERGE `restyle-ui` → `main`:** i due branch erano divergenti — `main` (deploy) aveva
i dati demo corretti (finestra 28.5–30.0, FASE 2.1, ERR-05, icona Gigi, login) ma NON
le fix visive; `restyle-ui` aveva le fix visive su dati vecchi (27.0–27.8).
Riconciliazione conservativa (backup tag `backup-main-premerge`/`backup-restyle-premerge`):
- **dati/logica**: tenuta la versione `main` (`demo_data.py`, `setup_view.py` con
  `val_color`, gauge axis 27.0–30.5, finestra 28.5–30.0) — nessun dato regredito;
- **fix visive**: riapplicate su `telemetry.py` di `main`; `app.css` (upload) merge pulito;
- **doc**: mie voci rinumerate **INC-005/INC-006** (main aveva già INC-003/004 diversi).

**File protetti:** nessuno toccato (agent/parser/prompt/gauge-logic/fuel).

**Verifica:** `py_compile` OK (telemetry/demo_data/setup_view/dashboard/console); dati
`main` preservati; nessun marker di conflitto residuo. Merge commit su `main`, poi
`restyle-ui` riallineato a `main`.

**Rifinitura post-verifica utente (02/07/2026):** l'utente ha segnalato testo ancora
troppo vicino/sovrapposto in Telemetria. Correzioni strutturali su `ui/telemetry.py`:
- titolo grafico spostato FUORI figura (markdown sopra il grafico) → legenda in alto
  senza overlap, asse "Giro" libero in basso;
- unità °C come **suffisso dei tick Y** (`88°`, `95°`…) invece dell'etichetta flottante
  → orizzontale, mai sovrapposta;
- heatmap: riquadri gomma allargati (34→40), font numero 17→14 e spaziatura
  numero/etichetta aumentata → niente più crowding; X riallineate simmetriche (38/162).

**FASE 4 (logo `.AI`):** `ui/sidebar.py` — aggiunto `!important` inline al `.AI` (batte
l'`!important` delle regole sidebar). Doc INC-007.

---

## TELEMETRIA-UPGRADE-1 — 3 fix + espansione a rischio zero (branch `restyle-ui`)

**Data:** 03/07/2026 · branch `restyle-ui` (poi merge `--ff-only` su `main`) · modello claude-opus-4-8 (Claude Code)

### Catalogo messaggi di questa iterazione
1. **Ripresa lavori (status/metodo):** leggere per intero prompt log + breakdown + progetto,
   verificare discordanze, controllare allineamento Git con `origin`, esporre il piano e
   attendere approvazione; non inventare/costruire. Subtask iniziale: nessuna.
2. **Utente:** «fai in modo che abbia tutto allineato qui su questo pc» → eseguito il
   fast-forward (locale era 13 commit dietro `origin/main`, vedi sotto).
3. **Utente:** «questo [PROMPT_LOG] non scriverlo, avverranno altre modifiche; aspetta istruzioni.»
4. **Utente:** incollato il prompt **TELEMETRIA-UPGRADE-1** (FASI 0–3, con STOP GATE).
5. **Utente:** «procedi con la fase 1» → diagnosi dei 3 bug.
6. **Utente:** «procedi con la fase 2» → i 3 fix, uno alla volta.
7. **Utente:** «installa kaleido e generami le anteprime» → PNG di line chart/gauge + heatmap.
8. **Utente:** «posso controllare ora o devi pushare?» → chiarito: modifiche solo locali, nessun push.
9. **Utente:** «vai avanti fino ai prossimi stop gate; controllerò a ogni push.»
10. **Utente (scelta guidata FASE 3):** incluse **tutte e 4** le voci del menu espansione.
11. **Utente:** «sì aggiorna i doc e poi ok push.»

### Passo preliminare — Allineamento Git
Locale (`main` e `restyle-ui`) era **13 commit dietro** `origin` (lavoro dall'altro PC:
punch-list v2, INC-004…007, ERR-05, merge UI-FIX-2, FASE 4). Fast-forward pulito a
`376880b`, `0/0` col remoto, tree clean, `py_compile` OK. Nessun dato perso.

### FASE 0–1 — Ricognizione + diagnosi (sola lettura)
File Telemetria: `ui/telemetry.py` (line chart/gauge/heatmap), `ui/demo_data.py` (dati),
`ui/components.py` (helper/token), `ui/router.py` (dispatch). Nessun file protetto coinvolto.
I 3 bug (unità `°`/`°C`, tooltip su legenda, heatmap slegata dalla sagoma) sono figli di
INC-005 → tracciati come **INC-008**. Note path prompt ↔ repo: `parser.py`→`backend/parser/csv_parser.py`,
`system_prompt.txt`→`_v4.txt`, font non in `static/` ma in `assets/fonts/` (base64, no Google Fonts).

### FASE 2 — 3 fix (solo `ui/telemetry.py`, un fix alla volta, `py_compile` dopo ciascuno)
1. `ticksuffix="°"→"°C"` (uniformità tick/annotazione/tooltip).
2. Legenda SOTTO il grafico (`y=-0.20`, `t`30→16/`b`48→88, `title_standoff=6`) → no overlap col box `x unified`.
3. Heatmap ancorata alla scocca (`_BODY_LEFT/RIGHT_X`, `_FRONT/REAR_AXLE_Y`; `_heat_corner_svg` centro-ruota).
Anteprime PNG generate via `kaleido` (installato SOLO nel `.venv` locale, gitignored): line chart, gauge, heatmap.

### FASE 3 — espansione (tutte e 4 le voci, rischio zero, colonne CSV esistenti)
- **Tabella giro-per-giro** ordinabile (`_laps_table_df` + `st.dataframe`): giro · consumo · 4 temp · 4 press.
- **Proiezione giri rimanenti** (`project_remaining_laps`, sola lettura, FUORI dalla fuel-logic protetta).
- **Feed cross-check** (`_cross_check_items` deterministico + `_gigi_diagnosi_summary` che riusa
  `console_response` da `session_state`, **zero LLM**).
- **Toggle °C/°F** e **raw/smoothed** sul line chart (`_temp_line_fig(unit, smoothed)`, `_to_unit`, `_smooth_series`).
- `ui/demo_data.HOT_PRESS_SERIES` (8 giri/gomma): **ultimo giro == valori dei gauge**, garantito da `assert` → coerenza.

### File protetti
Nessuno toccato. `agent.py`, parser, prompt, logica gauge/fuel invariati; la proiezione carburante è
una funzione nuova e separata, non tocca la strategia protetta.

### Verifica
`py_compile` OK (telemetry/demo_data); import intera catena UI OK; runtime: unità C/F (limite 95°C↔203°F,
range convertiti), smoothing 3-punti, tabella 8×10 con press ultimo-giro = gauge, proiezione 20L/3.2=6.2,
cross-check (Post.DX 105°C crit + retro sotto finestra warn), riuso diagnosi Gigi. Doc: INC-008 aperto+risolto,
riga stale ERR-02/04 rimossa da `AVVIO_RAPIDO.md`, README aggiornato.

**Decisione:** ☑ Mantenuto. Commit su `restyle-ui`, merge `--ff-only` su `main`, push di entrambi (dopo «ok push»).
Backlog rimasto: stile tasti login; Sidebar/Setup/Dashboard rimandati a fasi successive; video demo di backup da registrare.

### Addendum — Stile tasti login: bottone Google cockpit (03/07/2026)

**Messaggi:** utente «visto tutto, puoi procedere» → scelta guidata backlog = **"Stile tasti login"** →
scelta guidata direzione = **"Bottone Google in stile cockpit"** → «ok push».

**Intervento (solo `styles/login.css`, `pages/login.py` INTATTO — login sempre funzionante):**
`.pw-google-btn` da chiaro (`#f5f5f5`/Inter) a **cockpit dark**: superficie `--bg-tertiary`,
bordo `--border`, font JetBrains Mono, testo `--text-secondary` attenuato (segnala "non attivo"),
logo `opacity 0.9`, hover con accenno di bordo rosso; resta `cursor:not-allowed` e tag "· IN ARRIVO ·".
Motivazione: era l'unico elemento chiaro in una login tutta scura → stonava. Nessun file protetto toccato.

**Verifica:** `py_compile pages/login.py` OK; mockup prima/dopo generato. Item backlog "stile tasti login"
→ **CHIUSO** (spuntato in `AVVIO_RAPIDO.md`). Backlog residuo: Sidebar/Setup/Dashboard, video demo.

### Addendum — Sidebar: compattazione + polish (03/07/2026)

**Scoping (domande all'utente):** obiettivo = tutti e tre (funzionale+estetico+contenuto), MA collapse
già ok (non toccare), box "Sessione Attiva" tenuto com'è (demo fisso), problema reale = **sidebar troppo
vuota/spaziata** → compattare + riempire il vuoto in basso.

**Intervento (`ui/sidebar.py` + `assets/app.css`, solo selettori scoped `section[data-testid="stSidebar"]`,
nessun wildcard; collapse e dati box invariati; nessun file protetto):**
- **Densità:** `stVerticalBlock gap 0.45rem`, margini logo/box più stretti.
- **Fondo ancorato:** sidebar resa colonna a piena altezza + spacer flessibile (`.pw-sb-spacer` con
  `:has()`→`flex:1`) che spinge **Esci + footer** in fondo; degrada a `min-height` se il flex non regge.
- **Footer** `.pw-sb-footer`: `v0.2.0` + link GitHub (mono, hover rosso).
- **Divider** `.pw-sb-div` tra Navigazione e Sessione Attiva.

**Verifica:** `py_compile ui/sidebar.py` OK; import catena UI OK; mockup prima/dopo generato.
Non è un incident (polish, non bug) → nessun INC. Da confermare a schermo il pin-in-fondo (`:has()`/flex)
sul deploy; fallback graceful se non applicasse.

**Backlog residuo:** Setup (colore pressioni), Dashboard (routing bottoni), video demo di backup.

### Addendum — Sidebar: spaziatura uniforme (rework, flusso naturale) (03/07/2026)

**Data:** 03/07/2026 · branch `restyle-ui` · modello claude-opus-4-8 (Claude Code)

**Contesto (ripresa dopo `/clear`):** memoria persistente vuota → ricostruito lo status
leggendo per intero PROMPT_LOG/INCIDENTS/AVVIO_RAPIDO/README + Git (tutto allineato a
`b08f206`, `main`==`restyle-ui`==`origin/*`, 0/0). Prossima task scelta dall'utente = sidebar.

**Catalogo messaggi di questa iterazione:**
1. Utente: «a che punto siamo con la task di prima?» → chiarito che `/clear` ha azzerato il contesto.
2. Utente: «controlla la memoria persistente» → cartella memory vuota (nessun file).
3. Utente: incollato il **Setup/metodo** (scopo prompt_log + incidents; obiettivo: proseguire il
   breakdown/status; leggere tutto, verificare discordanze, allineamento Git, esporre piano e
   attendere approvazione; non inventare/costruire; repo link). Subtask iniziale: nessuna.
4. Scelta guidata prossima task → Utente (Other): «inizia col sistemare la sidebar, avevo fatto
   richieste prima ma non sono riuscite bene».
5. Scelta guidata sintomo → Utente: «spaziature irregolari; voglio la sidebar compatta senza scroll,
   ma l'ultima volta è venuta troppo compatta e alcune cose rischiano di sovrapporsi».
6. Scelta guidata Esci/footer → Utente: **«Flusso naturale (Consigliato)»** (no push-to-bottom).
7. Utente: «ok procedi».

**Diagnosi:** le spaziature irregolari + rischio overlap nascevano dal conflitto tra due meccanismi
del blocco "compattazione" precedente: `[data-testid="stVerticalBlock"] { flex:1 }` (stirava TUTTI i
blocchi verticali annidati) e `gap:0.45rem` (troppo stretto), sommati al push-to-bottom
(`min-height:100vh` + spacer `:has()` flex). Compattare e riempire in contemporanea = layout ballerino.

**Interventi (solo presentazione, nessun file protetto; auth/nav/logout e box sessione invariati):**
- `assets/app.css` (blocco sidebar): **rimossi** `min-height:100vh`/flex-column su `> div:first-child`,
  le regole flex annidate (`> div`/`stSidebarUserContent`), il `flex:1` su `stVerticalBlock` e la regola
  spacer `stElementContainer:has(.pw-sb-spacer)`. Resta un **unico gap uniforme `0.65rem`** (compatto ma
  respirabile). Commento di sezione aggiornato ("flusso naturale, spaziatura uniforme").
- `ui/sidebar.py`: rimosso il `<div class="pw-sb-spacer">`; al suo posto un **divider** `.pw-sb-div`
  tra "Sessione Attiva" ed "Esci" → flusso dall'alto, Esci/footer seguono naturalmente.

**Verifica:** `py_compile ui/sidebar.py` OK; `import ui.sidebar` OK (`render_sidebar` callable);
nessun riferimento orfano a `pw-sb-spacer` (grep py/css). Non è un incident (polish, non bug) → nessun INC.

**Decisione:** ☑ Mantenuto. Commit/push su `restyle-ui`+`main` solo dopo «ok push» esplicito (regola git).

**Follow-up (stesso giorno) — sidebar ancora scrollabile → compattazione dell'ingombro:**
Utente: «risulta sempre con le parti scorrevoli, la volevo fissa». Diagnosi: il flusso naturale
non bastava — la somma padding sidebar + 5 bottoni + box sessione superava il viewport → scroll
interno di Streamlit. Ridotto l'ingombro verticale (~95-100px) in `assets/app.css`, blocco sidebar:
`gap 0.65→0.5rem`; `.block-container padding-top 1.5→0.75rem`; container `> div:first-child`
`1rem/1.5rem → 0.75rem/0.9rem`; **override padding bottoni** (nav+Esci) `0.6→0.4rem`; `.pw-sb-div`
`margin 12→8px`; `.pw-sb-footer` `margin/padding-top 12→8px`. Flusso normale → nessun overlap.
Nota diagnostica lasciata all'utente: possibile **deploy stale** (INC-003) — Streamlit Cloud non
si aggiorna da solo; verificare in locale (`streamlit run app.py`). Solo CSS, nessun file protetto.
Non è un incident (polish) → nessun INC.

**Follow-up 2 (stesso giorno) — causa reale dello scroll: overflow nativo:**
Utente: «posso ancora scrollare con la rotella nella sidebar, perché? trova l'errore e fixa».
**Errore individuato:** compattare il contenuto non bastava — il contenitore-scroller della
sidebar ha `overflow-y:auto` di default in Streamlit, quindi basta 1px di eccedenza (altezza
finestra/zoom) perché la rotella scrolli, anche senza barra visibile. Le modifiche precedenti
riducevano l'altezza ma **non disattivavano il meccanismo di scroll**. **Fix:** `overflow:hidden`
sui contenitori-scroller della sidebar (`> div:first-child`, `stSidebarContent`,
`stSidebarUserContent` — coperti i vari testid delle versioni Streamlit) → pannello fisso. La
compattazione resta come garanzia che il contenuto stia nel viewport (hidden non taglia nulla su
schermi normali). Solo CSS, nessun file protetto. Non è un incident (polish) → nessun INC.

**Follow-up 3 (stesso giorno) — riempire il pannello (no spazi vuoti):**
Utente: «ora che è fissa, imposta meglio tutte le voci così da non lasciare spazi liberi» +
condiviso screenshot (`Catture di schermata/Screenshot 2026-07-03 194944.png`, letto). Dallo
screenshot: **grande fascia vuota in alto** (header nativo sidebar col bottone collapse che riserva
una banda) + voci raccolte al centro con spazio residuo sotto il footer. **Fix (solo `assets/app.css`):**
(1) catena flex a piena altezza (`> div:first-child` height:100vh + flex column; `stSidebarContent`/
`stSidebarUserContent` e wrapper flex:1) così il blocco voci occupa tutto il pannello; (2)
`justify-content: space-between` sul blocco voci → logo in alto, footer in basso, resto equidistante
(space-between aggiunge solo spazio, mai negativo → **impossibile l'overlap** del vecchio approccio);
(3) header sidebar `min-height:0` → eliminata la fascia vuota in alto (bottone « resta, ha z-index/min
propri). Overflow:hidden dei follow-up precedenti invariato (resta pannello fisso, no scroll). Non è
un incident (polish) → nessun INC.

**Follow-up 4 (stesso giorno) — «è uguale a prima»: causa reale = CSS in cache:**
Utente: «è ancora uguale a prima, fixala». Indagine: testid Streamlit 1.58 verificati nel frontend
(`stSidebarContent`/`stSidebarUserContent`/`stSidebarHeader`/`stVerticalBlock` esistono → selettori
corretti). **Causa vera:** `assets/css_loader.py` cacheva `app.css` in `@lru_cache(maxsize=1)` a
vita-processo e Streamlit **non sorveglia i file `.css`** → un semplice refresh serviva il CSS
vecchio; il fill/header del follow-up 3 non veniva mai caricato senza un restart completo del server.
**Fix:** cache legata all'`mtime` del file (`_app_style_cached(mtime)` + `_base_style_cached(mtime)`)
→ ogni modifica CSS si ricarica a un rerun/refresh, niente più restart. In più, robustezza sul fill:
`min-height: calc(100vh - 3rem)` sul blocco voci (forza l'altezza anche se la catena flex dei genitori
non regge). File toccati: `assets/css_loader.py`, `assets/app.css` — nessun file protetto. Verificato:
`py_compile` OK, `_app_style()` rilegge il file (contiene `space-between`). Non un incident → nessun INC.

**Follow-up 5 (stesso giorno) — Esci tagliato: il fill era troppo aggressivo:**
Utente: «il tasto Esci in fondo alla sidebar risulta tagliato, accentra meglio tutto in modo che
non venga male nulla». **Causa:** il fill del follow-up 4 forzava il blocco voci a
`min-height: calc(100vh - 3rem)` + `space-between`, ma quel blocco vive **dentro** il padding
(0.75rem sopra + 0.9rem sotto) e sotto l'header nativo → `blocco + padding + header > 100vh`, e con
`overflow:hidden` il fondo (Esci + footer) finiva sotto il taglio. **Fix (solo `assets/app.css`):**
(1) tolto il fill forzato sul blocco voci — via `min-height:calc(100vh-3rem)`, via `space-between`,
`flex:0 0 auto` → altezza **naturale**, non può più sforare (Esci mai tagliato); (2) `justify-content:
center` sul contenitore flex della sidebar → stack **centrato verticalmente** con margini uguali
sopra/sotto (niente fasce vuote sbilanciate); (3) gap voci a `0.6rem` (spaziatura uniforme). Overflow
hidden / header banda-zero / compattazione padding invariati. Non un incident (polish) → nessun INC.

---

## 03/07 — Setup: colore/evidenziazione pressioni

Utente: «andiamo col setup» → task backlog "colore pressioni". Metodo: analisi Setup
(`ui/setup_view.py` `_slider`), scelta criterio con l'utente (AskUserQuestion → «Finestra
ottimale ACC»). **Discrepanza trovata** analizzando `ui/demo_data.py`: esisteva già una
finestra a freddo documentata `26.0–27.0` psi (commento su cui si regge la storia demo:
posteriori 25.7/25.5 sotto finestra). La finestra `26.5–27.5` che avevo proposto NON
coincideva → segnalata all'utente, che ha scelto di **allineare a `26.0–27.0`** (coerenza
progetto). **Implementazione (solo layer presentazionale, nessun file protetto):**
- `ui/demo_data.py`: nuova costante tunable `COLD_PRESS_WINDOW=(26.0,27.0)` +
  `COLD_PRESS_AMBER_MARGIN=0.6`. `modules/setup_params.py` intatto.
- `ui/setup_view.py`: helper `_pressure_status_color(value)` (verde in finestra, ambra entro
  il margine, rosso oltre — soglie da demo_data). In `_slider`, per `key` che inizia con
  `tire_press_`, il valore prende il colore di stato + pallino ● accanto al numero; gli altri
  parametri invariati (bianco / rosso-suggerito-Gigi). In `_render_tyres`, legenda compatta
  sotto "PRESSIONI". Tutti stili inline → nessuna nuova CSS (niente problemi di cache).
Verifica: `py_compile` OK; smoke test classificatore (25.3→rosso, 25.5/25.7→ambra,
26.0–27.0→verde, 27.5→ambra, 27.7→rosso; demo COLD: ant.=verde, post.=ambra). Colore calcolato
sul valore corrente → si aggiorna muovendo lo slider. Non un incident (feature UI) → nessun INC.

---

## 03/07 — Dashboard: card + bottone uniti  ⟵ ANNULLATO (vedi sezione successiva)

> **NB:** questo intervento (commit `a4d4279`) è stato **annullato** su feedback utente
> («era meglio prima»): l'utente preferiva l'impaginazione a iframe e voleva in realtà
> lavorare sui **grafici**. `ui/dashboard.py` e `assets/app.css` ripristinati allo stato
> precedente (`c617e94`). Vedi la sezione "Dashboard: grafici SVG arricchiti".

Utente: «procedi con l'analisi della Dashboard». Analisi: il **routing** dei bottoni era già
implementato e funzionante (`ui/dashboard.py` → `nav.go_to`, confermato dal PROMPT_LOG punto 4.2),
quindi la voce di backlog risultava già evasa a livello funzionale. **Vero punto debole (UX):** le 3
card metriche erano in un **iframe** (`components.html`) e i bottoni "Apri" stavano **staccati** sotto,
in una riga separata — un bottone dentro l'iframe non può navigare (iframe isolato da Streamlit).
Scelta utente (AskUserQuestion → «Unire card + bottone»). **Fix (nessun file protetto, nessun dato
modificato):**
- `ui/dashboard.py`: rimosso l'iframe delle card (`_cards_html`); `_metric_card` → `_metric_card_inner`
  (contenuto senza box) + `_metric_cards()` data-driven (inner + btn + target). In `render()`,
  `st.columns(3)` e per ogni card `st.container(border=True, key="pw-dash-card-<k>")` con dentro il
  markdown **e** il `st.button` nativo → `nav.go_to`. Mapping **invariato** (Temp→Telemetria ·
  Pressione→Setup · Consumo→Engineer Console). Card "Chiedi a Gigi" lasciata com'è (CTA full-width).
  Gli SVG (sparkline/window-bar) sono inline puri → renderizzano nel doc principale coi font iniettati.
- `assets/app.css`: blocco scoped `[class*="st-key-pw-dash-card-"]` (sfondo #111, bordo #222, radius 12,
  padding, `height:100%` per colonne di pari altezza) + `.pw-dash-card-note{min-height:2.4em}` per
  allineare i 3 bottoni. Selettore scoped alla sola classe key.
Verifica: `py_compile` OK; test import → 3 card, mapping corretto, `_cards_html` rimosso, hook CSS
presenti. Non un incident (UX polish) → nessun INC.

---

## 03/07 — Dashboard: grafici SVG arricchiti

Utente: «ok era meglio prima, quello che volevo rifare erano i **grafici**, renderli migliori».
→ Prima cosa: **ripristinata** la Dashboard allo stato `c617e94` (`git checkout c617e94 -- ui/dashboard.py
assets/app.css`): tornano le card in iframe con i bottoni sotto (annullato l'intervento card+bottone).
Poi analisi grafici: le card usavano `sparkline_svg` (linea nuda) e `window_bar_svg` (barra+finestra),
i più "poveri" dell'app (Telemetria usa già Plotly). **Vincolo:** le 3 card stanno in UN iframe
(`components.html`) → dentro solo SVG, non Plotly (richiederebbe card native = il layout appena scartato).
Scelta utente (AskUserQuestion → «SVG arricchiti, mantiene il look»). **Implementazione (solo
presentazione, nessun file protetto, nessun dato):**
- `ui/components.py`: nuovo `_smooth_path` (Catmull-Rom→Bézier). `sparkline_svg` riscritta →
  frammento HTML con SVG (area sfumata via `linearGradient` con id univoco per-serie, curva morbida,
  linea-limite tratteggiata ambra opzionale) + etichette **in overlay HTML** (min/max, "lim N",
  punto finale) — HTML e non `<text>` SVG per non distorcersi con `preserveAspectRatio="none"`;
  chip di sfondo scuro per leggibilità sopra la linea. Firme estese con soli parametri opzionali
  (`limit`, `value_fmt`, `show_minmax`, `fill`) → retro-compatibili. `window_bar_svg` arricchita:
  valore sopra il marker + range finestra sotto la banda verde.
- `ui/dashboard.py`: Temp passa `limit=dd.TEMP_LIMIT` (95) e `value_fmt="{:.0f}"`; Consumo
  `value_fmt="{:.1f}"`; Pressione valore+range. Area grafico `46→52px min-height`, iframe `210→230`.
Verifica: `py_compile` OK; smoke test HTML → etichette attese presenti (max 105, min 82, lim 95,
valore 28.6, range 28.5–30.0, min/max consumo 3.0/3.3), id gradienti **unici** fra le 2 sparkline,
tag div/svg/span bilanciati. Non un incident → nessun INC.

**Backlog residuo:** video demo di backup (task utente, non-code).

---

## 04/07 — Documentazione: riconciliazione doc storici

Utente: «ok molto meglio i grafici era quello che volevo» → conferma Dashboard OK. Poi «quale potrebbe
essere la prossima task da fare» → AskUserQuestion → scelta **«Documentazione / README»**. Analisi (lettura
integrale README, README_EXTENSION, SPEC_ERRATA, le due spec v3/v4, verifica incrociata con `agent.py` e
`requirements.txt`). Discrepanze trovate: (1) `README_EXTENSION.md` obsoleto — descriveva `app.py` come
monolite «da sostituire», citava `parser.py`, `requirements` con `openai` e senza `plotly/requests`, costo
Vision su Sonnet, e incongruenza interna «47» vs tabella «49» parametri; (2) `PitWall_AI_Technical_Spec_v3.md`
già dichiarata obsoleta dalla v4 ma priva di avviso nel file. README.md invece **già accurato** (verificato:
`LLM_MODEL` default `claude-haiku-4-5` = `agent.py:40`; requirements combaciano). Scelta utente: **marcare
come superati** (non eliminare). **Fix (solo file `.md`, nessun codice/dato/file protetto):**
- `PitWall_AI_Technical_Spec_v3.md`: banner «DOCUMENTO SUPERATO → vedi v4/README» in testa.
- `README_EXTENSION.md`: banner «DOCUMENTO STORICO (v2, superato dal restyle)»; corretti i 4 punti fattuali
  (struttura reale con note storiche, requirements allineati al repo, `47→49` parametri, nota costo Vision +
  feature-flag `FEATURE_SCREENSHOT`).
- `README.md`: aggiunta tabella «Documentazione — quale file è valido» (Attuale vs Storico).
Non un incident → nessun INC.

**Backlog residuo:** video demo di backup (task utente, non-code).

---

## 04/07 — Prova-generale demo + allineamento script

Utente: «passiamo alla prova-generale demo» → «procedi». Prova a codice dei 7 passi di
`docs/demo_checklist.md` confrontati con l'app reale (lettura integrale `setup_view.py`,
`console.py`, `demo_data.py`, `test_session.csv`; smoke test import di 11 moduli). Esito
**funzionale ✅** (import OK, console demo 4/4 sezioni offline, i 5 scenari-chip rispondono
diversi, dati demo coerenti). Emersi **6 attriti script↔app** (nessun bug, sceneggiatura rimasta
indietro): (A) script «5 giri» ma schermate demo mostrano **8 giri** (hardcoded `demo_data`); (B)
[1:00] «sidebar→CSV→metriche» ma l'upload è nel Setup dietro toggle OFF e le card leggono da
`demo_data`, non dal CSV; (C) [2:30] «pressioni a freddo + ANALIZZA SESSIONE nel Setup» ma il
Setup non ha né radio freddo/caldo né bottone: l'analisi è in Engineer Console («⚙ ANALIZZA»);
(D) [4:30] «Parla con Gigi» chat separata inesistente (è la stessa Console); (E) retrotreno
scarico va raccontato sui dati a CALDO, non sul CSV a freddo (in finestra); (F) naming
«ANALIZZA SESSIONE»→«⚙ ANALIZZA». Scelta utente: **aggiornare lo script** (nessun codice/dato).
**Fix (solo `docs/demo_checklist.md`):** riscritta sez. 0 (dati a schermo = 8 giri demo, CSV
illustrativo 5 giri), passi [1:00]/[1:45]/[2:30]/[3:15]/[4:30] col flusso reale (Dashboard già
popolata → Telemetria → Setup senza analisi → Engineer Console con ⚙ ANALIZZA → follow-up
stessa console), checklist funzionale allineata. Non un incident → nessun INC.

**Backlog residuo:** video demo di backup (task utente, non-code).

---

## 04/07 — Giro a schermo (verifica visiva) + nuova richiesta backlog

Utente: «facciamo un giro a schermo insieme» → guida passo-passo (login → …). **Passo 1 (login)
verificato OK** dall'utente (font/hero/badge/bottone Google a posto). Poi richiesta:
«aggiungi alla checklist che vorrei rifare per bene le schermate aggiungendo magari mini
animazioni o roba simile per abbellire, che non siano troppo eccessive». Registrata come voce di
**backlog** in `AVVIO_RAPIDO.md` (In sospeso): "Restyle fine schermate + micro-animazioni
discrete" (fade/slide al load, hover soft, transizioni leggere; niente effetti eccessivi; dentro
il design system; nessun file protetto). **Da pianificare** (mostrare piano prima di costruire).
Non eseguita ora — solo annotata.

**Backlog residuo:** micro-animazioni schermate (DA PIANIFICARE) · video demo di backup (non-code).

---

## 04/07 — Giro a schermo completato (verifica visiva OK)

Utente ha completato con me il giro guidato a schermo (locale): «va tutto bene» a ogni passo →
**Login, Dashboard, Telemetria, Setup, Engineer Console tutti verificati OK**. In particolare
confermati a video i fix di sessione: grafici Dashboard arricchiti, unità °C/legenda/heatmap
Telemetria (INC-005/008), colore pressioni + legenda Setup, ".AI" rosso e "Esci" non tagliato
(INC-007/sidebar), upload non troncato (INC-006), Console 4 card + ⚙ ANALIZZA + interattività chip.
**Aggiornata `docs/demo_checklist.md`:** spuntati [x] i punti verificati (login, render schermate,
console, font-no-flash, stile dark, plotly leggibili); lasciati [ ] con nota quelli NON controllati
in questo giro (deploy sveglio, API live end-to-end, no-fetch-Google via DevTools, responsive 768px)
— report fedele, niente spunte non verificate. Solo `.md`, nessun codice.

**Backlog residuo:** micro-animazioni schermate (DA PIANIFICARE) · verifiche finali su deploy
(sveglio, API live, DevTools no-Google-fonts, 768px) · video demo di backup (non-code).

---

## 06/07 — Micro-animazioni discrete (tutte le schermate)

**Data:** 06/07/2026 · branch `main` (locale allineato dopo pull) · modello claude-opus-4-8 (Claude Code)

### Catalogo messaggi di questa iterazione
1. **Setup/metodo (status):** leggere per intero prompt log + breakdown + progetto, verificare
   discordanze, controllare allineamento Git con `origin`, esporre il piano e attendere approvazione;
   non inventare/costruire. Subtask iniziale: nessuna, attendere comando.
2. Utente: «Procedi con l'analisi».
3. Utente: «Approvo Passo 1 + 2, procedi» → allineamento Git + aggiornamento memoria persistente.
4. Utente: «procedi» → preparazione piano micro-animazioni.
5. **Scelta guidata (AskUserQuestion):** intensità = **Discreta**, ambito = **Tutte le schermate**.
6. Utente: «Confermo il piano, procedi con l'implementazione».

### Passo preliminare — Allineamento Git
Locale (`main` e `restyle-ui`) era **16 commit dietro** `origin` (lavoro 03–04/07 dall'altro PC:
TELEMETRIA-UPGRADE-1, login Google, sidebar, colore pressioni Setup, grafici Dashboard, doc,
demo checklist, giro a schermo). Fast-forward pulito `376880b → fbb157f`, `0/0`, tree clean,
`py_compile`/import OK. Memoria persistente aggiornata (nuova `pitwall-status`, indice + branch-merge).

### Intervento — micro-animazioni (SOLO CSS, zero file protetti, zero `.py`)
- `assets/app.css` (Dashboard/Telemetria/Setup/Console): `@keyframes pwFadeUp` (opacity 0→1 +
  `translateY 8px→0`, 200ms ease-out) applicato ai **figli diretti del vertical-block di primo
  livello** in `section[data-testid="stMain"]` (sidebar esclusa), con **stagger** nth-child
  (+40ms, cap `n+7` a 240ms). Hover soft: `.pw-metric-card` lift `-2px` + bordo accento; bottoni
  area principale con transizione morbida colore/bordo + micro-press `translateY(1px)` all'`:active`.
- `styles/login.css`: la login carica solo font+token (non app.css) → keyframe locali. `pwLoginFadeUp`
  (fade-up 10px, 350ms) su hero title/ruler/sub/tagline con stagger (0/80/160/240ms); `pwTraceIn`
  (fade a opacity 0.18) sulla traccia telemetria. **Guard `prefers-reduced-motion` aggiunto qui**
  (in app.css era già presente e copre i nuovi keyframe col selettore `*`/`!important`).

**Coerenza design system:** solo classi custom / selettori scoped a `stMain`, nessun wildcard;
accento `#E8002D`, font self-hosted; grafici Plotly/iframe **non toccati** (animo i contenitori).
`pages/login.py` e logica auth **invariati** (priorità #1 login sempre funzionante).

### Verifica
Import catena UI OK; `css_loader` rilegge il nuovo CSS (`pwFadeUp` presente → cache mtime funziona);
graffe bilanciate (app.css 215/215, login.css 45/45); keyframe totali coerenti (app.css 3, login.css 2).
Non è un incidente (polish, non bug) → **nessun INC**. Backlog `AVVIO_RAPIDO.md` spuntato.

**Rischio noto (da confermare a schermo):** Streamlit ri-renderizza a ogni interazione — se re-inserisce
il nodo, un click può far ripartire il fade (200ms). Con intensità discreta è impercettibile; se disturba,
limitare l'animazione ai soli cambi-pagina.

**Decisione:** ☑ Mantenuto. Commit `2f749bc`, push su `main` + `restyle-ui` (nuovo workflow: l'utente
verifica online → push diretto dopo implementazione approvata, senza «ok push» separato).

### Fix — animazioni non visibili online: selettore fragile (06/07)

**Messaggio utente:** «non vedo nessuna animazione, tutto uguale».

**Diagnosi:** `app.css` è iniettato inline (`app.py:32` → `inject_design_system()`, `include_app_css=True`),
quindi le regole erano nel DOM. Il problema: il selettore di load-in usava il **figlio diretto**
`section[data-testid="stMain"] .block-container > div[data-testid="stVerticalBlock"] > div`. Con
`requirements.txt` a `streamlit>=1.0` **non pinnato**, il deploy gira su una versione più nuova del
locale (1.57): se c'è un wrapper intermedio, il `>` non aggancia nulla → nessuna animazione. Il fade da
200ms era anche poco percepibile.

**Fix (solo `assets/app.css`):** riscritto con selettori **robusti su testid stabili** (confermati nel
bundle): fade-up dell'intero `stMainBlockContainer`/`.block-container` (`pwPageIn` 320ms) + fade-up dei
singoli `[data-testid="stElementContainer"]` (descendant, non dipende dal nesting) con stagger 45/90/120ms,
durata 280ms, offset `translateY 10px`. Su cambio pagina gli `stElementContainer` sono nodi nuovi →
l'animazione riparte = transizione visibile. `login.css` invariato (classi custom già presenti nel DOM,
iniettato inline da `login.py:14`). `prefers-reduced-motion` invariato.

**Verifica:** graffe 216/216, 4 keyframe; injection app.css confermata inline; testid `stElementContainer`/
`stMainBlockContainer` presenti nel bundle Streamlit. Nota per l'utente: **hard-refresh** (Ctrl+Shift+R)
e attendere il redeploy Cloud; la transizione è più evidente **cambiando pagina**.

**Esito (06/07):** dopo il fix il fade **ancora non si vedeva** nemmeno post-reboot dell'app. Causa reale
individuata: l'utente aveva **"Effetti di animazione" DISATTIVATO in Windows 11** → il browser attiva
`prefers-reduced-motion: reduce`, che il nostro guard rispetta azzerando ogni animazione. Riattivata
l'impostazione + hard-refresh → **fade visibile, confermato dall'utente ✅**. Il guard resta (accessibilità
corretta). Task micro-animazioni **CHIUSA**. Lezione: quando le animazioni "non si vedono" e il CSS è
iniettato, sospettare l'impostazione reduced-motion dell'OS prima di riscrivere codice.

---

## 06/07 — Verifiche finali deploy (pre-verifica codice + fix responsive login)

**Data:** 06/07/2026 · branch `main` · modello claude-opus-4-8 (Claude Code)

**Messaggi:** utente «passiamo alle verifiche finali sul deploy» → analisi dei punti aperti in
`docs/demo_checklist.md` → «procedi col fix responsive login e aggiorna la checklist».

**Pre-verifica lato codice (read-only) dei punti aperti:**
- **No fetch Google Fonts** ✅ — grep intero repo: 0 riferimenti a `fonts.googleapis`/`gstatic`/`<link>` font/
  `@import`; woff2 embeddati base64 in `assets/css_loader.py`. (Resta conferma DevTools sul deploy.)
- **CSV upload «5 giri»** ✅ — `ui/setup_view.py:296` emette «CSV letto: {laps} giri · consumo medio…»;
  `backend/data/test_session.csv` = header + 5 righe = 5 giri.
- **API live** ✅ infra — `agent.py` (`ANTHROPIC_API_KEY`, modello default `claude-haiku-4-5`, cascade-fallback);
  key da `st.secrets`/env (`console.py:214`). Per testarla live: Secrets su Cloud + toggle «Demo-mode» OFF
  (`console.py:347`) + domanda non-demo (una demo torna cache via `_is_demo_prompt`) → ⚙ ANALIZZA.
- **Responsive** ⚠️→fix — `app.css` aveva già `@media` 1100/768px; **`styles/login.css` non aveva media query**
  e l'hero 56px fisso poteva sforare su schermi stretti.

**Intervento (solo `styles/login.css`, nessun file protetto, logica auth invariata):** aggiunti due
breakpoint — `@media (max-width:768px)` (hero 56→44px, letter-spacing 6→4, ruler 260→200, card padding
ridotto) e `@media (max-width:430px)` (hero →32px, sub 11px, ruler 150). Così "PITWALL●AI" non va mai in
overflow. `docs/demo_checklist.md` aggiornato con le pre-verifiche (annotazioni oneste: `[x]` solo il
già-verificato, note "pre-verificato lato codice / resta conferma sul deploy" sugli altri).

**Verifica:** login.css graffe 55/55, 3 `@media`; nessun file `.py` toccato. Restano da spuntare sul deploy
(gruppo B, azioni utente nel browser): deploy sveglio, API live end-to-end, DevTools no-Google, resize 768px,
backup (video/screenshot) e sicurezza (.env). **Decisione:** ☑ Mantenuto; push su `main`+`restyle-ui`.

---

## 06/07 — Allineamento secondo PC (fast-forward) + verifica integrità

**Data:** 06/07/2026 (ripresa lavori su questo PC) · branch `restyle-ui`/`main` · modello claude-opus-4-8 (Claude Code)

### Catalogo messaggi di questa iterazione
1. **Setup/metodo (status):** leggere per intero prompt log + breakdown + progetto, verificare discordanze,
   controllare allineamento Git con `origin`, elaborare il prossimo passo, esporre il piano e attendere
   approvazione; non inventare/costruire. Subtask iniziale: nessuna.
2. **Utente (scelta guidata prossimo passo):** **«Allinea e poi stop»** — eseguire il fast-forward pull su
   `main`+`restyle-ui`, verifica integrità, poi fermarsi (nessun task di codice aperto).

### Diagnosi (sola lettura, pre-azione)
Questo PC era **8 commit indietro** rispetto a `origin` (lavoro del 06/07 fatto dall'altro PC e già pushato):
micro-animazioni (`2f749bc`) + fix "non visibili"/chiusura (`3a50322`,`ae6cac1`, causa reale = reduced-motion
OS disattivato in Win11, poi confermato ✅), fix responsive login (`fdd5b1e`), verifiche finali deploy
(`cb37668`,`0f88aa4`,`ecee4f7`), gitignore report personali (`c587064`). Working tree locale pulito → nessun
commit locale da preservare. Nessun'altra discordanza fra i file. README già accurato (04/07): non serve toccarlo.

### Interventi eseguiti
- **Allineamento Git:** `git pull --ff-only` su `restyle-ui` e `main` → entrambi da `fbb157f` a `c587064`,
  `0/0` col remoto, working tree pulito. Nessun dato perso (solo avanzamento).
- **Verifica integrità stato 06/07:** `py_compile` OK (app + `ui/*` + `modules/*` + parser/manager +
  `pages/login.py` + `css_loader.py`); smoke-import catena UI (11 moduli) OK; sanity CSS: `app.css` graffe
  216/216, `login.css` 55/55, guard `prefers-reduced-motion` presente in entrambi.

### Stato backlog
Tutto il backlog di **codice** risulta CHIUSO (micro-animazioni era l'ultimo task, chiuso il 06/07).
Residuo **non-code:** video demo di backup + alcuni check browser-side del `demo_checklist` (screenshot,
`.env` non in condivisione schermo). ERR-01…05 e INC-001…008 tutti RISOLTI.

### File protetti
Nessuno toccato (nessuna modifica di codice: solo allineamento Git + questa entry di log).

**Decisione:** ☑ Mantenuto. Fermo qui come richiesto («allinea e poi stop»). Commit/push **non** eseguiti
(regola git: solo dopo «ok push» esplicito); questa entry di PROMPT_LOG resta come modifica locale non committata.

---

## HOTFIX-1 — 6 criticità Alte pre-esame (da Audit 06/07/2026) · branch `restyle-ui`

**Data:** 06–07/07/2026 · branch `restyle-ui` · modello claude-opus-4-8 (Claude Code)

### Catalogo messaggi di questa iterazione
1. **Utente:** incollato il prompt **PROMPT_FASE_HOTFIX-1** (FASE 0 audit read-only → FASE 1 diagnosi/STOP
   gate → FASE 2–7 esecuzione uno-alla-volta → FASE 8 chiusura). 6 fix; file protetti con STOP gate dedicato.
2. **Utente:** «ok procedi, FIX-6 opzione B» → via all'esecuzione; FIX-6 = pre-seed nel login (non tocca setup_params).
3. **Utente:** «ok su FIX-1, procedi con FIX-2» → e così via, un OK per ogni fix (FIX-2, FIX-3, FIX-4).
4. **Utente:** «ok su FIX-4, ok procedi su agent.py» → autorizzazione esplicita al file protetto per FIX-5.
5. **Utente:** «ok su FIX-5, procedi con FIX-6 opzione B» → applicata la B.
6. **Utente:** «ok su FIX-6, procedi con la FASE 8» → chiusura (doc + proposta commit).

### FASE 0 — Audit (read-only)
Git su `restyle-ui` pulito (`e3381a0`). Baseline `test_parser` **12/12**. `requests` non importato in nessun
modulo del progetto (solo transitivo di streamlit). Versioni `.venv`: streamlit 1.58.0, anthropic 0.113.0,
pandas 3.0.3, plotly 6.8.0, python-dotenv 1.2.2 (Python 3.12.10). I 6 problemi tutti confermati nel codice.

### FASE 2–7 — Esecuzione (uno alla volta, `test_parser` 12/12 dopo ciascuno)
- **FIX-1** `requirements.txt`: pin `==` alle versioni locali; rimosso `requests` (transitivo di streamlit →
  resta disponibile). ⚠️ da confermare sui log di deploy Cloud al prossimo build.
- **FIX-2** `ui/console.py`: `with st.spinner("Gigi sta analizzando…")` attorno all'analisi. → INC-009.
- **FIX-3** `ui/console.py`: input+bottone in `st.form` (submit solo su ANALIZZA/Enter, mai su blur);
  rimossa la guardia morta `console_last_input`. Trade-off dichiarato: con form l'input si legge al submit. → INC-009.
- **FIX-4** `ui/flags.py`+`ui/console.py`+`.env.example`: `PITWALL_ALLOW_LIVE` (default 0) + `live_allowed()`;
  demo-mode forzata sul deploy, toggle `disabled` con caption. Protegge la API key. → INC-010.
- **FIX-5** `agent.py` (**file protetto — autorizzato «ok procedi su agent.py»**): `timeout=30.0`
  (`call_claude` + `chat_with_gigi`), cascata 4→2 modelli, messaggio d'errore generico (dettagli solo su
  `log_incident`). → INC-009.
- **FIX-6 opzione B** `pages/login.py`: pre-seed `setup_tire_press_rl/rr = 25.7/25.5` da `dd.COLD_PRESSURES`
  su entrambi i rami di login → nel Setup il retrotreno parte "sotto finestra" (ambra), coerente con la storia
  sovrasterzo. **`modules/setup_params.py` INTATTO** (default 26.8 preservati): scelta B per non toccare la
  fonte di verità dei range.

### File protetti
Solo `agent.py` (FIX-5, con autorizzazione esplicita). `modules/setup_params.py`, parser, prompt di sistema,
logica gauge/fuel: **non toccati**. Nessun selettore CSS wildcard/interno introdotto.

### Verifica
`py_compile` OK su tutti i file toccati (incl. `pages/login.py`); import dei moduli toccati + dipendenze OK;
`test_parser` **12/12** dopo ogni fix. Nota: `import app`/`import pages.login` "a freddo" sollevano
`NoSessionContext` su `switch_page` — **pre-esistente** (verificato con `git stash`), è solo l'effetto di
importare l'entrypoint Streamlit fuori da una sessione, non un errore introdotto dai fix. Doc: INC-009 e
INC-010 aperti+risolti in `INCIDENTS.md`.

### Esito
6 file modificati (+70/−43 ca.): `requirements.txt`, `ui/console.py`, `ui/flags.py`, `.env.example`,
`agent.py`, `pages/login.py`. FIX-1…FIX-6 applicati; nessun fix saltato. Restano da confermare a schermo
dall'utente (`streamlit run app.py`): spinner, no-auto-submit su blur, toggle bloccato in deploy, pressioni
retrotreno ambra nel Setup.

**Decisione:** ☑ Mantenuto. **Commit/push NON eseguiti** — attendo «ok push» (regola git). Proposti 6 commit
(uno per fix) nel messaggio di chiusura FASE 8.
