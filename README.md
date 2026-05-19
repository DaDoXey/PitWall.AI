# PitWall.AI

Virtual Race Engineer per Assetto Corsa Competizione 1.9+.

## Struttura del repository

- `backend/` — logica server, parsing, fisica e AI.
- `frontend/` — spazio UI futuro.
- `.env.example` — template per chiavi API.
- `requirements.txt` — dipendenze Python.

## Avvio rapido

1. Crea un ambiente virtuale Python.
2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
3. Copia `.env.example` in `.env` e inserisci la tua chiave `ANTHROPIC_API_KEY`.
   Opzionale: imposta `ANTHROPIC_API_VERSION` su `2023-06-01` se il wrapper non trova una versione valida automaticamente.
4. Avvia l'app Streamlit:
   ```bash
   streamlit run app.py
   ```

## Note architetturali

- `backend/core/physics.py` contiene solo calcoli deterministici.
- `backend/core/ai_logic.py` gestisce solo il wrapper Claude.
- `backend/parser/csv_parser.py` esegue parsing e validazione.
- `backend/database/manager.py` mantiene lo storico delle sessioni.
