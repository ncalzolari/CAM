# Listino Abbaino — PROVVISORIO (02/10/2026)

`python3 build_listino_abbaino.py` legge i prezzi da `../listini-db/listini.sqlite` (profili categoria
"PR.ALL.N SL50,SG50" — serie 127, finitura di default "CARTELLA CON ADDEBITO CAT B"; accessori/guarnizioni
abbaino-specifici già presenti nel DB) e produce `dati_abbaino.json` + `Listino_Abbaino.html` (calcolatore
standalone, stesso stile grafico degli altri listini di questo programma, sezione marginalità riservata con lo
stesso codice di sblocco).

## Fonte e limite principale
Catalogo tecnico AluK **SL50-SG50 v4E** (facciate continue a montanti/traversi), inserto autonomo **"Abbaino —
Soluzione per facciate SL"** in coda al PDF (pag. 233-246 del file caricato il 02/10/2026): infisso apribile
motorizzato per falde inclinate, da inserire nella griglia SL50/SG50. Campo L 700-1200 mm / H 500-2800 mm (H max
decrescente con L, vedi grafico), peso massimo tamponamento 70 kg con 1 motore.

**A differenza di C75S/D67/D77/S140, questo inserto non contiene una distinta di taglio** (nessuna formula tipo
"L-43"): solo il grafico di dimensionamento e il disegno di nodo 6.01/6.02. La distinta usata nel calcolatore è
quindi un'**ipotesi dichiarata**, non un dato di catalogo:
- **K877** (telaio perimetrale fisso, 2,43 kg/m) = 2L+2H
- **K875** (anta apribile, 0,68 kg/m) = 2(L−80)+2(H−80) — deduzione 40 mm/lato stile anta-in-telaio
- **K876, K767, K768** compaiono nel disegno di nodo ma **non sono quotati**: K876 per ruolo indeterminato dal
  solo disegno, K767/K768 perché il catalogo non ne dà il peso kg/m. Il costo è quindi per difetto.
- **Guarnizioni** (809230-809235, tutte abbaino-specifiche a listino): quantità ipotizzata = perimetro anta
  (2L+2H) per ciascuna, semplificata — nel nodo reale alcune corrono solo sul telaio o sulla sola battuta.
- **Accessori**: kit squadrette+cerniere `704250` (171,61 € listino, netto dopo sconto accessori 20%); motore
  `704251` citato nel disegno ma **assente dal listino prezzi**, impostato a 0 € — da completare appena si ha
  il prezzo d'acquisto.
- **Manodopera**: nessun dato di catalogo, ore a 0 di default (campo modificabile, marcato DA TARARE).
- **Vetro**: escluso dal costo, come per tutte le altre serie di questo programma.

Tutto quanto sopra è segnalato nella pagina stessa (avviso rosso in alto, note sulle singole righe). Da
correggere/completare con dati di produzione reali appena disponibili (prima commessa reale, o documentazione
tecnica aggiuntiva — es. blocchi FP Pro con la distinta di taglio, se esistono per questo sistema).
