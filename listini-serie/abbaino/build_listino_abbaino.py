#!/usr/bin/env python3
# Listino per l'infisso "Abbaino" (AluK SL50-SG50): apribile motorizzato per falda inclinata, inseribile nella
# griglia montanti/traversi SL50. Distinta di taglio dal Manuale di Assemblaggio SL50-SG50 (pag. "SL50 11.01 —
# INFISSO ABBAINO", immagine fornita dall'utente 02/10/2026): K877 = traversi/montanti stipite (telaio fisso,
# 2L+2H), K876 = traversi/montanti battente (anta apribile, 2(L-90)+2(H-90)), K875 = fermavetro (2(L-64)+2(H-64)).
# Guarnizioni e listelli isolanti con le quantità della stessa pagina. Vetro: vetrocamera 30mm, (L-180)x(H-180),
# 1 pz — formula nota ma ESCLUSA dal costo, come per tutte le altre serie di questo programma (vetro quotato a
# parte). Accessori 704250 (kit squadrette/cerniere) e 704251 (kit motore e staffe) confermati 1 pz ciascuno
# dalla stessa pagina; 704251 resta senza prezzo a listino (0 €, DA TARARE). Manodopera 4,5 h (confermata
# dall'utente 02/10/2026). Prezzi da ../listini-db/listini.sqlite.
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
    'K877': {'desc': 'Traversi (2×L) + montanti (2×H) stipite — telaio fisso', 'kg_m': 2.43, 'serie_prezzo': '127', 'formula': '2*L+2*H'},
    'K876': {'desc': 'Traversi (2×L-90) + montanti (2×H-90) battente — anta apribile', 'kg_m': 1.20, 'serie_prezzo': '127', 'formula': '2*(L-90)+2*(H-90)'},
    'K875': {'desc': 'Fermavetro (2×L-64 + 2×H-64)', 'kg_m': 0.68, 'serie_prezzo': '127', 'formula': '2*(L-64)+2*(H-64)'},
}
for p in PROFILI.values(): p['eur_kg'] = prezzo_profilo(p['serie_prezzo'])

ACCESSORI = {
    '704250': {'desc': 'Kit squadrette, cerniere', 'qty': 1},
    '704251': {'desc': 'Kit motore e staffe', 'qty': 1, 'prezzo_fisso': 0.0, 'nota': 'NON A LISTINO: prezzo da inserire (DA TARARE)'},
}
for cod, a in ACCESSORI.items():
    a['prezzo_netto'] = a.pop('prezzo_fisso') if 'prezzo_fisso' in a else prezzo_acc(cod)

# ml, formule dalla pag. "SL50 11.01": guarnizioni 2L+2H salvo 809231 (guarnizione telaio) 4L+4H; listelli
# isolanti 2L+2H salvo 808107C (13x10) 3L+4H. 808096C (listello 23x10) non è a listino in listini-db: assimilato
# al più vicino articolo censito, 809618 "LISTELLO ISOLANTE 22X10X2000 SL50" (22x10 vs 23x10) — DA VERIFICARE.
GUARNIZIONI = {
    '809230': {'desc': 'Guarnizione finitura traverso', 'formula': '2*L+2*H'},
    '809231': {'desc': 'Guarnizione telaio', 'formula': '4*L+4*H'},
    '809232': {'desc': 'Guarnizione anta', 'formula': '2*L+2*H'},
    '809233': {'desc': 'Guarnizione butilica nera', 'formula': '2*L+2*H'},
    '809234': {'desc': 'Guarnizione spugnosa nera 10x4', 'formula': '2*L+2*H'},
    '809235': {'desc': 'Guarnizione spugnosa nera 10x10', 'formula': '2*L+2*H'},
    '808107C': {'desc': 'Listello isolante 13x10', 'formula': '3*L+4*H'},
    '808102C': {'desc': 'Listello isolante 50x17', 'formula': '2*L+2*H'},
    'V09032': {'desc': 'Listello isolante', 'formula': '2*L+2*H'},
    '808096C': {'desc': 'Listello isolante 23x10', 'formula': '2*L+2*H', 'cod_prezzo': '809618',
                'nota': 'assimilato a 809618 "LISTELLO ISOLANTE 22X10X2000 SL50" (22x10, non 23x10) — DA VERIFICARE, 808096C non è a listino'},
}
# V09032 e 809618 sono venduti a pezzo di lunghezza fissa (2000mm): prezzo €/ml = prezzo al pezzo / 2000.
PEZZO_FISSO_MM = {'V09032': 2000, '809618': 2000}
for cod, g in GUARNIZIONI.items():
    cod_prz = g.get('cod_prezzo', cod)
    pr = prezzo_acc(cod_prz)
    g['eur_ml'] = r = (pr / PEZZO_FISSO_MM[cod_prz] * 1000) if cod_prz in PEZZO_FISSO_MM and pr is not None else pr

VETRO = {'tipo': 'Vetrocamera sp. 30 mm', 'pz': 1, 'formula_l': 'L-180', 'formula_h': 'H-180',
         'nota': 'formula nota dal manuale di assemblaggio, ma esclusa dal costo come nelle altre serie di questo programma (vetro quotato a parte)'}

OUT = {
    'fonte': 'AluK SL50-SG50 — Catalogo Tecnico v4E (inserto "Abbaino", dimensionamento) + Manuale di Assemblaggio (pag. "SL50 11.01 — Infisso Abbaino", distinta di taglio, immagine fornita dall\'utente 02/10/2026)',
    'dimensionamento': {'L_min': 700, 'L_max': 1200, 'H_min': 500, 'H_max': 2800,
                         'curva_H_max': [[700, 2850], [800, 2480], [900, 2230], [1000, 2000], [1100, 1820], [1200, 1670]],
                         'peso_max_kg': 70, 'nota': 'peso massimo tamponamento valido con 1 abbaino + 1 motore'},
    'profili': PROFILI, 'accessori': ACCESSORI, 'guarnizioni': GUARNIZIONI, 'vetro': VETRO,
    'par': {'sfrido': 0.09, 'eur_h': 65.0, 'ore': 4.5, 'ricarico': 2.13},  # sfrido/ricarico = default generico del programma; ore confermate dall'utente
}
json.dump(OUT, open(os.path.join(HERE, 'dati_abbaino.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('profili eur_kg:', {k: v['eur_kg'] for k, v in PROFILI.items()})
print('accessori eur:', {k: v['prezzo_netto'] for k, v in ACCESSORI.items()})
print('guarnizioni eur/ml:', {k: v['eur_ml'] for k, v in GUARNIZIONI.items()})

tpl = open(os.path.join(HERE, 'template_abbaino.html'), encoding='utf-8').read()
assert tpl.count('/*__DATI__*/') == 1
html = tpl.replace('/*__DATI__*/', json.dumps(OUT, ensure_ascii=False, separators=(',', ':')))
open(os.path.join(HERE, 'Listino_Abbaino.html'), 'w', encoding='utf-8').write(html)
print('HTML', len(html), 'bytes -> Listino_Abbaino.html')
