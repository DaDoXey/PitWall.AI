# PROMPT_LOG — PitWall.AI
**Corso:** AI Projects Development — ITS ICT Academy Roma  
**Autore:** Ferlito Edoardo  
**Aperto:** 11/05/2026 (Lezione 4 — Build Day 1)

---

## Come usare questo file

Per ogni iterazione del System Prompt o di un sotto-prompt, crea una nuova entry con:
- **Data e contesto** — quando e perché hai modificato il prompt
- **Modifica apportata** — cosa hai cambiato (diff concettuale, non necessariamente il testo completo)
- **Motivazione** — problema che stavi risolvendo
- **Risultato osservato** — cosa è cambiato nell'output del modello
- **Decisione** — mantenuto / modificato ulteriormente / rollback

---

## Entry #001 — System Prompt v3 (baseline)

| Campo | Valore |
|---|---|
| Data | 10/05/2026 |
| Modello testato | claude.ai (iterazione manuale) |
| Versione prompt | v3 (Spec §6) |
| Contesto | Finalizzazione spec prima del build |

**Modifica:** Documento di partenza — nessuna modifica rispetto alla Spec v3 §6.  
**Motivazione:** Stabilire la baseline da cui misurare le variazioni.  
**Scenari testati (manualmente su claude.ai):**
- TC-01: sottosterzo BMW M4 GT3 a Monza → Output strutturato in 4 sezioni ✅
- TC-02: scivolo posteriore + CSV → Diagnosi integra dati CSV ✅  
- TC-03: "Come regolo il turbo?" → Rifiuto corretto ✅

**Risultato:** Baseline approvata. Nessun rollback necessario.

---

## Entry #002 — System Prompt v3.1 — Distinzione Pressioni Freddo/Caldo

| Campo | Valore |
|---|---|
| Data | 19/05/2026 |
| Modello testato | Anthropic Claude Sonnet via /v1/messages |
| Versione prompt | v3.1 |
| Contesto | TC-08: pressione a caldo interpretata come target freddo |

**Modifica:** Aggiunto blocco obbligatorio nel system prompt per distinguere pressioni a freddo (garage) da pressioni a caldo (MFD in pista). Inserita istruzione di chiedere chiarimenti se il contesto non è specificato.

**Motivazione:** Evitare diagnosi sbagliate generiche quando il modello riceve valori PSI senza indicare se si tratta di garage o MFD.

**Risultato osservato:** Il modello ora utilizza due target distinti e riporta esplicitamente la fonte del dato (freddo vs caldo). In caso di input ambiguo, la logica richiede chiarimento invece di emettere consigli errati.

**Decisione:** Mantenuto.

---

## Entry #003 — Validazione UI e Acceptance Test TC-04..TC-08

| Campo | Valore |
|---|---|
| Data | 27/05/2026 |
| Modello testato | claude-haiku-4-5-20251001 via API |
| Versione prompt | v3.1 |
| Contesto | Convalida ultimo ciclo di build UI, branding e casi di test di accettazione |

**Modifica:** Aggiornata UI con tema racing dark, favicon/titolo `PitWall.AI` e logo custom; validazione dei casi di test di accettazione dal TC-04 al TC-08.

**Motivazione:** Verificare che l'app risponda correttamente a input vaghi, gestisca errori CSV, calcoli la strategia carburante e interpreti correttamente il contesto freddo/caldo.

**Risultato osservato:**
- TC-04: richiesta di chiarimento sui valori PSI prima di una diagnosi. ✅
- TC-05: CSV con colonna `lap` mancante genera errore di schema e non causa crash. ✅
- TC-06: calcolo carburante eseguito correttamente e restituisce output nel range atteso. ✅
- TC-07: input temperatura CSV supportato, risposta qualitativa coerente e richiesta di contesto aggiuntivo. ✅
- TC-08: pressione 26.7 PSI in contesto `a caldo` classificata come fuori range, analisi bloccata con messaggio di validazione. ✅

**Nota:** l'upload CSV viene parsato correttamente e visualizzato, ma l'MVP usa ancora i valori manuali dei widget per il report principale. Questo è un limite da correggere in una iterazione successiva.

**Decisione:** Mantenuto.

---

<!-- TEMPLATE — copia e incolla per ogni nuova entry

## Entry #XXX — [titolo breve]

| Campo | Valore |
|---|---|
| Data | GG/MM/AAAA |
| Modello testato | Claude Sonnet / GPT-4o mini |
| Versione prompt | vX.Y |
| Contesto | [es. "TC-04 non chiedeva chiarimento su input vago"] |

**Modifica:**  
**Motivazione:**  
**Risultato osservato:**  
**Decisione:** ☐ Mantenuto  ☐ Modificato ulteriormente  ☐ Rollback  

-->
