# Generatore listini a griglia C75S (senza vetro, RAL 7016)

## Uso
    pip install openpyxl
    python genera_listini.py
Genera i 5 file: FISSO / F1 / F2 / PF1 / PF2 _SENZA_VETRO.xlsx

## Struttura di ogni file
- **Prezzo**: griglia LISTINO (costo +213%) e griglia COSTO
- **Parametri** (celle gialle): euro/kg profili a taglio termico (art. 33320 CAT.B +ADD, 19,93)
  e profili normali (art. 10820, 14,82), sconto profili 43%, sconto accessori 20%,
  sfrido 9%, tariffa 65 euro/h, ricarico 213%. Prezzi e sconti letti da
  `../listini-db/listini.sqlite` (listino AluK C75S/C82S-CS 15-06-2026); senza database
  restano i valori incorporati nello script.
- **Coefficienti**: pesi kg separati tra profili a taglio termico (codici B: stipite,
  anta, battuta centrale, soglia) e normali (N/K: aggiuntivo, gocciolatoio, fermavetri),
  guarnizioni, accessori, ore (1h telaio + 1h/anta + 20' ferramenta/anta + 20'/vetro)
- **Ferramenta**: articoli Maico con prezzi letti da `ferramenta.csv` tramite il
  codice (colonna Unita' = pezzi per confezione, il prezzo e' diviso per l'unita').
  La colonna Fonte indica: netto 2025 / manuale / da inserire.
  Aggiornare il netto = sostituire il CSV e rilanciare lo script.

## Ferramenta Maico dipendente dalla misura (14/09/2026)
Il kit Multi-Matic in vista è calcolato per ogni misura dalle regole del poolfile WinPlus
"Finestra A-R 1 anta alluminio_contrasto" (export MaicoWinPlus 14/09/2026): FFB/FFH = anta − 20
(anta = formula della tipologia: F1 L−42/H−42, PF1 H−29,5, F2/PF2 L/2−9). Regole in `KIT_ANTA`:
cremonese per FFH (201730…201742), prolunghe sopra/sotto (201841/201750/201840), movimenti angolari
222201/222209, chiusure centrali (211929…211933), forbice + braccio per FFB (211673…211903), asta lato
cerniere (202269/205940/205941), cerniera angolare 250400 + bandella 215806, scontri fungo IS 356361.
Voci fisse (`FERR_FISSE_ANTA`, `FERR_SEMIFISSA`): martellina 1033 (manuale 5,50), scontro nottolino
personalizzato 355866 (non nel netto 2025: prezzo da inserire), asta a leva 221911, movimento angolare
prolungabile 222205, scontri anta semifissa (codice da inserire). I codici 77xxxx/78xxxx del poolfile sono
schemi di foratura (Bohrbild), non articoli. Negli xlsx il foglio `FerrGriglia` contiene il costo ferramenta
per cella (valori) e le formule delle griglie lo referenziano; il foglio `Ferramenta` mostra il kit della misura
di riferimento. Verifica: F1 1000×1500 → kit 37,34 €, costo 442,05, listino 1383,62.

## Assunzioni nei coefficienti
Supporti vetro 4/vetro, mascherine V51015 2 pz, fermavetro N45860 (battenti)
e coppia N45856 (fisso), squadrette V40022/V40037 prezzate come V40022.
Cremonese fissa GR1590: se serve variabile per altezza, servono i codici
delle altre grandezze.


## Versione HTML (14/09/2026)
`python3 build_html.py` genera **`Listini_C75S.html`**: pagina autonoma con gli stessi dati e le stesse formule di `genera_listini.py`
(importa lo script, quindi rigenera anche gli xlsx e legge i prezzi da `../listini-db/listini.sqlite`). A video: parametri (celle gialle) e
ferramenta modificabili e salvati nel browser, coefficienti, interrogazione di una misura con la scomposizione del costo, griglie LISTINO e
COSTO ricalcolate al volo, scarico degli xlsx con formule vive (SheetJS da CDN: serve la connessione la prima volta; in alternativa CSV).
`Listini_C75S_web.html` è la variante per la pubblicazione come Artifact claude.ai (download tramite capability).
Verifica: F1 1000×1500 → costo 442,05, listino 1383,62 come lo script; formule xlsx identiche a quelle di openpyxl (griglie con riferimento a `FerrGriglia`).
