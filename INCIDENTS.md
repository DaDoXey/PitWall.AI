---

# INCIDENTS — PitWall.AI
**Progetto:** PitWall.AI — Virtual Race Engineer per ACC
**Corso:** AI Projects Development — ITS ICT Academy Roma
**Autore:** Ferlito Edoardo

---

## INC-001 — Risposta LLM Troncata

| Campo | Dettaglio |
|---|---|
| ID | INC-001 |
| Data rilevamento | 19/05/2026 |
| Severità | Alta |
| Stato | RISOLTO |
| File coinvolto | `core/ai_logic.py` |

### Descrizione
Durante il primo test dell'agente PitWall.AI con dati reali
(Lamborghini Huracán GT3 EVO2 @ Monza), il report generato dall'LLM
risultava troncato. La sezione "Coerenza col feedback pilota" e tutto
il contenuto successivo venivano tagliati a metà, rendendo il report
inutilizzabile.

### Causa
Il parametro `max_tokens=1500` nella chiamata API ad Anthropic era
insufficiente. Il report completo con 4 sezioni obbligatorie
(Diagnosi, Causa Meccanica, Correzione Setup, Note Aggiuntive)
supera sistematicamente 1500 token quando l'input è dettagliato.

### Impatto
- Output incompleto — sezioni obbligatorie mancanti nella risposta
- Il meccanismo di retry esistente non veniva attivato perché la
  sezione "## Diagnosi" era presente (solo il resto veniva tagliato)
- Impossibile usare il report per diagnosi reali

### Fix Applicato
Modifica di una singola riga in `core/ai_logic.py`:

```python
# PRIMA
max_tokens=1500

# DOPO
max_tokens=2500
```

### Verifica
Dopo il fix, report completo con tutte e 4 le sezioni su input
dettagliato. Nessuna troncatura rilevata nei test successivi.

### Lezione Appresa
Il valore di `max_tokens` deve essere stimato in base alla lunghezza
massima attesa dell'output strutturato, non in base a un valore
arbitrario. Per output con formato fisso a 4 sezioni obbligatorie,
2500 token è il minimo sicuro con Claude Sonnet.

---

## INC-002 — Confusione Pressioni a Freddo / a Caldo

| Campo | Dettaglio |
|---|---|
| ID | INC-002 |
| Data rilevamento | 19/05/2026 |
| Severità | Critica |
| Stato | RISOLTO |
| File coinvolti | `core/physics.py`, `components/tab_setup.py`, `prompts/system_prompt.txt` |

### Descrizione
Durante l'analisi dei dati di test (pressioni ~26.7 PSI), l'agente
classificava i valori come "ottimali" indipendentemente dal fatto che
si trattasse di pressioni misurate a freddo (in garage) o a caldo
(lette dal MFD in pista durante la sessione). Questo produceva diagnosi
fisicamente sbagliate.

### Causa
Il sistema utilizzava 26.7 PSI come unico riferimento target per le
pressioni, senza distinguere tra i due contesti fisici:
- **A freddo (garage):** target 26.7 PSI — range sicuro 26.0–27.0 PSI
- **A caldo (MFD in pista):** target 29.0 PSI — range sicuro 28.5–30.0 PSI

Le pressioni a caldo sono ~2.5–3.5 PSI superiori a quelle impostate a
freddo. Trattarle come equivalenti porta a classificare come "ottimale"
una pressione a caldo di 26.7 PSI, che in realtà è circa 2.3 PSI sotto
la finestra operativa GT3 — condizione che causa usura irregolare delle
spalle e grip instabile.

### Impatto
- Diagnosi fisicamente incorrette per qualsiasi input con pressioni a
  caldo
- Il pilota avrebbe ricevuto consigli errati: nessuna correzione su
  pneumatici strutturalmente sottopressionati
- Violazione del principio fondamentale del sistema: i consigli devono
  essere vincolati ai range fisici reali di ACC

### Fix Applicato

**1. `core/physics.py` — Nuove costanti e metodo:**

Aggiunte costanti per il contesto a caldo:
```python
HOT_PRESSURE_MIN    = 28.5  # PSI operativa a caldo — letta dal MFD
HOT_PRESSURE_MAX    = 30.0  # PSI operativa a caldo — limite superiore GT3
HOT_PRESSURE_TARGET = 29.0  # PSI target operativo a caldo GT3
```

Aggiunto metodo `classify_pressure_context(psi, context)` che usa
il target corretto in base al contesto ("cold" o "hot").

**2. `components/tab_setup.py` — Radio button contesto:**

Aggiunto selettore obbligatorio prima degli input PSI:
```python
pressure_context = st.radio(
    "I valori PSI che stai inserendo sono:",
    options=[
        "A freddo (impostati in garage prima della sessione)",
        "A caldo (letti dal MFD in pista — tasto N)",
    ],
    horizontal=True,
)
ctx = "cold" if "freddo" in pressure_context else "hot"
```

**3. `prompts/system_prompt.txt` — Blocco distinzione obbligatoria:**

Aggiunto nella sezione PARAMETRI DI SICUREZZA:
```
PRESSIONI — DISTINZIONE OBBLIGATORIA
A FREDDO (garage): Target 26.7 PSI | Range 26.0–27.0 PSI
A CALDO (MFD):     Target 29.0 PSI | Range 28.5–30.0 PSI
Se il pilota non specifica il contesto, chiedere PRIMA di procedere.
```

### Verifica
Test TC-08: input PSI 26.7 con contesto "a caldo" → sistema classifica
correttamente come "cold" (sotto finestra operativa). Nessuna
classificazione "ottimale" scorretta nei test successivi.

### Lezione Appresa
Qualsiasi valore fisico che ha significati diversi in contesti diversi
dev'essere disambiguato esplicitamente nell'interfaccia prima di essere
processato. Non si può delegare all'utente l'assunzione implicita del
contesto.

---

## INC-003 — Gigi "non risponde" sul deploy online (input bloccato)

| Campo | Dettaglio |
|---|---|
| ID | INC-003 |
| Data rilevamento | 30/06/2026 |
| Severità | Alta (demo d'esame) |
| Stato | RISOLTO (azione: ri-deploy) |
| File coinvolti | nessuno (disallineamento deploy ↔ `main`) |

### Descrizione
Sul deploy `pitwall-ai-dado.streamlit.app` la Engineer Console non restituiva
risposta e l'input risultava bloccato. Il prompt di lavoro v2 ipotizzava un
`disabled=True` o un flag "display-only" nel codice.

### Causa
**Falso allarme di codice.** Tracciando il percorso reale nel branch `main`
(`app.py` → `ui/router.py` → `ui/console.py`): l'input è `st.chat_input` (mai
disabilitato), demo-mode è ON di default e serve sempre la risposta-cache a 4
sezioni, con fallback su errore API. Il sintomo proveniva dal **deploy fermo a un
commit precedente al merge del restyle**: il sito live eseguiva codice vecchio.

### Impatto
- Rischio di mostrare in sede d'esame una console muta, pur avendo il fix in `main`.

### Fix Applicato
Nessuna modifica di codice. **Ri-deploy / reboot** dell'app su Streamlit Cloud per
allinearla a `origin/main`. Verifica post-deploy: input attivo, 4 sezioni rese in
demo-mode senza API.

### Lezione Appresa
Prima di diagnosticare un bug "nel codice", verificare che l'ambiente che mostra il
sintomo (deploy) sia allineato al commit che si sta leggendo. Un deploy stale
riproduce bug già risolti.

---

## INC-004 — Console percepita "statica/non funzionante" + telemetria disallineata

| Campo | Dettaglio |
|---|---|
| ID | INC-004 |
| Data rilevamento | 30/06/2026 (post-deploy verifica visiva) |
| Severità | Alta (demo d'esame) |
| Stato | RISOLTO |
| File coinvolti | `ui/console.py`, `ui/telemetry.py` |

### Descrizione
Alla verifica online: (1) la Engineer Console "non rispondeva" — qualunque input
restituiva sempre la stessa analisi (sovrasterzo), e l'input era un `st.chat_input`
ancorato in fondo alla pagina, poco visibile e percepito come scollegato → demo
"solo visiva". (2) In Telemetria le due colonne della prima riga (line chart vs
heatmap) erano di altezza diversa → grafici disallineati.

### Causa
1. In demo-mode `get_console_analysis()` ritornava **sempre** `DEMO_RESPONSE`,
   indipendentemente dall'input → nessuna reattività percepita. Inoltre
   `st.chat_input` si fissa in fondo al viewport, lontano dalle card.
2. `ui/telemetry.py`: line chart `height=320` accanto a heatmap `height=410`.

### Fix Applicato
1. **Risposte cache per scenario** (`ui/console.py`): 5 risposte a 4 sezioni
   (sottosterzo, sovrasterzo, carburante, gomme, freni) con router per parole
   chiave `_pick_demo_response()`; ogni chip / frase seleziona l'analisi pertinente
   → demo interattiva e offline. Input sostituito da **campo + bottone «⚙ ANALIZZA»**
   in linea, con guardia anti ri-trigger (`console_last_input`).
2. **Allineamento** line chart `height=320 → 410` (= heatmap).

Nessun file protetto toccato; la chiamata `agent.py` resta invariata (path live).

### Lezione Appresa
Una demo "blindata" su cache non deve sembrare finta: differenziare le risposte per
input la rende credibile. E l'elemento d'azione (Analizza) va reso visibile e
contiguo all'output, non delegato a un input ancorato fuori vista.

---

## INC-005 — Bug visivi grafico Telemetria (asse °C, legenda, clipping, allineamento)

| Campo | Dettaglio |
|---|---|
| ID | INC-005 |
| Data rilevamento | 02/07/2026 |
| Severità | Bassa (cosmetico) |
| Stato | RISOLTO |
| File coinvolto | `ui/telemetry.py` |

### Sintomo
Nella pagina Telemetria: (1) l'etichetta "°C" dell'asse Y appariva ruotata/storta;
(2) la legenda si sovrapponeva al titolo del grafico; (3) gauge pressioni e heatmap
risultavano tagliati al primo render (visibili solo scrollando); (4) i numeri sulla
silhouette gomma non erano allineati alle 4 ruote.

### Causa
1. Plotly ruota di 90° il titolo dell'asse Y (`title_text="°C"`).
2. Legenda ancorata in alto (`y=1.02`) nella stessa fascia del titolo.
3. Heatmap con altezza contenitore fissa (`.wrap height:392px`) dentro un iframe che
   poteva eccederla → clipping; gauge con margine superiore troppo stretto.
4. Riquadri gomma posizionati in modo non simmetrico rispetto al centro-scocca.

### Fix Applicato (solo presentazione — valori/soglie/finestra invariati)
1. Titolo asse Y rimosso; "°C" reso come annotazione orizzontale in alto a sx.
2. Legenda spostata sotto il grafico (`orientation=h, y=-0.15`) + margine inferiore.
3. Heatmap che riempie l'iframe (`.wrap`/`html,body` `height:100%`, svg in `.svgbox`
   flessibile); gauge `height 170→180`, `margin-top 8→18`.
4. Riquadri gomma riposizionati simmetrici (anteriori `y=52`, posteriori `y=166`).

**Nota:** i dati/finestra a caldo (28.5–30.0, gauge axis 27.0–30.5) sono quelli di
`main` e NON sono stati toccati: la fix è stata riconciliata nel merge `restyle-ui`→`main`.

---

## INC-006 — Bottone upload Setup troncato ("Uplo…") con icona sovrapposta

| Campo | Dettaglio |
|---|---|
| ID | INC-006 |
| Data rilevamento | 02/07/2026 |
| Severità | Bassa (cosmetico) |
| Stato | RISOLTO |
| File coinvolto | `assets/app.css` |

### Sintomo
Negli uploader CSV/screenshot del Setup, il bottone Browse/Upload appariva troncato
("Uplo…") con l'icona nativa di Streamlit sovrapposta al testo.

### Causa
La regola `[data-testid="stFileUploaderDropzone"] button { width:40px; overflow:hidden }`
— pensata per le icone-bottone della sidebar — era scritta **senza scope**, quindi
colpiva anche gli uploader dell'area principale (Setup), forzandone il bottone a 40px
e tagliandone il testo.

### Fix Applicato
Regola (e le due correlate su icona/hover) scopate a
`section[data-testid="stSidebar"] …`, così l'area principale usa il dropzone nativo
completo senza overlap. Nessun selettore vietato introdotto (data-testid già in uso).

### Verifiche correlate (non-incident)
- **Toggle "Input sessione":** default già OFF (`flags.py PITWALL_SHOW_INPUTS=0`,
  `setup_view.py setdefault`). Comportamento confermato, nessuna modifica.
- **Rosso RL/RR nel Setup:** intenzionale — evidenziazione dei parametri suggeriti da
  Gigi (`SUGGESTED_PARAMS = {tire_press_rl, tire_press_rr, preload}` → rosso, resto
  bianco). NON è una soglia fuori-range. Già presente su `main`.

---

## INC-007 — Logo sidebar ".AI" bianco invece che rosso brand

| Campo | Dettaglio |
|---|---|
| ID | INC-007 |
| Data rilevamento | 02/07/2026 |
| Severità | Bassa (cosmetico) |
| Stato | RISOLTO |
| File coinvolto | `ui/sidebar.py` |

### Sintomo
Nel logo "PITWALL.AI" in sidebar, la parte ".AI" appariva bianca/grigia invece del
rosso brand `#E8002D`, pur avendo lo stile inline `color:#E8002D`.

### Causa
Le regole globali della sidebar in `assets/app.css` usano `!important`
(`[data-testid="stSidebar"] * { color: var(--text) !important; }` e
`section[data-testid="stSidebar"] span:not([data-testid="stIconMaterial"]) { color:#999 !important; }`):
uno stile inline **senza** `!important` perde contro un `!important` del foglio esterno,
quindi il rosso del ".AI" veniva sovrascritto.

### Fix Applicato
Aggiunto `!important` allo stile inline del ".AI" (`color:#E8002D !important`): un
`!important` inline batte quello di un foglio esterno. Fix di 1 riga, nessun selettore
Streamlit-interno introdotto, nessuna regola CSS globale modificata.

---

## INC-008 — Telemetria: unità °C incoerente, tooltip su legenda, heatmap disallineata

| Campo | Dettaglio |
|---|---|
| ID | INC-008 |
| Data rilevamento | 03/07/2026 |
| Severità | Bassa (cosmetico) |
| Stato | RISOLTO |
| File coinvolto | `ui/telemetry.py` |

### Sintomo
Round di rifinitura successivo a INC-005 (stessa pagina). Tre residui: (1) i tick
dell'asse Y del line chart mostravano solo `°` (`88°`, `95°`) mentre annotazione
soglia e tooltip usavano `°C`; (2) col mouse su un punto (es. giro 6) il box tooltip
`x unified` si sovrapponeva alla legenda posta in alto; (3) nella heatmap i valori
non risultavano ancorati alla sagoma della gomma (posteriori "alti" rispetto
all'assale reale).

### Causa
1. `update_yaxes(ticksuffix="°")` invece di `"°C"` → unità disallineata tra tick,
   annotazione e tooltip.
2. Legenda ancorata al bordo superiore del plot (`y=1.0`), nella stessa fascia dove
   Plotly rende il box `hovermode="x unified"`.
3. I 4 riquadri-gomma erano posizionati con coordinate assolute (`38/162`, `52/166`)
   slegate dal `<path>` della scocca: nessun ancoraggio condiviso alle ruote.

### Fix Applicato (solo presentazione — valori/soglie/finestra invariati)
1. `ticksuffix="°C"` → unità uniforme su tick, annotazione e tooltip.
2. Legenda spostata SOTTO il grafico (`orientation=h, y=-0.20`, centrata); `t` 30→16,
   `b` 48→88, `title_standoff=6` su "Giro" → tooltip (in alto) e legenda (in basso)
   non si sovrappongono mai.
3. Riquadri/valori heatmap **ancorati alla geometria della scocca**: costanti
   `_BODY_LEFT/RIGHT_X`, `_FRONT/REAR_AXLE_Y`, `_WHEEL_W/H`; builder `_heat_corner_svg`
   riscritto in modalità centro-ruota. Posteriori riportate sulla linea-assale reale.

### Espansione contestuale (FASE 3, non-incident — a rischio zero, colonne CSV esistenti)
Aggiunte alla Telemetria, nessun file protetto toccato: **tabella giro-per-giro
ordinabile**; **proiezione giri rimanenti** (`project_remaining_laps`, sola lettura,
fuori dalla fuel-logic protetta); **feed cross-check** (incongruenze deterministiche +
riuso della diagnosi di Gigi da `session_state`, zero chiamate LLM); **toggle °C/°F**
e **raw/smoothed** sul line chart. Nuova serie coerente `HOT_PRESS_SERIES` in
`ui/demo_data.py` (ultimo giro == valori dei gauge, garantito da `assert`).

### Lezione Appresa
Le rifiniture cosmetiche vanno ancorate alla geometria sorgente (la sagoma), non a
coordinate letterali: così restano corrette anche se il layout cambia. E un box
tooltip e una legenda non devono mai condividere la stessa fascia del grafico.

---

## INC-009 — Engineer Console: percezione freeze + auto-submit involontario + cascata API senza timeout

| Campo | Dettaglio |
|---|---|
| ID | INC-009 |
| Data rilevamento | 06/07/2026 (audit pre-esame) |
| Severità | Alta (demo d'esame) |
| Stato | RISOLTO |
| File coinvolti | `ui/console.py`, `agent.py` |

### Sintomo
Con demo-mode OFF (LLM reale) la Engineer Console poteva "congelarsi": nessun
feedback durante l'analisi (spinner assente, header Streamlit "Running…" nascosto
dal CSS), attese lunghissime, e talvolta chiamate API partite senza che l'utente
avesse premuto ANALIZZA (bastava togliere il focus dal campo di testo).

### Causa
1. **Nessuno spinner** attorno a `get_console_analysis()` (`ui/console.py`): la
   chiamata sincrona non dava alcun segnale di attività.
2. **Auto-submit su blur** (`ui/console.py`): la condizione
   `(analyze or typed.strip() != last_input)` faceva partire l'analisi a ogni
   rerun in cui il testo differiva dall'ultimo — inclusi i rerun da blur (es.
   click sul toggle demo-mode) → chiamate LLM involontarie.
3. **Cascata API senza timeout** (`agent.py`): client Anthropic senza `timeout`
   (default fino a ~10 min/chiamata) + cascata di 4 modelli × 2 tentativi = fino a
   8 chiamate sincrone → radice del freeze. Il messaggio d'errore esponeva inoltre
   i dettagli tecnici all'utente finale.

### Fix Applicato
1. `with st.spinner("Gigi sta analizzando…")` attorno all'analisi.
2. Input+bottone dentro `st.form("console_form")`: l'analisi parte SOLO al submit
   (click ANALIZZA o Enter nel campo); il blur non fa submit. Rimossa la guardia
   ora inutile `console_last_input`. Chip e flusso demo invariati.
3. `agent.py` (file protetto, modifica autorizzata): `timeout=30.0` sul client
   (`call_claude` e `chat_with_gigi`); `models_to_try` ridotto a 2
   (`CLAUDE_MODEL` + `claude-sonnet-4-6`); messaggio d'errore generico
   ("⚠️ Servizio temporaneamente non disponibile. Riprova tra poco."), i dettagli
   restano solo su `log_incident`.

### Verifica
`py_compile` + import OK; `test_parser` 12/12; demo-mode continua a servire la
cache offline senza toccare `agent.py`.

### Lezione Appresa
Ogni operazione sincrona che può durare va accompagnata da feedback visibile e da
un timeout esplicito; un input libero non deve mai auto-inviarsi su un evento
collaterale (blur) — `st.form` rende il submit esplicito.

---

## INC-010 — API key esposta sul deploy pubblico (toggle demo-mode disattivabile da chiunque)

| Campo | Dettaglio |
|---|---|
| ID | INC-010 |
| Data rilevamento | 06/07/2026 (audit pre-esame) |
| Severità | Alta (sicurezza / costo) |
| Stato | RISOLTO |
| File coinvolti | `ui/flags.py`, `ui/console.py`, `.env.example` |

### Sintomo
Sul deploy pubblico (`pitwall-ai-dado.streamlit.app`) chiunque poteva spegnere il
toggle "Demo-mode" e far partire chiamate LLM reali con la MIA `ANTHROPIC_API_KEY`
(nessun rate limiting; fino a più chiamate per prompt) → rischio consumo credito.

### Causa
`flags.demo_mode()` era liberamente disattivabile dal toggle in `ui/console.py`,
senza distinzione tra ambiente locale/esame e deploy pubblico.

### Fix Applicato
Nuova env var `PITWALL_ALLOW_LIVE` (default `0`) + helper `flags.live_allowed()`.
Quando la live non è consentita, `demo_mode()` ritorna SEMPRE `True` (cache forzata)
e il toggle in `ui/console.py` è reso `disabled` con caption "Live-mode disabilitato
in deploy". In locale / demo d'esame si imposta `PITWALL_ALLOW_LIVE=1` per riabilitare
il toggle e la LLM reale. `.env.example` aggiornato con la variabile documentata.

### Verifica
Smoke: default → `live_allowed=False`, `demo_mode()=True`; con `=1` → `live_allowed=True`.
`py_compile` + import OK; `test_parser` 12/12.

### Lezione Appresa
Le risorse a pagamento (API key) vanno protette per default sull'ambiente pubblico:
il comportamento "sicuro" (demo forzata) è il default, quello "aperto" (LLM reale)
è un'attivazione esplicita via env var, mai lasciata alla UI accessibile a tutti.

---

## INC-011 — Engineer Console demo: refuso numerico pressioni + routing keyword errato

| Campo | Dettaglio |
|---|---|
| ID | INC-011 |
| Data rilevamento | 06/07/2026 (audit) · risolto 07/07/2026 |
| Severità | Media (demo d'esame — output errato ma non blocca) |
| Stato | RISOLTO |
| File coinvolto | `ui/console.py` |

### Sintomo
1. Nella cache demo (`DEMO_RESPONSE`, `DEMO_TYRES`) la Correzione Setup diceva
   «pressioni posteriori **+1.0 psi · 25.5 → 26.5**», citando un solo valore mentre a
   freddo le due posteriori sono diverse (RL 25.7, RR 25.5): il numero era incoerente
   con i dati demo di `ui/demo_data.py`.
2. Una domanda sulle temperature contenente la parola «anteriore» (es. «temperatura
   anteriore alta») veniva instradata alla risposta **sottosterzo** invece che a quella
   **gomme**.

### Causa
1. Testo scritto sul solo valore RR, senza distinguere RL/RR (refuso di stesura).
2. In `_DEMO_ROUTES` la route sottosterzo includeva la keyword generica `"anteriore"`,
   che intercettava anche input su temperature/gomme (la route sottosterzo è la prima
   della lista → vinceva sul match successivo `"temperatur"`).

### Fix Applicato (solo cache demo — struttura a 4 sezioni invariata)
1. Riformulato in modo coerente con entrambe le gomme: «**+1.0 psi · RL 25.7 → 26.7 ·
   RR 25.5 → 26.5**» (nuovi valori dentro la finestra a freddo 26.0–27.0).
2. Rimossa la keyword `"anteriore"` dalla route sottosterzo (restano `sottosterz`,
   `sotto sterz`, `non gira`, `va largo`); nessun riordino delle route. Smoke test:
   «temperatura anteriore alta» → risposta **gomme** ✅; i 4 chip instradano corretti.

### Lezione Appresa
I dati citati nelle risposte cache vanno derivati dalla sorgente demo (mai valori
"a memoria"); e le keyword di routing devono essere abbastanza specifiche da non
rubare il match ad altri scenari — una parola generica come «anteriore» appartiene a
più contesti.

---

## INC-012 — Bug latenti chiusi in pulizia HOTFIX-3 (auth, classificazione demo, vision)

| Campo | Dettaglio |
|---|---|
| ID | INC-012 |
| Data rilevamento | 06/07/2026 (audit) · risolto 07/07/2026 |
| Severità | Bassa (latenti: non osservati in demo, chiusi proattivamente) |
| Stato | RISOLTO |
| File coinvolti | `db_auth.py`, `ui/console.py`, `modules/vision_parser.py`, `ui/setup_view.py` |

### Sintomo (potenziale)
1. **Auth:** `create_or_update_user` usava `INSERT OR REPLACE` → ad ogni login il
   `created_at` veniva resettato; inoltre il Custom Login genera un `user_id` nuovo
   ad ogni accesso e, con la stessa email, un upsert su `user_id` avrebbe potuto
   violare il vincolo `UNIQUE(email)` (rischio `IntegrityError`). Timestamp naive
   (senza timezone), non allineati alla convenzione UTC di `agent.py`.
2. **Console:** `_is_demo_prompt` faceva match bidirezionale (`norm in demo_norm`) →
   input brevissimi ("auto", "dietro", perfino 1 lettera) classificati come prompt
   demo anche con demo-mode OFF.
3. **Vision (dietro flag OFF):** `parse_setup_from_image` inviava gli upload con
   `media_type="image/png"` fisso → un JPEG dichiarato PNG poteva essere rifiutato.

### Causa
Codice scritto per il percorso "felice" senza coprire i casi limite; in demo-mode
(default) nessuno di questi percorsi è attivo, quindi i bug erano latenti.

### Fix Applicato
1. `db_auth.create_or_update_user`: upsert per **email** con due query (lookup →
   UPDATE che preserva `user_id`/`created_at`, altrimenti INSERT); timestamp
   `datetime.now(timezone.utc)`. Version-independent (nessun `ON CONFLICT`).
   Verificato su DB temporaneo: Demo 2× → `created_at` invariato, `last_login`
   aggiornato; Custom stessa email 2× → nessun crash.
2. `ui/console._is_demo_prompt`: tenuto solo il verso utile `demo_norm in norm`
   (copre l'uguaglianza esatta). Demo-mode invariato (routing serve comunque la cache).
3. `modules/vision_parser.parse_setup_from_image(..., media_type=None)` + passaggio
   di `media_type=img.type` da `ui/setup_view._screenshot_upload`. Feature resta OFF.

### Lezione Appresa
Anche i percorsi non attivi in demo vanno chiusi quando mappati: identità utente su
chiave naturale (email), timestamp timezone-aware, classificatori abbastanza stretti
da non catturare input generici, e MIME dell'upload propagato invece che assunto.

---

*INCIDENTS compilato il 19/05/2026 — PitWall.AI MVP · agg. 07/07/2026 (INC-003…INC-012)*

---
| 2026-06-04 08:27 UTC | Test incident log |
| 2026-06-04 10:39 UTC | Errore chiamata Claude: Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-sonnet-4-20250514'}, 'request_id': 'req_011Cbi5PETMBEDBNQcSih764'} |
| 2026-06-04 10:39 UTC | Tutti i modelli LLM hanno fallito — output di errore restituito all'utente. |
| 2026-06-04 10:39 UTC | Errore salvataggio sessione DB: table sessions has no column named session_id |
| 2026-06-04 10:39 UTC | Errore chiamata Claude: Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-sonnet-4-20250514'}, 'request_id': 'req_011Cbi5PdRUWnhr7493yh77R'} |
| 2026-06-04 10:39 UTC | Tutti i modelli LLM hanno fallito — output di errore restituito all'utente. |
| 2026-06-04 10:39 UTC | Errore salvataggio sessione DB: table sessions has no column named session_id |
| 2026-06-04 10:44 UTC | Errore chiamata Claude: Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-sonnet-4-20250514'}, 'request_id': 'req_011Cbi5jbwj9cKaRyzVB9aqk'} |
| 2026-06-04 10:44 UTC | Tutti i modelli LLM hanno fallito — output di errore restituito all'utente. |
| 2026-06-04 10:44 UTC | Errore salvataggio sessione DB: table sessions has no column named session_id |
| 2026-06-04 10:46 UTC | Errore salvataggio sessione DB: table sessions has no column named session_id |
