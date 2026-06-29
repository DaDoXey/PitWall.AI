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
- `HOT_PRESSURES` = `{fl 27.4, fr 27.5, rl 26.2, rr 26.0}` (display telemetria).

**Nessuna trasformazione automatica** freddo→caldo viene applicata: i valori a
caldo sono dati demo dedicati. Il line/gauge della Telemetria usa SOLO `HOT_*`.

---

## ERR-02 — Finestra pressioni a caldo nella demo: 27.0–27.8 psi

**Scostamento:** il `system_prompt_v4.txt` (protetto) definisce, per le GT3 in
generale, finestra a CALDO target 29.0 psi (range 28.5–30.0) e a FREDDO 26.0–27.0.
Il brief di restyle chiede invece, per il display Telemetria, finestra ottimale
**27.0–27.8 psi** con anteriori in finestra (27.4/27.5) e posteriori basse
(26.2/26.0).

**Decisione:** adottata la finestra del brief (27.0–27.8) come **valore demo di
presentazione**, hardcoded in `ui/demo_data.HOT_PRESS_WINDOW`. Il system prompt
(file protetto, range ACC reali) **non è stato toccato**: resta la fonte di verità
per i consigli dell'LLM. Da confermare con il committente al gate Fase 2 se si
vuole allineare la narrativa demo alla finestra del prompt.

---

## ERR-03 — Temperatura Post.DX al giro 8 = 105°C (coerenza)

**Requisito:** il valore di picco della posteriore destra deve essere **105°C**
(non 103) e coincidere tra Telemetria (tooltip giro 8), Heatmap e Dashboard.

**Decisione:** `ui/demo_data.TYRE_TEMP_SERIES["rr"]` termina a 105; il MAX per
gomma (heatmap) è derivato dalla serie (`TYRE_TEMP_MAX`), quindi 88/90/95/105
sono garantiti coerenti per costruzione. Limite finestra temperatura = 95°C.

---

## ERR-04 — Pressione media Dashboard: 26.6 → 26.8 psi

**Scostamento:** il brief indica per la card Dashboard "Pressione media 26.6 psi".
La media aritmetica dei 4 valori a caldo canonici
(27.4 + 27.5 + 26.2 + 26.0)/4 = **26.775 ≈ 26.8 psi**.

**Decisione:** la card Dashboard mostrerà **26.8 psi**, calcolata dalla sorgente
unica (`ui/demo_data.PRESS_AVG_HOT`), per non divergere dai 4 gauge della
Telemetria (coerenza numerica > numero letterale del brief). Il "26.6" del brief
è quindi rettificato a 26.8. Da confermare al gate Fase 4.
