> ⚠️ **DOCUMENTO STORICO (v2, superato dal restyle).** Questo file descrive la
> migrazione MVP → v2 (Setup completo + Vision) *com'era pianificata all'epoca*. La
> struttura del repo è poi cambiata con il restyle UI/UX: `app.py` è oggi una
> **shell + router** (non un monolite con 5 tab), il parsing CSV vive in
> `backend/parser/csv_parser.py` (non `parser.py`), e il modello di default è
> `claude-haiku-4-5`. Per lo **stato attuale** fare sempre riferimento a **`README.md`**.
> Conservato come traccia storica delle decisioni; le sezioni fattuali qui sotto sono
> state riconciliate con il repo reale.

# PitWall.AI — Estensione v2: Setup Completo + Vision

## Cosa aggiunge questa versione

### Nuovi moduli
| File | Descrizione |
|---|---|
| `modules/setup_params.py` | Definizione completa di tutti i parametri ACC (5 sezioni, 49 parametri totali — vedi tabella sotto) |
| `modules/vision_parser.py` | Parsing screenshot setup via Claude Vision API |
| `prompts/system_prompt_v4.txt` | System prompt aggiornato con tutti i nuovi range |
| `app.py` | Riscrittura completa con 5 tab setup + input da screenshot |
| `agent.py` | Aggiornamento minore — punta al prompt v4 |

### Parametri aggiunti (rispetto all'MVP)

| Sezione | Parametri MVP | Parametri v2 |
|---|---|---|
| Tyres | Pressioni (4) | Pressioni (4) + Camber (4) + Toe (4) + Caster (1) = **13** |
| Electronics | TC1, TC2, ABS (3) | TC1, TC2, ABS, ECU Map, Brake Bias = **5** |
| Mechanical Grip | ARB (2) + Preload (1) = 3 | ARB (2) + Wheel Rate (2) + Bumpstop Rate (2) + Bumpstop Range (2) + Preload (1) = **9** |
| Dampers | ✗ | Bump + Fast Bump + Rebound + Fast Rebound × 4 ruote = **16** |
| Aero | ✗ | Ride Height (2) + Splitter + Wing + Brake Ducts (2) = **6** |
| **Totale** | **6** | **49** |

---

## Integrazione nel repository esistente

### Struttura target (com'era pianificata all'epoca)
> ⚠️ **Storico.** La struttura reale attuale è diversa (vedi `README.md`): `app.py` è una
> shell+router, il parser CSV è `backend/parser/csv_parser.py`, il prompt attivo è
> `prompts/system_prompt_v4.txt`. Lo schema sotto è la pianificazione originale v2.
```
PitWall.AI/
├── app.py                          ← (allora) SOSTITUISCI — oggi è shell + router
├── agent.py                        ← (allora) SOSTITUISCI — punta al prompt v4
├── parser.py                       ← (allora) MVP — oggi backend/parser/csv_parser.py
├── modules/
│   ├── __init__.py                 ← CREA (file vuoto)
│   ├── setup_params.py             ← AGGIUNGI
│   └── vision_parser.py            ← AGGIUNGI
├── prompts/
│   ├── system_prompt.txt           ← (allora) v3 di backup
│   └── system_prompt_v4.txt        ← AGGIUNGI (prompt attivo)
├── data/
│   └── test_session.csv            ← invariato
├── .env
├── requirements.txt                ← aggiorna (vedi sotto)
└── README.md
```

### Crea il file `modules/__init__.py`
```bash
touch modules/__init__.py
```

### `requirements.txt` (stato attuale del repo)
```
streamlit>=1.0
anthropic>=0.26.0
python-dotenv>=1.0
pandas>=2.0
plotly>=5.0
requests>=2.30
```
Il `vision_parser.py` usa `anthropic`, già presente. (Nota storica: la bozza v2 elencava
anche `openai`, mai usato nel repo attuale — rimosso.)

---

## Feature: Input da Screenshot

### Come funziona
1. L'utente carica una foto del menu setup ACC dalla sidebar
2. Clicca "Leggi Parametri da Screenshot"
3. Claude Vision analizza l'immagine e riconosce i valori
4. L'utente vede un riepilogo dei parametri estratti
5. Clicca "Usa questi parametri nel form" → gli slider si posizionano automaticamente
6. L'utente può correggere manualmente valori errati prima di analizzare

### Limitazioni documentate
- Qualità immagine: risoluzione minima consigliata 1080p
- ACC non include etichette in tutte le schermate — la sezione Dampers può essere meno precisa
- Sempre presentare il riepilogo all'utente prima della conferma (mai auto-apply silenzioso)
- Non sostituisce la validazione manuale: il pilota deve sempre verificare i valori riconosciuti

### Costo per chiamata Vision
- ~$0.004–0.008 per immagine (immagine 1080p; ordine di grandezza stimato all'epoca su
  Claude Sonnet — il default attuale del progetto è `claude-haiku-4-5`, più economico)
- Separato dal costo dell'analisi principale
- N.B.: la feature screenshot è dietro feature-flag `FEATURE_SCREENSHOT` (default OFF)

---

## Nota sui range car-specific

I range nel `setup_params.py` sono **conservativi e car-agnostic**.
Questo è corretto per l'MVP e per mantenere la generalità del sistema prompt.

Per la v2.1 (roadmap):
- Aggiungere tabella `CAR_SPECIFIC_RANGES` in `setup_params.py`
- Es: BMW M4 GT3 ARB: 1–10, Porsche 992: 0–9, etc.
- Filtrare gli slider in base all'auto selezionata

---

## Test case aggiuntivi (da aggiungere a PROMPT_LOG)

| ID | Input | Verifica |
|---|---|---|
| TC-08 | Screenshot tab Mechanical Grip ACC | Parametri ARB, Wheel Rate, Bumpstop estratti correttamente |
| TC-09 | Setup completo + "troppo sottosterzo" | AI usa i valori del setup come riferimento nella correzione |
| TC-10 | "Come regolo il fast rebound?" | Risposta con spiegazione tecnica + valore numerico |
| TC-11 | Screenshot illeggibile / sfocato | Messaggio errore chiaro, no crash |
| TC-12 | Ride height front > ride height rear | AI segnala rake negativo anomalo |
