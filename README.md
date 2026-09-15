# CAM — Nord Infissi

Raccolta degli strumenti CAM / preventivazione per la produzione di serramenti in alluminio.

**[`index.html`](index.html)** raccoglie i link a tutti i programmi HTML standalone del repo (apri il file nel browser).

## `commesse-lmt65/`
Generatore di commesse (tagli, lavorazioni, distinta, job XML per FSTLine) per il centro
di lavoro **FOM LMT 65**. App HTML standalone offline.
Serie AluK: C75S, C82S-CS (finestre), D67 / D77 = IWG 67ID / IWG 77ID (porte), S140 (alzante
scorrevole L&S / scorrevole in linea).

- Programma pronto all'uso: `commesse-lmt65/dist/Commesse_LMT65.html`
- Documentazione e stato del progetto: `commesse-lmt65/docs/DOSSIER_PROGETTO_LMT65.md`
- Guida per lo sviluppo: `commesse-lmt65/CLAUDE.md`
- Build e test: `cd commesse-lmt65 && ./build.sh`

## `commesse-cor80/`
Spinoff indipendente di `commesse-lmt65` per la serie **Cortizo COR 80 Evolution** (stesso motore
di calcolo, dati a sé). Nessun job di produzione di riferimento: tutte le lavorazioni sono `[DA TARARE]`.

- Programma pronto all'uso: `commesse-cor80/dist/Commesse_COR80.html`
- Documentazione: `commesse-cor80/docs/DOSSIER_COR80.md`

## `listini-serie/`
Generatore dei listini a griglia (prezzo per L × H) per **C75S**, **D67/D77** (porte) e **S140**:
legge le distinte delle tipologie direttamente dal programma commesse e i prezzi da `listini-db/`.

- Programma pronto all'uso: `listini-serie/Listini_Serie.html`

## `listini-db/`
Prezzi AluK (profili, accessori, ferramenta) in `listini.sqlite`, caricati dai listini PDF ufficiali;
sorgente dati per `listini-c75s/` e `listini-serie/`.

## `listini-c75s/`
Versione originale del listino, solo serie **C75S senza vetro, RAL 7016** — mantenuta come
riferimento storico (gli stessi dati vivono ora anche dentro `listini-serie/`).
FISSO, F1, F2, PF1, PF2. Produce i 5 file `.xlsx` con fogli Prezzo (griglia LISTINO e griglia
COSTO), Parametri, Coefficienti e Ferramenta.

```
pip install openpyxl
cd listini-c75s && python3 genera_listini.py
```

I 5 `.xlsx` versionati qui sono l'output esatto dello script con i parametri correnti
(rigenerandoli si riottengono identici); vedi `listini-c75s/README.md` per assunzioni e
voci di ferramenta ancora da completare.
