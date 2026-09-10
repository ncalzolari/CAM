# Commesse LMT65 — guida per Claude Code

Generatore di commesse (tagli + lavorazioni + distinta) per il centro di lavoro **FOM LMT 65** (FSTLine), senza FP Pro.
App HTML **standalone offline**: `dist/Commesse_LMT65.html` (+ `dist/dati_serie.js`, archivio dati esterno opzionale letto all'avvio).
Serie: **AluK C75S** e **C82S-CS** (finestre, ferramenta Maico) — validate su job di produzione; **AluK D67 = IWG 67ID** e **D77 = IWG 77ID** (porte) — aggiunte il 07/09/2026, lavorazioni ferramenta DA TARARE; **Cortizo COR 80 Evolution** (`COR80`, finestre/portefinestre ala 39 e ala 21, ante a scomparsa/semivista/in vista) — aggiunta il 08/09/2026, stessa ferramenta Maico di C75S, tutte le lavorazioni DA TARARE (sez. 11 del dossier).

**Leggi prima `docs/DOSSIER_PROGETTO_LMT65.md`**: contiene le regole di produzione calibrate (sez. 5), il formato job (sez. 4), i sospesi (sez. 7) e tutto sulle porte (sez. 10). Le regole di produzione vincono sul catalogo: non "correggere" quote calibrate in base al catalogo.

## Struttura
- `src/app_template.html` — HTML/CSS con il segnaposto `/*__DATI__*/` (dopo `<script src="dati_serie.js"></script><script>`).
- `src/dati_app.json` — DATI base (C75S/C82S-CS): tipologie, ded, drain, maico, dxf_sez, libreria, vetrazione…
- `src/dati_porte.json` — DATI porte D67/D77, **generato** da `tools/build_porte.py` + `tools/porte_ferr.py` (non editare a mano: modifica gli script).
- `src/dati_cor80.json` — DATI serie Cortizo COR80, **generato** da `tools/build_cor80.py` (metadati tipologie, drenaggi, tavole vetro: modificare lo script, non il JSON).
- `src/app_logic.js` — logica dell'app (contiene il segnaposto `lavPorta` che `assemble.py` sostituisce con `src/porte_logic.js`).
- `src/porte_logic.js` — modulo lavorazioni porte (`lavPorta`), parametrico su `DATI.porte_ferr`.
- `src/cor80_logic.js` — motore di composizione COR80 (`componiMatriceCOR80`, sostituisce il segnaposto in `app_logic.js`), parametrico su `t.composta_cor80`.
- `data/catalogo_D67_D77/*.json` — trascrizioni del catalogo AluK (distinte di taglio 8.01-8.39, indice profili, accessori, lavorazioni del manuale).
- `data/catalogo_COR80/*.json` — trascrizioni del catalogo Cortizo COR 80 Evolution 12/2025 (`distinte.json` p.298-327, `profili_lista.json`, `vetrazione.json`, `accessori.json`), generate da `tools/cor80_estrai_catalogo.py <cartella PDF>` (+ correzioni manuali nella tabella FIX).
- `data/dxf/` — sezioni DXF dei profili: `D67`/`D77` dalla libreria macchina (`tools/dxf2svg.py` → `data/dxf_sez_porte.json`); `COR80` dai DXF Cortizo "SinCotas" (`tools/dxf_cor80.py` → `data/dxf_sez_cor80.json`, legge solo la sezione ENTITIES, layer 0/00_ALUMINIO/00_POLIAMIDAS).
- `tests/` — collaudi Playwright headless (Chromium); `tests/reference/` = versione precedente dell'app per la regressione.
- `docs/inventario_LDT_macchina.txt` — inventario delle macro .ldt della macchina (FP_CAM).

## Build
```
python3 tools/dxf2svg.py        # (solo se cambiano i DXF)
python3 tools/build_porte.py    # distinte JSON -> src/dati_porte.json
python3 tools/porte_ferr.py     # aggiunge porte_ferr + libreria a src/dati_porte.json
python3 tools/dxf_cor80.py      # (solo se cambiano i DXF Cortizo) -> data/dxf_sez_cor80.json
python3 tools/build_cor80.py    # catalogo COR80 JSON -> src/dati_cor80.json
python3 tools/assemble.py       # template + DATI (base ∪ porte ∪ COR80) + logica -> dist/Commesse_LMT65.html
```
oppure `./build.sh` (fa tutto e lancia i test).

## Test (obbligatori prima di consegnare)
```
npm install            # playwright (Chromium già presente in ambiente Anthropic; altrove: npx playwright install chromium)
node tests/regress.js  # C75S/C82S: l'output DEVE restare IDENTICO alla reference
node tests/job_test.js # porte: distinta + job XML + schemi pezzo senza errori
node tests/test_porte.js '[{"serie":"D67","tid":"D67_UN_ANTA_SOGLIA_AUTOMATICA_INT_Z","L":1000,"H":2200,"mano":"dx"}]'
node tests/cor80_test.js          # COR80: 14 righe (tipologie, divisore d'anta, maniglia centrata, 2 composte) -> distinta, lavorazioni [DA TARARE], job SYST COR80, schemi (--full per il JSON)
```
Se Playwright cerca un Chromium di build diversa da quello in `/opt/pw-browsers`, basta un symlink della cartella `chromium_headless_shell-<build>` (con `chrome-headless-shell-linux64/chrome-headless-shell` → `chrome-linux/headless_shell`).

## Regole di lavoro
- Sostituzioni nel codice sempre con **assert** sul numero di occorrenze (vedi `tools/patch1_applicata_2026-09-07.py`, `tools/patch2_cor80_applicata_2026-09-08.py`, `tools/patch3_cor80_opzioni_2026-09-08.py`, `tools/patch4_cor80_composta_2026-09-08.py`): una replace silenziosa ha già nascosto una toolbar per giorni.
- Una serie "a tipologia" (telaio/anta/vetro definiti da `telaio_rif`/`anta_rif`/`vetro_tav` come le porte) si dichiara in `DATI.serie_info[serie]` con `tip_profili:true`; `in_vista:true` attiva FX + ferramenta Maico di C75S (formule anta per tipologia `anta_h`/`anta_l`/`anta_l2`, `ferr:false` per le ante a scomparsa, `stulp:true` per le due ante con inversore); `da_tarare:true` marca ogni lavorazione `[DA TARARE]`; `specchio_y:{facce,asse}` specchia le Y delle facce indicate (COR80: F1/F4 rispetto a +40, taratura FSTLine 10/09/2026).
- Le quote vanno ancorate a tabelle/assi (AM, asse cerniera, HBB…), mai copiate come numeri sparsi.
- Ciò che non è validato su produzione resta marcato `[DA TARARE]` / `stato: da_tarare`. Meglio un foro mancante e dichiarato che uno inventato.
- Convenzione facce macchina (C75S, verificata): F1 superiore (zero a destra), F2 destra, F3 sinistra, F4 inferiore (zero a sinistra); ante ruotate 180° (rimappa solo a video). Per le porte le facce sono per analogia: vedi `DATI.porte_ferr.facce`, `x_da_alto_dx`, `dx_specchio`.
- Il file `dist/dati_serie.js` accanto all'HTML integra/sostituisce i DATI all'avvio (per id tipologia/libreria, merge per le sezioni-oggetto).
- Le correzioni puntuali alle lavorazioni (ΔX/ΔY/ΔZ, cambio faccia per serie/profilo/faccia/testo) si fanno dal pannello "Tarature lavorazioni" del programma (`DATI.tarature`, `applicaTarature()`), non nel codice: il codice contiene solo le regole strutturali (formule, specchiature di serie).
