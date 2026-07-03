# PitWall.AI — Avvio rapido (lavorare da un altro PC)

Mini-guida per riprendere il lavoro su un secondo computer e tenere i due PC in
sincronia tramite GitHub.

Repo: <https://github.com/DaDoXey/PitWall.AI>
Branch attivi: `main` (deploy Streamlit Cloud) e `restyle-ui` (allineato a `main`).
Rollback disponibile: branch `backup-pre-restyle`.

---

## 1. Primo trasferimento (una volta sola)

Il codice è tutto su GitHub, **ma** due cose NON sono nel repo (sono in
`.gitignore`): il file `.env` (con la `ANTHROPIC_API_KEY`) e i database locali
(`pitwall_auth.db`, `pitwall_sessions.db`). Per averli sull'altro PC:

- Usa lo zip di backup (`PitWall.AI_backup_2026-06-30.zip`, già in OneDrive), che
  contiene **tutto** incluso `.env` e i DB, **oppure**
- clona da GitHub (passo 2) e copia a mano solo `.env` (e, se ti servono, i `.db`).

> Lo zip **non** include `.venv` (446 MB, specifico di questo PC) né i
> `__pycache__`: si rigenerano (passo 3).

---

## 2. Clonare il repo (se parti da GitHub)

```bash
git clone https://github.com/DaDoXey/PitWall.AI.git
cd PitWall.AI
```

Se la cartella esiste già (da zip), salta il clone: è già un repo collegato.

---

## 3. Creare l'ambiente Python

```bash
python -m venv .venv

# Windows (PowerShell/CMD)
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 4. Variabili d'ambiente

Serve un file `.env` nella radice del progetto con almeno:

```
ANTHROPIC_API_KEY=la_tua_chiave
```

(Se hai usato lo zip, il `.env` c'è già. Riferimento: `.env.example`.)

> Nota: in **demo-mode** (default ON) la Engineer Console usa una risposta cache
> pre-validata, quindi gira anche senza chiave. La chiave serve per le risposte
> LLM reali e per la lettura screenshot (vision).

---

## 5. Avviare l'app

```bash
streamlit run app.py
```

Login: **Quick Login → "Demo Pilot"**.

---

## 6. Sincronizzare i due PC (d'ora in poi)

Niente più zip: si lavora con git.

**Prima di iniziare** a lavorare su un PC:
```bash
git pull
```

**Quando hai finito** (per portare le modifiche sull'altro PC):
```bash
git add -A
git commit -m "descrizione modifiche"
git push
```

Lavora sul branch che preferisci; ricorda di tenere allineati `main` e
`restyle-ui` se modifichi solo uno dei due:
```bash
git checkout main && git merge --ff-only restyle-ui && git push origin main
```

---

## In sospeso (promemoria)

- ~~Stile tasti del login~~ → **fatto il 03/07**: bottone Google riportato in stile
  cockpit dark (`styles/login.css`, `.pw-google-btn`).
- ~~Sidebar~~ → **compattata + centrata il 03/07**: pannello fisso (no scroll), stack ad
  altezza naturale **centrato verticalmente** (`justify-content:center`), gap uniforme `0.6rem`.
  Tolto il fill forzato (`min-height:100vh`/`space-between`) che tagliava l'Esci in fondo.
  CSS ora si ricarica su modifica (cache per mtime in `css_loader.py`). Collapse/box sessione invariati.
- ~~Setup (colore pressioni)~~ → **fatto il 03/07**: i 4 valori pressione si colorano vs
  finestra ottimale a freddo (verde `26.0–27.0`, ambra ±0.6, rosso oltre) con pallino ● +
  legenda. Soglie tunable in `ui/demo_data.py` (`COLD_PRESS_WINDOW`). `setup_params.py` intatto.
- ~~Dashboard (grafici)~~ → **fatto il 03/07**: il routing era già ok; il vero obiettivo erano i
  **grafici**. Layout iframe mantenuto (un tentativo di card native col bottone dentro è stato
  **annullato** perché l'utente preferiva l'impaginazione di prima). Sparkline arricchite (area
  sfumata, curva morbida, min/max, linea-limite tratteggiata 95°C) e window-bar con valore+range
  — in `ui/components.py` (`sparkline_svg`/`window_bar_svg`, etichette in overlay HTML per non
  distorcersi). Nessun dato toccato.
- ~~Documentazione~~ → **riconciliata il 04/07**: `README_EXTENSION.md` e
  `PitWall_AI_Technical_Spec_v3.md` marcati come **storici/superati** (banner in testa);
  corrette le incongruenze fattuali della v2 (struttura reale, requirements, modello,
  47→49 parametri). Aggiunta a `README.md` la tabella «quale doc è valido» (v4 + README
  attuali). Nessun codice/dato toccato.
- **Video demo di backup** ancora da registrare (rischio già costato punti).

> ERR-01…ERR-05 e INC-001…INC-008 risultano **RISOLTI** (vedi `SPEC_ERRATA.md` /
> `INCIDENTS.md`). Telemetria: 3 fix + espansione fatti il 03/07 (TELEMETRIA-UPGRADE-1).

## File da NON committare (già in `.gitignore`)

`.env`, `.venv/`, `__pycache__/`, `*.db` locali. Trasferiscili solo via zip o copia
manuale, mai con `git add`.
