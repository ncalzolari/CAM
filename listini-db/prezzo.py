#!/usr/bin/env python3
"""Interroga listini.sqlite: prezzo di listino e netto (sconto in tabella sconti) di accessori e profili AluK.

Esempi:
  python3 prezzo.py V40014 809119 712010          # accessori per codice (netto = listino x (1 - sconto accessori))
  python3 prezzo.py --cerca squadr                 # ricerca nella descrizione
  python3 prezzo.py --serie 313 --finitura 20      # €/kg profilo: grezzo serie + aggregazione colore, netto con sconto profili
  python3 prezzo.py --serie 313 --finitura 20 --kg 12.5   # importo per un peso
  python3 prezzo.py --sconti                       # sconti in vigore
"""
import argparse, os, sqlite3, sys
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'listini.sqlite')

def accessorio(db, codice):
    return db.execute('SELECT * FROM v_accessori WHERE codice=?', (codice,)).fetchone()

def profilo(db, serie, finitura=None):
    if finitura: return db.execute('SELECT * FROM v_profili WHERE serie=? AND aggregazione=?', (serie, finitura)).fetchone()
    return db.execute('SELECT * FROM v_profili WHERE serie=? AND aggregazione IS NULL', (serie,)).fetchone() or \
           db.execute('SELECT fornitore,decorrenza,serie,serie_descr,gruppo,stato,grezzo_eur_kg,NULL,NULL,NULL,grezzo_eur_kg,sconto,ROUND(grezzo_eur_kg*(1-sconto),4) FROM v_profili WHERE serie=? LIMIT 1', (serie,)).fetchone()

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('codici', nargs='*'); ap.add_argument('--cerca'); ap.add_argument('--serie'); ap.add_argument('--finitura'); ap.add_argument('--kg', type=float); ap.add_argument('--sconti', action='store_true')
    a = ap.parse_args()
    db = sqlite3.connect(DB); db.row_factory = sqlite3.Row
    if a.sconti or not (a.codici or a.cerca or a.serie):
        for r in db.execute('SELECT fornitore, categoria, sconto, decorrenza FROM sconti ORDER BY 1,2,4'): print(f"{r['fornitore']:6} {r['categoria']:10} {r['sconto']*100:5.1f}%  dal {r['decorrenza']}")
        for r in db.execute('SELECT fornitore, tipo, decorrenza, file FROM listini ORDER BY 1,2'): print(f"listino {r['fornitore']} {r['tipo']:10} decorrenza {r['decorrenza']}  ({r['file']})")
    for c in a.codici:
        r = accessorio(db, c.upper())
        if not r: print(f"{c}: non in listino"); continue
        print(f"{r['codice']:12} {r['descrizione'][:44]:44} {r['um']}  listino {r['prezzo_listino']:9.3f}/{r['um']} ({r['pz_conf']:g} pz)  unit. {r['prezzo_unitario']:8.4f}  sconto {r['sconto']*100:.0f}%  NETTO conf {r['prezzo_netto_conf']:9.3f}  unit. {r['prezzo_netto_unitario']:8.4f}")
    if a.cerca:
        for r in db.execute("SELECT * FROM v_accessori WHERE descrizione LIKE ? OR codice LIKE ? ORDER BY codice", (f'%{a.cerca.upper()}%', f'%{a.cerca.upper()}%')):
            print(f"{r['codice']:12} {r['descrizione'][:48]:48} {r['um']}  unit. listino {r['prezzo_unitario']:8.4f}  netto {r['prezzo_netto_unitario']:8.4f}")
    if a.serie:
        r = profilo(db, a.serie, a.finitura)
        if not r: print(f"serie {a.serie} / finitura {a.finitura}: non in listino"); sys.exit(1)
        r = list(r)
        print(f"serie {r[2]} {r[3]} [{r[4]}, {r[5]}]  grezzo {r[6]:.2f} €/kg" + (f" + finitura {r[7]} {r[8]} {r[9]:.2f}" if r[7] else '') + f"  = listino {r[10]:.2f} €/kg  sconto {r[11]*100:.0f}%  NETTO {r[12]:.4f} €/kg")
        if a.kg: print(f"  {a.kg:g} kg -> listino {r[10]*a.kg:.2f} €  netto {r[12]*a.kg:.2f} €")
