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
- `COLD_PRESSURES` = `{fl 26.5, fr 26.5, rl 26.2, rr 26.0}` (riferimento garage/CSV);
- `HOT_PRESSURES` = `{fl 29.0, fr 29.2, rl 28.2, rr 28.0}` (display telemetria).

**Vincolo fisico (rev. 2026-06-30):** a caldo SEMPRE > a freddo (la gomma in
esercizio scalda e la pressione sale di ~2.5–3.5 psi). I valori a caldo del
retrotreno (28.2 / 28.0) restano comunque **sotto la finestra** (28.5–30.0):
il caso didattico "posteriore scarico → sovrasterzo in trazione" è preservato,
ma ora è anche fisicamente corretto (in precedenza il retrotreno a caldo
mostrava 26.2 / 26.0, cioè SOTTO il valore a freddo: impossibile).

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

**Decisione:** adottato **20–300 step 10** in `modules/setup_params.py` (default 60,
in range), come da brief. Il file protetto **non è stato toccato** e resta 20–200.
→ **Divergenza nota e accettata:** se in demo si imposta un precarico > 200 Nm, il
consiglio dell'LLM potrebbe ragionare entro 200. Da confermare al committente se si
vuole allineare anche il prompt (richiede modifica a file protetto, fuori scope).
