# Listino Abbaino (02/10/2026)

`python3 build_listino_abbaino.py` legge i prezzi da `../listini-db/listini.sqlite` (profili categoria
"PR.ALL.N SL50,SG50" — serie 127, finitura di default "CARTELLA CON ADDEBITO CAT B"; accessori/guarnizioni
abbaino-specifici già presenti nel DB) e produce `dati_abbaino.json` + `Listino_Abbaino.html` (calcolatore
standalone, stesso stile grafico degli altri listini di questo programma, sezione marginalità riservata con lo
stesso codice di sblocco).

## Fonte
AluK SL50-SG50 — infisso apribile motorizzato per facciate inclinate, da inserire nella griglia montanti/traversi
SL50/SG50. Dimensionamento dal Catalogo Tecnico v4E, inserto "Abbaino" (pag. 233-246 del PDF caricato
02/10/2026): campo L 700-1200 mm / H 500-2800 mm (H max decrescente con L, vedi grafico), peso massimo
tamponamento 70 kg con 1 motore. **Distinta di taglio dal Manuale di Assemblaggio SL50-SG50**, pag.
"SL50 11.01 — Infisso Abbaino" (immagine fornita dall'utente 02/10/2026):
- **K877** (telaio fisso, 2,43 kg/m) = traversi stipite 2×L + montanti stipite 2×H
- **K876** (anta apribile/battente, 1,20 kg/m) = traversi battente 2×(L−90) + montanti battente 2×(H−90)
- **K875** (fermavetro, 0,68 kg/m) = 2×(L−64) + 2×(H−64)
- **Guarnizioni/listelli isolanti**: 809230/809232/809233/809234/809235/808102C/808107C/V09032 a 2L+2H (808107C
  a 3L+4H), **809231** (guarnizione telaio) a 4L+4H — quantità dalla stessa pagina.
- **Vetro**: vetrocamera sp. 30 mm, 1 pz, (L−180)×(H−180) — formula nota ma **esclusa dal costo**, come per
  tutte le altre serie di questo programma (vetro quotato a parte, non raddoppiato nel listino).
- **Accessori**: kit squadrette+cerniere `704250` (1 pz, 171,61 € listino, netto dopo sconto accessori 20%),
  kit motore e staffe `704251` (1 pz, 450 € netto d'acquisto confermato dall'utente 02/10/2026 — non è a listino
  AluK, prezzo fisso inserito a mano).
- **Manodopera**: 4,5 ore (confermato dall'utente 02/10/2026), campo modificabile.

## Dati ancora da completare
- **808096C** (listello isolante 23×10): non è a listino prezzi → prezzato in via approssimativa con l'articolo
  più vicino disponibile, `809618` "LISTELLO ISOLANTE 22X10X2000 SL50" (22×10, non 23×10) — da verificare.

Segnalato nella pagina stessa (riga evidenziata in rosso).
