#!/usr/bin/env python3
"""Esporta i listini a griglia (prezzi di vendita, senza vetro) in xlsx: un file per serie, un foglio per tipologia.
Stesse formule del programma Listini_Serie.html (coef/kitRighe/costo) con i parametri di consegna di dati_listini_serie.json."""
import json, os, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
HERE = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(os.path.join(HERE, 'dati_listini_serie.json'), encoding='utf-8'))
r2 = lambda x: round(x * 100 + 1e-9) / 100
ev = lambda co, L, H: co[0] + co[1] * L + co[2] * H
def coef(S, t):
    tt = [0, 0, 0]; nn = [0, 0, 0]; gg = [0, 0, 0]; acc = 0
    for p in t['profili']:
        if p['kg_m'] is None: continue
        a = tt if p['classe'] == 'tt' else nn
        for i in range(3): a[i] += p['pz'] * (p['kg_m'] / 1000) * p['lin'][i]
    for g in t['guarn']:
        if g['pr'] is None: continue
        for i in range(3): gg[i] += (g['pr'] / 1000) * g['lin'][i]
    for a in t['acc']:
        if a['pr'] is not None: acc += a['pz'] * a['pr']
    return tt, nn, gg, acc
def kit_righe(S, t, L, H):
    kit = t['kit']; out = []; p = S['param']
    if kit['tipo'] != 'blk': return out
    lin = lambda e: __import__('re').fullmatch(r'[0-9LH+\-*/().]+', str(e).replace(' ', '')) and e
    def lin_ev(expr):
        s = str(expr).replace(',', '.').replace(' ', ''); import re
        s = re.sub(r'L/2', '(L/2)', s); s = re.sub(r'(\d)([LH(])', r'\1*\2', s); s = re.sub(r'\)([LH(\d])', r')*\1', s)
        return eval(s, {'__builtins__': {}}, {'L': L, 'H': H})
    aw = lin_ev(kit.get('anta_l') or 'L'); ah = lin_ev(kit.get('anta_h') or 'H')
    n_cern = next(q for lim, q in D.get('cerniere_per_anta', [[1300, 2], [2400, 3], [None, 4]]) if lim is None or ah <= lim)
    soglia = False
    for r in kit['righe']:
        if r.get('fascia_h') and not (r['fascia_h'][0] <= ah <= r['fascia_h'][1]): continue
        if r.get('fascia'):
            if r.get('fascia_h') is None and soglia: continue
            if not (r['fascia'][0] <= aw <= r['fascia'][1]): continue
            if r.get('fascia_h') is None: soglia = True
        pr = r['pr'] if r['pr'] is not None else 0
        sc = p['sc_acc'] if (r['pr'] is not None and 'listino AluK' in (r.get('fonte') or '')) else 0
        q = r['cern'] * n_cern if r.get('cern') else r['q']
        out.append((r['cod'], q, r2(pr * (1 - sc))))
    return out
def costo(S, t, c, L, H):
    p = S['param']; tt, nn, gg, acc = c
    kgT = ev(tt, L, H); kgN = ev(nn, L, H); gua = ev(gg, L, H)
    ferr = r2(sum(q * n for _, q, n in kit_righe(S, t, L, H)))
    co = r2(((kgT * (p['eur_kg_tt'] + p['add_kg']) + kgN * (p['eur_kg_n'] + p['add_kg'])) * (1 - p['sc_prof']) + (gua + acc) * (1 - p['sc_acc'])) * (1 + p['sfrido']) + ferr + t['ore'] * p['eur_h'])
    return co, r2(co * (1 + p['ricarico']))
def rng(a, b): return list(range(a, b + 1, 100))
def esporta(serie, out_dir):
    S = D['serie'][serie]; wb = Workbook(); wb.remove(wb.active); p = S['param']; oggi = datetime.date.today().strftime('%d/%m/%Y')
    idx = wb.create_sheet('Indice'); idx.append([f"LISTINI A GRIGLIA — {S['nome']} — SENZA VETRO — prezzi di vendita in €, IVA esclusa — {oggi}"]); idx.append([])
    idx.append(['Parametri: €/kg TT', p['eur_kg_tt'], '€/kg non isolati', p['eur_kg_n'], 'verniciatura €/kg', p['add_kg'], 'sconto profili', p['sc_prof'], 'sconto accessori', p['sc_acc'], 'sfrido', p['sfrido'], '€/h', p['eur_h'], 'ricarico', p['ricarico']])
    idx.append([]); idx.append(['Foglio', 'Tipologia', 'Variante', 'L min', 'L max', 'H min', 'H max', 'Ore']); idx['A1'].font = Font(bold=True, size=12)
    for k in S['ordine']:
        t = S['tip'][k]; c = coef(S, t); Ls = rng(*t['L']); Hs = rng(*t['H'])
        ws = wb.create_sheet(k[:31]); ws.append([f"LISTINO — {t['nome']} — {t.get('variante') or ''} — {S['nome']} — SENZA VETRO"]); ws['A1'].font = Font(bold=True)
        ws.append(['H \\ L'] + Ls)
        for cell in ws[2]: cell.font = Font(bold=True); cell.fill = PatternFill('solid', fgColor='E8E8E8'); cell.alignment = Alignment(horizontal='center')
        for H in Hs:
            ws.append([H] + [costo(S, t, c, L, H)[1] for L in Ls]); ws.cell(ws.max_row, 1).font = Font(bold=True)
            for j in range(2, len(Ls) + 2): ws.cell(ws.max_row, j).number_format = '#,##0.00'
        ws.append([]); ws.append([f"Prezzi di listino in €, IVA esclusa, senza vetro. Ore manodopera {t['ore']} h. Generato il {oggi}."])
        ws.column_dimensions['A'].width = 9
        for j in range(len(Ls)): ws.column_dimensions[ws.cell(2, j + 2).column_letter].width = 10
        ws.freeze_panes = 'B3'
        idx.append([k, t['nome'], t.get('variante') or '', t['L'][0], t['L'][1], t['H'][0], t['H'][1], t['ore']])
    for col, w in zip('ABCDEFGH', (10, 60, 60, 8, 8, 8, 8, 6)): idx.column_dimensions[col].width = w
    out = os.path.join(out_dir, f'Listini_{serie}.xlsx'); wb.save(out); return out, len(S['ordine'])
if __name__ == '__main__':
    out_dir = os.path.join(HERE, 'dist'); os.makedirs(out_dir, exist_ok=True)
    for serie in D['serie']:
        f, n = esporta(serie, out_dir); print(f, n, 'tipologie')
    # controllo
    S = D['serie']['D67']; t = S['tip']['P1IA67']; print('D67 P1IA67 1000x2200 ->', costo(S, t, coef(S, t), 1000, 2200))
    S = D['serie']['S140']; t = S['tip']['SXX140']; print('S140 SXX140 2900x2400 ->', costo(S, t, coef(S, t), 2900, 2400))
