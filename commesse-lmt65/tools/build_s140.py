#!/usr/bin/env python3
"""AluK S140 (alzante scorrevole / scorrevole in linea) per il programma commesse.
Sorgente unica delle tipologie: listini-serie/tipologie_s140.json (generato da listini-serie/genera_tipologie_s140.py dalle
distinte di taglio ufficiali AluK S140 v5A sez. 8) -> stesse 36 tipologie, stessi id/codici del listino (allineamento listino/commesse).
Catalogo profili/vetrazione: data/catalogo_S140/catalogo_S140.json. Produce src/dati_s140.json (non editare a mano).
Lavorazioni macchina: non ancora definite (manuale lavorazioni S140 v3A da trascrivere) -> solo distinta di taglio, accessori, guarnizioni, vetro."""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(os.path.dirname(ROOT), 'listini-serie', 'tipologie_s140.json'), encoding='utf-8'))['tipologie']
CAT = json.load(open(os.path.join(ROOT, 'data', 'catalogo_S140', 'catalogo_S140.json'), encoding='utf-8'))
DXF = json.load(open(os.path.join(ROOT, 'data', 'dxf_sez_s140.json'), encoding='utf-8'))  # sezioni profilo (tools/dxf_s140.py)
# dimensioni di sezione (w = profondità, h = altezza in vista) dal sinottico 2.01/2.02 e sez. 5 — orientative, per gli schemi
DIM = {'U10022': ('telaio', 140, 62.3), 'U10000': ('telaio', 140, 62.3), 'U10060': ('telaio', 120, 62.3), 'U10061': ('telaio', 116, 62.3),
       'U10400': ('soglia', 122.4, 25), 'U10401': ('soglia', 131.2, 25), 'U10402': ('soglia', 107.2, 25), 'U10403': ('soglia', 110.7, 25),
       'U10140': ('anta', 62, 82), 'U10120': ('montante', 19, 62), 'U10600': ('montante', 46, 82), 'U10601': ('aggiuntivo', 54.6, 16.6),
       'N10630': ('binario', 18, 10.8), 'N10901': ('finitura', 10, 27.6), 'N10902': ('gocciolatoio', 27.6, 18), 'N10903': ('finitura', 10, 27.6),
       'N10904': ('cover', 24.8, 65.5), 'N10905': ('cover', 66.3, 23), 'N10906': ('cover', 24.8, 65.5), 'N10909': ('cover', 23, 67.5),
       'N10602': ('montante', 40.7, 68.7), 'N10911': ('cover', 45, 14.8), 'N10820': ('fermavetro', 18, 3), 'N10821': ('fermavetro', 18, 8), 'N10822': ('fermavetro', 18, 13), 'N10823': ('fermavetro', 18, 18)}
SC = {'U10022': ('TELL', 'TELH'), 'U10000': ('TELL', 'TELH'), 'U10060': ('TELL', 'TELH'), 'U10061': ('TELI', 'TEHI'), 'U10400': ('SOGL', 'SOGL'), 'U10401': ('SOGL', 'SOGL'), 'U10402': ('SOGL', 'SOGL'), 'U10403': ('SOGE', 'SOGE'),
      'U10140': ('ANTL', 'ANTH'), 'U10120': ('SLIM', 'SLIM'), 'U10600': ('MONT', 'MONT'), 'U10601': ('RIPO', 'RIPO'), 'N10630': ('BINA', 'BINA'), 'N10901': ('FINL', 'FINL'), 'N10902': ('GOCC', 'GOCC'), 'N10903': ('FINX', 'FINX'),
      'N10904': ('COVT', 'COVM'), 'N10905': ('COVS', 'COVS'), 'N10906': ('COVC', 'COVC'), 'N10909': ('SCAT', 'SCAT'), 'N10602': ('MOXO', 'MOXO'), 'N10911': ('COXO', 'COXO')}
def sc_di(art, desc, mis):
    if art == 'N10823': return ('FVSL' if 'orizzontale' in desc else 'FVSH') if 'fisso' in desc else ('FERL' if 'orizzontale' in desc else 'FERH')
    a, b = SC.get(art, ('AGGL', 'AGGH')); return a if ('L' in mis and 'H' not in mis) else b
# tavole di vetrazione 7.04 (anta U10140/U10120) e 7.05 (fisso U10000/U10401/U10600): A = guarnizione interna, B = fermavetro
AB = {'28': (8, 18), '30': (6, 18), '32': (4, 18), '34': (7, 13), '36': (5, 13), '38': (8, 8), '40': (6, 8), '42': (4, 8), '44': (7, 3), '46': (5, 3), '48': (3, 3)}
def tavola(profili, dA):
    righe = {mm: {'A': AB[mm][0] + dA, 'g': v['g_int'], 'B': AB[mm][1], 'fv': v['fv'], 'ext': v['g_est']} for mm, v in CAT['vetrazione'].items() if not mm.startswith('_')}
    return {'profili': profili, 'righe': righe}
VETR = {'tavS140A': tavola(['U10140', 'U10120'], 0), 'tavS140F': tavola(['U10000', 'U10401', 'U10600'], 0.3)}
tip = []
for t in T:
    fisso = any('fisso' in p['desc'] for p in t['profili'] if p['art'] == 'N10823')
    prof = []
    for p in t['profili']:
        q = {'art': 'FVxx' if p['art'] == 'N10823' else p['art'], 'desc': p['desc'], 'pz': p['pz'], 'mis': p['mis'], 'ang': p.get('ang', '90-90'), 'sc': sc_di(p['art'], p['desc'], p['mis'])}
        if p['art'] == 'N10823': q['fv'] = True; q['tav'] = 'tavS140F' if 'fisso' in p['desc'] else 'tavS140A'
        prof.append(q)
    vetro = [{'pz': v['pz'], 'l': v['l'], 'h': v['h'], 'anta': not (fisso and i == len(t['vetro']) - 1)} for i, v in enumerate(t['vetro'])]
    gua = [{'art': g['art'], 'desc': g['desc'], 'mis': g['mis'], 'gv': g['art'] == '809122'} for g in t['guarnizioni']]
    var = re.sub(r'\s*\[distinta[^\]]*\]', '', t['variante']).replace(' — STANDARD', '')
    schema = t['sigla'].replace('S140R ', '')
    tip.append({'id': t['id'], 'serie': 'S140', 'nome': f"{t['gruppo']} — {var}", 'cod': t['cod'], 'rif': t['rif'] + ' (catalogo AluK S140 v5A 02.01.2026)', 'forma': 'S:' + schema, 'schema': schema,
                'famiglia': 'S140R' if t['sigla'].startswith('S140R') else 'S140 L&S', 'gruppo': t['gruppo'], 'variante': t['variante'], 'sigla': t['sigla'], 'soglia': t['soglia'], 'montante': t['montante'], 'lato': t.get('lato'),
                'porta': False, 'ferr': False, 'stulp': False, 'sopraluce': False, 'telaio_rif': t['profili'][0]['art'], 'anta_rif': 'U10140', 'vetro_tav': 'tavS140A', 'ore': t['ore'], 'specchiature': t['specchiature'], 'ante_mobili': t['ante_mobili'],
                'anta_l': t['anta_l'], 'anta_h': t['anta_h'], 'profili': prof, 'accessori': [{'art': a['art'], 'desc': a['desc'], 'pz': a['pz']} for a in t['accessori']], 'guarnizioni': gua, 'vetro': vetro,
                'kit_s140': {'anta_l': t['anta_l'], 'anta_h': t['anta_h'], 'righe': [{'cod': k['cod'], 'desc': k['desc'], 'q': k['q'], 'fascia': k.get('fascia'), 'fascia_h': k.get('fascia_h')} for k in t['kit']]},
                'avviso': 'Serie S140: distinta di taglio, accessori e guarnizioni dalle distinte ufficiali AluK (sez. 8), ferramenta per anta mobile dal listino. LAVORAZIONI MACCHINA NON ANCORA DEFINITE (manuale lavorazioni S140 v3A da trascrivere): il job contiene solo i tagli.'})
altezze = {a: h for a, (tipo, w, h) in DIM.items()}
profili_ana = {a: {'tipo': tipo, 'forma': 'L', 'w': w, 'h': h, 'nome': (CAT['profili'].get(a) or {}).get('desc', a), 'serie': 'S140', 'peso_g_m': round(((CAT['profili'].get(a) or {}).get('kg_m') or 0) * 1000)} for a, (tipo, w, h) in DIM.items()}
# sezioni DXF: match esatto codice profilo -> file (le varianti con suffisso _A/_B/.../_L restano in
# data/dxf_sez_s140.json per uso futuro ma non sono agganciate a nessun profilo). U10022 (telaio) non ha un DXF
# con questo nome nell'archivio ricevuto: confermato dall'utente il 15/09/2026 che "U10020.DXF" (140,0 mm di
# larghezza, esatta la quota di catalogo di U10022) è lo stesso profilo con una sigla di esportazione diversa.
ALIAS_DXF = {'U10022': 'U10020'}
dxf_sez = {}
mancanti = []
for art in profili_ana:
    fonte = ALIAS_DXF.get(art, art)
    if fonte in DXF:
        s = DXF[fonte]
        dxf_sez[art] = {'d': s['d'], 'x': 0, 'y': 0, 'w': s['w'], 'h': s['h'], 'cam': {'x': 0, 'y': 0, 'w': s['w'], 'h': s['h']},
                         'cam_nota': 'camera = ingombro totale del DXF ricevuto (da tarare sulla libreria macchina)'}
    else:
        mancanti.append(art)

OUT = {'serie_info': {'S140': {'nome': 'S140 — AluK S140 alzante scorrevole / scorrevole in linea', 'porta': False, 'sigla': 'S140', 'syst': 'S140', 'in_vista': False, 'tip_profili': True, 'da_tarare': True, 'vetro_default': '28',
                                'nota': 'AluK S140 v5A (02.01.2026): 36 tipologie = le stesse del programma listini (listini-serie/tipologie_s140.json). Telaio 2 binari U10022, 1 binario OX U10000, 3 binari U10060/U10061; anta U10140; soglia ribassata U10400/U10401/U10402+U10403; montante slim U10120. Lavorazioni macchina da definire (manuale v3A).'}},
       'varianti_porte': {'S140': {'ala': {}, 'telaio_int': 'U10022', 'nome_ala': ''}},   # telaio/anta/vetro definiti dalla tipologia (come COR80)
       'tipologie': tip, 'altezze': altezze, 'profili_ana': profili_ana, 'dxf_sez': dxf_sez, 'vetrazione': VETR,
       's140_note': {'fonte': CAT.get('_fonte', ''), 'nodi': CAT.get('nodi', {})}}
json.dump(OUT, open(os.path.join(ROOT, 'src', 'dati_s140.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('dati_s140.json: tipologie', len(tip), '| profili', len(profili_ana), '| sezioni DXF', len(dxf_sez), '(mancanti:', mancanti, ')', '| vetrazione', list(VETR), 'mm', list(VETR['tavS140A']['righe']))
