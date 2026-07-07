# PitWall.AI — Istruzioni di progetto

> Caricato automaticamente a ogni sessione dentro `PitWall.AI/`.
> **Virtual Race Engineer** per Assetto Corsa Competizione (GT3) — Python + Streamlit + LLM
> **Claude** (Anthropic). Autore: **Edoardo Ferlito** (ITS ICT Academy Roma). Lavoro in **italiano**.

## Regole di workflow (VINCOLANTI)

1. **Status a inizio sessione**: leggi lo stato git (l'hook `SessionStart` lo stampa già) e, se
   riprendi un lavoro, `PROMPT_LOG.md` / `INCIDENTS.md` per l'ultimo punto.
2. **Un fix alla volta**, nell'ordine concordato, con **verifica prima del successivo**.
3. **STOP gate sui file protetti** (vedi sotto): mai modificarli senza «ok procedi» esplicito.
4. **Niente `git commit` / `git push` senza «ok push»** esplicito dell'utente.
5. **Niente wildcard CSS `*`** né nuovi selettori interni Streamlit in `assets/app.css`.
6. Criterio di qualità cleanup: **zero cambiamenti visibili** — ogni differenza a schermo = bug.

Questi punti 3/4/5 sono anche **guardrail tecnici** (hook `PreToolUse`, vedi
`.claude/hooks/`): un tentativo di violarli viene **bloccato**, anche se parte da un sub-agente.

## File protetti (fonte di verità ACC / logica — le UI li *chiamano*, non li modificano)

- `agent.py` · `backend/parser/csv_parser.py`
- `prompts/system_prompt_v4.txt` · `backend/prompts/system_prompt.txt`
- `modules/setup_params.py` (protetto-adiacente) · `app_legacy.py` (monolite verbatim)
- Logica **gauge / fuel** e i **numeri** in `ui/demo_data.py`: non alterare.

**Sbloccare un file protetto** (solo dopo «ok procedi» dell'utente): crea il file
`.claude/.unlock-protected`; l'hook lascia passare le modifiche finché il file esiste.
Rimuovilo appena finito. I marker di sblocco vengono **azzerati a ogni inizio sessione**.

## Autorizzare commit/push (solo dopo «ok push»)

Crea `.claude/.unlock-git`, esegui commit/push, poi rimuovilo.
`git add` su file `.db` è **sempre bloccato** (dati auth/utente, gitignored).

## Baseline di verifica (obbligatoria prima di dire "fatto")

- `.venv/Scripts/python.exe backend/tests/test_parser.py` → deve restare **12/12**.
- `python -m py_compile` sui file toccati.
- Nessun file protetto modificato (a meno di STOP gate esplicito).
- L'agente `verifier` esegue tutto questo in un colpo.

## Architettura (mappa rapida — evita di ri-derivarla)

Shell+router `app.py` (auth gate + design system) → package `ui/` (`router`, `sidebar`/`nav`,
`dashboard`, `telemetry`, `console`, `setup_view`, `demo_data`=sorgente dati demo unica,
`flags`, `components`, `catalog`). `pages/login.py` (SQLite mock + OAuth placeholder).
`agent.py` client LLM (system prompt v4). `modules/setup_params.py` (range ACC),
`modules/vision_parser.py`. `backend/parser/csv_parser.py`, `backend/database/manager.py`.
`app_legacy.py` monolite preservato. **Demo-mode** ON sul deploy (`PITWALL_ALLOW_LIVE=0`)
protegge la API key; la Console serve una risposta-cache a 4 sezioni.

## Igiene di contesto (risparmio token)

- **NON leggere per intero** senza motivo: `app_legacy.py` (~68 KB, mai importato dall'UI
  restyle), `PROMPT_LOG.md` (~92 KB), i font base64 in `assets/`. Filtra le ricerche
  (`glob`/`type`) ed escludili quando non servono.
- Per ricerche ampie usa un **sub-agente** (`Explore`/agenti dedicati): restituisce la
  conclusione, non i dump dei file → il contesto principale resta leggero.
- I dettagli storici sono in `PROMPT_LOG.md`/`INCIDENTS.md`/`SPEC_ERRATA.md`: consultali
  mirati, non a tappeto.

## Agenti dedicati (`.claude/agents/`)

`hotfix4-auditor` (audit + piano HOTFIX-4, read-only) · `dead-code-hunter` · `doc-sync`
· `verifier` · `css-ui-guardian`. Sono **read-only**: propongono, le modifiche le applica il
thread principale (può editare file **non** protetti dopo l'ok; i protetti restano gated).

### Invocazione mirata (per output focalizzato)
Instrada ogni compito all'agente giusto e riporta **solo** il suo output, conciso e strutturato.
Gli agenti scattano **da soli**: (a) `verifier`/`css-ui-guardian`/`doc-sync` hanno `description`
proattive; (b) l'hook `post_edit_router` (PostToolUse) inietta un promemoria appena si tocca
l'area di competenza (codice .py → verifier, UI/CSS → css-ui-guardian, doc → doc-sync), con
dedup di 10 min. L'utente **non** deve selezionarli; può comunque forzarli a parole
("usa l'agente <nome>…").

| Trigger tipico | Agente | Output atteso |
|---|---|---|
| "verifica" / dopo ogni fix | `verifier` | `test_parser` X/12, py_compile, file protetti sì/no, verdetto |
| "cerca codice morto" | `dead-code-hunter` | lista simbolo→`file:riga`, prova, rischio falso positivo |
| "coerenza doc" / pre-consegna | `doc-sync` | incoerenze doc↔doc / doc↔codice + correzione proposta |
| "rischi CSS/UI" / dopo edit UI | `css-ui-guardian` | wildcard / nuovi selettori Streamlit / regressioni visive |
| "audit HOTFIX" / nuovi fix | `hotfix4-auditor` | candidati ordinati per valore/rischio + piano |

Regola d'oro: **un agente per compito**; il thread principale sintetizza, non ripete i dump.

## Skill

`/hotfix` — avvia un ciclo di fix col workflow standard (status → piano → STOP gate →
un fix alla volta → verifica → commit-per-fix).
