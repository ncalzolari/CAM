#!/usr/bin/env python3
# Importa la tabella "Vetri Alluminio" del preventivatore IWG (../listini-db/Listino_Vetri_IWG.xlsx,
# esportazione da catalogo_vetri) in vetri_iwg.json: prezzi di listino vetro (IVA esclusa) usati dal
# calcolo di marginalita' riservato in Listini_Serie.html. Le altre due schede del file (Vetri PVC
# CLIMA 76, Vetri PVC listino esteso) sono di una linea PVC non gestita da questo programma e non
# vengono importate.
import json, os
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'listini-db', 'Listino_Vetri_IWG.xlsx')

wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb['Vetri Alluminio']
rows = list(ws.iter_rows(values_only=True))
out = []
for r in rows[1:]:
    if not isinstance(r[0], (int, float)): continue   # salta la riga di nota finale
    cod, comp, prezzo, ug, psi, tl, rw, fs, peso, mm = r[:10]
    out.append({'cod': int(cod), 'comp': comp, 'prezzo': round(float(prezzo), 2), 'ug': ug, 'psi': psi,
                'tl': tl, 'rw': rw, 'fs': fs, 'peso': peso, 'mm': int(mm)})
out.sort(key=lambda v: (v['mm'], v['prezzo']))
json.dump(out, open(os.path.join(HERE, 'vetri_iwg.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'composizioni vetro alluminio importate da', os.path.basename(SRC), '| spessori:', sorted({v['mm'] for v in out}))
