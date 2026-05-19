# Copilot rules for PitWall.AI

- Non modificare le costanti fisiche in `backend/core/physics.py`.
  Questi valori sono immutabili per ACC 1.9+ e garantiscono correttezza sul dominio.
- Mantieni una netta separazione tra UI, logica applicativa e LLM.
  `app.py` deve contenere solo interfaccia e orchestrazione, non logica di dominio.
- Usa `backend/core/physics.py` solo per calcoli deterministici e non invocare mai l'LLM da lì.
- Usa `backend/core/ai_logic.py` solo per commento qualitativo e chiamate Claude.
- `backend/parser/csv_parser.py` deve gestire esclusivamente parsing e validazione del CSV ACC.
- Rispetta PEP8 con max 88 caratteri per riga e codice leggibile.
- Non hardcodare chiavi API nei sorgenti; usa variabili ambiente in `.env` o `.env.example`.
- Non chiamare l'LLM per calcoli deterministici o stime numeriche che possono essere fatte con `physics.py`.
