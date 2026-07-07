# SPEC_ERRATA — PitWall.AI (restyle UI/UX)

Registro delle **correzioni e coerenze dati** introdotte durante il restyle.
Scopo: tracciare ogni scostamento tra prototipo/brief e i valori effettivamente
mostrati a video, e garantire la coerenza numerica richiesta dalla checklist
pre-demo (Dashboard ↔ Telemetria ↔ Heatmap).

> File protetti NON modificati: `prompts/system_prompt_v4.txt` (range ACC reali),
> `agent.py`, parser, logica fuel/gauge. Le correzioni qui sotto riguardano SOLO
> i dati demo di presentazione (hardcoded in `ui/demo_data.py`).

---

## ERR-01 — Pressioni: distinzione FREDDO (garage/CSV) vs CALDO (display)

**Contesto:** la Telemetria mostra pressioni "a caldo"; il CSV/garage contiene
pressioni "a freddo". Sono grandezze fisicamente distinte e non vanno mescolate.

**Decisione:** in `ui/demo_data.py` due dizionari separati ed espliciti:
- `COLD_PRESSURES` = `{fl 26.5, fr 26.5, rl 25.7, rr 25.5}` (riferimento garage/CSV);
- `HOT_PRESSURES` = `{fl 29.0, fr 29.2, rl 28.2, rr 28.0}` (display telemetria).

**Vincolo fisico (rev. 2026-06-30):** a caldo SEMPRE > a freddo (la gomma in
esercizio scalda e la pressione sale di ~2.5–3.5 psi). I valori a caldo del
retrotreno (28.2 / 28.0) restano comunque **sotto la finestra** (28.5–30.0):
il caso didattico "posteriore scarico → sovrasterzo in trazione" è preservato,
ma ora è anche fisicamente corretto (in precedenza il retrotreno a caldo
mostrava 26.2 / 26.0, cioè SOTTO il valore a freddo: impossibile).

**Rev. FASE 2.1 (02/07/2026):** il delta cold→hot al retrotreno è stato portato da
+2.0 a **+2.5** (allineato al tipico +2.5–3.5) abbassando SOLO il freddo
(rl 26.2→25.7, rr 26.0→25.5) e lasciando **invariato il caldo** (28.2/28.0). Così
nessun valore visibile della telemetria cambia (gauge, heatmap, media 28.6,
finestra), la narrativa "retrotreno scarico" è preservata e la causa diventa più
esplicita (freddo retro sotto la finestra a freddo 26.0–27.0). L'advice cache di
Gigi (`ui/console.py`) è stato risincronizzato: posteriori a freddo **+1.0 · 25.5→26.5**.
→ **FASE 2.1 CHIUSA.**

**Nessuna trasformazione automatica** freddo→caldo viene applicata: i valori a
caldo sono dati demo dedicati. Il line/gauge della Telemetria usa SOLO `HOT_*`.

---

## ERR-02 — Finestra pressioni a caldo nella demo: 28.5–30.0 psi (rev. 2026-06-30)

**Scostamento:** il `system_prompt_v4.txt` (protetto) definisce, per le GT3 in
generale, finestra a CALDO target 29.0 psi (range 28.5–30.0) e a FREDDO 26.0–27.0.
La prima versione del restyle aveva adottato una finestra demo non standard
**27.0–27.8 psi** (con posteriori 26.2/26.0): comoda per la narrativa ma
fisicamente incoerente (a caldo < a freddo) e divergente dal prompt protetto.

**Decisione (rev. v2):** la finestra demo è stata **riallineata alla finestra ACC
reale del prompt protetto: 28.5–30.0 psi** (`ui/demo_data.HOT_PRESS_WINDOW`).
Anteriori in finestra (29.0/29.2), posteriori sotto finestra (28.2/28.0) ma
> a freddo. Così demo e LLM condividono la stessa finestra di riferimento: niente
più divergenza, e nessun rischio che un docente noti "a caldo sotto a freddo".
La risposta-cache di Gigi (`ui/console.DEMO_RESPONSE`) è stata risincronizzata
sui nuovi valori.

---

## ERR-03 — Temperatura Post.DX al giro 8 = 105°C (coerenza)

**Requisito:** il valore di picco della posteriore destra deve essere **105°C**
(non 103) e coincidere tra Telemetria (tooltip giro 8), Heatmap e Dashboard.

**Decisione:** `ui/demo_data.TYRE_TEMP_SERIES["rr"]` termina a 105; il MAX per
gomma (heatmap) è derivato dalla serie (`TYRE_TEMP_MAX`), quindi 88/90/95/105
sono garantiti coerenti per costruzione. Limite finestra temperatura = 95°C.

---

## ERR-04 — Pressione media Dashboard: 28.6 psi (rev. 2026-06-30)

**Scostamento:** il brief indicava "Pressione media 26.6 psi". Con il riallineamento
della finestra a caldo (ERR-02), la media aritmetica dei 4 valori a caldo
(29.0 + 29.2 + 28.2 + 28.0)/4 = **28.6 psi**.

**Decisione:** la card Dashboard mostra **28.6 psi**, calcolata dalla sorgente unica
(`ui/demo_data.PRESS_AVG_HOT`), per non divergere dai 4 gauge della Telemetria
(coerenza numerica > numero letterale del brief). La nota della card resta
"Retrotreno sotto finestra (28.5–30.0)": l'avviso si riferisce alle posteriori
(28.2/28.0), che sono sotto soglia, mentre la media include gli anteriori in finestra.

---

## ERR-05 — Precarico differenziale: UI 20–300 Nm vs prompt protetto 20–200

**Scostamento:** il brief v2 chiede per lo slider Precarico differenziale il range
ACC **20–300 Nm, step 10**. Il file protetto `prompts/system_prompt_v4.txt` (riga 57)
dichiara invece **20–200 Nm** come range di riferimento per i consigli dell'LLM.
(Nota: il brief affermava "il prompt clampa a 20–100"; verificato — il prompt è a
**20–200**, non 20–100.)

**Decisione (iniziale):** adottato 20–300 step 10 in `modules/setup_params.py`, in
divergenza col prompt protetto (20–200). Rischio: precarico > 200 Nm in demo mentre
l'LLM ragiona entro 200.

**CHIUSO (02/07/2026):** su decisione del committente lo slider UI è stato allineato al
prompt protetto → `modules/setup_params.py` riga 206 ora **`min:20, max:200, step:10`**
(default 60, in range). Nessun file protetto toccato (`system_prompt_v4.txt` era già a
20–200). Divergenza risolta. **Stato: RISOLTO.**

---

## ERR-06 — Prompt di sistema protetto EFFETTIVO: `system_prompt_v4.txt`

**Scostamento:** la Spec v3 §9 indica come artefatto protetto `prompts/system_prompt.txt`.
Nella repo reale esistono più prompt e il riferimento della spec non è quello caricato:
- `prompts/system_prompt_v4.txt` — **è quello effettivamente caricato** da `agent.py`
  (fonte di verità dei range ACC per i consigli dell'LLM);
- `backend/prompts/system_prompt.txt` (v3) — presente ma **non caricato da nessun modulo**;
- `prompts/chat_system_prompt.txt` — prompt del canale chat di Gigi.

**Decisione:** si dichiara `prompts/system_prompt_v4.txt` come **successore e artefatto
protetto effettivo** (v4 supera v3). Va trattato come file protetto (nessuna riscrittura
senza STOP gate). `backend/prompts/system_prompt.txt` resta come reperto storico v3, non
attivo. **Stato: DOCUMENTATO** (allineamento documentale, nessun file di prompt toccato).

---

## ERR-07 — Gap funzionali del branch restyle: RF-04 e storico SQLite non raggiungibili in UI

**Scostamento:** due funzioni descritte nella spec risultano implementate SOLO nel monolite
`app_legacy.py`, che **non è importato** dalla shell/router attuale (`app.py` → `ui/`):
- **RF-04 — calcolo carburante deterministico** (giri × consumo + margine);
- **storico sessioni SQLite** (`backend/database/manager.py`, salvataggio/lettura sessioni).

Nella UI **deployata** (branch restyle) queste non sono quindi raggiungibili: la Strategia
carburante è illustrata via risposta-cache demo (Engineer Console) e la Telemetria offre una
proiezione giri di sola lettura, fuori dalla fuel-logic protetta; lo storico non è esposto.

**Decisione:** è uno **scope consapevole della demo d'esame** (priorità: demo blindata e
coerente, non copertura funzionale completa). Recupero previsto **post-esame** (roadmap):
ricablare RF-04 e lo storico dalle basi già presenti in `app_legacy.py`/`backend/` dentro le
pagine `ui/`, dietro feature-flag, senza toccare la logica fuel/gauge protetta.
**Stato: DOCUMENTATO** (dichiarazione di scope; nessuna modifica di codice).

---

## ERR-08 — Range precarico differenziale: tre valori in circolazione

**Scostamento:** per il precarico differenziale coesistono tre riferimenti:
- Spec v3 / prompt v3: **20–100 Nm**;
- Prompt v4 (`system_prompt_v4.txt`) + `modules/setup_params.py`: **20–200 Nm** (stato attuale,
  cfr. ERR-05 già chiuso);
- Dato ACC reale (BMW M4 GT3): fino a **20–300 Nm**.

**Decisione (committente, opzione A):** si **documenta e mantiene 20–200 Nm** come range di
riferimento del progetto — **ceiling conservativo** rispetto al 300 reale, ma coerente con il
prompt protetto v4 e con lo slider UI già allineato (ERR-05). Vantaggio: nessuna modifica a
file protetti/params, nessuna riapertura di ERR-05; l'LLM e la UI ragionano sullo stesso range.
Limite accettato: più stretto del dato ACC reale (300). Un'eventuale estensione a 20–300
andrà in una **sessione dedicata con STOP gate** sui file prompt/params protetti.
**Stato: DOCUMENTATO** (solo documentazione; `system_prompt_v4.txt` e `setup_params.py` NON
toccati in questa sessione).
