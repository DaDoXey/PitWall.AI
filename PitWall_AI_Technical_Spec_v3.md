> ⚠️ **DOCUMENTO SUPERATO.** Questa v3 (Release Candidate MVP, 10/05/2026) è stata
> sostituita dalla **Specifica Tecnica v4** (`PitWall_AI_Technical_Spec_v4.md`), il
> documento post-building che recepisce lo stato effettivo del progetto. La v4 dichiara
> obsolete v1/v2/v3. Conservato solo come traccia storica: per lo stato attuale fare
> riferimento a **v4** e a **`README.md`**.

---

# PitWall.AI — Specifica Tecnica v3 (Consolidata e Unificata)

**Repository:** https://github.com/DaDoXey/PitWall.AI.git

| Campo | Valore |
|---|---|
| Versione | 3.0 |
| Data | 10/05/2026 |
| Stato | RELEASE CANDIDATE — Pronta per Build MVP |
| Autore | Ferlito Edoardo |
| Sostituisce | v1 (alpha, 05/05/2026) + v2 (addendum, 05/05/2026) |

> **Nota di versioning:** La v2 era un addendum di 2 pagine privo di autosufficienza documentale. La presente v3 è il documento unico e definitivo di riferimento per l'MVP. Le specifiche v1 e v2 sono da considerarsi obsolete.

---

## 0. Sintesi del Progetto

| Campo | Dettaglio |
|---|---|
| Nome | PitWall.AI |
| Descrizione | Virtual Race Engineer che analizza feedback del pilota e dati di sessione per ottimizzare setup e strategia su Assetto Corsa Competizione. |
| Tipo di sistema | Assistente operativo basato su LLM (Single-Agent, Stateless per MVP). |
| Target | Sim-racer amatoriali e competitivi su ACC privi di competenze avanzate di ingegneria del veicolo. |
| Output principale | Report Markdown strutturato: Diagnosi / Causa Meccanica / Correzione Setup / Strategia. |
| Interfaccia MVP | Streamlit (web app locale). |

---

## 1. Obiettivo del Sistema

Il sistema agisce come filtro critico tra il feedback soggettivo del pilota e i limiti fisici del simulatore ACC. Non si limita a rispondere in linguaggio naturale: deve identificare la causa meccanica del problema, validarla contro i dati oggettivi di sessione (ove presenti), e produrre una modifica incrementale, numericamente precisa e vincolata ai range reali del simulatore.

**Principio guida:** modifiche incrementali sempre — mai setup completi da zero.

---

## 2. Requisiti Funzionali (con Criteri di Accettazione)

| ID | Requisito | Criterio di Accettazione |
|---|---|---|
| RF-01 | Il sistema deve accettare feedback in linguaggio naturale. | L'input viene processato e produce una risposta strutturata nelle 4 sezioni definite. |
| RF-02 | Il sistema deve parsare file CSV di sessione ACC. | I campi `temperature`, `pressioni`, `consumi` vengono estratti correttamente dallo schema definito. |
| RF-03 | Il sistema deve restituire consigli con valori numerici nei range ACC. | Nessun valore suggerito è fuori dai range dichiarati nel System Prompt. |
| RF-04 | Il sistema deve calcolare la strategia carburante. | Dato `consumo_per_giro` e `durata_gara`, il calcolo è verificabile a mano con la formula esplicita. |
| RF-05 | Il sistema deve segnalare incongruenze tra feedback e dati CSV. | Se il pilota dichiara "troppo caldo" ma le temperature CSV sono basse, il sistema lo segnala esplicitamente nella sezione Diagnosi. |
| RF-06 | Il sistema deve chiedere chiarimenti se l'input è troppo vago. | Input `"l'auto va male"` → risposta `"Puoi specificare in quale fase della curva?"` prima di procedere. |

### Confronto v1→v3

| Requisito | v1 | v3 |
|---|---|---|
| RF-01 | Presente, non verificabile | Presente + criterio di accettazione esplicito |
| RF-02 | "CSV/testo" generico | Schema CSV definito (sezione 5) |
| RF-03 | Menzionato senza range | Range numerici vincolati nel prompt (sezione 6) |
| RF-04 | Menzionato senza formula | Formula esplicita (sezione 4.2) |
| RF-05 | Assente in v1, generico in v2 | Logica di cross-check definita (RF-05) |
| RF-06 | Citato in gestione errori | Requisito funzionale con criterio verificabile |

---

## 3. Architettura del Sistema

### 3.1 Overview (Single-Agent, Stateless)

```
[Pilota]
    │
    ├─ Feedback testuale (linguaggio naturale)
    └─ File CSV sessione (opzionale)
              │
              ▼
    ┌─────────────────────┐
    │   INTERFACCIA       │  ← Streamlit
    │   (Input Layer)     │
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │   PARSING ENGINE    │  ← pandas (CSV) + validazione schema
    │                     │
    └─────────┬───────────┘
              │  Contesto strutturato (JSON interno)
              ▼
    ┌─────────────────────┐
    │   LLM AGENT         │  ← Anthropic Claude Sonnet / OpenAI GPT-4o
    │   (Core Engine)     │  ← System Prompt v3 (sezione 6)
    │   Chain-of-Thought  │
    └─────────┬───────────┘
              │  Output Markdown (4 sezioni)
              ▼
    ┌─────────────────────┐
    │   OUTPUT LAYER      │  ← st.markdown() + validazione sezioni
    └─────────────────────┘
```

### 3.2 Scelta del Modello LLM

| Modello | Pro | Contro | Decisione MVP |
|---|---|---|---|
| Claude Sonnet (Anthropic) | CoT nativo, ottimo per vincoli, costi contenuti | API key separata | **Primario** |
| GPT-4o mini (OpenAI) | Costo minimo | CoT meno affidabile su vincoli complessi | Fallback |

Motivazione: la catena di ragionamento obbligatoria (Diagnosi → Causa → Correzione) richiede un modello con capacità di ragionamento strutturato superiore ai modelli "mini". Il costo per interazione rimane sotto $0.01.

### 3.3 Gestione Contesto (Stateless per MVP)

Per l'MVP, ogni chiamata API è indipendente. Il contesto di sessione (feedback + CSV parsato) viene inviato interamente in ogni richiesta. La gestione multi-turno (memoria di stint) è esclusa dallo scope MVP e inserita nella roadmap v2 (sezione 9).

---

## 4. Logica di Elaborazione

### 4.1 Pipeline di Elaborazione Input

```
Input testuale → Validazione lunghezza/contenuto
                      │
                      ├─ Input vuoto → blocco pre-chiamata
                      └─ Input valido ─────────────────────┐
                                                            │
Input CSV (opz.) → Validazione schema                      │
                      │                                     │
                      ├─ Schema errato → messaggio errore   │
                      └─ Schema valido → estrazione campi   │
                                            │               │
                                            └───────────────┘
                                                    │
                                            Cross-check coerenza
                                            feedback ↔ dati CSV
                                                    │
                                            Costruzione contesto JSON
                                                    │
                                            Chiamata LLM con System Prompt
```

### 4.2 Formula Calcolo Carburante

```
carburante_necessario = ceil(durata_gara_min / tempo_giro_min) × consumo_per_giro_L
carico_consigliato    = carburante_necessario × (1 + margine_sicurezza)

dove:
  margine_sicurezza = 0.05  (5% — configurabile)
  durata_gara_min   = input pilota
  tempo_giro_min    = input pilota o media da CSV (colonna non presente nello schema base — vedi nota)
  consumo_per_giro_L = input pilota o media colonna `fuel_cons` da CSV
```

> **Nota:** Lo schema CSV base (sezione 5) non include `lap_time`. Se il pilota fornisce solo durata gara e consumo, il sistema deve richiedere il tempo sul giro medio prima di calcolare.

### 4.3 Logica di Cross-Check CSV ↔ Feedback

| Condizione Rilevata | Comportamento Agente |
|---|---|
| Pilota: "troppo caldo" — CSV: temp < 85°C | Segnalare incongruenza in sezione Diagnosi, chiedere conferma scenario |
| Pilota: "pressioni ok" — CSV: press > 28.0 psi | Correggere con dati oggettivi, notare discrepanza percettiva |
| Pilota: "consumo alto" — CSV: `fuel_cons` nella norma | Diagnosi su stile di guida, non su setup meccanico |
| CSV assente | Procedere su solo feedback testuale, segnalare limitazione diagnostica |

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
| `tire_press_fl` | float | psi (freddo) | No |
| `tire_press_fr` | float | psi (freddo) | No |
| `tire_press_rl` | float | psi (freddo) | No |
| `tire_press_rr` | float | psi (freddo) | No |
| `tire_temp_fl` | float | °C (core) | No |
| `tire_temp_fr` | float | °C (core) | No |
| `tire_temp_rl` | float | °C (core) | No |
| `tire_temp_rr` | float | °C (core) | No |

> **Nota tecnica:** ACC non esporta CSV nativo. Il file deve essere prodotto manualmente o tramite tool di terze parti (es. CrewChief, ACC Session Exporter). I valori di pressione nello schema sono pressioni a freddo (impostabili in garage), non operative a caldo.

### 5.2 Pressioni Operative a Caldo (Riferimento)

Le pressioni nel CSV rappresentano i valori impostati a freddo. Le pressioni operative a caldo (target diagnostico reale) sono tipicamente 2.5–3.5 psi superiori. Il sistema deve comunicare questa distinzione al pilota nelle Note Aggiuntive quando rileva valori CSV prossimi ai limiti del range.

---

## 6. System Prompt Ottimizzato (v3)

```
RUOLO
Sei PitWall.AI, un Senior Race Engineer virtuale specializzato in auto GT3 su
Assetto Corsa Competizione (ACC). Il tuo compito esclusivo è assistere il pilota
nell'ottimizzazione del setup e nella strategia di gara attraverso modifiche
incrementali, precise e tecnicamente fondate.

════════════════════════════════════════
METODO DI RAGIONAMENTO — OBBLIGATORIO
════════════════════════════════════════
Per ogni richiesta del pilota, segui SEMPRE questi 3 passi nell'ordine indicato.
Non saltare passi. Non comprimere passi in uno solo.

  Passo 1 — DIAGNOSI
  Analizza il problema descritto dal pilota. Se sono presenti dati CSV,
  verifica la coerenza tra feedback soggettivo e dati oggettivi.
  Segnala esplicitamente qualsiasi incongruenza rilevata.

  Passo 2 — CAUSA MECCANICA
  Identifica la causa tecnica più probabile. Considera nell'ordine:
  comportamento aerodinamico, bilanciamento meccanico (molle/ARB),
  differenziale (precarico/rampe), geometria (camber/toe), pressioni gomme.
  Non attribuire cause multiple senza una gerarchia di probabilità.

  Passo 3 — CORREZIONE
  Suggerisci una modifica specifica con valore numerico. La modifica deve
  essere incrementale (mai un setup completo da zero) e vincolata ai range
  ACC definiti di seguito.

════════════════════════════════════════
PARAMETRI DI SICUREZZA ACC — GT3
════════════════════════════════════════
Non suggerire MAI valori fuori da questi range.
Non suggerire MAI modifiche a parametri non regolabili in ACC.

  Pressione gomme (freddo):     26.0 – 27.5 psi
  Camber anteriore:            -2.5° a -4.0°
  Camber posteriore:           -1.5° a -3.0°
  Barre antirollio:             0 – 10 (specifico per auto, usa range relativo)
  Precarico differenziale:      20 – 100 Nm
  TC1 (Traction Control):       0 – 11
  TC2 (TC Cut):                 0 – 11
  ABS:                          0 – 11

════════════════════════════════════════
FORMATO OUTPUT — OBBLIGATORIO
════════════════════════════════════════
Struttura SEMPRE la risposta con esattamente queste 4 sezioni Markdown.
Non omettere sezioni. Non aggiungere sezioni non previste.

  ## Diagnosi
  [Analisi del problema dichiarato dal pilota. Se presenti dati CSV:
   confronto feedback vs dati oggettivi. Segnalare incongruenze.]

  ## Causa Meccanica Probabile
  [Identificazione tecnica della causa. Terminologia ACC corretta.
   Se più cause possibili: elencarle in ordine di probabilità decrescente.]

  ## Correzione Setup Consigliata
  [Modifica specifica con valore numerico. Esempio:
   "Aumenta il precarico differenziale da 65 Nm a 75 Nm."]

  ## Note Aggiuntive
  [Avvertenze operative, verifiche da fare in pista, disclaimer standard:
   "Verifica sempre il comportamento dell'auto dopo ogni modifica."]

════════════════════════════════════════
UTILIZZO DATI CSV (se forniti)
════════════════════════════════════════
Se il pilota fornisce dati CSV di sessione, utilizzali per:
  - Verificare la coerenza tra feedback soggettivo e dati oggettivi
  - Segnalare incongruenze (es. pilota lamenta calore, pressioni CSV basse)
  - Raffinare i consigli con valori specifici estratti dai dati

════════════════════════════════════════
VINCOLI OPERATIVI
════════════════════════════════════════
  DO:
  ✓ Usa terminologia tecnica corretta di ACC
  ✓ Chiedi chiarimenti se l'input è troppo vago (es. "in quale fase
    della curva?" prima di diagnosticare)
  ✓ Lavora sempre su modifiche incrementali al setup esistente
  ✓ Distingui tra pressioni a freddo (garage) e operative a caldo

  DO NOT:
  ✗ Non inventare dati non presenti nell'input del pilota
  ✗ Non suggerire "regolazione del turbo" o altri parametri inesistenti
    in ACC (es. mappature turbo, sospensioni attive)
  ✗ Non richiedere o analizzare file di telemetria binaria (.ld — MoTeC)
  ✗ Non dare giudizi sulle capacità o errori di guida del pilota
  ✗ Non proporre setup completi da zero
```

---

## 7. Interfaccia Utente — Specifiche Streamlit

### 7.1 Componenti UI (MVP)

| Componente Streamlit | Scopo | Obbligatorio |
|---|---|---|
| `st.text_area("Descrivi il problema")` | Input feedback pilota in linguaggio naturale | Sì |
| `st.selectbox("Auto", ["BMW M4 GT3", "Ferrari 296 GT3", "Porsche 992 GT3-R", ...])` | Contestualizzazione per parametri specifici | Sì |
| `st.file_uploader("Carica CSV sessione", type=["csv"])` | Upload dati telemetria opzionale | No (opzionale) |
| `st.button("Analizza")` | Trigger elaborazione | Sì |
| `st.markdown(risposta)` | Rendering output strutturato | Sì |

### 7.2 Flusso UI

```
[Apertura app]
    │
    ├─ Selectbox Auto (obbligatorio)
    ├─ Text area feedback (obbligatorio)
    └─ File uploader CSV (opzionale)
              │
        [Button "Analizza"]
              │
        Validazione input lato client
              │
        Spinner "Analisi in corso..."
              │
        st.markdown(risposta strutturata)
```

---

## 8. Gestione degli Errori

| Scenario | Comportamento | Messaggio Utente |
|---|---|---|
| CSV formato errato / schema non valido | Blocco parsing, no chiamata LLM | "Il file non è un CSV valido di ACC. Verifica il formato." |
| Input testuale vuoto | Blocco pre-chiamata | "Descrivi il problema che stai riscontrando in pista." |
| API timeout / errore di rete | Retry 1 volta, poi fallback | "Servizio temporaneamente non disponibile." |
| Output LLM privo della sezione "Diagnosi" | Retry 1 volta | Se fallisce: "Errore nella generazione del consiglio." |
| Pilota chiede parametro non regolabile in ACC | Rifiuto nel prompt, risposta educativa | "Questo parametro non è regolabile in ACC." |
| Input vago senza contesto (es. "l'auto va male") | Richiesta chiarimento | "Puoi specificare in quale fase della curva si manifesta il problema?" |

---

## 9. Stack Tecnologico

```
Linguaggio:        Python 3.10+
Interfaccia:       Streamlit
LLM (primario):    Anthropic Claude Sonnet (via API)
LLM (fallback):    OpenAI GPT-4o mini (via API)
Parsing dati:      pandas
Gestione env:      python-dotenv (.env file per API keys)
Versionamento:     Git / GitHub

Installazione dipendenze:
pip install streamlit anthropic openai python-dotenv pandas
```

**Struttura Repository:**
```
PitWall.AI/
├── app.py                  # Entry point Streamlit
├── agent.py                # Logica chiamata LLM + system prompt
├── parser.py               # Parsing e validazione CSV
├── prompts/
│   └── system_prompt.txt   # System Prompt v3 (sezione 6)
├── data/
│   └── test_session.csv    # CSV di test (sezione 5.1)
├── .env                    # API keys (non versionato)
├── .env.example            # Template variabili ambiente
├── requirements.txt
└── README.md
```

---

## 10. Piano di Test (Casi di Accettazione)

| ID | Input | Risultato Atteso | Tipo |
|---|---|---|---|
| TC-01 | "Ho troppo sottosterzo a centro curva sulla BMW M4 GT3 a Monza" (no CSV) | Diagnosi + causa meccanica tra diff/ARB/camber + modifica numerica nei range | Funzionale |
| TC-02 | "L'auto scivola dietro in accelerazione" + CSV: `tire_temp_rr: 102°C`, `tire_press_rr: 26.8` | Diagnosi con dati CSV integrati, causa su pressioni/temp posteriori, correzione numerica | Integrazione |
| TC-03 | "Come regolo il turbo?" | Risposta di rifiuto: parametro non regolabile in ACC | Anti-allucinazione |
| TC-04 | "L'auto va male" | Richiesta di chiarimento sulla fase della curva, no diagnosi prematura | RF-06 |
| TC-05 | CSV con colonne mancanti o intestazioni errate | Messaggio di errore formato, no crash | Gestione errori |
| TC-06 | "Gara 20 min, consumo 3.2 L/giro, tempo giro medio 1:52" | Calcolo carburante corretto: ceil(20/1.867) × 3.2 × 1.05 ≈ 36.1 L | RF-04 |
| TC-07 | Pilota: "troppo caldo" + CSV: `tire_temp_fl: 72°C` | Segnalazione incongruenza esplicita in sezione Diagnosi | RF-05 |

---

## 11. Sessione AI — Documentazione (Requisito Professoressa)

*Questa sezione documenta il processo iterativo di sviluppo del System Prompt tramite confronto con modelli LLM, come richiesto dalla valutazione della Lezione 2.*

| Campo | Dettaglio |
|---|---|
| Modello utilizzato per iterazione | Claude (claude.ai) |
| Prompt iniziale sottoposto | Bozza da specifica v2 (ruolo + CoT + parametri GT3) |
| Output utile ottenuto | Struttura 4 sezioni output, vincoli "DO/DO NOT", logica cross-check CSV |
| Modifiche apportate dopo il confronto | Aggiunta distinzione pressioni freddo/caldo; esplicitazione formula carburante; sezione "NON FARE" per parametri .ld MoTeC; richiesta chiarimento su input vago prima di diagnosticare |
| Scenari di test eseguiti | TC-01 (sottosterzo), TC-02 (con dati CSV), TC-03 (parametro inesistente) |

---

## 12. Sicurezza e Privacy

| Rischio | Soluzione |
|---|---|
| API key esposta nel codice | Gestione tramite `.env` + `.gitignore` |
| Consigli errati applicati in gara | Disclaimer obbligatorio in ogni output: *"Verifica sempre il comportamento dell'auto dopo ogni modifica."* |
| API provider down | Retry logic + messaggio di cortesia (sezione 8) |
| Dati sensibili utente | I dati trattati sono esclusivamente dati di simulazione. Nessun dato personale raccolto o trasmesso. |

---

## 13. Metriche di Successo (MVP)

| Metrica | Metodo di Verifica | Target |
|---|---|---|
| Accuratezza range parametri | Revisione manuale su tutti i test case (TC-01/TC-07) | 100% valori entro range ACC |
| Tasso rilevamento incongruenze | Test TC-07 e varianti | Segnalazione in 100% dei casi con delta >10°C |
| Correttezza calcolo carburante | Verifica TC-06 a mano con formula | Errore ≤ 0.5 L |
| Rifiuto parametri non ACC | Test TC-03 e varianti | Rifiuto in 100% dei casi |
| Risposta a input vago | Test TC-04 | Chiarimento richiesto prima di diagnosi in 100% dei casi |

---

## 14. Fuori Scope (MVP)

- Analisi telemetria binaria `.ld` (MoTeC)
- Interfaccia grafica complessa (GUI nativa)
- Automazione comandi nel simulatore
- Memoria persistente tra sessioni (multi-stint context)
- Supporto classi vettura diverse da GT3
- Generazione setup completi ex-novo

---

## 15. Roadmap Post-MVP

| Fase | Feature | Priorità |
|---|---|---|
| v1.1 | Supporto GT4 e GTC (range parametri separati) | Alta |
| v1.2 | Memoria di sessione (sliding window multi-stint) | Alta |
| v1.3 | Esportazione report PDF | Media |
| v2.0 | Integrazione telemetria real-time via ACC Shared Memory | Bassa |

---

## 16. Registro Versioni

| Versione | Data | Modifica | Autore |
|---|---|---|---|
| 1.0 (alpha) | 05/05/2026 | Prima bozza concettuale. | Ferlito Edoardo |
| 2.0 (addendum) | 05/05/2026 | Inserimento logica CoT e vincoli parametri ACC. | Ferlito Edoardo |
| 3.0 (RC) | 10/05/2026 | Documento unificato e autosufficiente. Integrazione direttive Lezione 2. System Prompt ottimizzato. Schema CSV definito. Interfaccia Streamlit specificata. Gestione errori tabulare. Sessione AI documentata. | Ferlito Edoardo |

---

## Note e Chiarimenti

- **NC-01:** Le foto allegate riportano "Barre antirollio: range 0–10 (specifico per auto)". Il range 0–10 è corretto come riferimento relativo (scala ACC), ma il numero di click disponibili varia per modello (es. BMW M4 GT3: 1–10; alcune auto: 0–8). Il System Prompt usa il range 0–10 come ceiling conservativo; raffinamento per auto specifica è in scope v1.1.
- **NC-02:** Lo schema CSV nella foto (Immagine 4) non include `lap_time`. La formula carburante in sezione 4.2 richiede quindi input esplicito del tempo giro dal pilota se il CSV non lo contiene. Questo comportamento è stato codificato in RF-06 esteso.
- **NC-03:** Il documento del professore menziona "verifica PC, studio PDF lezioni, PROMPT_LOG, INCIDENTS" come materiali mancanti non obbligatori. Questi non impattano la specifica tecnica ma sono rilevanti per la valutazione complessiva del corso.
