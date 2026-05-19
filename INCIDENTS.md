---

# INCIDENTS — PitWall.AI
**Progetto:** PitWall.AI — Virtual Race Engineer per ACC
**Corso:** AI Projects Development — ITS ICT Academy Roma
**Autore:** Ferlito Edoardo

---

## INC-001 — Risposta LLM Troncata

| Campo | Dettaglio |
|---|---|
| ID | INC-001 |
| Data rilevamento | 19/05/2026 |
| Severità | Alta |
| Stato | RISOLTO |
| File coinvolto | `core/ai_logic.py` |

### Descrizione
Durante il primo test dell'agente PitWall.AI con dati reali
(Lamborghini Huracán GT3 EVO2 @ Monza), il report generato dall'LLM
risultava troncato. La sezione "Coerenza col feedback pilota" e tutto
il contenuto successivo venivano tagliati a metà, rendendo il report
inutilizzabile.

### Causa
Il parametro `max_tokens=1500` nella chiamata API ad Anthropic era
insufficiente. Il report completo con 4 sezioni obbligatorie
(Diagnosi, Causa Meccanica, Correzione Setup, Note Aggiuntive)
supera sistematicamente 1500 token quando l'input è dettagliato.

### Impatto
- Output incompleto — sezioni obbligatorie mancanti nella risposta
- Il meccanismo di retry esistente non veniva attivato perché la
  sezione "## Diagnosi" era presente (solo il resto veniva tagliato)
- Impossibile usare il report per diagnosi reali

### Fix Applicato
Modifica di una singola riga in `core/ai_logic.py`:

```python
# PRIMA
max_tokens=1500

# DOPO
max_tokens=2500
```

### Verifica
Dopo il fix, report completo con tutte e 4 le sezioni su input
dettagliato. Nessuna troncatura rilevata nei test successivi.

### Lezione Appresa
Il valore di `max_tokens` deve essere stimato in base alla lunghezza
massima attesa dell'output strutturato, non in base a un valore
arbitrario. Per output con formato fisso a 4 sezioni obbligatorie,
2500 token è il minimo sicuro con Claude Sonnet.

---

## INC-002 — Confusione Pressioni a Freddo / a Caldo

| Campo | Dettaglio |
|---|---|
| ID | INC-002 |
| Data rilevamento | 19/05/2026 |
| Severità | Critica |
| Stato | RISOLTO |
| File coinvolti | `core/physics.py`, `components/tab_setup.py`, `prompts/system_prompt.txt` |

### Descrizione
Durante l'analisi dei dati di test (pressioni ~26.7 PSI), l'agente
classificava i valori come "ottimali" indipendentemente dal fatto che
si trattasse di pressioni misurate a freddo (in garage) o a caldo
(lette dal MFD in pista durante la sessione). Questo produceva diagnosi
fisicamente sbagliate.

### Causa
Il sistema utilizzava 26.7 PSI come unico riferimento target per le
pressioni, senza distinguere tra i due contesti fisici:
- **A freddo (garage):** target 26.7 PSI — range sicuro 26.0–27.0 PSI
- **A caldo (MFD in pista):** target 29.0 PSI — range sicuro 28.5–30.0 PSI

Le pressioni a caldo sono ~2.5–3.5 PSI superiori a quelle impostate a
freddo. Trattarle come equivalenti porta a classificare come "ottimale"
una pressione a caldo di 26.7 PSI, che in realtà è circa 2.3 PSI sotto
la finestra operativa GT3 — condizione che causa usura irregolare delle
spalle e grip instabile.

### Impatto
- Diagnosi fisicamente incorrette per qualsiasi input con pressioni a
  caldo
- Il pilota avrebbe ricevuto consigli errati: nessuna correzione su
  pneumatici strutturalmente sottopressionati
- Violazione del principio fondamentale del sistema: i consigli devono
  essere vincolati ai range fisici reali di ACC

### Fix Applicato

**1. `core/physics.py` — Nuove costanti e metodo:**

Aggiunte costanti per il contesto a caldo:
```python
HOT_PRESSURE_MIN    = 28.5  # PSI operativa a caldo — letta dal MFD
HOT_PRESSURE_MAX    = 30.0  # PSI operativa a caldo — limite superiore GT3
HOT_PRESSURE_TARGET = 29.0  # PSI target operativo a caldo GT3
```

Aggiunto metodo `classify_pressure_context(psi, context)` che usa
il target corretto in base al contesto ("cold" o "hot").

**2. `components/tab_setup.py` — Radio button contesto:**

Aggiunto selettore obbligatorio prima degli input PSI:
```python
pressure_context = st.radio(
    "I valori PSI che stai inserendo sono:",
    options=[
        "A freddo (impostati in garage prima della sessione)",
        "A caldo (letti dal MFD in pista — tasto N)",
    ],
    horizontal=True,
)
ctx = "cold" if "freddo" in pressure_context else "hot"
```

**3. `prompts/system_prompt.txt` — Blocco distinzione obbligatoria:**

Aggiunto nella sezione PARAMETRI DI SICUREZZA:
```
PRESSIONI — DISTINZIONE OBBLIGATORIA
A FREDDO (garage): Target 26.7 PSI | Range 26.0–27.0 PSI
A CALDO (MFD):     Target 29.0 PSI | Range 28.5–30.0 PSI
Se il pilota non specifica il contesto, chiedere PRIMA di procedere.
```

### Verifica
Test TC-08: input PSI 26.7 con contesto "a caldo" → sistema classifica
correttamente come "cold" (sotto finestra operativa). Nessuna
classificazione "ottimale" scorretta nei test successivi.

### Lezione Appresa
Qualsiasi valore fisico che ha significati diversi in contesti diversi
dev'essere disambiguato esplicitamente nell'interfaccia prima di essere
processato. Non si può delegare all'utente l'assunzione implicita del
contesto.

---

*INCIDENTS compilato il 19/05/2026 — PitWall.AI MVP*

---
