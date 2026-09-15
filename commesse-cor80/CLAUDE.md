# Commesse COR80 — guida per Claude Code

Generatore di commesse (tagli + lavorazioni + distinta) per il centro di lavoro **FOM LMT 65** (FSTLine), un solo prodotto: **Cortizo COR 80 Evolution**.
Nato il 15/09/2026 come **spinoff indipendente** di `commesse-lmt65` (che copre le serie AluK: C75S, C82S-CS, D67, D77, S140): stesso motore di calcolo (copiato, non condiviso), solo i dati COR80.
App HTML **standalone offline**: `dist/Commesse_COR80.html` (+ `dist/dati_serie.js`, archivio dati esterno opzionale letto all'avvio).

**Leggi prima `docs/DOSSIER_COR80.md`**: contiene tutto quello che si sa sulla serie (fonti, tipologie, distinte, vetrazione, drenaggi, opzioni, costruttore a griglia, tarature, orientamento macchina, sospesi). Nessun job FP Pro di riferimento: la serie non è mai stata prodotta, ogni lavorazione è marcata `[DA TARARE]`.

## Struttura
- `src/app_template.html` — HTML/CSS con il segnaposto `/*__DATI__*/` (dopo `<script src="dati_serie.js"></script><script>`). Motore generico, copiato identico da commesse-lmt65.
- `src/app_logic.js` — logica dell'app (motore generico, guidato dai dati: profili/accessori/guarnizioni/vetro/dxf_sez/lav_def per serie). Contiene anche gli hook per porte (`lavPorta`, mai usato qui: resta il suo stub no-op) e S140 (`kitS140Accessori`, mai invocato: nessuna tipologia ha `kit_s140`) — codice morto innocuo, non rimosso per non toccare un motore condiviso e collaudato.
- `src/cor80_logic.js` — motore di composizione COR80 (`componiMatriceCOR80`), sostituisce il segnaposto in `app_logic.js`.
- `src/dati_base_ferramenta.json` — **le due sole tabelle generiche che il motore legge incondizionatamente all'avvio** e che COR80 riusa da C75S per scelta di progetto ("stessa ferramenta Maico"): `maico` (quote Maico) e `ded.C75S` (tabella detrazioni, fallback `DED[t.serie]||DED['C75S']`). Il resto sono oggetti vuoti richiesti dal motore ma non usati da COR80 (`varianti`, `traversi_default`, `pb_telaio`, `stulp_map`, `composta`, `ante_disponibili`, `nota_detrazioni`, `faccia_fisica`). Vedi la nota in fondo al dossier.
- `src/dati_cor80.json` — DATI serie COR80, **generato** da `tools/build_cor80.py` (metadati tipologie, drenaggi, tavole vetro: modificare lo script, non il JSON).
- `data/catalogo_COR80/*.json` — trascrizioni del catalogo Cortizo COR 80 Evolution 12/2025 (`distinte.json` p.298-327, `profili_lista.json`, `vetrazione.json`, `accessori.json`), generate da `tools/cor80_estrai_catalogo.py <cartella PDF>` (+ correzioni manuali nella tabella FIX dello script).
- `data/dxf/COR80/*.dxf` — 57 DXF Cortizo "SinCotas" (sezioni profilo).
- `data/dxf_sez_cor80.json` — sezioni SVG, generate da `tools/dxf_cor80.py` (legge solo la sezione ENTITIES, layer 0/00_ALUMINIO/00_POLIAMIDAS).
- `tools/patch2…patch7*.py` — patch storiche applicate ad `app_logic.js` **in commesse-lmt65** (conservate qui come documentazione/provenienza: l'`app_logic.js` copiato le contiene già tutte applicate, non vanno rieseguite).
- `tests/cor80_test.js` — collaudo Playwright headless (14 righe: tipologie, divisore d'anta, maniglia centrata, 2 composte).
- `docs/DOSSIER_COR80.md` — tutto il sapere di dominio sulla serie.

## Build
```
python3 tools/dxf_cor80.py      # (solo se cambiano i DXF Cortizo) -> data/dxf_sez_cor80.json
python3 tools/build_cor80.py    # catalogo COR80 JSON -> src/dati_cor80.json
python3 tools/assemble.py       # template + dati_base_ferramenta + dati_cor80 + app_logic + cor80_logic -> dist/Commesse_COR80.html
python3 tools/build_web.py      # versione per Artifact claude.ai -> dist/Commesse_COR80_web.html
```
oppure `npm run build` (fa i tre passi assemble/build_web, non i DXF che cambiano raramente).

## Test (obbligatori prima di consegnare)
```
npm install             # playwright (Chromium già presente in ambiente Anthropic; altrove: npx playwright install chromium)
node tests/cor80_test.js          # 14 righe -> distinta, lavorazioni [DA TARARE], job SYST COR80, schemi (--full per il JSON)
```
Se Playwright cerca un Chromium di build diversa da quello in `/opt/pw-browsers`, basta un symlink della cartella `chromium_headless_shell-<build>` (con `chrome-headless-shell-linux64/chrome-headless-shell` → `chrome-linux/headless_shell`).

## Regole di lavoro (ereditate da commesse-lmt65, ancora valide qui)
- Sostituzioni nel codice sempre con **assert** sul numero di occorrenze: una replace silenziosa ha già nascosto una toolbar per giorni in commesse-lmt65.
- Le quote vanno ancorate a tabelle/assi (AM, asse cerniera, HBB…), mai copiate come numeri sparsi.
- Ciò che non è validato su produzione resta marcato `[DA TARARE]` / `stato: da_tarare`. Meglio un foro mancante e dichiarato che uno inventato. **Tutta** la serie COR80 è in questo stato: nessun job di produzione di riferimento esiste ancora.
- Convenzione facce macchina: F1 superiore (zero a destra), F2 destra, F3 sinistra, F4 inferiore (zero a sinistra); per COR80 le facce 1 e 4 sono **specchiate** rispetto all'asse a +40 (profondità profilo 80 mm), incorporato nei valori di `lav_def.COR80` (vedi dossier).
- Il file `dist/dati_serie.js` accanto all'HTML integra/sostituisce i DATI all'avvio (per id tipologia/libreria, merge per le sezioni-oggetto).
- Le correzioni puntuali alle lavorazioni (ΔX/ΔY/ΔZ, cambio faccia) si fanno dal pannello "Tarature lavorazioni" del programma, non nel codice.
- I **valori** delle lavorazioni stanno nella **libreria operativa** `DATI.lav_def.COR80[chiave]`, letta con `lavDef(chiave)`; si modifica dal foglio Libreria, salvata in `localStorage` ed esportata in `dati_serie.js`.
- **Orientamento in macchina**: `DATI.ruota180.COR80` (tutta la serie ruotata di 180° rispetto ai DXF Cortizo); `ruotato180(prof, serie)`/`trasfDxf()` ruotano solo i disegni, mai le facce/Y del job da soli — usare il pulsante "scambia le facce delle lavorazioni" per quello.
