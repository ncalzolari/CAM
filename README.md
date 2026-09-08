# CAM — Nord Infissi

Raccolta degli strumenti CAM / preventivazione per la produzione di serramenti in alluminio.

## `commesse-lmt65/`
Generatore di commesse (tagli, lavorazioni, distinta, job XML per FSTLine) per il centro
di lavoro **FOM LMT 65**. App HTML standalone offline.
Serie AluK: C75S, C82S-CS (finestre) e D67 / D77 = IWG 67ID / IWG 77ID (porte); Cortizo COR 80 Evolution
(finestre e portefinestre, ante a scomparsa / semivista / in vista).

- Programma pronto all'uso: `commesse-lmt65/dist/Commesse_LMT65.html`
- Documentazione e stato del progetto: `commesse-lmt65/docs/DOSSIER_PROGETTO_LMT65.md`
- Guida per lo sviluppo: `commesse-lmt65/CLAUDE.md`
- Build e test: `cd commesse-lmt65 && ./build.sh`

## `listini-c75s/`
Generatore dei listini a griglia (prezzo per L × H) per la serie **C75S senza vetro, RAL 7016**:
FISSO, F1, F2, PF1, PF2. Produce i 5 file `.xlsx` con fogli Prezzo (griglia LISTINO e griglia
COSTO), Parametri, Coefficienti e Ferramenta.

```
pip install openpyxl
cd listini-c75s && python3 genera_listini.py
```

I 5 `.xlsx` versionati qui sono l'output esatto dello script con i parametri correnti
(rigenerandoli si riottengono identici); vedi `listini-c75s/README.md` per assunzioni e
voci di ferramenta ancora da completare.
