# Database listini (AluK)

Listini fornitore caricati dai PDF in un database SQLite interrogabile, con gli sconti concordati e i prezzi netti calcolati.

| File | Contenuto |
|---|---|
| `listini.sqlite` | database (tabelle + viste) |
| `csv/*.csv` | esportazione delle tabelle (separatore `;`), leggibile e confrontabile in git |
| `carica_listini_aluk.py` | loader: PDF → SQLite + CSV (`pip install pymupdf`) |
| `prezzo.py` | interrogazione da riga di comando |
| `Listino_profili_260615.pdf`, `Listino_Accessori_AluK_260615.pdf` | listini AluK con decorrenza 15-06-2026 |

## Sconti in vigore (tabella `sconti`)
- AluK **profili 38 %** sul €/kg di listino (grezzo + aggregazione colore)
- AluK **accessori 20 %** sul prezzo di listino (confezione e unitario)

Per cambiarli: `sqlite3 listini.sqlite "INSERT OR REPLACE INTO sconti VALUES('AluK','profili',0.40,'2027-01-01')"` — le viste usano sempre lo sconto con decorrenza più recente.

## Tabelle
- `listini` — un record per listino caricato (fornitore, tipo `profili`/`accessori`, decorrenza, file). Ricaricare lo stesso listino lo sostituisce.
- `accessori` — 1.691 articoli: codice, descrizione, UM (CF confezione / PZ / ML), prezzo listino della confezione, pezzi per confezione (metri per rotolo per le guarnizioni), minimo di vendita, prezzo unitario, stato, note.
- `profili_serie` — 57 serie commerciali a 3 cifre con €/kg del grezzo (es. 313 C77K 16,15; 312 D67 15,92; 366 C67K 15,92).
- `finiture` — aggregazioni colore a 2 caratteri con €/kg aggiuntivo (FA…FE cartella senza addebito, 20/23/25/30 con addebito, 60-75 fuori cartella, ossidati, effetto legno, bicolore) e maggiorazioni (sabbiatura, seaside, pretrattamento).
- `addebiti` — importi fissi (3++20, 3++60…, cambio colore).
- `colori` — 90 codici colore a 6 caratteri con classe, sigla, aggregazione monocolore/bicolore, sezione dell'elenco.
- Viste: `v_accessori` (listino + netto), `v_profili` (serie × finitura: listino €/kg e netto €/kg), `v_sconto`.

Il prezzo di un profilo AluK si ottiene per peso: **articolo di fatturazione = serie (3 cifre) + aggregazione colore (2 caratteri)**, es. `31320` = C77K verniciato cartella cat. B con addebito = 16,15 + 1,75 = 17,90 €/kg di listino, 11,098 €/kg netto.

## Esempi
```
python3 prezzo.py --sconti
python3 prezzo.py V40014 809119 712010
python3 prezzo.py --cerca "guarn. int"
python3 prezzo.py --serie 313 --finitura 20 --kg 12.5
sqlite3 listini.sqlite "SELECT codice, descrizione, prezzo_netto_unitario FROM v_accessori WHERE codice LIKE 'V40%'"
```

## Note
- Il vecchio articolo `10820` usato dal generatore `listini-c75s` (serie 108 + agg. 20 = 14,82 €/kg) non esiste più in questo listino: la serie commerciale dei profili C75S/C82S-CS (B23xxx) va confermata (candidate 313 C77K / 314 C77K-CS).
- Gli accessori `V52055` e `V40037` usati nelle distinte C75S non compaiono nel listino accessori 15-06-2026.
- Per aggiungere un altro fornitore: nuovo loader che scrive nelle stesse tabelle con `fornitore` diverso e la sua riga in `sconti`.
