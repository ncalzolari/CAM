# Commesse LMT65 — guida per Claude Code

Generatore di commesse (tagli + lavorazioni + distinta) per il centro di lavoro **FOM LMT 65** (FSTLine), senza FP Pro.
App HTML **standalone offline**: `dist/Commesse_LMT65.html` (+ `dist/dati_serie.js`, archivio dati esterno opzionale letto all'avvio).
Serie: **AluK C75S** e **C82S-CS** (finestre, ferramenta Maico) — validate su job di produzione; **AluK D67 = IWG 67ID** e **D77 = IWG 77ID** (porte) — aggiunte il 07/09/2026, lavorazioni ferramenta DA TARARE.

**Leggi prima `docs/DOSSIER_PROGETTO_LMT65.md`**: contiene le regole di produzione calibrate (sez. 5), il formato job (sez. 4), i sospesi (sez. 7) e tutto sulle porte (sez. 10). Le regole di produzione vincono sul catalogo: non "correggere" quote calibrate in base al catalogo.

## Struttura
- `src/app_template.html` — HTML/CSS con il segnaposto `/*__DATI__*/` (dopo `<script src="dati_serie.js"></script><script>`).
- `src/dati_app.json` — DATI base (C75S/C82S-CS): tipologie, ded, drain, maico, dxf_sez, libreria, vetrazione…
- `src/dati_porte.json` — DATI porte D67/D77, **generato** da `tools/build_porte.py` + `tools/porte_ferr.py` (non editare a mano: modifica gli script).
- `src/app_logic.js` — logica dell'app (contiene il segnaposto `lavPorta` che `assemble.py` sostituisce con `src/porte_logic.js`).
- `src/porte_logic.js` — modulo lavorazioni porte (`lavPorta`), parametrico su `DATI.porte_ferr`.
- `data/catalogo_D67_D77/*.json` — trascrizioni del catalogo AluK (distinte di taglio 8.01-8.39, indice profili, accessori, lavorazioni del manuale).
- `data/dxf/` — sezioni DXF dei profili dalla libreria macchina; `data/dxf_sez_porte.json` generato da `tools/dxf2svg.py`.
- `tests/` — collaudi Playwright headless (Chromium); `tests/reference/` = versione precedente dell'app per la regressione.
- `docs/inventario_LDT_macchina.txt` — inventario delle macro .ldt della macchina (FP_CAM).

## Build
```
python3 tools/dxf2svg.py        # (solo se cambiano i DXF)
python3 tools/build_porte.py    # distinte JSON -> src/dati_porte.json
python3 tools/porte_ferr.py     # aggiunge porte_ferr + libreria a src/dati_porte.json
python3 tools/assemble.py       # template + DATI (base ∪ porte) + logica -> dist/Commesse_LMT65.html
```
oppure `./build.sh` (fa tutto e lancia i test).

## Test (obbligatori prima di consegnare)
```
npm install            # playwright (Chromium già presente in ambiente Anthropic; altrove: npx playwright install chromium)
node tests/regress.js  # C75S/C82S: l'output DEVE restare IDENTICO alla reference
node tests/job_test.js # porte: distinta + job XML + schemi pezzo senza errori
node tests/test_porte.js '[{"serie":"D67","tid":"D67_UN_ANTA_SOGLIA_AUTOMATICA_INT_Z","L":1000,"H":2200,"mano":"dx"}]'
```

## Regole di lavoro
- Sostituzioni nel codice sempre con **assert** sul numero di occorrenze (vedi `tools/patch1_applicata_2026-09-07.py`): una replace silenziosa ha già nascosto una toolbar per giorni.
- Le quote vanno ancorate a tabelle/assi (AM, asse cerniera, HBB…), mai copiate come numeri sparsi.
- Ciò che non è validato su produzione resta marcato `[DA TARARE]` / `stato: da_tarare`. Meglio un foro mancante e dichiarato che uno inventato.
- Convenzione facce macchina (C75S, verificata): F1 superiore (zero a destra), F2 destra, F3 sinistra, F4 inferiore (zero a sinistra); ante ruotate 180° (rimappa solo a video). Per le porte le facce sono per analogia: vedi `DATI.porte_ferr.facce`, `x_da_alto_dx`, `dx_specchio`.
- Il file `dist/dati_serie.js` accanto all'HTML integra/sostituisce i DATI all'avvio (per id tipologia/libreria, merge per le sezioni-oggetto).
