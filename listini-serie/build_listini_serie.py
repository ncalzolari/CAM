#!/usr/bin/env python3
# Listini a griglia per le altre serie (AluK D67/D77 porte, Cortizo COR80): distinte dal programma commesse
# (src/dati_*.json), prezzi AluK da listini-db, kit Maico dalle regole WinPlus (listini-c75s/genera_listini.py),
# ferramenta porte dalla libreria FP D67 (fp_blk_D67.json). Pesi porte e prezzi Cortizo in file modificabili.
# Produce dati_listini_serie.json, Listini_Serie.html (autonomo) e Listini_Serie_web.html (Artifact).
import json, os, re, sys, io, contextlib, sqlite3
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
APP = os.path.join(ROOT, 'commesse-lmt65', 'src'); DB = os.path.join(ROOT, 'listini-db', 'listini.sqlite')
sys.path.insert(0, os.path.join(ROOT, 'listini-c75s'))
with contextlib.redirect_stdout(io.StringIO()):
    import genera_listini as g          # KIT_ANTA, FERR_FISSE_ANTA, FERR_SEMIFISSA, NETTO (rigenera anche gli xlsx C75S)

def carica(nome): return json.load(open(os.path.join(APP, nome), encoding='utf-8'))
D = {}
for f in ('dati_app.json', 'dati_porte.json', 'dati_cor80.json'):
    for k, v in carica(f).items():
        if k == 'tipologie': D.setdefault('tipologie', []).extend(v)
        elif isinstance(v, dict): D.setdefault(k, {}).update(v)
        else: D[k] = v
TIP = {t['id']: t for t in D['tipologie']}
db = sqlite3.connect(DB)
def prezzo_acc(cod):
    r = db.execute("SELECT prezzo_unitario FROM v_accessori WHERE codice=? ORDER BY CASE listino WHEN 'c75s_c82s' THEN 1 ELSE 0 END LIMIT 1", (cod,)).fetchone()
    return r[0] if r else None
def eur_kg_serie(serie_aluk, agg='20'):
    r = db.execute("SELECT listino_eur_kg FROM v_profili WHERE serie=? AND aggregazione=?", (serie_aluk, agg)).fetchone(); return r[0] if r else None
DECORRENZA = db.execute("SELECT MAX(decorrenza) FROM listini WHERE fornitore='AluK'").fetchone()[0]

# ---- file modificabili: pesi profili porte, prezzi Cortizo ----
def carica_json(nome, default):
    p = os.path.join(HERE, nome)
    if os.path.exists(p): return json.load(open(p, encoding='utf-8'))
    return default
PESI = carica_json('pesi_profili.json', {"_nota": "kg/m per articolo (porte AluK D67/D77: dal catalogo o da FP Pro). null = da inserire.", "pesi": {}})
CORTIZO = carica_json('prezzi_cortizo.json', {"_nota": "Prezzi Cortizo: eur_kg profili (listino) e prezzo unitario accessori/guarnizioni (€/pz o €/m). null = da inserire.", "eur_kg": None, "sconto_profili": 0.0, "sconto_accessori": 0.0, "accessori": {}})

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
    if serie == 'COR80': return 'tt'
    return 'tt' if art.startswith('U') else 'n'          # porte AluK: U = profili a taglio termico; N fermavetri, K soglie/accessori

CAT_PESI = carica_json(os.path.join('..', 'commesse-lmt65', 'data', 'catalogo_D67_D77', 'pesi_profili_catalogo.json'), {'pesi': {}})['pesi']   # catalogo tecnico AluK D67-D77 v4C
def peso_kg_m(serie, art):
    if serie == 'COR80':
        p = (D['profili_ana'].get(art) or {}).get('peso_g_m'); return (p/1000.0, 'catalogo Cortizo') if p else (None, 'da inserire')
    p = PESI['pesi'].get(art)
    if p: return (p, 'pesi_profili.json')
    c = CAT_PESI.get(art); return (c['kg_m'], 'catalogo AluK D67-D77') if c else (None, 'da inserire')

def fermavetro(t, vetro):
    tav = D['vetrazione'].get(t.get('vetro_tav') or ('tavD67' if t['serie']=='D67' else 'tavD77' if t['serie']=='D77' else ''), {})
    r = (tav.get('righe') or {}).get(str(vetro)); return (r or {}).get('fv'), (r or {}).get('g')

# ---- kit ferramenta porte dalla libreria FP D67 (blocchi .BLK) ----
BLK = json.load(open(os.path.join(ROOT, 'commesse-lmt65', 'data', 'catalogo_D67_D77', 'fp_blk_D67.json'), encoding='utf-8'))
def blocco_per(t):
    n = t['id']; due = t['forma'] == 'P2'; est = t.get('apertura') == 'est'
    if 'AUTOMATICA' in n: return ('350-21' if due else '350-02') if not est else ('360-02' if not due else '350-21')
    if 'K1769' in n or 'K2069' in n: return ('370-06' if est else '350-04') if not due else ('370-06' if est else '350-04')
    if 'K1490' in n: return ('370-01' if est else '350-20') if due else ('360-01' if est else '350-01')
    return '350-01'
def kit_blk(t):
    b = BLK.get(blocco_per(t)); out = []
    if not b: return out, None
    for f in b['accessori']:
        if f.get('Optional') == '1' or f.get('Type') != '1': continue          # opzionali esclusi; guarnizioni (T4) già nella distinta
        if f.get('Apertura') == '2': continue                                   # coppia DX/SX: una sola
        pr = prezzo_acc(f['Code']); fascia = None
        m = re.search(r'\((\d+)-(\d+)\s*MM\)', f['Description'])
        if f.get('RefDim') == '101' and m: fascia = [int(m.group(1)), int(m.group(2))]     # soglia automatica per larghezza anta
        out.append({'cod': f['Code'], 'desc': f['Description'][:60], 'q': int(f.get('Multiply') or 1), 'pr': pr, 'fonte': 'listino AluK' if pr is not None else 'da inserire', 'fascia': fascia})
    return out, b['descrizione']

# ---- configurazione delle griglie ----
CONFIG = {
 'D67': {'nome': 'AluK D67 — IWG 67ID (porte)', 'aluk': '312', 'vetro': '28',
   'griglie': [('D67_UN_ANTA_SOGLIA_AUTOMATICA_INT_Z', (800,1400), (2000,2600), 3.5), ('D67_UN_ANTA_SOGLIA_K1769_INT_Z', (800,1400), (2000,2600), 3.5),
               ('D67_DUE_ANTE_SOGLIA_AUTOMATICA_INT', (1200,2200), (2000,2600), 5.5), ('D67_DUE_ANTE_SOGLIA_K1490_INT_Z', (1200,2200), (2000,2600), 5.5),
               ('D67_UN_ANTA_SOGLIA_K1490_EST_Z', (800,1400), (2000,2600), 3.5), ('D67_DUE_ANTE_SOGLIA_K1490_EST_Z', (1200,2200), (2000,2600), 5.5)]},
 'D77': {'nome': 'AluK D77 — IWG 77ID (porte)', 'aluk': '315', 'vetro': '28',
   'griglie': [('D77_UN_ANTA_SOGLIA_AUTOMATICA_INT_Z', (800,1400), (2000,2600), 3.5), ('D77_UN_ANTA_SOGLIA_K2069_INT_Z', (800,1400), (2000,2600), 3.5),
               ('D77_DUE_ANTE_SOGLIA_AUTOMATICA_INT', (1200,2200), (2000,2600), 5.5), ('D77_DUE_ANTE_SOGLIA_K1490_INT_Z', (1200,2200), (2000,2600), 5.5),
               ('D77_UN_ANTA_SOGLIA_K1490_EST_Z', (800,1400), (2000,2600), 3.5), ('D77_DUE_ANTE_SOGLIA_K1490_EST_Z', (1200,2200), (2000,2600), 5.5)]},
 'COR80': {'nome': 'Cortizo COR 80 Evolution (finestre)', 'aluk': None, 'vetro': '28',
   'griglie': [('COR80_FISSO_ALA21', (500,3000), (600,2700), 4/3), ('COR80_FISSO_ALA39', (500,3000), (600,2700), 4/3),
               ('COR80_1A_VISTA', (500,1200), (500,2000), 8/3), ('COR80_2A_VISTA', (800,2000), (500,2000), 13/3),
               ('COR80_PF1_VISTA', (500,1200), (1900,2700), 8/3), ('COR80_PF2_VISTA', (800,1800), (1900,2700), 13/3),
               ('COR80_1A_SEMIVISTA', (500,1200), (500,2000), 8/3), ('COR80_2A_SEMIVISTA', (800,2000), (500,2000), 13/3),
               ('COR80_1A_SCOMPARSA', (500,1200), (500,2000), 8/3), ('COR80_2A_SCOMPARSA', (800,2000), (500,2000), 13/3)]},
}
OUT = {'decorrenza': DECORRENZA, 'serie': {}, 'kit_maico': [[d, c, r, q] for d, c, r, q in g.KIT_ANTA],
       'fisse_anta': [[d, c or '', q, m] for d, c, q, m in g.FERR_FISSE_ANTA], 'semifissa': [[d, c or '', q, m] for d, c, q, m in g.FERR_SEMIFISSA],
       'netto': {c: round(p, 4) for c, p in g.NETTO.items()}, 'pesi_mancanti': {}, 'prezzi_mancanti': {}}
for serie, cfg in CONFIG.items():
    par = {'sfrido': 0.09, 'eur_h': 65.0, 'ricarico': 2.13}
    if cfg['aluk']:
        par.update(eur_kg_tt=eur_kg_serie(cfg['aluk']) or 0, eur_kg_n=eur_kg_serie(cfg['aluk']) or 0, sc_prof=0.38, sc_acc=0.20)
        fonte = f"listino AluK profili serie {cfg['aluk']} cat. B con addebito (decorrenza {DECORRENZA}), accessori listino AluK; profili N/K prezzati come i TT (nessun listino separato)"
    else:
        par.update(eur_kg_tt=CORTIZO.get('eur_kg') or 0, eur_kg_n=CORTIZO.get('eur_kg') or 0, sc_prof=CORTIZO.get('sconto_profili') or 0, sc_acc=CORTIZO.get('sconto_accessori') or 0)
        fonte = "prezzi Cortizo da prezzi_cortizo.json (listino Cortizo non caricato)"
    S = {'nome': cfg['nome'], 'param': par, 'fonte': fonte, 'vetro': cfg['vetro'], 'ordine': [], 'tip': {}}
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
            pr = prezzo_acc(cod) if serie != 'COR80' else CORTIZO['accessori'].get(cod)
            a = dict(a, art=cod)
            if pr is None: OUT['prezzi_mancanti'].setdefault(serie, set()).add(a['art'])
            acc.append({'art': a['art'], 'desc': a.get('desc', ''), 'pz': a.get('pz') or 0, 'pr': pr})
        gua = []
        for gg in t.get('guarnizioni', []):
            art = g_art if (gg.get('gv') or gg['art'].startswith('809119')) and g_art else gg['art']
            co = lin(gg['mis']);
            if co is None: continue
            pr = prezzo_acc(art) if serie != 'COR80' else CORTIZO['accessori'].get(art)
            if pr is None: OUT['prezzi_mancanti'].setdefault(serie, set()).add(art)
            gua.append({'art': art, 'desc': gg.get('desc', ''), 'mis': gg['mis'], 'lin': co, 'pr': pr})
        kit = {'tipo': 'nessuno'}
        if serie == 'COR80' and t['forma'] in ('1', '2', 'P1', 'P2'):
            anta_l = t.get('anta_l') or t.get('anta_l2'); anta_h = t.get('anta_h'); in_vista = ('_VISTA' in tid or '_SEMIVISTA' in tid) and '_RID' not in tid
            kit = {'tipo': 'maico' if in_vista else 'maico_scomparsa', 'anta': [anta_l, anta_h], 'due': t['forma'] in ('2', 'P2')}
        elif serie in ('D67', 'D77') and t['forma'] in ('P1', 'P2'):
            righe, nome_blk = kit_blk(t); anta = next((p for p in t['profili'] if 'Traverso battente' in p.get('desc', '')), None)
            gia = {a['art'] for a in acc}; righe = [r for r in righe if r['cod'] not in gia]      # voci già nella distinta della tipologia
            for r in righe:
                if r['cod'].startswith('7322') and 'SERR' in r['desc'].upper() or 'INCONTRO' in r['desc'].upper() or 'SCONTRO' in r['desc'].upper(): r['fonte'] += ' — serratura da confermare'
            n_ante = 2 if t['forma'] == 'P2' else 1
            righe.append({'cod': '', 'desc': f'Cerniere AluK per porta ({3*n_ante} pz) — codice DA INSERIRE', 'q': 3*n_ante, 'pr': None, 'fonte': 'da inserire', 'fascia': None})
            kit = {'tipo': 'blk', 'blocco': nome_blk, 'righe': righe, 'anta_l': anta['mis'] if anta else 'L-94', 'nota': 'kit dalla libreria FP D67' + (' riusato per D77' if serie == 'D77' else '') + ' (voci non opzionali; da verificare)'}
        if serie in ('D67', 'D77'):
            gruppo = f"Porta {'2 ante' if t['forma']=='P2' else '1 anta'} — apertura {'esterna' if t.get('apertura')=='est' else 'interna'}"
            sog = 'soglia automatica' if 'AUTOMATICA' in tid else 'soglia K1490' if 'K1490' in tid else 'soglia K1769' if 'K1769' in tid else 'soglia K2069' if 'K2069' in tid else 'soglia'
            variante = sog + (' con zoccolo' if tid.endswith('_Z') else ' senza zoccolo')
        else: gruppo, variante = t['nome'], ''
        S['tip'][key] = {'id': tid, 'gruppo': gruppo, 'variante': variante, 'nome': t['nome'], 'forma': t['forma'], 'L': list(Lr), 'H': list(Hr), 'ore': ore, 'profili': profili, 'acc': acc, 'guarn': gua, 'kit': kit,
                         'vetro': [{'pz': v.get('pz', 1), 'l': lin(v['l']), 'h': lin(v['h'])} for v in t.get('vetro', []) if lin(v['l']) and lin(v['h'])]}
        S['ordine'].append(key)
    OUT['serie'][serie] = S
OUT['pesi_mancanti'] = {k: sorted(v) for k, v in OUT['pesi_mancanti'].items()}; OUT['prezzi_mancanti'] = {k: sorted(v) for k, v in OUT['prezzi_mancanti'].items()}
# file modificabili: creo/aggiorno i modelli con le chiavi mancanti (valori null)
for art in sorted({a for s in ('D67', 'D77') for a in OUT['pesi_mancanti'].get(s, [])}): PESI['pesi'].setdefault(art, None)
for art in OUT['prezzi_mancanti'].get('COR80', []): CORTIZO['accessori'].setdefault(art, None)
json.dump(PESI, open(os.path.join(HERE, 'pesi_profili.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(CORTIZO, open(os.path.join(HERE, 'prezzi_cortizo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
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
