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

*INCIDENTS compilato il 19/05/2026 — PitWall.AI MVP · agg. 02/07/2026 (INC-003…INC-006)*

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
