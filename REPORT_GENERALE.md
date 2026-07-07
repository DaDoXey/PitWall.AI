# PitWall.AI — Report Generale di Stato

> **Scopo di questo documento.** Fotografia sintetica e onesta dello stato del progetto,
> pensata per una **revisione esterna** (valutazione di un eventuale **HOTFIX-4**).
> Data: **07/07/2026** · Autore progetto: **Edoardo Ferlito** (ITS ICT Academy Roma).
> Commit di riferimento: **`ce4447f`** (`main` == `restyle-ui` == `origin/*`, tree pulito).

---

## 1. Cos'è PitWall.AI

**Virtual Race Engineer** per *Assetto Corsa Competizione* (GT3). L'utente carica i dati di
una sessione, descrive un problema di guida/setup, e **Gigi** (l'ingegnere virtuale)
risponde con un'analisi tecnica in **4 sezioni** (Diagnosi · Causa Meccanica · Correzione
Setup · Note), vincolata ai **range reali di ACC**.

- **Stack:** Python + **Streamlit**, LLM **Claude** (Anthropic).
- **Deploy:** Streamlit Community Cloud → <https://pitwall-ai-dado.streamlit.app>
- **Modello LLM:** `claude-haiku-4-5` di default (env `LLM_MODEL`), fallback `claude-sonnet-4-6`.

### Architettura (sintesi)
Shell + router `app.py` (auth gate + design system) → package `ui/` (router, sidebar, nav,
dashboard, telemetry, console, setup_view, **demo_data** = sorgente dati demo unica, flags,
components, catalog). `pages/login.py` (SQLite mock + OAuth placeholder). `agent.py` client
LLM (system prompt v4). `modules/setup_params.py` (range ACC = fonte di verità),
`modules/vision_parser.py` (lettura setup da screenshot). `backend/parser/csv_parser.py`,
`backend/database/manager.py` (storico SQLite). `app_legacy.py` monolite preservato verbatim.

### Demo-mode
La Engineer Console serve di default una **risposta-cache pre-validata** a 4 sezioni: non
dipende dalla rete e ricade sulla cache anche se la LLM fallisce. Sul deploy pubblico la
demo è **forzata ON** (`PITWALL_ALLOW_LIVE=0`) per **proteggere la API key**. Tutti i numeri
mostrati provengono da `ui/demo_data.py` (coerenza Dashboard ↔ Telemetria ↔ Heatmap).

---

## 2. Salute attuale (verificata)

| Indicatore | Stato |
|---|---|
| Test parser (`backend/tests/test_parser.py`) | ✅ **12/12** |
| `py_compile` sui file toccati | ✅ OK |
| Git `main`/`restyle-ui`/`origin` | ✅ allineati a `ce4447f`, tree pulito |
| DB (`.db`) e `.env` | ✅ non tracciati (gitignore) — nessun segreto nel repo |
| Dati demo (coerenza cross-schermata) | ✅ verificata (check esplicito in `demo_data`) |
| Criterio HOTFIX-3 "zero cambiamenti visibili" | ✅ confermato a schermo dall'utente |

**Backlog di CODICE: sostanzialmente chiuso.** Incidenti `INC-001…012` ed errata
`ERR-01…08` tutti risolti/documentati.

---

## 3. Cosa è stato fatto (storia recente)

- **HOTFIX-1** — 6 criticità **Alte** (deps pinnate, gate demo/live, ecc.). Chiuso.
- **HOTFIX-2** — 7 priorità **Medie**: log runtime separati dai doc d'esame
  (`PITWALL_PROMPT_LOG_PATH`/`PITWALL_INCIDENTS_PATH`), fix cache demo console (INC-011),
  rimozione wildcard CSS + script `data-theme` morto, README onesto sui selettori,
  SPEC_ERRATA (precarico 20–200), **CI GitHub Actions** per il test parser. Chiuso.
- **Revisione generale 07/07** — 3 imprecisioni minori corrette (ERR-01 advice stale,
  `OPENAI_API_KEY` residuo in `.env.example`, DEMO_FUEL 68→67 L). Pushato.
- **HOTFIX-3** — 07/07, criterio *zero cambiamenti visibili*. **8 commit** (`f6b0dfd`→`ce4447f`):
  - `FIX-1` rimozione dead code (`placeholder_panel`, `create_session`/`update_session_activity`).
  - `FIX-2` **auth upsert per email UNIQUE** che preserva `created_at`/`user_id` + timestamp
    UTC → chiude il crash `UNIQUE(email)` su re-login Custom (**INC-012**).
  - `FIX-3` `_is_demo_prompt` più stretto (niente match permissivo bidirezionale) (**INC-012**).
  - `FIX-4` `assert` → `raise ValueError` in `demo_data` (attivo anche con `python -O`).
  - `FIX-5` `media_type` dinamico da uploader in `vision_parser` (**INC-012**).
  - `FIX-6` dedup `_row_to_session` + note thread-safety in `manager`.
  - `FIX-8` **LICENSE MIT** (© 2026 Edoardo Ferlito) + `frontend/` marcata come scaffold.

---

## 4. Debito tecnico aperto — candidati HOTFIX-4

Ordinati per rapporto valore/rischio. Nessuno è bloccante per la demo d'esame.

### 4.1 — `agent.py` token: default 2048 vs INC-001 (2500 minimo) 🟡 *code↔doc*
`MAX_OUTPUT_TOKENS = int(get_env_var("PITWALL_MAX_OUTPUT_TOKENS", "2048"))` (riga 34), ma
**INC-001** documenta **2500** come minimo sicuro per l'output a 4 sezioni. Contraddizione
reale, oggi **mascherata** (demo-mode serve la cache; `.env.example` imposta 4000).
**Opzioni:** (a) alzare il default a ≥2500 — tocca `agent.py`, **file protetto → STOP gate**;
(b) aggiornare il testo di INC-001 se 2048 è ritenuto sufficiente. *Da decidere.*

### 4.2 — `agent.py` FIX-7 (dead code) — **già analizzato, RIMANDATO** 🟢 *pulizia*
Su `agent.py` (file protetto): `import re` alla riga 8 ha **0 usi**; il wrapper
`check_and_warn()` (righe 125-129) è un semplice pass-through di `check_context_size()`.
Proposta a verbale in PROMPT_LOG: rimuovere entrambi (call site → `check_context_size`
diretto) **mantenendo** `chat_with_gigi` (usato da `app_legacy.py:1154,1174`) con solo un
commento. Rimandato per prudenza (file protetto): da fare in sessione dedicata con STOP gate.

### 4.3 — Storico sessioni SQLite (RF-04) 🔵 *feature, fuori scope pre-esame*
La tabella `sessions` è predisposta ma la **scrittura non è collegata** (commento esplicito
in `db_auth.py`). `manager.py` ha i getter e un helper condiviso, ma il flusso di
salvataggio/ricarica reale è incompleto. Riconnessione pianificata **post-15/07**.

### 4.4 — Robustezza demo/live e vision (osservazioni) 🔵 *nice-to-have*
- I getter DB e alcuni rami usano `except Exception: return []` (silenziosi ma commentati):
  ok per la demo, ma andrebbero loggati se in futuro si attiva lo storico reale.
- `vision_parser` ora accetta `media_type`: verificare il comportamento con formati diversi
  da PNG/JPEG quando `FEATURE_SCREENSHOT=1` (oggi dietro flag OFF).

### 4.5 — Qualità/accessibilità (post-esame) ⚪ *fuori scope dichiarato*
a11y/responsive, riduzione payload font base64, riorganizzazione cartelle: esplicitamente
rimandati a **dopo l'esame**.

---

## 5. Backlog non-code

- **Video demo di backup** — da registrare **solo quando la demo soddisfa l'autore**
  (al 07/07 giudicata "ancora lontana").
- **Azione manuale deploy** — aggiungere `PITWALL_PROMPT_LOG_PATH`/`PITWALL_INCIDENTS_PATH`
  negli **Streamlit Secrets** (dashboard `share.streamlit.io`; `.env` locale già fatto).
  Non urgente: sul deploy la live è OFF.
- **Da confermare** (non bloccanti): primo run verde della CI su GitHub Actions; log build
  Cloud dopo redeploy.

---

## 6. Vincoli da rispettare in un eventuale HOTFIX-4

> Questi vincoli sono **cogenti** — chi propone HOTFIX-4 deve tenerne conto.

- **File protetti** (non riscrivere; le UI li *chiamano*, non li modificano): `agent.py`,
  `backend/parser/csv_parser.py`, `prompts/system_prompt_v4.txt`,
  `backend/prompts/system_prompt.txt`, logica **gauge/fuel**; `modules/setup_params.py`
  protetto-adiacente. Qualunque tocco richiede **STOP gate + ok esplicito**.
- **Non toccare:** `app_legacy.py`, i **numeri** in `demo_data.py`, parser, system prompts.
- **CSS:** vietati selettori **wildcard `*`** e **nuovi** selettori interni Streamlit.
- **Baseline di verifica:** `test_parser` deve restare **12/12**; `py_compile` sui file toccati.
- **Un fix alla volta**, nell'ordine, con verifica prima del successivo.
- **Nessun commit/push** senza «ok push» esplicito dell'autore.

---

## 7. Domanda per la revisione

*Alla luce di quanto sopra, esiste materiale sufficiente per un **HOTFIX-4** prima
dell'esame, o conviene fermarsi qui?* In particolare:

1. Il punto **4.1** (token 2048 vs 2500) va risolto **modificando `agent.py`** o
   **aggiornando INC-001**?
2. Vale la pena chiudere **4.2** (dead code `agent.py`, già analizzato) nella stessa sessione
   protetta di 4.1, per toccare `agent.py` una volta sola?
3. Il resto (4.3–4.5) è correttamente **fuori scope pre-esame** o c'è qualcosa da anticipare?

---

*Documento generato automaticamente il 07/07/2026 a fronte del commit `ce4447f`.
Le fonti di dettaglio sono `PROMPT_LOG.md`, `INCIDENTS.md`, `SPEC_ERRATA.md`, `README.md`.*
