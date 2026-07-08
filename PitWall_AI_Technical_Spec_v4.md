# PitWall.AI — Specifica Tecnica v4 (Post-Building, Consolidata)

> ⚠️ **Documento storico — stack LLM superato.** Questa specifica descrive uno stack
> con OpenAI/GPT-4o mini e il pacchetto `openai`, **rimosso dal codice**: PitWall usa oggi
> **solo Anthropic** (default `claude-haiku-4-5`, fallback `claude-sonnet-4-6`). Architettura e
> flussi restano validi come riferimento; per lo stack LLM attuale vedi `README.md` e `agent.py`.

**Repository:** https://github.com/DaDoXey/PitWall.AI.git

| Campo | Valore |
|---|---|
| Versione | 4.0 |
| Data | 19/05/2026 |
| Stato | CONGELATA — MVP Building Completato |
| Autore | Ferlito Edoardo |
| Sostituisce | v3 (RC, 10/05/2026) |

> **Nota di versioning:** La v4 è il documento post-building che recepisce
> i bug fix documentati in INCIDENTS (INC-001, INC-002), aggiorna lo stack
> con le versioni effettivamente utilizzate, documenta i costi API Claude e
> formalizza la struttura UI espansa rispetto alla v3. Le specifiche v1, v2
> e v3 sono da considerarsi obsolete.

---

## 0. Sintesi del Progetto

| Campo | Dettaglio |
|---|---|
| Nome | PitWall.AI |
| Descrizione | Virtual Race Engineer che analizza feedback del pilota e dati di sessione per ottimizzare setup e strategia su Assetto Corsa Competizione. |
| Tipo di sistema | Assistente operativo basato su LLM (Single-Agent, Stateless — MVP). |
| Target | Sim-racer amatoriali e competitivi su ACC privi di competenze avanzate di ingegneria del veicolo. |
| Output principale | Report Markdown strutturato: Diagnosi / Causa Meccanica / Correzione Setup / Note Aggiuntive. |
| Interfaccia MVP | Streamlit (web app locale). |
| Database | SQLite locale (file `database/pitwall.db`, creato automaticamente). |

---

## 1. Obiettivo del Sistema

Il sistema agisce come filtro critico tra il feedback soggettivo del pilota
e i limiti fisici del simulatore ACC. Non si limita a rispondere in linguaggio
naturale: deve identificare la causa meccanica del problema, validarla contro
i dati oggettivi di sessione (ove presenti), e produrre una modifica
incrementale, numericamente precisa e vincolata ai range reali del simulatore.

**Principio guida:** modifiche incrementali sempre — mai setup completi da zero.

**Principio architetturale:** la logica fisica non tocca mai l'LLM.
- `core/physics.py` → calcoli deterministici (nessuna chiamata API)
- `core/ai_logic.py` → solo commento qualitativo, riceve dati già processati
- `app.py` → solo orchestrazione UI, nessuna logica

---

## 2. Requisiti Funzionali (con Criteri di Accettazione)

| ID | Requisito | Criterio di Accettazione | Stato MVP |
|---|---|---|---|
| RF-01 | Il sistema deve accettare feedback in linguaggio naturale. | L'input viene processato e produce una risposta strutturata nelle 4 sezioni definite. | ✅ Implementato |
| RF-02 | Il sistema deve parsare file CSV di sessione ACC. | I campi `temperature`, `pressioni`, `consumi` vengono estratti correttamente dallo schema definito. | ✅ Implementato |
| RF-03 | Il sistema deve restituire consigli con valori numerici nei range ACC. | Nessun valore suggerito è fuori dai range dichiarati nel System Prompt. | ✅ Implementato |
| RF-04 | Il sistema deve calcolare la strategia carburante. | Dato `consumo_per_giro` e `durata_gara`, il calcolo è verificabile a mano con la formula esplicita. | ✅ Implementato |
| RF-05 | Il sistema deve segnalare incongruenze tra feedback e dati CSV. | Se il pilota dichiara "troppo caldo" ma le temperature CSV sono basse, il sistema lo segnala esplicitamente nella sezione Diagnosi. | ✅ Implementato |
| RF-06 | Il sistema deve chiedere chiarimenti se l'input è troppo vago. | Input `"l'auto va male"` → risposta `"Puoi specificare in quale fase della curva?"` prima di procedere. | ✅ Implementato |
| RF-07 | Il sistema deve distinguere pressioni a freddo da pressioni a caldo. | Il pilota seleziona il contesto (freddo/caldo) tramite radio button. Il sistema usa target diversi per i due contesti. | ✅ Implementato (aggiunto in v4 — fix INC-002) |

### Confronto v3→v4

| Requisito | v3 | v4 |
|---|---|---|
| RF-01 a RF-06 | Presenti e verificabili | Confermati — nessuna modifica |
| RF-07 | Assente — causa bug INC-002 | Aggiunto post-building con fix completo |
| max_tokens | 1500 — insufficiente | 2500 — fix INC-001 |
| Struttura UI | Componenti base definiti | Struttura componenti espansa (cartella `components/`) |
| Database | SQLite menzionato | SQLite confermato locale, schema aggiornato |

---

## 3. Architettura del Sistema

### 3.1 Overview (Single-Agent, Stateless)

```
[Pilota]
    │
    ├─ Feedback testuale (linguaggio naturale)
    ├─ Selezione contesto pressioni (freddo / caldo)  ← NUOVO v4
    └─ File CSV sessione (opzionale)
              │
              ▼
    ┌─────────────────────┐
    │   INTERFACCIA       │  ← Streamlit + Custom CSS
    │   (Input Layer)     │  ← components/ (header, sidebar, tabs)
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │   PHYSICS ENGINE    │  ← core/physics.py
    │   (Deterministico)  │  ← Validazione + calcoli (NO LLM)
    └─────────┬───────────┘
              │  Risultati validati + dati strutturati
              ▼
    ┌─────────────────────┐
    │   PARSING ENGINE    │  ← parser/csv_parser.py
    │                     │  ← pandas — solo se CSV presente
    └─────────┬───────────┘
              │  Contesto strutturato (JSON interno)
              ▼
    ┌─────────────────────┐
    │   LLM AGENT         │  ← Anthropic Claude Sonnet 4
    │   (Core Engine)     │  ← System Prompt v3 (prompts/system_prompt.txt)
    │   Chain-of-Thought  │  ← max_tokens=2500
    └─────────┬───────────┘
              │  Output Markdown (4 sezioni)
              ▼
    ┌─────────────────────┐
    │   OUTPUT LAYER      │  ← components/engineer_report.py
    │                     │  ← st.markdown() + validazione sezioni
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │   DATABASE LAYER    │  ← database/manager.py
    │   (SQLite locale)   │  ← Storico sessioni
    └─────────────────────┘
```

### 3.2 Scelta del Modello LLM

| Modello | Stringa API | Uso | Costo Stimato |
|---|---|---|---|
| Claude Sonnet 4 | `claude-sonnet-4-20250514` | Produzione / Demo | $0.02–$0.04 per chiamata |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | Sviluppo / Test iterativi | $0.001–$0.003 per chiamata |

> **Nota:** Il modello è configurabile tramite variabile `.env` (`LLM_MODEL`).
> Per lo sviluppo si raccomanda Haiku per contenere i costi; per le demo
> finali e la documentazione PROMPT_LOG si usa Sonnet.

**Motivazione Sonnet vs. modelli mini:** la catena di ragionamento
obbligatoria (Diagnosi → Causa → Correzione) richiede un modello con
capacità di ragionamento strutturato superiore. Haiku è sufficiente per
test funzionali; Sonnet garantisce output di qualità superiore sui
vincoli tecnici di dominio ACC.

### 3.3 Gestione Contesto (Stateless per MVP)

Per l'MVP, ogni chiamata API è indipendente. Il contesto di sessione
(feedback + CSV parsato + risultati physics) viene inviato interamente
in ogni richiesta. La gestione multi-turno è esclusa dallo scope MVP
(roadmap v1.2).

---

## 4. Logica di Elaborazione

### 4.1 Pipeline di Elaborazione Input

```
Input testuale → Validazione lunghezza/contenuto
                      │
                      ├─ Input vuoto → blocco pre-chiamata
                      └─ Input valido ─────────────────────┐
                                                            │
Selezione contesto PSI → "cold" | "hot"                   │
    (radio button UI)                                       │
                      │                                     │
                      └───────────────────────────────────┐ │
                                                          │ │
Input CSV (opz.) → Validazione schema                    │ │
                      │                                  │ │
                      ├─ Schema errato → messaggio errore│ │
                      └─ Schema valido → estrazione campi│ │
                                            │            │ │
                                            └────────────┘ │
                                                    │       │
                                            Cross-check coerenza
                                            feedback ↔ dati CSV
                                                    │
                                         physics.classify_pressure_context()
                                         (usa target corretto freddo/caldo)
                                                    │
                                            Costruzione contesto JSON
                                                    │
                                            Chiamata LLM con System Prompt
                                            (max_tokens=2500)
```

### 4.2 Formula Calcolo Carburante (Deterministica — NO LLM)

```
carburante_necessario = ceil(durata_gara_min / tempo_giro_min) × consumo_per_giro_L
carico_consigliato    = carburante_necessario × (1 + margine_sicurezza)

dove:
  margine_sicurezza  = 0.05   (5% — configurabile)
  durata_gara_min    = input pilota
  tempo_giro_min     = input pilota (formato mm:ss → float)
  consumo_per_giro_L = input pilota o media colonna fuel_cons da CSV
```

Implementata come funzione Python deterministica in `core/physics.py`.
Non delegata all'LLM.

### 4.3 Logica di Cross-Check CSV ↔ Feedback

| Condizione Rilevata | Comportamento Agente |
|---|---|
| Pilota: "troppo caldo" — CSV: temp < 85°C | Segnalare incongruenza in sezione Diagnosi, chiedere conferma scenario |
| Pilota: "pressioni ok" — CSV: press > 28.0 psi | Correggere con dati oggettivi, notare discrepanza percettiva |
| Pilota: "consumo alto" — CSV: `fuel_cons` nella norma | Diagnosi su stile di guida, non su setup meccanico |
| CSV assente | Procedere su solo feedback testuale, segnalare limitazione diagnostica |

### 4.4 Logica Pressioni Freddo/Caldo (NUOVO v4)

| Contesto | Target PSI | Range Sicuro | Sorgente Valore |
|---|---|---|---|
| A freddo (garage) | 26.7 PSI | 26.0 – 27.0 PSI | Impostazione garage prima della sessione |
| A caldo (in pista) | 29.0 PSI | 28.5 – 30.0 PSI | Lettura MFD in pista (tasto N) |

Compensazione termica: **0.1 PSI per ogni 1°C** di variazione.
Le pressioni a caldo sono tipicamente 2.5–3.5 PSI superiori a quelle
impostate a freddo.

---

## 5. Schema Dati CSV

### 5.1 Schema Standard ACC (MVP)

```csv
lap,fuel_cons,tire_press_fl,tire_press_fr,tire_press_rl,tire_press_rr,tire_temp_fl,tire_temp_fr,tire_temp_rl,tire_temp_rr
1,3.2,26.5,26.4,26.8,26.7,88,90,95,102
2,3.1,26.6,26.5,26.9,26.8,90,91,97,104
```

| Colonna | Tipo | Unità | Obbligatoria |
|---|---|---|---|
| `lap` | int | — | Sì |
| `fuel_cons` | float | Litri/giro | Sì |
| `tire_press_fl` | float | PSI (freddo) | No |
| `tire_press_fr` | float | PSI (freddo) | No |
| `tire_press_rl` | float | PSI (freddo) | No |
| `tire_press_rr` | float | PSI (freddo) | No |
| `tire_temp_fl` | float | °C (core) | No |
| `tire_temp_fr` | float | °C (core) | No |
| `tire_temp_rl` | float | °C (core) | No |
| `tire_temp_rr` | float | °C (core) | No |

> **Nota tecnica:** ACC non esporta CSV nativo. Il file deve essere prodotto
> manualmente o tramite tool di terze parti (es. CrewChief, ACC Session
> Exporter). I valori di pressione nello schema sono pressioni a freddo.

### 5.2 Pressioni Operative a Caldo (Riferimento)

Le pressioni nel CSV rappresentano i valori impostati a freddo. Le pressioni
operative a caldo (target diagnostico reale) sono tipicamente 2.5–3.5 PSI
superiori. Il sistema comunica questa distinzione al pilota e usa target
separati in base al contesto selezionato (RF-07).

---

## 6. System Prompt (v3 — in uso)

Il system prompt è caricato da `prompts/system_prompt.txt` a runtime da
`core/ai_logic.py`. Non è hardcodato nel codice.

**Sezioni principali del prompt:**
- Ruolo: Senior Race Engineer virtuale ACC
- Metodo di ragionamento obbligatorio: Passo 1 Diagnosi → Passo 2 Causa
  Meccanica → Passo 3 Correzione
- Parametri di sicurezza ACC GT3 con range numerici vincolati
- Formato output obbligatorio: 4 sezioni Markdown
- Blocco PRESSIONI — DISTINZIONE OBBLIGATORIA (aggiunto post INC-002)
- Utilizzo dati CSV
- Vincoli operativi DO / DO NOT

**Parametri di sicurezza ACC — GT3 (estratto):**

```
Pressione gomme (freddo):     26.0 – 27.0 psi  (target: 26.7)
Pressione gomme (caldo):      28.5 – 30.0 psi  (target: 29.0)
Camber anteriore:            -2.5° a -4.0°
Camber posteriore:           -1.5° a -3.0°
Barre antirollio:             0 – 10 (range relativo ACC)
Precarico differenziale:      20 – 100 Nm
TC1 (Traction Control):       0 – 11
TC2 (TC Cut):                 0 – 11
ABS:                          0 – 11
```

---

## 7. Interfaccia Utente — Struttura Streamlit

### 7.1 Struttura Componenti (v4)

```
app.py                          ← Orchestratore (solo chiamate a components/*)
│
├── assets/
│   ├── style.css               ← Design system completo (dark theme F1)
│   └── css_loader.py           ← inject_css() — iniezione CSS in Streamlit
│
└── components/
    ├── header.py               ← render_header(db_status)
    ├── sidebar.py              ← render_sidebar() → dict
    ├── tire_display.py         ← render_tire_grid(pressures, status)
    ├── tab_setup.py            ← render_tab_setup(sidebar_data)
    ├── tab_fuel.py             ← render_tab_fuel()
    ├── tab_history.py          ← render_tab_history()
    ├── engineer_report.py      ← render_engineer_report(response, physics_data)
    └── temp_chart.py           ← render_temperature_chart(csv_data)
```

### 7.2 Design System

| Token | Valore | Uso |
|---|---|---|
| `--bg-primary` | `#0D0D0D` | Sfondo principale |
| `--bg-secondary` | `#1A1A1A` | Card e panel |
| `--bg-tertiary` | `#242424` | Input fields |
| `--accent-green` | `#00FF87` | In Range / ottimale |
| `--accent-red` | `#FF3131` | Overheating / critico |
| `--accent-blue` | `#00A3FF` | Cold / freddo |
| `--accent-yellow` | `#FFD600` | Warning / borderline |
| `--text-primary` | `#F0F0F0` | Testo principale |
| `--text-secondary` | `#8A8A8A` | Label e testo secondario |
| Font | Inter → Roboto → system-ui | Stack completo |

### 7.3 Flusso UI

```
[Sidebar]
  Selectbox Auto + Tracciato + Condizioni
  Temp. Ambiente + Temp. Pista

[Tab 1 — Analisi Setup]
  Radio "PSI a freddo / a caldo"    ← NUOVO v4 (fix INC-002)
  Input pressioni FL/FR/RL/RR (step 0.1)
  Input temperature gomme FL/FR/RL/RR
  Visualizzatore gomme 2x2 (colori dinamici)
  Text area feedback pilota
  File uploader CSV (opzionale)
  Expander parametri avanzati (camber, brake bias, diff, TC, ABS)
  Button "Analizza" → spinner → report

[Tab 2 — Strategia Carburante]
  Input durata gara + tempo giro + consumo/giro
  Calcolo deterministico via physics.py (NO LLM)
  Output: giri stimati + carburante base + carico +5%

[Tab 3 — Storico Sessioni]
  Filtri auto/tracciato + refresh
  Dataframe ultime sessioni (cache ttl=30s)
  Expander dettaglio sessione selezionata
```

---

## 8. Gestione degli Errori

| Scenario | Comportamento | Messaggio Utente |
|---|---|---|
| CSV formato errato / schema non valido | Blocco parsing, no chiamata LLM | "Il file non è un CSV valido di ACC. Verifica il formato." |
| Input testuale vuoto | Blocco pre-chiamata | "Descrivi il problema che stai riscontrando in pista." |
| Contesto pressioni non selezionato | Blocco pre-chiamata | "Specifica se i valori PSI sono a freddo o a caldo." |
| API timeout / errore di rete | Retry 1 volta, poi fallback | "Servizio temporaneamente non disponibile." |
| Output LLM privo della sezione "Diagnosi" | Retry 1 volta | Se fallisce: "Errore nella generazione del consiglio." |
| Pilota chiede parametro non regolabile in ACC | Rifiuto nel prompt, risposta educativa | "Questo parametro non è regolabile in ACC." |
| Input vago senza contesto (es. "l'auto va male") | Richiesta chiarimento | "Puoi specificare in quale fase della curva si manifesta il problema?" |
| Formato mm:ss tempo giro non valido (Tab carburante) | st.warning con esempio | "Formato non valido. Esempio corretto: 1:52" |

---

## 9. Stack Tecnologico

```
Linguaggio:          Python 3.10+
Interfaccia:         Streamlit
CSS custom:          assets/style.css (dark theme, iniettato via st.markdown)
LLM (produzione):    Anthropic Claude Sonnet 4 — claude-sonnet-4-20250514
LLM (sviluppo):      Anthropic Claude Haiku 4.5 — claude-haiku-4-5-20251001
LLM (fallback):      OpenAI GPT-4o mini (via API)
Grafici:             Plotly Express
Parsing dati:        pandas
Database:            SQLite (sqlite3 — built-in Python, no ORM)
Gestione env:        python-dotenv (.env per API keys)
Versionamento:       Git / GitHub
Formatter:           Black (max 88 caratteri)
Test:                pytest
```

**Struttura Repository (v4):**

```
PitWall.AI/
├── app.py                        # Entry point Streamlit (orchestratore)
├── core/
│   ├── __init__.py
│   ├── physics.py                # ACCPhysicsEngine — calcoli deterministici
│   └── ai_logic.py               # PitWallAgent — client LLM
├── parser/
│   ├── __init__.py
│   └── csv_parser.py             # Parsing e validazione CSV sessione ACC
├── database/
│   ├── __init__.py
│   ├── manager.py                # SQLite — storico sessioni
│   └── pitwall.db                # Database locale (in .gitignore)
├── components/
│   ├── header.py
│   ├── sidebar.py
│   ├── tire_display.py
│   ├── tab_setup.py
│   ├── tab_fuel.py
│   ├── tab_history.py
│   ├── engineer_report.py
│   └── temp_chart.py
├── assets/
│   ├── style.css
│   └── css_loader.py
├── prompts/
│   └── system_prompt.txt         # System Prompt v3
├── data/
│   └── test_session.csv          # CSV di test
├── tests/
│   ├── test_physics.py
│   └── test_parser.py
├── .github/
│   └── copilot-instructions.md   # Regole permanenti per VS Code Copilot
├── .env                          # API keys (NON versionato)
├── .env.example
├── requirements.txt
└── README.md
```

**Dipendenze (`requirements.txt`):**

```
streamlit>=1.35.0
anthropic>=0.28.0
openai>=1.30.0
python-dotenv>=1.0.0
pandas>=2.0.0
plotly>=5.20.0
pytest>=8.0.0
```

---

## 10. Costi API Claude (Documentazione)

| Scenario | Modello | max_tokens | Costo Stimato per Chiamata |
|---|---|---|---|
| Analisi setup completa (produzione) | claude-sonnet-4-20250514 | 2500 | $0.02 – $0.04 |
| Test funzionale (sviluppo) | claude-haiku-4-5-20251001 | 2500 | $0.001 – $0.003 |
| Test iterativo prompt | claude-haiku-4-5-20251001 | 1000 | < $0.001 |

**Strategia di contenimento costi durante lo sviluppo:**

1. Usare `claude-haiku-4-5-20251001` per tutti i test iterativi durante
   il building (configurabile via variabile `LLM_MODEL` nel file `.env`).
2. Passare a `claude-sonnet-4-20250514` solo per le demo finali e per
   documentare i risultati nel PROMPT_LOG.
3. Per l'iterazione sul system prompt, usare Claude.ai (piano gratuito)
   prima di testare via API.
4. max_tokens=2500 è il minimo sicuro per l'output completo a 4 sezioni — impostato dopo fix INC-001 (era 1500).
   Non aumentare ulteriormente senza necessità.

**Costo totale stimato MVP (sviluppo + test):** < $2.00

---

## 11. Piano di Test (Casi di Accettazione)

| ID | Input | Risultato Atteso | Tipo | Stato |
|---|---|---|---|---|
| TC-01 | "Ho troppo sottosterzo a centro curva sulla BMW M4 GT3 a Monza" (no CSV) | Diagnosi + causa tra diff/ARB/camber + modifica numerica nei range | Funzionale | Da verificare |
| TC-02 | "L'auto scivola dietro in accelerazione" + CSV: `tire_temp_rr: 102°C`, `tire_press_rr: 26.8` | Diagnosi con CSV integrati, causa su pressioni/temp posteriori, correzione numerica | Integrazione | Da verificare |
| TC-03 | "Come regolo il turbo?" | Risposta di rifiuto: parametro non regolabile in ACC | Anti-allucinazione | Da verificare |
| TC-04 | "L'auto va male" | Richiesta di chiarimento sulla fase della curva, no diagnosi prematura | RF-06 | Verificato |
| TC-05 | CSV con colonne mancanti o intestazioni errate | Messaggio di errore formato, no crash | Gestione errori | Verificato |
| TC-06 | "Gara 20 min, consumo 3.2 L/giro, tempo giro medio 1:52" | Calcolo: ceil(20/1.867) × 3.2 × 1.05 ≈ 36.1 L | RF-04 | Verificato |
| TC-07 | Pilota: "troppo caldo" + CSV: `tire_temp_fl: 72°C` | Segnalazione incongruenza esplicita in sezione Diagnosi | RF-05 | Verificato |
| TC-08 | PSI a caldo: 26.7 — contesto selezionato "a caldo" | Sistema classifica come "cold" (sotto finestra 28.5–30.0) — NO "ottimale" | RF-07 | Verificato |

> TC-08 è il test case aggiunto in v4 per validare il fix INC-002.

---

## 12. Sessione AI — Documentazione

| Campo | Dettaglio |
|---|---|
| Modello utilizzato per iterazione prompt | Claude (claude.ai — piano gratuito) |
| Modello utilizzato per building e test | claude-haiku-4-5-20251001 (sviluppo), claude-sonnet-4-20250514 (produzione) |
| Prompt iniziale sottoposto | System Prompt v3 sezione 6 della spec |
| Output utile ottenuto | Struttura 4 sezioni, CoT obbligatoria, range parametri GT3 |
| Modifiche apportate dopo il confronto | Distinzione pressioni freddo/caldo; max_tokens 1500→2500; blocco PRESSIONI nel prompt |
| Scenari di test eseguiti | TC-01 (sottosterzo Monza), TC-02 (CSV), TC-03 (parametro inesistente), TC-04 (input vago), TC-05 (schema CSV), TC-06 (carburante), TC-07 (temperature gomme), TC-08 (pressione a caldo) |
| Bug rilevati durante il building | INC-001 (risposta troncata), INC-002 (confusione freddo/caldo) |
| Riferimento completo iterazioni | PROMPT_LOG.md |
| Riferimento completo bug | INCIDENTS.md |

---

## 13. Sicurezza e Privacy

| Rischio | Soluzione |
|---|---|
| API key esposta nel codice | Gestione tramite `.env` + `.gitignore` |
| Consigli errati applicati in gara | Disclaimer obbligatorio in ogni output: *"Verifica sempre il comportamento dell'auto dopo ogni modifica."* |
| API provider down | Retry 1 volta + messaggio di cortesia (sezione 8) |
| Dati sensibili utente | I dati trattati sono esclusivamente dati di simulazione. Nessun dato personale raccolto o trasmesso. |
| Database locale esposto | `database/pitwall.db` in `.gitignore` — non versionato |

---

## 14. Metriche di Successo (MVP)

| Metrica | Metodo di Verifica | Target |
|---|---|---|
| Accuratezza range parametri | Revisione manuale su TC-01/TC-08 | 100% valori entro range ACC |
| Tasso rilevamento incongruenze | Test TC-07 e varianti | Segnalazione in 100% dei casi con delta >10°C |
| Correttezza calcolo carburante | Verifica TC-06 a mano con formula | Errore ≤ 0.5 L |
| Rifiuto parametri non ACC | Test TC-03 e varianti | Rifiuto in 100% dei casi |
| Risposta a input vago | Test TC-04 | Chiarimento richiesto prima di diagnosi in 100% dei casi |
| Classificazione corretta PSI freddo/caldo | Test TC-08 | 100% classificazioni corrette per contesto |
| Completezza report (4 sezioni) | Verifica post-fix INC-001 | 0 risposte troncate su input standard |

---

## 15. Fuori Scope (MVP)

- Analisi telemetria binaria `.ld` (MoTeC)
- Interfaccia grafica complessa (GUI nativa)
- Automazione comandi nel simulatore
- Memoria persistente tra sessioni (multi-stint context)
- Supporto classi vettura diverse da GT3
- Generazione setup completi ex-novo
- Database remoto / hosting cloud

---

## 16. Roadmap Post-MVP

| Fase | Feature | Priorità |
|---|---|---|
| v1.1 | Supporto GT4 e GTC (range parametri separati) | Alta |
| v1.2 | Memoria di sessione (sliding window multi-stint) | Alta |
| v1.3 | Esportazione report PDF | Media |
| v1.4 | Ottimizzazione UI — revisione UX e accessibilità | Media |
| v2.0 | Integrazione telemetria real-time via ACC Shared Memory | Bassa |
| v2.1 | Migrazione database SQLite → PostgreSQL per deploy cloud | Bassa |

---

## 17. Registro Versioni

| Versione | Data | Modifica | Autore |
|---|---|---|---|
| 1.0 (alpha) | 05/05/2026 | Prima bozza concettuale. | Ferlito Edoardo |
| 2.0 (addendum) | 05/05/2026 | Inserimento logica CoT e vincoli parametri ACC. | Ferlito Edoardo |
| 3.0 (RC) | 10/05/2026 | Documento unificato. System Prompt ottimizzato. Schema CSV. UI Streamlit. Gestione errori. Sessione AI documentata. | Ferlito Edoardo |
| 4.0 (CONGELATA) | 19/05/2026 | Post-building. Fix INC-001 (max_tokens) e INC-002 (pressioni freddo/caldo). Struttura UI espansa (components/). Documentazione costi API. TC-08 aggiunto. Stack aggiornato con versioni effettive. RF-07 formalizzato. | Ferlito Edoardo |

---

## 18. Note e Chiarimenti

- **NC-01:** Range barre antirollio 0–10 usato come ceiling conservativo.
  Varia per auto (BMW M4 GT3: 1–10; alcune auto: 0–8). Raffinamento
  per auto specifica in scope v1.1.
- **NC-02:** Schema CSV base non include `lap_time`. La formula carburante
  richiede input esplicito del tempo giro dal pilota se il CSV non lo
  contiene (RF-06 esteso).
- **NC-03:** Database SQLite scelto per semplicità MVP. File locale
  `database/pitwall.db` creato automaticamente al primo avvio.
  Migrazione a PostgreSQL in roadmap v2.1 se necessario deploy cloud.
- **NC-04:** I valori PSI nei CSV di sessione rappresentano pressioni
  a freddo. I valori letti dal MFD in pista sono pressioni a caldo
  (~2.5–3.5 PSI superiori). Il sistema gestisce entrambi i contesti
  tramite RF-07 e il metodo `classify_pressure_context()`.
