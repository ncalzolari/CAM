import json, re, unicodedata
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = os.path.join(ROOT,'data','catalogo_D67_D77')+'/'
d67 = json.load(open(E+'distinte_D67.json'))
d77 = json.load(open(E+'distinte_D77.json'))
idx = json.load(open(E+'profili_index.json'))
dxf = json.load(open(os.path.join(ROOT,'data','dxf_sez_porte.json')))

def norm_mis(m):
    m = str(m).replace(',', '.').replace(' ', '')
    return m

def sc_code(desc):
    d = desc.lower()
    if 'traverso stipite' in d: return 'TELL'
    if 'montante stipite' in d: return 'TELH'
    if 'traverso battente' in d: return 'ANTL'
    if 'centr' in d and 'battente' in d: return 'ANTC'
    if 'montante battente' in d: return 'ANTH'
    if 'zoccolo' in d: return 'ZOCC'
    if 'soglia' in d and 'guarnizione' not in d: return 'SOGL'
    if 'guarnizione soglia' in d: return 'GSOG'
    if 'spazzolino' in d: return 'SPAZ'
    if 'battuta per vie' in d: return 'ESOD'
    if 'profilo di battuta' in d: return 'BATT'
    if 'tagliavetro' in d: return 'TAGV'
    if 'inversione' in d or 'inv.' in d or 'invers' in d:
        return 'INVL' if 'trav' in d else 'INVH'
    if 'fermavetro' in d:
        if 'sopraluce' in d: return 'FVSL' if (' o' in d[:14] or 'orizz' in d) else 'FVSH'
        return 'FERL' if ('orizz' in d or ' o.' in d) else 'FERH'
    if 'aggiuntivo' in d:
        if 'trav' in d: return 'AGTL' if 'stipite' in d else 'AGAL'
        return 'AGTH' if 'stipite' in d else 'AGAH'
    return 'ALTR'

def slug(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode()
    t = t.upper().replace("'", ' ')
    t = re.sub(r'\bPORTA\b|\bCON\b|\bA\b|\bAD\b|\bSU\b', ' ', t)
    return re.sub(r'[^A-Z0-9]+', '_', t).strip('_')

def cod_tip(page, serie):
    t = page['titolo_it'].upper()
    ante = '2' if 'DUE ANTE' in t else '1'
    ap = {'interna': 'I', 'esterna': 'E', 'ante libere': 'V'}[page['apertura']]
    sog = 'A' if 'AUTOMATICA' in t else 'K' if 'K1490' in t else 'S' if 'K1769' in t or 'K2069' in t else 'P' if 'PANNELLO' in t else 'L' if 'SOPRALUCE' in t else 'X'
    extra = 'E' if 'ESODO' in t else ''
    serieC = serie[1:]  # 67 / 77
    zoc = 'Z' if any(p['desc_it'].lower().startswith('zoccolo') for p in page['profili']) else ''
    return f"P{ante}{ap}{sog}{extra}{zoc}{serieC}"

def build_tip(page, serie):
    t = page['titolo_it']
    ante2 = 'DUE ANTE' in t.upper()
    sopraluce = any('H1' in p['mis'] or 'H2' in p['mis'] for p in page['profili'])
    prof = []
    for p in page['profili']:
        mis = norm_mis(p['mis'])
        if mis in ('-', '') or p['taglio'] in ('-', ''):
            continue  # asta catenacci: va negli accessori
        art = p['art']
        fv = art == '-' and 'fermavetro' in p['desc_it'].lower()
        if fv: art = 'FVxx'
        sc = sc_code(p['desc_it'])
        dl = p['desc_it'].lower()
        if '(sx)' in dl: sc = sc[:3] + 'S'
        elif '(dx)' in dl: sc = sc[:3] + 'D'
        prof.append({'art': art, 'desc': p['desc_it'], 'pz': int(p['pz']), 'mis': mis, 'ang': p['taglio'], 'sc': sc} | ({'fv': True} if fv else {}))
    acc = []
    for a in page['accessori']:
        pz = a['pz']
        try: pzn = int(str(pz).strip())
        except: pzn = None
        desc = a['desc_it'] + ('' if pzn is not None or pz in ('-', '') else f' ({pz})')
        acc.append({'art': a['art'], 'desc': desc, 'pz': pzn})
    for p in page['profili']:
        if norm_mis(p['mis']) in ('-', '') and p['art'] != '-':
            acc.append({'art': p['art'], 'desc': p['desc_it'], 'pz': int(p['pz']) if str(p['pz']).isdigit() else None})
    gua = [{'art': g['art'], 'desc': g['desc_it'], 'mis': norm_mis(g['mis'])} for g in page['guarnizioni'] if norm_mis(g['mis']) not in ('-', '')]
    vetro = []
    for v in page['vetro']:
        if str(v.get('l', '-')).startswith('L') or str(v.get('l', '-')).startswith('H'):
            vetro.append({'pz': int(v['pz']) if str(v['pz']).isdigit() else 1, 'l': norm_mis(v['l']), 'h': norm_mis(v['h'])})
    anta_rif = next((p['art'] for p in page['profili'] if 'montante battente' in p['desc_it'].lower()), None)
    tel_rif = next((p['art'] for p in page['profili'] if 'montante stipite' in p['desc_it'].lower()), None)
    ap = page['apertura']
    nome = t.capitalize().replace("porta ad un'anta", "Porta a un'anta").replace('Porta ad due', 'Porta a due')
    nome = nome[0].upper() + nome[1:]
    nome = re.sub(r'\bk(\d{4})', lambda m: 'K'+m.group(1), nome)
    nome_ap = {'interna': 'ap. interna', 'esterna': 'ap. esterna', 'ante libere': 'ante libere'}[ap]
    zoc = any(p['desc_it'].lower().startswith('zoccolo') for p in page['profili'])
    tid = f"{serie}_{slug(t)}_{ {'interna':'INT','esterna':'EST','ante libere':'VENT'}[ap] }" + ('_Z' if zoc else '')
    if zoc: nome += ' e zoccolo'
    return {
        'id': tid, 'serie': serie, 'nome': f"{nome} — {nome_ap}", 'cod': cod_tip(page, serie),
        'rif': f"{serie} {page['pagina']} (catalogo AluK 14.10.2024)", 'forma': 'P2' if ante2 else 'P1',
        'porta': True, 'apertura': 'est' if ap == 'esterna' else 'int', 'ventola': ap == 'ante libere',
        'sopraluce': sopraluce, 'anta_rif': anta_rif, 'telaio_rif': tel_rif,
        'avviso': 'Serie nuova (IWG ' + serie[1:] + 'ID): distinta dal catalogo AluK, senza riscontro di produzione. Lavorazioni ferramenta marcate "da tarare": verificare a video in FSTLine e sul primo pezzo.' + (' Inserire H2 = altezza sopraluce; H1 = H − H2.' if sopraluce else ''),
        'profili': prof, 'accessori': acc, 'guarnizioni': gua, 'vetro': vetro,
    }

tipologie = [build_tip(p, 'D67') for p in d67] + [build_tip(p, 'D77') for p in d77]
ids = [t['id'] for t in tipologie]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
cods = [t['cod'] for t in tipologie]
assert len(cods) == len(set(cods)), [c for c in cods if cods.count(c) > 1]

# ---- profili: anagrafica, altezze, sezioni ----
sin = {r['art']: r for r in idx['sinottico']}
ind = {r['art']: r for r in idx['indice']}
used = sorted({p['art'] for t in tipologie for p in t['profili'] if p['art'] != 'FVxx'})
def dims(art):
    q = sin.get(art, {}).get('quote', '') or ''
    m = re.findall(r'[\d.]+', q.split('(')[0])
    return [float(x) for x in m]
altezze, profili_ana = {}, {}
NOMINAL_H = {  # altezza nominale nel piano di taglio (da sinottico/catalogo); ali escluse
    'U51200': 66, 'U51201': 66, 'U51220': 66, 'U51240': 66, 'U52200': 66, 'U52201': 66, 'U52220': 66, 'U52240': 66,
    'U20001': 71, 'U28003': 71, 'U20000': 53, 'U28002': 53,
    'U51320': 82, 'U51340': 96, 'U51300': 74, 'U52320': 96, 'U52340': 96, 'U52300': 74,
    'U20630': 160, 'U28630': 160, 'U20601': 96, 'U28602': 96,
    'N51260': 37, 'N52260': 42, 'U51630': 50, 'U52630': 50, 'U52360': 50,
    'U51501': 32, 'U52500': 29, 'U51502': 24, 'U52501': 24,
    'K1769': 20, 'K2069': 20, 'K1490': 36, 'K1488': 23, 'K1486': 18, 'K1483': 20, 'K1577': 29,
}
for art in used:
    dm = dims(art)
    h = NOMINAL_H.get(art, dm[-1] if dm else 50)
    altezze[art] = h
    desc = ind.get(art, {}).get('desc_it', sin.get(art, {}).get('gruppo', ''))
    serie = ind.get(art, {}).get('serie', '')
    tipo = 'telaio' if art in ('U51200','U51201','U51220','U51240','U52200','U52201','U52220','U52240','U20001','U28003') else \
           'anta' if art in ('U51320','U51340','U51300','U52320','U52340','U52300') else \
           'traverso' if art in ('U20601','U28602') else 'accessorio'
    w = dm[0] if dm else None
    profili_ana[art] = {'tipo': tipo, 'forma': 'A' if tipo == 'anta' else 'L', 'w': w, 'h': h, 'nome': f"{desc} ({serie})".strip()}
dxf_sez = {}
for art in used:
    if art in dxf:
        s = dxf[art]
        dxf_sez[art] = {'d': s['d'], 'x': 0, 'y': 0, 'w': s['w'], 'h': s['h'], 'cam': {'x': 0, 'y': 0, 'w': s['w'], 'h': s['h']}, 'cam_nota': 'camera = ingombro totale (da tarare)'}

# ---- vetrazione porte ----
vet = {'D67': {'profili': ['U51320', 'U51340', 'U51300'], 'righe': {}}, 'D77': {'profili': ['U52320', 'U52340', 'U52300'], 'righe': {}}}
for r in idx['vetrazione']['righe']:
    s = r['serie']
    fv = r['fermavetro_squadrato'] if r['fermavetro_squadrato'] not in ('-', '', None) else (r['fermavetro_tubolare'] if r['fermavetro_tubolare'] not in ('-', '', None) else r['fermavetro_a_clips'])
    vet[s]['righe'][str(r['spessore_vetro_mm'])] = {'A': r['quota_A_mm'], 'g': r['guarnizione_interna'], 'B': r['quota_B_mm'], 'fv': fv,
        'fv_sq': r['fermavetro_squadrato'], 'fv_tub': r['fermavetro_tubolare'], 'fv_clip': r['fermavetro_a_clips']}

out = {
    'serie_info': {
        'D67': {'nome': 'D67 — IWG 67ID (AluK, porte 67 mm)', 'porta': True, 'sigla': 'IWG 67ID', 'syst': 'D67'},
        'D77': {'nome': 'D77 — IWG 77ID (AluK, porte 77 mm)', 'porta': True, 'sigla': 'IWG 77ID', 'syst': 'D77'},
    },
    'varianti_porte': {
        'D67': {'ala': {'U51200': 'U51220', 'U51201': 'U51240'}, 'telaio_int': 'U51200', 'telaio_est': 'U51201'},
        'D77': {'ala': {'U52200': 'U52220', 'U52201': 'U52240'}, 'telaio_int': 'U52200', 'telaio_est': 'U52201'},
    },
    'tipologie': tipologie, 'altezze': altezze, 'profili_ana': profili_ana, 'dxf_sez': dxf_sez,
    'vetrazione': {'tavD67': vet['D67'], 'tavD77': vet['D77']},
    'porte_note': {
        'fonte': 'Catalogo tecnico AluK D67/D77 v4C (23.06.2025) sez. 8 distinte di taglio 14.10.2024; manuale lavorazioni v4.A.',
        'stato': 'Serie nuova, mai prodotta con FP Pro: nessun riscontro di produzione. Formule = catalogo.',
    },
}
json.dump(out, open(os.path.join(ROOT,'src','dati_porte.json'), 'w'), ensure_ascii=False, indent=1)
print(len(tipologie), 'tipologie;', len(used), 'profili;', len(dxf_sez), 'sezioni DXF;', 'vetri D67', len(vet['D67']['righe']), 'D77', len(vet['D77']['righe']))
for t in tipologie: print(f" {t['cod']:10} {t['id']:45} {t['nome']}")
print('profili senza DXF:', [a for a in used if a not in dxf])
