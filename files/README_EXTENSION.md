# PitWall.AI — Estensione v2: Setup Completo + Vision

## Cosa aggiunge questa versione

### Nuovi moduli
| File | Descrizione |
|---|---|
| `modules/setup_params.py` | Definizione completa di tutti i parametri ACC (5 sezioni, 47 parametri totali) |
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

### Struttura target
```
PitWall.AI/
├── app.py                          ← SOSTITUISCI con questo
├── agent.py                        ← SOSTITUISCI con questo
├── parser.py                       ← invariato (MVP)
├── modules/
│   ├── __init__.py                 ← CREA (file vuoto)
│   ├── setup_params.py             ← AGGIUNGI
│   └── vision_parser.py            ← AGGIUNGI
├── prompts/
│   ├── system_prompt.txt           ← invariato (v3, mantieni come backup)
│   └── system_prompt_v4.txt        ← AGGIUNGI
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

### Aggiorna `requirements.txt`
```
streamlit
anthropic
openai
python-dotenv
pandas
```
Nessuna dipendenza aggiuntiva: `vision_parser.py` usa già `anthropic` che era nel requirements.

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
- ~$0.004–0.008 per immagine (Claude Sonnet, immagine 1080p)
- Separato dal costo dell'analisi principale

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
