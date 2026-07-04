# PitWall.AI — Script Demo & Checklist Esame (FASE 7)

> Documento operativo per la presentazione d'esame. Obiettivo: una demo fluida di
> ~5 minuti, con un piano B se il deploy o le API non rispondono.

---

## 0. Dati della demo

> ⚠️ **Distinzione importante (verificata in prova-generale 04/07):** le schermate sono in
> **demo-mode blindata** e leggono da `ui/demo_data.py` (**8 giri**, Monza · BMW M4 GT3) —
> NON dal CSV. Il CSV serve solo a *mostrare* la funzione di upload; caricarlo non cambia i
> numeri a video. Quindi **a voce parla sempre di "8 giri"**, che è ciò che si vede.

- **Dati a schermo (demo-mode, `ui/demo_data.py`):** **8 giri**, best 1:47.812, consumo medio
  **3.2 L/giro** (25.6 L totali).
  - Temperature a caldo: anteriori in range (88/90 °C), **Post.DX 105 °C** (oltre il limite 95 °C).
  - Pressioni **a caldo** (gauge/heatmap): ant. 29.0/29.2 in finestra, **post. 28.2/28.0 SOTTO
    finestra** (28.5–30.0) → è QUI che si legge il "retrotreno scarico".
  - **Caso didattico:** asse posteriore termicamente sovraccarico + pressioni posteriori sotto
    finestra → sovrasterzo in trazione. **Raccontalo sui dati a CALDO** (Telemetria/heatmap),
    non sulle pressioni a freddo.
- **CSV di sessione (illustrativo):** `backend/data/test_session.csv` (5 giri, pressioni a
  **freddo** 26.4–27.0 PSI, consumo 3.0–3.3). Usalo solo per far vedere l'upload nel Setup;
  le sue pressioni a freddo sono in finestra, quindi NON commentarci sopra il retrotreno.
- **Deploy:** https://pitwall-ai-dado.streamlit.app
- **Auto/pista già impostate in demo:** BMW M4 GT3 · Monza · Asciutto (il CSV ACC non contiene questi metadati).

---

## 1. Script demo (~5 min)

### [0:00] Apertura — login (30s)
- Apri il deploy. Mostra la **schermata di login** restyled (hero, badge MVP, form quick-login).
- Accedi col quick-login DEV. *Frase:* «Auth a SQLite, OAuth Google già predisposto».

### [0:30] Onboarding — Gigi (30s)
- Mostra la **welcome card di Gigi** (icona nuova, font self-hosted, niente flash).
- *Frase:* «Gigi è l'ingegnere virtuale: presento i dati, lui dà l'analisi tecnica».

### [1:00] Dashboard — metriche già popolate (45s)
- La **Dashboard** è già piena (demo-mode): **card metriche** con dato + grafico (sparkline
  temperature/consumo, window-bar pressione) e la nota d'**alert** su Post.DX e retrotreno.
- *Frase:* «8 giri, consumo medio 3.2 L, temperatura massima Post.DX 105°C — già evidenziata».
- *(Opzionale)* per mostrare la funzione upload: Setup → toggle **«Input sessione»** →
  expander **«Dati sessione»** → carica `test_session.csv`. **Nota:** è dimostrativo, le metriche
  restano quelle demo (non si ricalcolano dal CSV).

### [1:45] Telemetria (45s)
- Vai su **Telemetria**: line chart temperature per giro (toggle °C/°F, raw/smoothed),
  4 gauge pressioni, **heatmap 2×2** con il posteriore destro rosso; sotto, tabella giro-per-giro.
- *Frase:* «Si vede a colpo d'occhio: asse posteriore in sofferenza termica, pressioni post. sotto finestra».

### [2:30] Setup (45s)
- Apri **Setup** (BMW M4 GT3 · Monza già impostate): scorri i 5 tab, mostra un paio di slider
  (pressioni, ARB).
- *Frase:* «I 4 valori di pressione si colorano da soli vs la finestra ottimale a freddo
  (verde/ambra/rosso); i parametri suggeriti da Gigi sono in rosso».
- *(Nessun bottone Analizza qui: l'analisi si fa nella Engineer Console — passo successivo.)*

### [3:15] Engineer Console — feedback + analisi (75s)
- Apri **Engineer Console** (Gigi · online). Scrivi nel campo un feedback:
  *«L'auto scivola dietro in accelerazione»* (o usa un chip: Sottosterzo/Gomme/…).
- Premi **«⚙ ANALIZZA»**.
- Mostra il **report a 4 sezioni** numerato (01 Diagnosi → 02 Causa → 03 Correzione → 04 Note),
  con la card **Correzione** evidenziata come «Scheda Setup».
- *Frase:* «Output strutturato, terminologia ACC, correzione numerica azionabile —
  pressioni post. +1.0 psi, precarico 60→75 Nm».

### [4:30] Follow-up con Gigi (30s)
- **Nella stessa Engineer Console**, prova un altro scenario: clicca un chip diverso
  (es. **Analizza gomme**) o scrivi una nuova domanda → il report cambia in tempo reale.
- *Frase:* «Risposte diverse per scenario, tutte offline in demo-mode: la demo non dipende dalla rete».

### Chiusura
- *Frase:* «Design system unico, font self-hosted, deploy su Streamlit Cloud».

---

## 2. Checklist pre-esame (da spuntare la sera prima)

> ✅ **Giro a schermo del 04/07 (locale):** login, Dashboard, Telemetria, Setup e Console
> verificati insieme — tutto OK. Restano da spuntare solo i punti che NON abbiamo controllato
> a quel giro (evidenziati sotto): deploy sveglio, API live, no-fetch-Google via DevTools,
> responsive 768px, e la sezione Backup/Sicurezza.

### Funzionale
- [ ] Deploy raggiungibile e **sveglio** (apri il link 10 min prima — Streamlit Cloud va in sleep). *(da fare sul deploy)*
- [ ] **`ANTHROPIC_API_KEY`** valida e con credito (testa una analisi reale end-to-end). *(da fare — giro fatto in demo-mode)*
- [x] Login quick-DEV funziona. *(04/07)*
- [x] Dashboard/Telemetria/heatmap renderizzano (dati demo-mode) senza errori. *(04/07)*
- [ ] *(Opzionale)* Upload `test_session.csv` nel Setup mostra il messaggio «CSV letto: 5 giri…».
- [x] Engineer Console → **«⚙ ANALIZZA»** (o un chip) restituisce le **4 sezioni** senza errori. *(04/07)*
- [x] Cambiando chip/testo nella Console il report cambia (interattività demo). *(04/07)*

### Visivo (la verifica rimandata di tutte le fasi 1–6!)
- [x] Font corretti (Orbitron/Inter/JetBrains) — **niente flash** di font di sistema. *(04/07)*
- [ ] Nessun fetch a Google Fonts (DevTools → Network, filtra "fonts.google"). *(da verificare con DevTools)*
- [x] Card metriche, sparkline, gauge gomme, report 4 sezioni: stile coerente dark. *(04/07)*
- [x] Grafici plotly leggibili (assi/griglia/legenda). *(04/07)*
- [ ] Prova a **restringere la finestra** (responsive 768px): niente overflow rotto.

### Backup (piano B)
- [ ] **Registra un video** della demo completa che funziona (mp4, 1080p) — da proiettare se rete/API cadono.
- [ ] Screenshot chiave salvati: login, telemetria, report 4 sezioni.
- [ ] Copia locale eseguibile: `streamlit run app.py` con `.env` valido, testata offline-ish.
- [ ] CSV demo a portata di mano anche su chiavetta.

### Sicurezza (non mostrare a schermo)
- [ ] **`.env` con la API key NON in condivisione schermo** (è in `.gitignore`, ma sincronizzato su OneDrive — attenzione).
- [ ] Nessuna chiave nei log/terminale durante la demo.

---

## 3. Domande probabili & risposte secche

- **«Perché Streamlit?»** → Prototipazione rapida di data-app in Python, deploy gratuito, focus sul dominio (ACC) non sull'infra web.
- **«Come eviti allucinazioni del modello?»** → System prompt vincolato a 4 sezioni + terminologia ACC + uso esplicito dei dati CSV/setup come contesto; correzioni sempre con valore numerico verificabile.
- **«Freddo vs caldo sulle pressioni?»** → Distinzione obbligatoria (INC-002): finestra a freddo ~26.7 PSI, a caldo ~29.0; senza il contesto il modello classifica con la finestra sbagliata.
- **«Scalabilità / multiutente?»** → SQLite per l'MVP, OAuth Google predisposto; migrabile a Postgres.
- **«Font self-hosted, perché?»** → Affidabilità su Cloud e niente latenza/flash da Google Fonts: woff2 embeddati base64 una sola volta.
