# PitWall.AI — Script Demo & Checklist Esame (FASE 7)

> Documento operativo per la presentazione d'esame. Obiettivo: una demo fluida di
> ~5 minuti, con un piano B se il deploy o le API non rispondono.

---

## 0. Dati della demo

- **CSV di sessione:** `backend/data/test_session.csv` (5 giri).
  - Posteriori caldi (RL ~94–98 °C, **RR ~101–105 °C**) vs anteriori in range (~87–92 °C).
  - Pressioni ~26.4–27.0 PSI (finestra a freddo OK), consumo ~3.0–3.3 L/giro.
  - **Caso didattico:** asse posteriore termicamente sovraccarico → spunto perfetto per
    raccontare sovrasterzo in trazione / pressioni-temperature.
- **Deploy:** https://pitwall-ai-dado.streamlit.app
- **Auto/pista da impostare a mano:** BMW M4 GT3 · Monza · Asciutto (il CSV ACC non contiene questi metadati).

---

## 1. Script demo (~5 min)

### [0:00] Apertura — login (30s)
- Apri il deploy. Mostra la **schermata di login** restyled (hero, badge MVP, form quick-login).
- Accedi col quick-login DEV. *Frase:* «Auth a SQLite, OAuth Google già predisposto».

### [0:30] Onboarding — Gigi (30s)
- Mostra la **welcome card di Gigi** (icona nuova, font self-hosted, niente flash).
- *Frase:* «Gigi è l'ingegnere virtuale: presento i dati, lui dà l'analisi tecnica».

### [1:00] Caricamento dati (45s)
- Sidebar → carica `test_session.csv`.
- Mostra le **card metriche** (dato + sparkline) e l'**alert automatico** sulle temperature.
- *Frase:* «5 giri, consumo medio, temperatura massima — già evidenziata in giallo/rosso».

### [1:45] Telemetria (45s)
- Scorri alla **sezione Telemetria**: line chart temperature per giro, bar chart consumo,
  **heatmap 2×2** con il posteriore destro rosso.
- *Frase:* «Si vede a colpo d'occhio: asse posteriore in sofferenza termica».

### [2:30] Setup + Feedback (60s)
- Imposta **BMW M4 GT3 / Monza / Asciutto**.
- Nei tab setup, mostra un paio di slider (pressioni, ARB).
- Scrivi un feedback: *«Sovrasterzo in uscita dalle curve lente, posteriore instabile»*.
- Seleziona **pressioni a freddo**. Premi **ANALIZZA SESSIONE**.

### [3:30] Report AI (60s)
- Mostra il **report a 4 sezioni** (Diagnosi → Causa → Correzione → Note) numerato.
- Evidenzia una **correzione numerica concreta** (es. pressioni/ARB/preload).
- *Frase:* «Output strutturato, terminologia ACC, valori azionabili».

### [4:30] Chat con Gigi (30s)
- Apri **Parla con Gigi**, domanda di follow-up (es. «e se la pista sale a 40°C?»).
- Mostra l'avatar animato e la risposta contestuale.

### Chiusura
- *Frase:* «Design system unico, font self-hosted, deploy su Streamlit Cloud».

---

## 2. Checklist pre-esame (da spuntare la sera prima)

### Funzionale
- [ ] Deploy raggiungibile e **sveglio** (apri il link 10 min prima — Streamlit Cloud va in sleep).
- [ ] **`ANTHROPIC_API_KEY`** valida e con credito (testa una analisi reale end-to-end).
- [ ] Login quick-DEV funziona.
- [ ] Upload `test_session.csv` → metriche, telemetria, heatmap renderizzano.
- [ ] **ANALIZZA SESSIONE** restituisce le 4 sezioni senza errori.
- [ ] Chat con Gigi risponde.

### Visivo (la verifica rimandata di tutte le fasi 1–6!)
- [ ] Font corretti (Orbitron/Inter/JetBrains) — **niente flash** di font di sistema.
- [ ] Nessun fetch a Google Fonts (DevTools → Network, filtra "fonts.google").
- [ ] Card metriche, sparkline, gauge gomme, report 4 sezioni: stile coerente dark.
- [ ] Grafici plotly leggibili (assi/griglia/legenda).
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
