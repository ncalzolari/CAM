#!/usr/bin/env python3
# Listino PROVVISORIO per l'infisso "Abbaino" (AluK SL50-SG50, catalogo tecnico v4E, inserto "Abbaino — Soluzione
# per facciate SL" in coda al catalogo facciate continue): apribile motorizzato per falda inclinata, inseribile
# nella griglia montanti/traversi SL50. A differenza di C75S/D67/D77/S140, il catalogo NON contiene una distinta
# di taglio (nessuna formula tipo "L-43"): solo il grafico di dimensionamento (L 700-1200 / H 500-2800, in
# funzione del peso tamponamento, max 70 kg con 1 motore) e il disegno di nodo 6.01/6.02. La distinta qui sotto
# è quindi un'IPOTESI dichiarata (profili K877 = telaio perimetrale, K875 = anta apribile con deduzione 40mm/lato
# stile anta-in-telaio), marcata [DA TARARE]. Profili K876/K767/K768 compaiono nel disegno di nodo ma non sono
# quotabili: K876 per ruolo indeterminato, K767/K768 perché il catalogo non ne dà il peso kg/m. Il motore 704251
# non è a listino (prezzo 0, DA TARARE). Vetro escluso dal costo come nelle altre serie di questo programma.
import json, os, sqlite3
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
DB = os.path.join(ROOT, 'listini-db', 'listini.sqlite')
db = sqlite3.connect(DB)

FINITURA = 'CARTELLA CON ADDEBITO CAT B'   # stessa finitura di default usata per D67/D77/S140 in questo programma
def prezzo_profilo(serie_cod):
    r = db.execute("SELECT netto_eur_kg FROM v_profili WHERE serie=? AND finitura=?", (serie_cod, FINITURA)).fetchone()
    return r[0] if r else None
def prezzo_acc(cod):
    r = db.execute("SELECT prezzo_netto_unitario FROM v_accessori WHERE codice=?", (cod,)).fetchone()
    return r[0] if r else None

PROFILI = {
    'K877': {'desc': 'Telaio perimetrale fisso', 'kg_m': 2.43, 'serie_prezzo': '127', 'formula': '2L+2H', 'nota': 'quantità ipotizzata (nessuna distinta di taglio nel catalogo)'},
    'K875': {'desc': 'Anta apribile', 'kg_m': 0.68, 'serie_prezzo': '127', 'formula': '2(L-80)+2(H-80)', 'nota': 'deduzione 40mm/lato ipotizzata (tipica anta-in-telaio), da verificare'},
}
for p in PROFILI.values(): p['eur_kg'] = prezzo_profilo(p['serie_prezzo'])

ACCESSORI = {
    '704250': {'desc': 'Kit squadrette e cerniere per abbaino', 'qty': 1},
    '704251': {'desc': 'Motore per abbaino e staffa di ancoraggio', 'qty': 1, 'prezzo_fisso': 0.0, 'nota': 'NON A LISTINO: prezzo da inserire (DA TARARE)'},
}
for a in ACCESSORI.values():
    if 'prezzo_fisso' not in a: a['prezzo_netto'] = prezzo_acc(next(k for k, v in ACCESSORI.items() if v is a))
for cod, a in ACCESSORI.items():
    if 'prezzo_netto' not in a: a['prezzo_netto'] = a.pop('prezzo_fisso')

GUARNIZIONI = {   # ML, quantità ipotizzata = perimetro anta (2L+2H), semplificata: nel nodo reale alcune corrono solo sul telaio o sulla sola battuta
    '809230': {'desc': 'Guarn. copriviti traverso'},
    '809231': {'desc': 'Guarn. telaio'},
    '809232': {'desc': 'Guarn. anta'},
    '809233': {'desc': 'Guarn. butilica nera'},
    '809234': {'desc': 'Guarn. spugnosa nera 10x4'},
    '809235': {'desc': 'Guarn. spugnosa nera 10x10'},
}
for cod, g in GUARNIZIONI.items(): g['prezzo_netto'] = prezzo_acc(cod)

NON_QUOTATI = [
    {'cod': 'K876', 'desc': 'Profilo di nodo (ruolo non determinabile dal solo disegno 6.01/6.02)'},
    {'cod': 'K767', 'desc': 'Profilo anta — peso kg/m assente dal catalogo'},
    {'cod': 'K768', 'desc': 'Profilo anta — peso kg/m assente dal catalogo'},
]

OUT = {
    'fonte': 'AluK SL50-SG50 Catalogo Tecnico v4E — inserto "Abbaino" (pag. 233-246 del PDF caricato il 02/10/2026)',
    'dimensionamento': {'L_min': 700, 'L_max': 1200, 'H_min': 500, 'H_max': 2800,
                         'curva_H_max': [[700, 2850], [800, 2480], [900, 2230], [1000, 2000], [1100, 1820], [1200, 1670]],
                         'peso_max_kg': 70, 'nota': 'peso massimo tamponamento valido con 1 abbaino + 1 motore'},
    'profili': PROFILI, 'accessori': ACCESSORI, 'guarnizioni': GUARNIZIONI, 'non_quotati': NON_QUOTATI,
    'par': {'sc_prof': 0.0, 'sfrido': 0.09, 'eur_h': 65.0, 'ricarico': 2.13},  # sc_prof/sc_acc già netti da DB; sfrido/ricarico = default generico del programma (non specifico abbaino)
}
json.dump(OUT, open(os.path.join(HERE, 'dati_abbaino.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('profili:', {k: v['eur_kg'] for k, v in PROFILI.items()})
print('accessori:', {k: v['prezzo_netto'] for k, v in ACCESSORI.items()})
print('guarnizioni:', {k: v['prezzo_netto'] for k, v in GUARNIZIONI.items()})

tpl = open(os.path.join(HERE, 'template_abbaino.html'), encoding='utf-8').read()
assert tpl.count('/*__DATI__*/') == 1
html = tpl.replace('/*__DATI__*/', json.dumps(OUT, ensure_ascii=False, separators=(',', ':')))
open(os.path.join(HERE, 'Listino_Abbaino.html'), 'w', encoding='utf-8').write(html)
print('HTML', len(html), 'bytes -> Listino_Abbaino.html')
