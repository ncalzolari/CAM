# Listini a griglia — altre serie (AluK D67/D77 porte, Cortizo COR80)

`python3 build_listini_serie.py` legge le distinte delle tipologie dal programma commesse
(`../commesse-lmt65/src/dati_app.json`, `dati_porte.json`, `dati_cor80.json`), i prezzi AluK da
`../listini-db/listini.sqlite` (profili: serie 312 D67 / 315 D77 cat. B con addebito, sconto 38%;
accessori sconto 20%), il kit Maico in vista dalle regole WinPlus (`../listini-c75s/genera_listini.py`) e la
ferramenta porte dai blocchi FP D67 (`fp_blk_D67.json`, voci non opzionali, soglia automatica per fascia di
larghezza anta; per D77 è riusato il kit D67). Porte: gruppi "Porta 1/2 ante — apertura interna/esterna" con menù soglia; standard = soglia automatica
senza zoccolo (nodo U51320 interna, U51340 esterna con 732040÷732046 + K1486 + 809944), le altre in variante.
Le esterne con soglia automatica non hanno distinta a catalogo: `deriva_est_automatica()` le ricava dalle 8.18/8.19
(soglia K1769/K2069) applicando le differenze delle 8.07/8.08 (anta H−55, fermavetro H−247, K1486, 809944,
soglia automatica per larghezza); kit ferramenta dal blocco FP 360-02 (1 anta) e 350-21 (2 ante, riusato).
Produce `dati_listini_serie.json`, `Listini_Serie.html`
(autonomo) e `Listini_Serie_web.html` (Artifact).

Stesso modello di costo dei listini C75S: profili a peso × €/kg scontato + accessori e guarnizioni scontati,
sfrido, ferramenta per misura, manodopera; listino = costo × (1 + ricarico). Sezione riservata con marginalità.

## Dati da completare (file modificabili, oppure celle rosse nella pagina)
- `pesi_profili.json`: kg/m dei profili porte (U51200, U51320, U20630, N48823, K1488… e D77). Nessuna fonte
  a disposizione: catalogo AluK o archivio FP Pro (densità kg/ml).
- `prezzi_cortizo.json`: €/kg profili Cortizo, sconti e prezzi unitari di accessori/guarnizioni COR80
  (listino Cortizo non caricato).
- Porte: cerniere AluK (codice e prezzo) e serrature da confermare (voci del kit FP marcate).
- COR80 a scomparsa: cerniere Multi Power da inserire.
I valori inseriti nella pagina restano nel browser; per renderli definitivi metterli nei file e rigenerare.

## Regole porte D67/D77 (aggiornamento)
- **Verniciatura**: all'apertura del programma la verniciatura torna sempre all'aggregazione **20 — CARTELLA CON ADDEBITO CAT B** (+1,75 €/kg, base RAL 7016 opaco); la scelta fatta nella sessione non viene ripristinata al riavvio.
- **Cerniere porte**: sempre cerniere a stelo AluK **H51300-B1** (nero R.9005, 48,66 € listino, sconto accessori applicato). Quantità per anta in funzione dell'altezza anta (regola catalogo AluK tab. 10.51 estesa alle cerniere a stelo): ≤1300 → 2, ≤2400 → 3, oltre → 4. L'altezza anta è presa dal montante battente della tipologia (H−55 con soglia automatica, H−79 con soglia K).
- **Serratura porte**: pacchetto standard al posto della serratura del blocco FP: 1 serratura Performa 3 catenacci + scrocco E35 I85 nera (68,67 €), 1 incontro centrale F29x229 nero (10,03 €), 2 incontri deviatori F29x186 neri (9,96 € cad.), 1 cilindro sagomato 123P 22/10/22 alluminio con pomolo nylon (14,05 €). Prezzi netti di acquisto, senza sconto ulteriore; codici interni (SERR-PERFORMA, INC-PERFORMA-229/186, CIL-123P-22-10-22) modificabili nella tabella ferramenta. Stesso pacchetto per 1 e 2 ante.
- **Porte 2 ante con soglia automatica**: il blocco FP 350-21 non elenca le soglie automatiche; il kit aggiunge 2 soglie (una per anta, fascia in base alla larghezza anta L/2−37,5; se la larghezza cade sul bordo di due fasce viene presa la soglia più corta) e 2 spazzolini K1488 dal blocco a 1 anta.
- **Profili K…**: sempre classe non isolata (€/kg serie 108 grezzo, 13,07). Pesi completi per D67/D77; manca solo COR-7088 (COR80).
- **Ore manodopera**: valore fisso per tipologia (6 h porta 1 anta, 10 h porta 2 ante, uguali per apertura interna ed esterna), modificabile nella scheda e memorizzato; non è calcolato da lavorazioni o misure.
