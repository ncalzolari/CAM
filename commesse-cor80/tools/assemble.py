# Programma Commesse COR80 — spinoff indipendente da commesse-lmt65 (15/09/2026), un solo prodotto: Cortizo COR 80 Evolution.
# Assembla src/app_template.html + src/dati_base_ferramenta.json (regole Maico/ded generiche, condivise con C75S
# per scelta di progetto: stessa ferramenta Multi-Matic) + src/dati_cor80.json + src/app_logic.js + src/cor80_logic.js
# -> dist/Commesse_COR80.html. Il placeholder lavPorta resta il suo stub no-op (nessuna serie porta qui).
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, 'src') + '/'
DIST = os.path.join(ROOT, 'dist') + '/'
D = json.load(open(F + 'dati_base_ferramenta.json'))
def merge(D, P):
    ids = {t['id']: i for i, t in enumerate(D.get('tipologie', []))}
    D.setdefault('tipologie', [])
    for t in P.get('tipologie', []):
        if t['id'] in ids: D['tipologie'][ids[t['id']]] = t
        else: D['tipologie'].append(t)
    for k, v in P.items():
        if k in ('tipologie', 'libreria'): continue
        if isinstance(v, dict) and isinstance(D.get(k), dict): D[k].update(v)
        else: D[k] = v
    if 'libreria' in P:
        D.setdefault('libreria', [])
        lid = {l['id']: i for i, l in enumerate(D['libreria'])}
        for l in P['libreria']:
            if l['id'] in lid: D['libreria'][lid[l['id']]] = l
            else: D['libreria'].append(l)
merge(D, json.load(open(F + 'dati_cor80.json')))
os.makedirs(DIST, exist_ok=True)
json.dump(D, open(DIST + 'dati_cor80_merged.json', 'w'), ensure_ascii=False, separators=(',', ':'))
tpl = open(F + 'app_template.html', encoding='utf-8').read()
js = open(F + 'app_logic.js', encoding='utf-8').read()
stub2 = "if(typeof componiMatriceCOR80!=='function'){ window.componiMatriceCOR80 = function(){ return; }; }"
assert js.count(stub2) == 1
js = js.replace(stub2, open(F + 'cor80_logic.js', encoding='utf-8').read())
assert tpl.count('/*__DATI__*/') == 1
html = tpl.replace('/*__DATI__*/', 'const DATI = ' + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + ';' + js)
open(DIST + 'Commesse_COR80.html', 'w', encoding='utf-8').write(html)
print('HTML', len(html), 'bytes; tipologie', len(D['tipologie']), 'serie', sorted({t['serie'] for t in D['tipologie']}))
