# Generatore listini a griglia C75S (senza vetro, RAL 7016)

## Uso
    pip install openpyxl
    python genera_listini.py
Genera i 5 file: FISSO / F1 / F2 / PF1 / PF2 _SENZA_VETRO.xlsx

## Struttura di ogni file
- **Prezzo**: griglia LISTINO (costo +213%) e griglia COSTO
- **Parametri** (celle gialle): 14,82 euro/kg CAT.B +ADD, sconto profili 43%,
  sconto accessori 20%, sfrido 9%, tariffa 65 euro/h, ricarico 213%
- **Coefficienti**: pesi kg (da distinte AluK + pesi catalogo), guarnizioni,
  accessori, ore (1h telaio + 1h/anta + 20' ferramenta/anta + 20'/vetro)
- **Ferramenta**: articoli Maico con prezzi letti da `ferramenta.csv` tramite il
  codice (colonna Unita' = pezzi per confezione, il prezzo e' diviso per l'unita').
  La colonna Fonte indica: netto 2025 / manuale / da inserire.
  Aggiornare il netto = sostituire il CSV e rilanciare lo script.

## Da completare (righe gialle a 0 nel foglio Ferramenta)
- Cerniere a vista (set anta) / Forbice a vista + braccio
- Scontri anta semifissa (F2/PF2)
- Scontro nottolino 355866: non presente nel netto 2025
- Martellina DK 1033: non presente nel netto 2025, prezzo manuale 5,50 in
  `FERR_ANTA` (genera_listini.py); se il codice compare nel CSV vince il CSV
Fonte prezzi mancanti: export lot FP Pro di un serramento a vista (F1/F2),
come fatto per il F12 (file con <lot> e <fitting>).

## Assunzioni nei coefficienti
Supporti vetro 4/vetro, mascherine V51015 2 pz, fermavetro N45860 (battenti)
e coppia N45856 (fisso), squadrette V40022/V40037 prezzate come V40022.
Cremonese fissa GR1590: se serve variabile per altezza, servono i codici
delle altre grandezze.
