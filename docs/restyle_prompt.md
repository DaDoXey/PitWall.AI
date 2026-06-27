# PitWall.AI — Prompt Restyle UX/UI per Claude Code (Multi-Fase, Definitivo)

> Incolla questo file in Claude Code. È strutturato a fasi con STOP gate obbligatori.
> Le decisioni di design sono già prese (vedi DESIGN BRIEF): non chiedermele di nuovo, applicale.
> Claude Code NON deve procedere alla fase successiva senza la mia conferma esplicita.

---

## ⛔ REGOLE GLOBALI (valide per tutte le fasi)

1. **STOP gate obbligatori.** Alla fine di ogni fase ti fermi, mi mostri il risultato e **aspetti il mio "ok, vai" prima di continuare**. Mai incatenare le fasi.
2. **FILE PROTETTI — non toccare mai, per nessun motivo:**
   - `agent.py` (logica chiamata LLM + retry/fallback modelli)
   - `backend/parser/csv_parser.py` e `backend/parser/__init__.py` (parsing/validazione CSV)
   - I system prompt: `prompts/system_prompt_v4.txt`, `prompts/chat_system_prompt.txt`, `backend/prompts/system_prompt.txt`
   - **NB: la logica gauge e fuel strategy NON sono file separati — vivono DENTRO `app.py`** (gauge pressioni/temperature gomme ~riga 1532; tab Strategia Carburante ~riga 1678). In `app.py` quindi tocca **solo markup/stile**, mai i calcoli: medie, range ACC, conversione pressioni freddo/caldo (INC-002), formula carburante.
   - Questo è un restyle **UI/CSS**. Dei gauge si tocca **solo l'aspetto**, mai il calcolo. Se una modifica estetica sembra richiedere di toccare la logica di questi file/blocchi, **fermati e chiedimelo**.
3. **Vincolo critico Streamlit Cloud — NON negoziabile:**
   - La CSS injection con `st.markdown(unsafe_allow_html=True)` su **selettori interni di Streamlit** (es. `button[kind="secondary"]`, classi generate) **è inaffidabile su Streamlit Cloud**: funziona in locale e si rompe in deploy.
   - Per i componenti UI custom usa **`st.components.v1.html()` con HTML nativo + inline styles**.
   - **Vietati i selettori wildcard (`*`)**: fanno danni collaterali al DOM interno di Streamlit. Usa selettori precisi `data-testid`.
4. **Restyle incrementale.** Mai riscrivere `app.py` da zero. Un componente alla volta, app sempre funzionante tra un passo e l'altro.
5. **Deploy target:** Streamlit Community Cloud (`pitwall-ai-dado.streamlit.app`). Ogni soluzione deve reggere **lì**, non solo in locale.

---

## 🎨 DESIGN BRIEF (decisioni già prese — applicare, non ridiscutere)

**Direzione visiva**
- Dark racing **rifinito** con anima **pit-wall reale** e forte presenza di **telemetria/grafici**. Estetica **pulita e professionale**, non gaming chiassoso.
- **PRIORITÀ ASSOLUTA: dark mode perfetto.** L'esame è imminente: le fasi 1-6 si concentrano sul tema scuro. Il design system va comunque strutturato con token (`:root`) predisposti per un secondo tema, ma il **light mode è nice-to-have POST-esame** — non implementarlo/rifinirlo ora, non costruire il toggle finché non te lo chiedo. Non spendere tempo su contrasti e colori grafici per il tema chiaro in questa fase.

**Palette (fonte di verità — i colori in deriva nel codice vanno sanati)**
```
Backgrounds (dark):  #0a0a0a  /  #111111  /  #1a1a1a
Accento primario:    #E8002D     Hover: #CC0028
Testo (dark):        #FFFFFF (primario) / #999999 (secondario) / #666666 (muted)
Status green:        #00C853
Bordi:               #222 / #333
Light mode:          deriva il set chiaro mantenendo #E8002D come accento e
                     garantendo buon contrasto (vedi più sotto).
Font:                Orbitron (titoli) · Inter (testo) · JetBrains Mono (numerici/codice)
```
> ⚠️ Colori come `#00FF87` / `#00A3FF` trovati nel codice **non** sono il design system: sono il problema "colori hardcoded incoerenti". Migra tutto verso la palette qui sopra.

**Struttura**
- **Sidebar persistente** = contesto globale (auto, circuito, sessione, login/utente).
- **Tab orizzontali** nell'area principale per le categorie setup (Tyres / Electronics / Mechanical Grip / Dampers / Aero).
- **Dashboard stile cockpit/cruscotto**: fascia hero con metriche live + **card modulari**, ogni card con **dato numerico E grafico**.

**Gigi (race engineer)**
- Non una chat banale: una **"console ingegnere"** integrata, dove lo consulti come il tuo vero race engineer, con **contesto sempre visibile** (auto/circuito/sessione) e il report a 4 sezioni che nasce lì dentro.
- **Nuova icona:** sagoma **pulita e minimale di un ingegnere**, niente fronzoli. Avatar **statico ma curato**.

**Report 4 sezioni (Diagnosi / Causa / Correzione / Note)**
- Mix di formati (card/accordion/tab/timeline) ma con **gerarchia visiva immediata**, leggibile "a colpo d'occhio come i dati nel box".

**Telemetria e grafici (elemento portante del progetto)**
- **Sezione telemetria completa**: pressioni + temperature gomme (4 ruote), consumo/stint, andamento parametri setup.
- **Stile misto secondo il dato**: linee temporali giro-per-giro, gauge circolari, **heatmap gomme su schema auto**.
- **Plotly interattivo** (hover, zoom) con **animazione progressiva** all'analisi.

**Vincoli tecnici**
- Restiamo su **Streamlit** (compromesso pragmatico): `st.components.v1.html()` per i pezzi custom, `streamlit-extras` con parsimonia, **plotly** per i grafici. Niente front-end separato.
- **Desktop-first**, mobile che non si rompe ma non ottimizzato al millimetro.
- **Buon contrasto** (testo leggibile in dark e light) senza audit WCAG completo.
- **Login:** estetica rinnovata + micro-miglioramenti del flusso, **logica OAuth Google intatta**.

---

## 📍 FASE 0 — Lettura e mappatura del codice (NO CODICE)

Leggi e riassumi:
1. `app.py` — individua e **conta**, con numero di riga: ogni `unsafe_allow_html`, ogni `<style>` inline, ogni `st.markdown` con HTML, ogni `st.components.v1.html`, ogni `st.rerun`.
2. `assets/style.css`, `styles/login.css`, `assets/css_loader.py`, `pages/login.py`.
3. Asset: `assets/gt3_silhouette.svg` e dove vive l'attuale icona di Gigi.
4. `requirements.txt` (verifica `plotly`, `streamlit-extras`).

**Output FASE 0** (solo testo):
- Mappa dei punti dove vive lo stile (file + righe).
- Colori realmente usati nel codice vs palette ufficiale → evidenzia le derive.
- Componenti UI principali e dove sono definiti.
- Conferma esplicita dei file protetti che NON toccherai.

➡️ **STOP. Mostrami la mappa e aspetta il mio ok.**

---

## 📍 FASE 1 — Design system (PRIMO CODICE) — focus DARK

Produci:
1. File CSS centrale unico (es. `assets/design_system.css`) con `:root` di **CSS custom properties**: colori, spaziature, tipografia, raggi, ombre, breakpoint. **Struttura i token sotto `[data-theme="dark"]`** così che un futuro tema chiaro sia aggiungibile, ma **rifinisci e implementa solo il dark**. NON costruire il toggle né il set light ora.
2. **Font self-hosted** (Orbitron / Inter / JetBrains Mono) caricati **una sola volta**, per eliminare il re-fetch di Google Fonts a ogni render (niente flash/latenza).

Non applicare ancora nulla ai componenti: solo il sistema di token + come viene caricato.

➡️ **STOP. Approvo i token prima di andare avanti.**

---

## 📍 FASE 2 — Nuova icona di Gigi

1. Proponimi **2-3 concept SVG** di una sagoma **pulita e minimale di un ingegnere** (coerente con la palette e lo stile pit-wall). Descrivili e mostrami il codice SVG.
2. Aspetta che io scelga.
3. Realizza la versione scelta come asset SVG e predisponi dove sostituirà l'icona attuale.

➡️ **STOP dopo i concept. Scelgo io, poi finalizzi.**

---

## 📍 FASE 3 — Estrazione stile inline → CSS esterno (incrementale)

Sposta lo stile da `app.py` verso il CSS esterno, **un lotto alla volta**, partendo dai blocchi più riusati. Per ogni lotto:
- Mostra "prima" (riga in `app.py`) e "dopo" (regola CSS).
- Usa `data-testid` precisi, mai wildcard `*`.
- Componenti custom dipendenti da selettori interni Streamlit → riscrivili con `st.components.v1.html()`.
- App funzionante dopo ogni lotto.

➡️ **STOP tra un lotto e l'altro.**

---

## 📍 FASE 4 — Restyle componenti chiave (uno alla volta)

Ordine:
1. **Login** — estetica nuova + micro-miglioramenti flusso, **logica OAuth intatta**.
2. **Sidebar** (contesto globale) + **shell dashboard** stile cockpit.
3. **Card modulari** della dashboard (dato + grafico).
4. **Console Gigi** — area integrata "consulta il tuo ingegnere", contesto sempre visibile, con la nuova icona della FASE 2.
5. **Report 4 sezioni** — gerarchia visiva immediata.
6. **Tab setup** (Tyres/Electronics/Mechanical Grip/Dampers/Aero) + slider + metriche.
7. **Gauge** — **solo aspetto**, logica intoccabile.

Per ogni componente: proposta → mio ok → implementazione → verifica visiva.

➡️ **STOP dopo ogni componente.**

---

## 📍 FASE 5 — Sezione telemetria completa (plotly)

Costruisci la sezione telemetria leggendo i dati dal CSV già parsato (senza toccare `backend/parser/csv_parser.py`):
- **Linee temporali** giro-per-giro (pressioni, temperature, consumo/stint).
- **Gauge circolari** per i valori istantanei/sintetici.
- **Heatmap gomme su schema auto** (4 ruote, press + temp).
- Tutti **plotly interattivi** (hover, zoom) con **animazione progressiva** all'analisi.
- Coerenza cromatica con il design system; soglie/limiti ACC evidenziati visivamente (es. fuori-range in `#E8002D`, ok in `#00C853`).

➡️ **STOP. Mostrami la sezione completa.**

---

## 📍 FASE 6 — Responsività, contrasto, pulizia rerun

1. `@media query` **desktop-first**: l'app non deve rompersi su tablet/telefono (mobile = bonus, non ottimizzazione spinta).
2. Verifica **contrasto** nel tema dark (testo, caption, accenti) — buono, senza audit formale.
3. Riduci/raggruppa gli `st.rerun` che generano flicker, **senza alterare la logica funzionale**.

➡️ **STOP. Report finale del restyle.**

---

## 📍 FASE 7 — Backup demo video (esame ~2 luglio)

Aiutami a preparare una **registrazione di backup** della demo, da usare come rete di sicurezza se la live va storta:
1. **Scaletta del video** (2-4 min): login → caricamento `demo_session_monza_bmw.csv` (BMW M4 GT3 a Monza, 8 giri) → console Gigi → report 4 sezioni → telemetria/grafici → strategia carburante.
2. **Punti da evidenziare** che impressionano: cross-check oggettivo/soggettivo, grafici telemetria, vincoli range ACC rispettati.
3. **Checklist registrazione** (risoluzione, finestra, audio/commento, durata, cosa NON mostrare).
4. Nota i **punti deboli** da non sollecitare in demo (es. raccomandazione bumpstop priva di supporto CSV).

➡️ **STOP. Mi consegni scaletta + checklist.**

---

## ✅ VERIFICA FINALE

- [ ] Nessun file protetto modificato (`agent.py`, `backend/parser/csv_parser.py`, i `*_prompt*.txt`) e nessun calcolo gauge/fuel alterato dentro `app.py`.
- [ ] Zero CSS injection su selettori interni Streamlit per componenti custom (usato `st.components.v1.html()`).
- [ ] Zero selettori wildcard `*`.
- [ ] Design system con token strutturati; **dark mode rifinito** (light rimandato post-esame); derive `#00FF87`/`#00A3FF` eliminate.
- [ ] Font self-hosted, caricati una sola volta.
- [ ] Nuova icona Gigi integrata.
- [ ] Sezione telemetria completa con grafici plotly interattivi.
- [ ] App testata **in deploy su Streamlit Cloud**, non solo in locale.
- [ ] App funzionante a ogni step intermedio.

Riepilogami: file toccati, righe spostate da inline a CSS, componenti ridisegnati, problemi residui.
