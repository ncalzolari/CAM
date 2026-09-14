#!/usr/bin/env python3
# Listini a griglia per le altre serie AluK (D67/D77 porte, S140 scorrevoli): distinte dal programma commesse e da tipologie_s140.json
# (src/dati_*.json), prezzi AluK da listini-db, kit Maico dalle regole WinPlus (listini-c75s/genera_listini.py),
# ferramenta porte dalla libreria FP D67 (fp_blk_D67.json), S140 dal catalogo tecnico (catalogo_S140.json). Pesi in pesi_profili.json (modificabile).
# Produce dati_listini_serie.json, Listini_Serie.html (autonomo) e Listini_Serie_web.html (Artifact).
import json, os, re, sys, io, contextlib, sqlite3
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
APP = os.path.join(ROOT, 'commesse-lmt65', 'src'); DB = os.path.join(ROOT, 'listini-db', 'listini.sqlite')
sys.path.insert(0, os.path.join(ROOT, 'listini-c75s'))
with contextlib.redirect_stdout(io.StringIO()):
    import genera_listini as g          # KIT_ANTA, FERR_FISSE_ANTA, FERR_SEMIFISSA, NETTO (rigenera anche gli xlsx C75S)

def carica(nome): return json.load(open(os.path.join(APP, nome), encoding='utf-8'))
D = {}
for f in ('dati_app.json', 'dati_porte.json'):
    for k, v in carica(f).items():
        if k == 'tipologie': D.setdefault('tipologie', []).extend(v)
        elif isinstance(v, dict): D.setdefault(k, {}).update(v)
        else: D[k] = v
S140_CAT = json.load(open(os.path.join(ROOT, 'commesse-lmt65', 'data', 'catalogo_S140', 'catalogo_S140.json'), encoding='utf-8'))
S140_PREZZO_FIX = {'V50051': 0.2132}   # a listino 21,32 EUR per confezione da 100 pz (il DB riporta il prezzo confezione come unitario)
S140_TIP = json.load(open(os.path.join(HERE, 'tipologie_s140.json'), encoding='utf-8'))['tipologie']
TIP = {t['id']: t for t in D['tipologie'] + S140_TIP}
def deriva_est_automatica(serie, base_id, due):
    """Porta apertura esterna con soglia automatica senza zoccolo (attacco al piede standard 14/09/2026, catalogo nodo U51340 +
    soglia 732040÷732046 + gocciolatoio K1486 + guarnizione 809944), derivata dalla distinta con soglia K1769/K2069 (8.18/8.19)
    applicando le differenze tra le distinte interne 8.07/8.08 (automatica) e le corrispondenti con soglia a profilo."""
    import copy
    b = TIP[base_id]; t = copy.deepcopy(b)
    t['id'] = f"{serie}_{'DUE_ANTE' if due else 'UN_ANTA'}_SOGLIA_AUTOMATICA_EST"; t['cod'] = f"{'P2' if due else 'P1'}EA{serie[1:]}"
    ante = 'a due ante' if due else "ad un'anta"
    t['nome'] = f"Porta {ante} con soglia automatica — ap. esterna (derivata)"
    t['rif'] = f"derivata da {b.get('rif','')} con attacco al piede della 8.0{8 if due else 7}"
    t['profili'] = [dict(p, mis=p['mis'].replace('H-57', 'H-55')) for p in b['profili'] if p['art'] not in ('K1483', 'K1769', 'K2069')]
    for p in t['profili']:
        if p['art'].startswith('FV') and p['mis'].startswith('H-'): p['mis'] = 'H-247'
    if not due: t['profili'].append({'art': 'K1486', 'pz': 1, 'mis': 'L-148', 'desc': 'Profilo portaspazzolino / gocciolatoio'})
    t['accessori'] = [a for a in b['accessori'] if a['art'] not in ('732086', '732087', '732107')] + [{'art': '732040÷732046', 'desc': 'Soglia automatica (per larghezza anta)', 'pz': 2 if due else 1}] + ([{'art': 'K1486', 'desc': 'Portaspazzolino', 'pz': 2}] if due and not any(a['art'] == 'K1486' for a in b['accessori']) else [])   # come la 8.08 interna: K1486 x2 + aste K1777 x2 (già nella base)
    t['guarnizioni'] = [dict(g, mis=g['mis'].replace('3L', '2L')) for g in b['guarnizioni']] + [{'art': '809944', 'desc': 'Guarnizione sottoporta soglia automatica', 'mis': 'L'}]
    TIP[t['id']] = t; return t['id']
for serie, k in (('D67', 'K1769'), ('D77', 'K2069')):
    deriva_est_automatica(serie, f'{serie}_UN_ANTA_SOGLIA_{k}_EST', False); deriva_est_automatica(serie, f'{serie}_DUE_ANTE_SOGLIA_{k}_EST', True)
db = sqlite3.connect(DB)
def prezzo_acc(cod):
    r = db.execute("SELECT prezzo_unitario FROM v_accessori WHERE codice=? ORDER BY CASE listino WHEN 'c75s_c82s' THEN 1 ELSE 0 END LIMIT 1", (cod,)).fetchone()
    if r is None and not cod.endswith('-B'):                                       # articoli a listino solo con suffisso colore nero (-B)
        r = db.execute("SELECT prezzo_unitario FROM v_accessori WHERE codice=? LIMIT 1", (cod + '-B',)).fetchone()
    return r[0] if r else None
def eur_kg_grezzo(serie_aluk):
    r = db.execute("SELECT grezzo_eur_kg FROM v_profili WHERE serie=? LIMIT 1", (serie_aluk,)).fetchone(); return r[0] if r else None
def eur_kg_articolo(art):
    r = db.execute("SELECT listino_eur_kg FROM v_profili_articoli WHERE articolo=?", (art,)).fetchone(); return r[0] if r else None
SERIE_N_GREZZO = {'D67': '166', 'D77': '166', 'S140': '114'}   # S140: PR.ALL.N COMPL S140   # listino profili generale: PR.ALL.N F.VETRI+COMP.K (profili non isolati K…, fermavetri N…); la 101 FVETRI+COMPLEM ha lo stesso €/kg. Il listino C75S/C82S-CS (articoli 108xx/333xx) vale solo per quelle serie.
DECORRENZA = db.execute("SELECT MAX(decorrenza) FROM listini WHERE fornitore='AluK'").fetchone()[0]

# ---- file modificabili: pesi profili porte, prezzi Cortizo ----
def carica_json(nome, default):
    p = os.path.join(HERE, nome)
    if os.path.exists(p): return json.load(open(p, encoding='utf-8'))
    return default
PESI = carica_json('pesi_profili.json', {"_nota": "kg/m per articolo (porte AluK D67/D77: dal catalogo o da FP Pro). null = da inserire.", "pesi": {}})

def lin(expr):
    """coefficienti (c, cL, cH) di una formula lineare in L e H ('2*(L-170)+2*(H-170)', 'L/2-9', '3L+4H')."""
    s = str(expr).replace(',', '.').replace(' ', '')
    if not re.fullmatch(r'[0-9LH+\-*/().]+', s): return None
    s = re.sub(r'L/2', '(L/2)', s); s = re.sub(r'(\d)([LH(])', r'\1*\2', s); s = re.sub(r'\)([LH(\d])', r')*\1', s)
    try:
        f = lambda L, H: eval(s, {'__builtins__': {}}, {'L': L, 'H': H})
        c = f(0, 0); return (c, f(1, 0) - c, f(0, 1) - c)
    except Exception: return None

def classe_profilo(serie, art):
    if serie == 'S140': return (S140_CAT['profili'].get(art) or {}).get('classe') or ('tt' if art.startswith('U') else 'n')
    return 'tt' if art.startswith('U') else 'n'          # porte AluK: U = profili a taglio termico; N fermavetri, K soglie/accessori

CAT_PESI = carica_json(os.path.join('..', 'commesse-lmt65', 'data', 'catalogo_D67_D77', 'pesi_profili_catalogo.json'), {'pesi': {}})['pesi']   # catalogo tecnico AluK D67-D77 v4C
def peso_kg_m(serie, art):
    p = PESI['pesi'].get(art)
    if p: return (p, 'pesi_profili.json')
    if serie == 'S140':
        k = (S140_CAT['profili'].get(art) or {}).get('kg_m'); return (k, 'catalogo AluK S140 v5A') if k else (None, 'da inserire')
    c = CAT_PESI.get(art); return (c['kg_m'], 'catalogo AluK D67-D77') if c else (None, 'da inserire')

def fermavetro(t, vetro):
    tav = D['vetrazione'].get(t.get('vetro_tav') or ('tavD67' if t['serie']=='D67' else 'tavD77' if t['serie']=='D77' else ''), {})
    r = (tav.get('righe') or {}).get(str(vetro)); return (r or {}).get('fv'), (r or {}).get('g')

# ---- kit ferramenta porte dalla libreria FP D67 (blocchi .BLK) ----
BLK = json.load(open(os.path.join(ROOT, 'commesse-lmt65', 'data', 'catalogo_D67_D77', 'fp_blk_D67.json'), encoding='utf-8'))
def blocco_per(t):
    n = t['id']; due = t['forma'] == 'P2'; est = t.get('apertura') == 'est'
    if 'AUTOMATICA' in n: return ('350-21' if due else '350-02') if not est else ('360-02' if not due else '350-21')   # 2 ante esterna automatica: nessun blocco dedicato, riusato 350-21
    if 'K1769' in n or 'K2069' in n: return ('370-06' if est else '350-04') if not due else ('370-06' if est else '350-04')
    if 'K1490' in n: return ('370-01' if est else '350-20') if due else ('360-01' if est else '350-01')
    return '350-01'
FINITURA_BASE = '20'                  # aggregazione AluK impostata sempre all'apertura: cartella con addebito cat. B (RAL 7016 opaco)
CERNIERA_PORTA = 'H51300-B1'          # cerniera a stelo AluK, colore nero R.9005 — sempre per le porte D67/D77
CERNIERE_PER_ANTA = [[1300, 2], [2400, 3], [None, 4]]   # n. cerniere per anta in funzione dell'altezza anta (regola catalogo AluK 10.51 estesa alle cerniere a stelo)
SERRATURA_STD = [   # pacchetto serratura standard porte (prezzi netti di acquisto, nessuno sconto ulteriore) — codici interni modificabili nella tabella ferramenta
    ('SERR-PERFORMA', 'Serratura Performa 3 catenacci + scrocco E35 I85 nera', 1, 68.67),
    ('INC-PERFORMA-229', 'Incontro centrale F29x229 nero per Performa meccanica', 1, 10.03),
    ('INC-PERFORMA-186', 'Incontro deviatori F29x186 nero per Performa', 2, 9.96),
    ('CIL-123P-22-10-22', 'Cilindro sagomato 123P 22/10/22 alluminio con pomolo nylon', 1, 14.05),
    ('201-10510', 'Kit maniglia passante colore argento', 1, 26.50),
]
ACC_A_PESO = {   # accessori a codice K (profili non isolati venduti a peso): lunghezza per (1 anta, 2 ante)
    'K1486': ('L-148', 'L/2-91.5'),      # portaspazzolino: larghezza anta − 54 (come nella distinta a 1 anta)
    'K1777': ('H/2-27.5', 'H/2-27.5'),   # asta catenacci: ipotesi metà altezza anta per asta (superiore e inferiore) — DA VERIFICARE
}
ASACA_CCE = [(330, 20.50), (430, 20.00), (530, 21.00), (630, 25.05), (730, 23.84), (830, 22.00), (930, 22.00), (1030, 26.84), (1130, 25.00), (1230, 24.00), (1330, 28.00), (1430, 44.40), (1530, 44.35)]
# soglia automatica ASACA 25x20 (fornitore CCE, prezzi netti, compatibilità verificata): sostituisce le AluK 732040-732046; lunghezza nominale = prima >= larghezza anta
def righe_asaca(q=1):
    return [{'cod': f'ASACA{n}', 'desc': f'Antispifero sottoporta ASACA 25x20 L={n} (anta {n-99}-{n})' + (' (1 per anta)' if q > 1 else ''), 'q': q, 'pr': pr, 'fonte': 'netto fornitore CCE', 'fascia': [n - 100, n]} for n, pr in ASACA_CCE]
def kit_blk(t):
    b = BLK.get(blocco_per(t)); out = []
    if not b: return out, None
    for f in b['accessori']:
        if f.get('Optional') == '1' or f.get('Type') != '1': continue          # opzionali esclusi; guarnizioni (T4) già nella distinta
        if f.get('Apertura') == '2': continue                                   # coppia DX/SX: una sola
        pr = prezzo_acc(f['Code']); fascia = None
        m = re.search(r'\((\d+)-(\d+)\s*MM\)', f['Description'])
        if f.get('RefDim') == '101' and m: fascia = [int(m.group(1)), int(m.group(2))]     # soglia automatica per larghezza anta
        if fascia: continue                                                    # soglie automatiche AluK: sostituite dalle ASACA (CCE)
        out.append({'cod': f['Code'], 'desc': f['Description'][:60], 'q': int(f.get('Multiply') or 1), 'pr': pr, 'fonte': 'listino AluK' if pr is not None else 'da inserire', 'fascia': fascia})
    if 'AUTOMATICA' in t['id']: out += righe_asaca(2 if t['forma'] == 'P2' else 1)
    return out, b['descrizione']

# ---- configurazione delle griglie ----
CONFIG = {
 'D67': {'nome': 'AluK D67 — IWG 67ID (porte)', 'aluk': '312', 'vetro': '28',
   'griglie': [('D67_UN_ANTA_SOGLIA_AUTOMATICA_INT', (800,1400), (2000,2600), 6.0), ('D67_UN_ANTA_SOGLIA_AUTOMATICA_INT_Z', (800,1400), (2000,2600), 6.0), ('D67_UN_ANTA_SOGLIA_K1769_INT_Z', (800,1400), (2000,2600), 6.0),
               ('D67_DUE_ANTE_SOGLIA_AUTOMATICA_INT', (1200,2200), (2000,2600), 10.0), ('D67_DUE_ANTE_SOGLIA_K1490_INT_Z', (1200,2200), (2000,2600), 10.0), ('D67_DUE_ANTE_SOGLIA_K1769_INT_Z', (1200,2200), (2000,2600), 10.0),
               ('D67_UN_ANTA_SOGLIA_AUTOMATICA_EST', (800,1400), (2000,2600), 6.0), ('D67_UN_ANTA_SOGLIA_K1490_EST_Z', (800,1400), (2000,2600), 6.0), ('D67_UN_ANTA_SOGLIA_K1769_EST_Z', (800,1400), (2000,2600), 6.0), ('D67_UN_ANTA_SOGLIA_K1769_EST', (800,1400), (2000,2600), 6.0),
               ('D67_DUE_ANTE_SOGLIA_AUTOMATICA_EST', (1200,2200), (2000,2600), 10.0), ('D67_DUE_ANTE_SOGLIA_K1490_EST_Z', (1200,2200), (2000,2600), 10.0), ('D67_DUE_ANTE_SOGLIA_K1769_EST_Z', (1200,2200), (2000,2600), 10.0), ('D67_DUE_ANTE_SOGLIA_K1769_EST', (1200,2200), (2000,2600), 10.0)]},
 'D77': {'nome': 'AluK D77 — IWG 77ID (porte)', 'aluk': '315', 'vetro': '28',
   'griglie': [('D77_UN_ANTA_SOGLIA_AUTOMATICA_INT', (800,1400), (2000,2600), 6.0), ('D77_UN_ANTA_SOGLIA_AUTOMATICA_INT_Z', (800,1400), (2000,2600), 6.0), ('D77_UN_ANTA_SOGLIA_K2069_INT_Z', (800,1400), (2000,2600), 6.0),
               ('D77_DUE_ANTE_SOGLIA_AUTOMATICA_INT', (1200,2200), (2000,2600), 10.0), ('D77_DUE_ANTE_SOGLIA_K1490_INT_Z', (1200,2200), (2000,2600), 10.0), ('D77_DUE_ANTE_SOGLIA_K2069_INT_Z', (1200,2200), (2000,2600), 10.0),
               ('D77_UN_ANTA_SOGLIA_AUTOMATICA_EST', (800,1400), (2000,2600), 6.0), ('D77_UN_ANTA_SOGLIA_K1490_EST_Z', (800,1400), (2000,2600), 6.0), ('D77_UN_ANTA_SOGLIA_K2069_EST_Z', (800,1400), (2000,2600), 6.0), ('D77_UN_ANTA_SOGLIA_K2069_EST', (800,1400), (2000,2600), 6.0),
               ('D77_DUE_ANTE_SOGLIA_AUTOMATICA_EST', (1200,2200), (2000,2600), 10.0), ('D77_DUE_ANTE_SOGLIA_K1490_EST_Z', (1200,2200), (2000,2600), 10.0), ('D77_DUE_ANTE_SOGLIA_K2069_EST_Z', (1200,2200), (2000,2600), 10.0), ('D77_DUE_ANTE_SOGLIA_K2069_EST', (1200,2200), (2000,2600), 10.0)]},
 'S140': {'nome': 'AluK S140 — alzante scorrevole / scorrevole in linea', 'aluk': '335', 'vetro': '28',
   'griglie': [(t['id'], {'S1': (1600,3600), 'S2': (1800,4000), 'S3': (2700,6000), 'S4': (3600,8000), 'S6': (5400,9000)}[t['forma']] if '_LS_' in t['id'] else (1600,3000),
                (2000,2700) if '_LS_' in t['id'] else (2000,2500), t['ore']) for t in S140_TIP]},      # ore = 4,5 h per specchiatura (genera_tipologie_s140.py)
}
OUT = {'decorrenza': DECORRENZA, 'serie': {}, 'kit_maico': [[d, c, r, q] for d, c, r, q in g.KIT_ANTA],
       'fisse_anta': [[d, c or '', q, m] for d, c, q, m in g.FERR_FISSE_ANTA], 'semifissa': [[d, c or '', q, m] for d, c, q, m in g.FERR_SEMIFISSA],
       'netto': {c: round(p, 4) for c, p in g.NETTO.items()}, 'cerniere_per_anta': CERNIERE_PER_ANTA, 'pesi_mancanti': {}, 'prezzi_mancanti': {}}
for serie, cfg in CONFIG.items():
    par = {'sfrido': 0.09, 'eur_h': 65.0, 'ricarico': 2.13}
    if cfg['aluk']:
        par.update(eur_kg_tt=eur_kg_grezzo(cfg['aluk']) or 0, eur_kg_n=eur_kg_grezzo(SERIE_N_GREZZO[serie]) or 0, sc_prof=0.38, sc_acc=0.20, finitura=FINITURA_BASE, add_kg=0.0)
        finiture = [{'agg': a, 'nome': n, 'add': f} for a, n, f in db.execute("SELECT aggregazione, finitura, finitura_eur_kg FROM v_profili WHERE serie=? ORDER BY aggregazione", (cfg['aluk'],))]
        par['add_kg'] = next((f['add'] for f in finiture if f['agg'] == FINITURA_BASE), 0.0)     # RAL 7016 opaco = cartella con addebito cat. B (agg. 20)
        fonte = f"listino AluK {DECORRENZA}: profili TT serie {cfg['aluk']} grezzo {par['eur_kg_tt']} €/kg, profili non isolati (N, K) grezzo {par['eur_kg_n']} €/kg (serie {SERIE_N_GREZZO[serie]} F.VETRI+COMP.K) + addebito verniciatura per aggregazione (base RAL 7016 opaco = agg. 20 cartella con addebito cat. B); accessori listino AluK."
    S = {'nome': cfg['nome'], 'param': par, 'fonte': fonte, 'vetro': cfg['vetro'], 'ordine': [], 'tip': {}, 'finiture': finiture if cfg['aluk'] else []}
    for tid, Lr, Hr, ore in cfg['griglie']:
        t = TIP[tid]; key = t.get('cod') or tid
        fv_art, g_art = fermavetro(t, cfg['vetro'])
        profili = []
        for p in t['profili']:
            art = fv_art if p['art'].startswith('FV') else p['art']
            if not art or art == '-': continue
            co = lin(p['mis'])
            if co is None: continue
            kg, fpeso = peso_kg_m(serie, art)
            profili.append({'art': art, 'desc': p.get('desc', ''), 'pz': p['pz'], 'mis': p['mis'], 'lin': co, 'classe': classe_profilo(serie, art), 'kg_m': kg, 'fonte_peso': fpeso})
            if kg is None: OUT['pesi_mancanti'].setdefault(serie, set()).add(art)
        acc = []
        for a in t.get('accessori', []):
            if a['art'] in ('-',) or '÷' in a['art']: continue                      # voci senza codice o fasce (soglia automatica: nel kit)
            cod = a['art'].split('/')[0].strip()
            if cod in ACC_A_PESO and serie in ('D67', 'D77'):                                # profili K elencati come accessori: prezzati a peso come profili non isolati
                mis = ACC_A_PESO[cod][1 if t['forma'] == 'P2' else 0]; kg, fpeso = peso_kg_m(serie, cod)
                profili.append({'art': cod, 'desc': a.get('desc', ''), 'pz': a.get('pz') or 1, 'mis': mis, 'lin': lin(mis), 'classe': classe_profilo(serie, cod), 'kg_m': kg, 'fonte_peso': fpeso})
                if kg is None: OUT['pesi_mancanti'].setdefault(serie, set()).add(cod)
                continue
            pr = prezzo_acc(cod)
            if serie == 'S140' and cod in S140_PREZZO_FIX: pr = S140_PREZZO_FIX[cod]
            a = dict(a, art=cod)
            if pr is None: OUT['prezzi_mancanti'].setdefault(serie, set()).add(a['art'])
            acc.append({'art': a['art'], 'desc': a.get('desc', ''), 'pz': a.get('pz') or 0, 'pr': pr})
        gua = []
        for gg in t.get('guarnizioni', []):
            art = g_art if (gg.get('gv') or gg['art'].startswith('809119')) and g_art else gg['art']
            co = lin(gg['mis']);
            if co is None: continue
            pr = prezzo_acc(art)
            barra = next((x['barra_m'] for x in S140_CAT['guarnizioni'] if x['art'] == art), None) if serie == 'S140' else None
            if pr is not None and barra: pr = round(pr / barra, 4)                   # articoli venduti a barra (labirinti, cover PVC): €/m
            if pr is None: OUT['prezzi_mancanti'].setdefault(serie, set()).add(art)
            gua.append({'art': art, 'desc': gg.get('desc', '') + (f' (barra {barra} m)' if barra else ''), 'mis': gg['mis'], 'lin': co, 'pr': pr})
        kit = {'tipo': 'nessuno'}
        if serie == 'S140':
            righe = []
            for r in t['kit']:
                pr = r['pr'] if r.get('pr') is not None else prezzo_acc(r['cod'])
                if pr is None: OUT['prezzi_mancanti'].setdefault(serie, set()).add(r['cod'])
                righe.append({'cod': r['cod'], 'desc': r['desc'], 'q': r['q'], 'pr': pr, 'fonte': r.get('fonte') or ('listino AluK' if pr is not None else 'da inserire'), 'fascia': r.get('fascia'), 'fascia_h': r.get('fascia_h')})
            kit = {'tipo': 'blk', 'blocco': f"catalogo S140 sez. 3 — {t['ante_mobili']} anta/e mobile/i", 'righe': righe, 'anta_l': t['anta_l'], 'anta_h': t['anta_h'], 'nota': 'kit ferramenta per anta mobile dalle distinte S140 (meccanismo per altezza anta, asta per larghezza anta; voci opzionali escluse)'}
        elif serie in ('D67', 'D77') and t['forma'] in ('P1', 'P2'):
            righe, nome_blk = kit_blk(t); anta = next((p for p in t['profili'] if 'Traverso battente' in p.get('desc', '')), None)
            if t['forma'] == 'P2' and 'AUTOMATICA' in tid and not any(r['cod'] == 'K1488' for r in righe):     # il blocco FP a 2 ante non elenca lo spazzolino soglia: uno per anta, dal blocco a 1 anta
                sog1, _ = kit_blk({'id': tid.replace('DUE_ANTE', 'UN_ANTA'), 'forma': 'P1', 'apertura': t.get('apertura')})
                for r in sog1:
                    if r['cod'] == 'K1488': righe.append(dict(r, q=2 * r['q'], desc=r['desc'] + ' (1 per anta)'))
            gia = {a['art'] for a in acc}; righe = [r for r in righe if r['cod'] not in gia]      # voci già nella distinta della tipologia
            righe = [r for r in righe if not (r['cod'].startswith('7322') and any(w in r['desc'].upper() for w in ('SERR', 'INCONTRO', 'SCONTRO', 'COPRIFRESATA')))]   # serratura del blocco FP sostituita dal pacchetto standard
            righe += [{'cod': c, 'desc': d, 'q': q, 'pr': pr, 'fonte': 'netto fornitore', 'fascia': None} for c, d, q, pr in SERRATURA_STD]
            n_ante = 2 if t['forma'] == 'P2' else 1
            righe = [r for r in righe if not r['cod'].startswith('H5')]      # eventuali cerniere del blocco FP: sostituite dalla regola sotto
            pr_cern = prezzo_acc(CERNIERA_PORTA)
            righe.append({'cod': CERNIERA_PORTA, 'desc': 'Cerniera a stelo per porta R.9005 nera (dima T10020)', 'q': n_ante, 'cern': n_ante, 'pr': pr_cern, 'fonte': 'listino AluK' if pr_cern is not None else 'da inserire', 'fascia': None})
            anta_h = next((p for p in t['profili'] if 'Montante battente' in p.get('desc', '')), None)
            kit = {'tipo': 'blk', 'blocco': nome_blk, 'righe': righe, 'anta_l': anta['mis'] if anta else 'L-94', 'anta_h': anta_h['mis'] if anta_h else 'H-70', 'nota': 'kit dalla libreria FP D67' + (' riusato per D77' if serie == 'D77' else '') + ' (voci non opzionali; da verificare)'}
        if serie in ('D67', 'D77'):
            gruppo = f"Porta {'2 ante' if t['forma']=='P2' else '1 anta'} — apertura {'esterna' if t.get('apertura')=='est' else 'interna'}"
            sog = 'soglia automatica' if 'AUTOMATICA' in tid else 'soglia K1490' if 'K1490' in tid else 'soglia K1769' if 'K1769' in tid else 'soglia K2069' if 'K2069' in tid else 'soglia'
            variante = sog + (' con zoccolo' if tid.endswith('_Z') else ' senza zoccolo') + (' — STANDARD' if 'AUTOMATICA' in tid and not tid.endswith('_Z') else '')
        elif serie == 'S140': gruppo, variante = ('Alzante scorrevole (S140 L&S)' if '_LS_' in tid else 'Scorrevole in linea (S140R)'), t['nome'] + (' — soglia standard — STANDARD' if t.get('soglia') == 'standard' else '') + ' [distinta ' + t.get('rif','').replace('S140 ','') + ']'
        else: gruppo, variante = t['nome'], ''
        S['tip'][key] = {'id': tid, 'gruppo': gruppo, 'variante': variante, 'nome': t['nome'], 'forma': t['forma'], 'L': list(Lr), 'H': list(Hr), 'ore': ore, 'profili': profili, 'acc': acc, 'guarn': gua, 'kit': kit,
                         'vetro': [{'pz': v.get('pz', 1), 'l': lin(v['l']), 'h': lin(v['h'])} for v in t.get('vetro', []) if lin(v['l']) and lin(v['h'])]}
        S['ordine'].append(key)
    OUT['serie'][serie] = S
OUT['pesi_mancanti'] = {k: sorted(v) for k, v in OUT['pesi_mancanti'].items()}; OUT['prezzi_mancanti'] = {k: sorted(v) for k, v in OUT['prezzi_mancanti'].items()}
# file modificabili: creo/aggiorno i modelli con le chiavi mancanti (valori null)
for art in sorted({a for s in ('D67', 'D77', 'S140') for a in OUT['pesi_mancanti'].get(s, [])}): PESI['pesi'].setdefault(art, None)
json.dump(PESI, open(os.path.join(HERE, 'pesi_profili.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(OUT, open(os.path.join(HERE, 'dati_listini_serie.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('serie:', {s: len(v['tip']) for s, v in OUT['serie'].items()}, '| pesi mancanti:', {k: len(v) for k, v in OUT['pesi_mancanti'].items()}, '| prezzi mancanti:', {k: len(v) for k, v in OUT['prezzi_mancanti'].items()})

# ---- pagina HTML (autonoma + web) ----
import hashlib
def fnv(t):
    x = 0x811c9dc5
    for c in t.encode(): x = ((x ^ c) * 0x01000193) & 0xffffffff
    return x
CODICE = '140979'
html = open(os.path.join(HERE, 'template_serie.html'), encoding='utf-8').read()
html = html.replace('/*__DATI__*/', json.dumps(OUT, ensure_ascii=False)).replace('__MG_H__', hashlib.sha256(CODICE.encode()).hexdigest()).replace('__MG_F__', str(fnv(CODICE)))
open(os.path.join(HERE, 'Listini_Serie.html'), 'w', encoding='utf-8').write(html)
w = html
for tag in ['<!DOCTYPE html>\n', '<html lang="it">\n', '<head>\n', '<meta charset="utf-8">\n', '<meta name="viewport" content="width=device-width, initial-scale=1">\n', '</head>\n', '<body>\n', '</body>\n', '</html>\n']:
    assert w.count(tag) == 1, tag; w = w.replace(tag, '')
old = """function scarica(dati, nome){
  const tipoMime = nome.endsWith('.csv') ? 'text/csv;charset=utf-8' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([dati], {type: tipoMime})); a.download = nome; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href), 3000);
  $('#esito').textContent = `File ${nome} generato.`;
}"""
assert w.count(old) == 1
w = w.replace(old, """let __dlCap = null, __dlPronto = false, __dlInCorso = false;
if(window.claude && typeof claude.use==='function') claude.use('downloads').then(d=>{ __dlCap = d; __dlPronto = true; }).catch(()=>{ __dlPronto = true; });
function scarica(dati, nome){
  if(!__dlCap){ $('#esito').textContent = __dlPronto ? 'Salvataggio non disponibile in questa vista: usa il file Listini_Serie.html scaricato.' : 'Un attimo: salvataggio in preparazione, riprova.'; return; }
  if(__dlInCorso){ $('#esito').textContent = 'Conferma prima il salvataggio precedente.'; return; }
  __dlInCorso = true; $('#esito').textContent = `Preparo ${nome}…`;
  __dlCap.save({filename: nome, data: dati}).then(()=>{ $('#esito').textContent = `File ${nome} salvato.`; })
    .catch(e=>{ const c = e && e.code; if(c==='declined'){ $('#esito').textContent = ''; return; } $('#esito').textContent = c==='rate_limited' ? 'Attendi: una richiesta di salvataggio è ancora aperta.' : 'Salvataggio non riuscito: ' + ((e && (e.message||e.code)) || e); })
    .finally(()=>{ __dlInCorso = false; });
}""")
open(os.path.join(HERE, 'Listini_Serie_web.html'), 'w', encoding='utf-8').write(w)
print('html:', len(html), 'bytes; web:', len(w), 'bytes')
