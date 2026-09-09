# Database listini (AluK)

Listini fornitore caricati dai PDF in un database SQLite interrogabile, con gli sconti concordati e i prezzi netti calcolati.

| File | Contenuto |
|---|---|
| `listini.sqlite` | database (tabelle + viste) |
| `csv/*.csv` | esportazione delle tabelle (separatore `;`), leggibile e confrontabile in git |
| `carica_listini_aluk.py` | loader: PDF → SQLite + CSV (`pip install pymupdf`) |
| `prezzo.py` | interrogazione da riga di comando |
| `Listino_profili_260615.pdf`, `Listino_Accessori_AluK_260615.pdf`, `Listino_C75S_C82SCS_260615.pdf` | listini AluK con decorrenza 15-06-2026 |

## Sconti in vigore (tabella `sconti`)
- AluK **profili 38 %** sul listino profili generale (porte D67/D77): €/kg grezzo + aggregazione colore
- AluK **profili C75S/C82S-CS 43 %** sugli articoli a kg del listino C75S/C82S-CS (categoria `profili_c75s_c82s`)
- AluK **accessori 20 %** sul prezzo di listino (confezione e unitario), per entrambi i listini

Per cambiarli: `sqlite3 listini.sqlite "INSERT OR REPLACE INTO sconti VALUES('AluK','profili',0.40,'2027-01-01')"` — le viste usano sempre lo sconto con decorrenza più recente.

## Tabelle
- `listini` — un record per listino caricato (fornitore, tipo `profili` / `accessori` / `c75s_c82s`, decorrenza, file). Ricaricare lo stesso listino lo sostituisce.
- `accessori` — 1.691 articoli: codice, descrizione, UM (CF confezione / PZ / ML), prezzo listino della confezione, pezzi per confezione (metri per rotolo per le guarnizioni), minimo di vendita, prezzo unitario, stato, note.
- `profili_serie` — 57 serie commerciali a 3 cifre con €/kg del grezzo (es. 313 C77K 16,15; 312 D67 15,92; 366 C67K 15,92).
- `finiture` — aggregazioni colore a 2 caratteri con €/kg aggiuntivo (FA…FE cartella senza addebito, 20/23/25/30 con addebito, 60-75 fuori cartella, ossidati, effetto legno, bicolore) e maggiorazioni (sabbiatura, seaside, pretrattamento).
- `addebiti` — importi fissi (3++20, 3++60…, cambio colore).
- `colori` — 90 codici colore a 6 caratteri con classe, sigla, aggregazione monocolore/bicolore, sezione dell'elenco.
- `accessori` del listino C75S/C82S-CS (36 articoli, tipo `c75s_c82s`): in più confezioni per imballo e pezzi per imballo (`cf_imballo`, `pz_imballo`); codici con suffisso colore (`V52055-B`, `V52083-B`).
- `profili_articoli` — listino C75S/C82S-CS: 73 articoli profilo a kg già composti (serie + aggregazione): **333xx = profili a taglio termico** (33300 grezzo 18,18; 33320 cat. B con addebito 19,93; 333FB senza addebito 19,93), **108xx = profili non isolati** (10800 grezzo 13,07; 10820 cat. B 14,82), **182xx = profili con guarnizione premontata** (18200 grezzo 18,18), 33390 bicolore 21,13.
- `serie_app` — serie del programma commesse → serie commerciale del listino (D67 → 312, D77 → 315, C75S e C82S-CS → 333 con nota sull'attribuzione 333/108/182 per profilo).
- Viste: `v_accessori` (listino + netto, colonna `listino` = accessori generale o c75s_c82s), `v_profili` (serie × finitura del listino profili generale), `v_profili_articoli` (articoli a kg del listino C75S/C82S-CS), `v_sconto`.

Il prezzo di un profilo AluK si ottiene per peso: **articolo di fatturazione = serie (3 cifre) + aggregazione colore (2 caratteri)**, es. `31320` = C77K verniciato cartella cat. B con addebito = 16,15 + 1,75 = 17,90 €/kg di listino, 11,098 €/kg netto.

## Esempi
```
python3 prezzo.py --sconti
python3 prezzo.py V40014 809119 712010
python3 prezzo.py --cerca "guarn. int"
python3 prezzo.py --serie 313 --finitura 20 --kg 12.5
python3 prezzo.py --serie C75S --finitura 20 --kg 10     # -> articolo 33320
python3 prezzo.py --articolo 10820
sqlite3 listini.sqlite "SELECT codice, descrizione, prezzo_netto_unitario FROM v_accessori WHERE codice LIKE 'V40%'"
```

## Note
- Il listino profili generale vale per le **porte D67 / D77** (IWG 67ID / 77ID): `serie_app` → D67 = serie 312 (15,92 €/kg), D77 = serie 315 (16,15 €/kg). Le finestre **C75S / C82S-CS** hanno il proprio listino (`Listino_C75S_C82SCS_260615.pdf`) con articoli a kg già composti.
- Il generatore `listini-c75s` usa l'articolo `10820` (14,82 €/kg, profili **non isolati**) per tutti i profili: per i profili a taglio termico B23xxx l'articolo corretto è probabilmente `33320` (19,93 €/kg) — da confermare con AluK/fatture. Lo sconto 43 % del generatore coincide con quello del database per questo listino.
- `V52055` è a listino come `V52055-B` (nero); `V40037` non compare in nessuno dei due listini accessori.
- Per aggiungere un altro fornitore: nuovo loader che scrive nelle stesse tabelle con `fornitore` diverso e la sua riga in `sconti`.
