---
name: hotfix
description: Avvia un ciclo di fix su PitWall.AI col workflow standard del progetto (status → piano → STOP gate → un fix alla volta → verifica → commit-per-fix). Invoca quando l'utente scrive /hotfix o vuole aprire una sessione di correzioni/pulizia su PitWall.
---

# Skill: ciclo HOTFIX di PitWall

Applica **sempre** questo flusso. Non saltare passi. Lavora in italiano.

## FASE 0 — Status
- Leggi lo stato git (l'hook SessionStart lo stampa già; altrimenti `git status`,
  `git log --oneline -1`). Se riprendi, leggi l'ultimo punto in `PROMPT_LOG.md`/`INCIDENTS.md`.
- Verifica l'allineamento `main` == `restyle-ui` == `origin/*`.

## FASE 1 — Piano
- Se non c'è già un elenco di fix, lancia l'agente **`hotfix4-auditor`** (read-only) per
  produrlo, oppure usa `dead-code-hunter`/`doc-sync` secondo il tema.
- Esponi il piano **ordinato** (un fix per voce), con: file toccati, se tocca **file protetti**,
  rischio, e il criterio di verifica. **Attendi l'ok dell'utente** prima di modificare.

## FASE 2 — Esecuzione (un fix alla volta)
- Applica **un solo fix**, poi **verifica** prima del successivo.
- **File protetti** (`agent.py`, `backend/parser/csv_parser.py`, `prompts/system_prompt_v4.txt`,
  `backend/prompts/system_prompt.txt`, `modules/setup_params.py`, `app_legacy.py`): richiedono
  «ok procedi» esplicito. Solo allora crea `.claude/.unlock-protected`, fai la modifica,
  poi rimuovi il marker.
- CSS: niente wildcard `*` né nuovi selettori interni Streamlit (l'hook blocca).
- Criterio cleanup: **zero cambiamenti visibili** salvo richiesta esplicita.

## FASE 3 — Verifica
- Dopo ogni fix, lancia l'agente **`verifier`** (o esegui:
  `.venv/Scripts/python.exe backend/tests/test_parser.py` → 12/12; `py_compile` sui file
  toccati; nessun file protetto inatteso).
- Per modifiche a CSS/UI, lancia **`css-ui-guardian`**.

## FASE 4 — Documentazione
- Aggiorna `PROMPT_LOG.md` (entry della sessione) e, se emergono bug latenti, `INCIDENTS.md`
  (nuovo INC-xxx). Se serve, `doc-sync` per la coerenza.

## FASE 5 — Chiusura (STOP gate finale)
- Riepiloga i fix (fatti / saltati / rimandati), i file toccati, le decisioni.
- Proponi **commit separati, uno per fix**, con messaggi convenzionali
  (`fix(...)`, `refactor(...)`, `chore:`, `docs:`) e footer
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- **FERMATI. Nessun commit/push finché l'utente non scrive «ok push».**
  Solo allora: crea `.claude/.unlock-git`, esegui commit + push (allinea `main` a
  `restyle-ui` ff-only), poi rimuovi il marker.
- Aggiorna la memoria persistente con il nuovo stato.
