import json
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT,'src')+'/'
DIST = os.path.join(ROOT,'dist')+'/'
D = json.load(open(F+'dati_app.json'))
P = json.load(open(F+'dati_porte.json'))
# merge: tipologie by id; dict sections merged; new sections added
ids = {t['id']: i for i, t in enumerate(D['tipologie'])}
for t in P['tipologie']:
    if t['id'] in ids: D['tipologie'][ids[t['id']]] = t
    else: D['tipologie'].append(t)
for k, v in P.items():
    if k == 'tipologie': continue
    if isinstance(v, dict) and isinstance(D.get(k), dict): D[k].update(v)
    else: D[k] = v
if 'libreria' in P:
    lid = {l['id']: i for i, l in enumerate(D['libreria'])}
    for l in P['libreria']:
        if l['id'] in lid: D['libreria'][lid[l['id']]] = l
        else: D['libreria'].append(l)
json.dump(D, open(DIST+'dati_app_merged.json', 'w'), ensure_ascii=False, separators=(',', ':'))
tpl = open(F+'app_template.html', encoding='utf-8').read()
js = open(F+'app_logic.js', encoding='utf-8').read()
stub = "if(typeof lavPorta!=='function'){ window.lavPorta = function(){ return []; }; }"
assert js.count(stub)==1
js = js.replace(stub, open(F+'porte_logic.js', encoding='utf-8').read())
assert tpl.count('/*__DATI__*/') == 1
html = tpl.replace('/*__DATI__*/', 'const DATI = ' + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + ';' + js)
open(DIST+'Commesse_LMT65.html', 'w', encoding='utf-8').write(html)
print('HTML', len(html), 'bytes; tipologie', len(D['tipologie']), 'serie', sorted({t['serie'] for t in D['tipologie']}))
