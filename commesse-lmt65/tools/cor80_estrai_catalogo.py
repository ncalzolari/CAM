# Trascrizione del catalogo Cortizo COR 80 EVOLUTION (12/2025, PDF in 6 parti) -> data/catalogo_COR80/*.json
# Uso: python3 tools/cor80_estrai_catalogo.py <cartella con i PDF COR_80_EVOLUTION_*pagineN.pdf>
# Serve pymupdf. Le pagine trascritte: distinte di taglio 298-327 (sez. 7), elenco profili 42-51 (sez. 1),
# tavole di vetrazione 265-289 (sez. 6). Le correzioni manuali sono nella tabella FIX in fondo.
import sys, os, re, json, glob
import pymupdf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'catalogo_COR80')

def carica(cartella):
    files = sorted(glob.glob(os.path.join(cartella, '*COR_80*.pdf')), key=lambda x: int(re.search(r'pagine(\d+)', x).group(1)))
    pages = {}
    for f in files:
        for p in pymupdf.open(f):
            t = p.get_text()
            m = re.search(r'12 2025\n(\d+)\n', t)
            if m: pages[int(m.group(1))] = [l.strip() for l in t.split('\n') if l.strip()]
    return pages

isCode = lambda s: re.fullmatch(r'COR-\d{4}', s)
isAcc = lambda s: re.fullmatch(r'\d{6}', s)
isQty = lambda s: re.fullmatch(r'x ?\d+', s)
isForm = lambda s: re.fullmatch(r'(La|Ha|Lv\d?|Hv\d?|L|H|H1|H2)( ?= ?)?[LHa0-9/.+\- ]*', s) and re.search(r'[LH]', s)
isGask = lambda s: re.fullmatch(r'(\d+(L|H|La|Ha|Lv\d?|Hv\d?)(\+\d+(L|H|La|Ha|Lv\d?|Hv\d?))*)', s.replace(' ', ''))

def distinta(n, b):
    tit = next((l for l in b if re.match(r'(Ventana|Puerta|Divisor)', l)), '')
    j = b.index(tit)
    if j + 1 < len(b) and re.match(r'[a-z(]', b[j + 1]) and not isQty(b[j + 1]): tit += ' ' + b[j + 1]
    prof, acc, gask, vetro, opz = [], [], [], [], []
    i = 0; sez_opz = False
    while i < len(b):
        l = b[i]
        if 'OPTION' in l.upper() or 'OPCIÓN' in l.upper(): sez_opz = True
        if isCode(l):
            i += 1; k = 0
            while i + 1 < len(b) and isQty(b[i]) and isForm(b[i + 1]):
                (opz if sez_opz else prof).append({'art': l, 'pz': int(re.sub(r'\D', '', b[i])), 'mis': b[i + 1]}); i += 2; k += 1
            if k == 0 and i < len(b) and re.match(r'Ha ?- ?4', b[i]):
                opz.append({'art': l, 'pz': 1, 'mis': b[i]}); i += 1
            continue
        if isAcc(l) and i + 1 < len(b):
            nxt = b[i + 1]
            if isQty(nxt): (opz if sez_opz else acc).append({'art': l, 'pz': int(re.sub(r'\D', '', nxt))}); i += 2; continue
            if isGask(nxt) or re.fullmatch(r'\(Ha-124\)/500\+1', nxt.replace(' ', '')):
                (opz if sez_opz else gask).append({'art': l, 'mis': nxt.replace(' ', '')}); i += 2; continue
        m = re.match(r'^(\d{6}) (\d\w+( \+ \d\w+)*)$', l)
        if m: gask.append({'art': m.group(1), 'mis': m.group(2).replace(' ', '')}); i += 1; continue
        if l.startswith('e=28mm'):
            i += 1
            while i < len(b) and (isQty(b[i]) or re.match(r'(Lv|Hv)\d? ?=', b[i])):
                if isQty(b[i]): vetro.append({'pz': int(re.sub(r'\D', '', b[i])), 'l': None, 'h': None})
                else:
                    for key0, val in re.findall(r'(Lv\d?|Hv\d?) ?= ?([LH][LH0-9/.+\- ]*?)(?= (?:Lv|Hv)\d? ?=|$)', b[i]):
                        key = 'l' if key0.startswith('L') else 'h'
                        if vetro and vetro[-1][key] is None: vetro[-1][key] = val.strip()
                        else: vetro.append({'pz': 1, key: val.strip(), ('h' if key == 'l' else 'l'): None})
                i += 1
            continue
        i += 1
    return {'pagina': n, 'ala': '39' if n < 311 else '21', 'titolo_es': tit, 'profili': prof, 'accessori': acc, 'guarnizioni': gask, 'vetro': vetro, 'opzioni': opz}

def profili(pages):
    out = {}
    for n in range(42, 52):
        b = pages[n]; i = 0
        while i < len(b):
            m = re.fullmatch(r'(COR-\d{4,6}( XX)?)', b[i])
            if m and i + 4 < len(b) and re.fullmatch(r'[\d,]+|-', b[i + 3]):
                num = lambda s: float(s.replace(',', '.')) if s != '-' else None
                out[m.group(1)] = {'desc_es': b[i + 1], 'desc_en': b[i + 2], 'peso_g_m': num(b[i + 3]), 'sup_dm2_m': num(b[i + 4]), 'pag': n}
                i += 5; continue
            i += 1
    return out

def vetrazione(pages):
    """tabelle 'junquillo recto': codice, A (fermavetro), B (battuta), [vetro, guarnizione interna]..., guarnizione esterna"""
    def tab(n):
        b = pages[n]; out = {}; i = 0
        while i < len(b):
            if re.fullmatch(r'(2093|2019|2065|2018|2117|2015|2094|2017|2016|2122|2119|7098|7011|7090|7518|7517)', b[i]) and i + 3 < len(b) and re.fullmatch(r'\d+,\d\d', b[i + 1]) and re.fullmatch(r'\d+,\d\d', b[i + 2]):
                code = b[i]; A = float(b[i + 1].replace(',', '.')); B = float(b[i + 2].replace(',', '.'))
                j = i + 3; rows = []; ext = None
                while j < len(b) and re.fullmatch(r'\d+', b[j]) and j + 1 < len(b) and re.fullmatch(r'\d,\d\d', b[j + 1]):
                    rows.append([int(b[j]), float(b[j + 1].replace(',', '.'))]); j += 2
                    if j < len(b) and re.fullmatch(r'\d,\d\d', b[j]) and ext is None: ext = float(b[j].replace(',', '.')); j += 1
                out['COR-' + code] = {'A': A, 'B': B, 'ext': ext, 'righe': rows}
                i = j
            else: i += 1
        return out
    v = {
        'nota': 'righe = [spessore vetro, guarnizione interna mm]; guarnizione esterna fissa (ext). Codici guarnizione interna nero: 4=430024 5=430025 6=430026 7=430027 8=430028 (grigio 43001x). Esterna: 416657 (3,0 nero, ante vista/semivista), 240124 (3,6 nero, fissi ala 39/21), 240138 (2,0 nero, semivista ridotta).',
        'semivista': {'pag': 270, 'profili': ['COR-5670', 'COR-5672', 'COR-5676', 'COR-5678'], 'tab': tab(270)},
        'semivista_tubolare': {'pag': 273, 'profili': ['COR-5671', 'COR-5673', 'COR-5677', 'COR-5679'], 'tab': tab(273)},
        'vista': {'pag': 281, 'profili': ['COR-5690', 'COR-5692', 'COR-5695', 'COR-5697'], 'tab': tab(281)},
        'vista_tubolare': {'pag': 284, 'profili': ['COR-5691', 'COR-5693', 'COR-5696', 'COR-5698'], 'tab': tab(284)},
        'fisso_ala39': {'pag': 275, 'profili': ['COR-5611', 'COR-5613', 'COR-5615', 'COR-5617', 'COR-5631', 'COR-5633', 'COR-5635'], 'tab': tab(275)},
        'fisso_ala39_recto': {'pag': 277, 'profili': [], 'tab': tab(277), 'nota': 'fermavetri clip 20xx su telaio ala 39 con supplemento COR-8149'},
        'fisso_ala21': {'pag': 286, 'profili': ['COR-5619', 'COR-7419', 'COR-7434', 'COR-5637', 'COR-5639', 'COR-7561', 'COR-7576', 'COR-7578', 'COR-5600'], 'tab': tab(286)},
        # tavole anta a scomparsa (p.265-266, 288-289): fermavetro fisso, varia solo la guarnizione interna
        'scomparsa': {'pag': 265, 'profili': ['COR-5604', 'COR-5607', 'COR-5624', 'COR-5627'], 'fv': 'COR-7088',
                      'righe': [[40, 2.5, '416607'], [38, 4.5, '416617'], [36, 6.5, '416627'], [34, 8.5, '416637']],
                      'nota': 'A=3,5 B=42,5; guarnizioni interne nero (grigio 4166x6); COR-7188 = fermavetro grigio'},
        'scomparsa_44': {'pag': 266, 'profili': ['COR-5605', 'COR-5608', 'COR-5625', 'COR-5628'], 'fv': 'COR-7088',
                         'righe': [[46, 2.5, '416607'], [44, 4.5, '416617'], [42, 6.5, '416627'], [40, 8.5, '416637']]},
        'semivista_ridotta': {'pag': 288, 'profili': ['COR-5604', 'COR-5607'], 'fv': 'COR-8082', 'ext': '240138',
                              'righe': [[40, 2.5, '416607'], [38, 4.5, '416617'], [36, 6.5, '416627'], [34, 8.5, '416637']],
                              'nota': 'stessa anta COR-5604 con fermavetro metallico COR-8082 e guarnizione esterna 240138 (2,0)'},
    }
    return v

# ---- correzioni manuali alle distinte (refusi del catalogo o del parser) ----
def fix(d):
    n = d['pagina']
    if n == 299:  # il testo "OPCIÓN SIN ÁNGULO" precede la distinta: tutto era finito in opzioni
        o = d['opzioni']; d['opzioni'] = []
        for e in o:
            if e.get('mis') in ('L - 118', 'H - 118'): d['opzioni'].append(e)   # fermavetro a 45 senza angolo 417088
            elif 'mis' in e and e['art'].startswith('COR'): d['profili'].append(e)
            elif 'mis' in e: d['guarnizioni'].append(e)
            else: d['accessori'].append(e)
        d['opzioni'].insert(0, {'nota': 'Opzione senza angolo 417088: fermavetro COR-7088 tagliato a 45° L-118 / H-118 (invece di L-188 / H-188 a 90° con angolo)'})
    if n == 300:
        d['opzioni'].insert(0, {'nota': 'Opzione senza angolo 417088: fermavetro COR-7088 a 45° L/2-94 / H-118'})
    if n == 305:
        d['nota'] = "Il catalogo indica l'anta COR-6672 (codice assente dall'elenco profili): trascritta come COR-5672 (anta semivista portafinestra)."
        for p in d['profili']:
            if p['art'] == 'COR-6672': p['art'] = 'COR-5672'
    if n == 306:
        d['nota'] = 'Il catalogo riporta COR-5635 x1 L (il traverso inferiore è la soglia integrata? a p.305 sono x2 L): trascritto come a catalogo.'
    if n in (315, 316, 317, 325, 326, 327):  # COR-5600 L-59.5 / H1-38 = opzione senza tappi 455600
        keep = []
        for p in d['profili']:
            if p['art'] == 'COR-5600' and p['mis'].replace(' ', '') in ('L-59.5', 'H1-38', 'H1-38.1'): d['opzioni'].append(p)
            else: keep.append(p)
        d['profili'] = keep
        d['opzioni'].insert(0, {'nota': 'Opzione senza tappi complemento telaio 455600: COR-5600 L-59,5 / H1-38'})
    if n == 324:  # "OPCIÓN MANILLA CENTRADA" precede la distinta
        o = d['opzioni']; d['opzioni'] = []
        for e in o:
            if e['art'] in ('COR-6645', '426645', '238297'): d['opzioni'].append(e)
            elif 'mis' in e: d['guarnizioni'].append(e)
            else: d['accessori'].append(e)
    if n == 326:
        for a in d['accessori']:
            if a['art'] == '477923': a['art'] = '407923'; a['nota'] = 'catalogo: 477923 (refuso per 407923 clip di sicurezza vetro)'
    # vetri delle pagine a 2 ante + fisso inferiore: "Lv1 = L/2 - 146 Hv1 = H1 - 148.6" su una riga
    VETRI = {316: [(2, 'L/2-146', 'H1-148.6'), (2, 'L/2-60.6', 'H2-60.6')],
             317: [(2, 'L/2-129', 'H1-148.6'), (2, 'L/2-60.6', 'H2-60.6')],
             326: [(2, 'L/2-114.9', 'H1-117.6'), (2, 'L/2-60.6', 'H2-60.6')],
             327: [(2, 'L/2-97.9', 'H1-117.6'), (2, 'L/2-60.6', 'H2-60.6')]}
    if n in VETRI: d['vetro'] = [{'pz': q, 'l': l, 'h': h} for q, l, h in VETRI[n]]
    for v in d['vetro']:
        for k in ('l', 'h'):
            if v[k]: v[k] = v[k].replace(' ', '')
    for p in d['profili'] + d['opzioni']:
        if 'mis' in p: p['mis'] = re.sub(r'^(La|Ha)=', '', p['mis'].replace(' ', ''))
    return d

if __name__ == '__main__':
    pages = carica(sys.argv[1])
    os.makedirs(OUT, exist_ok=True)
    PAG = [298, 299, 300, 302, 303, 304, 305, 306, 307, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 322, 323, 324, 325, 326, 327]
    dist = [fix(distinta(n, pages[n])) for n in PAG]
    json.dump(dist, open(os.path.join(OUT, 'distinte.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(profili(pages), open(os.path.join(OUT, 'profili_lista.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(vetrazione(pages), open(os.path.join(OUT, 'vetrazione.json'), 'w'), ensure_ascii=False, indent=1)
    print('distinte', len(dist), '| profili', len(profili(pages)), '->', OUT)
