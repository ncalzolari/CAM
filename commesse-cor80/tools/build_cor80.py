# Serie Cortizo COR 80 EVOLUTION: data/catalogo_COR80/*.json + data/dxf_sez_cor80.json -> src/dati_cor80.json
# Genera tipologie (distinte sez. 7 del catalogo 12/2025), anagrafica profili, sezioni DXF, tavole vetrazione,
# drenaggi e libreria. Le lavorazioni ferramenta usano le regole Maico Multi-Matic di C75S (stessa ferramenta):
# quote Y/Z/facce DA TARARE sui profili Cortizo. Vedi docs/DOSSIER_PROGETTO_LMT65.md sez. 11.
import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, 'data', 'catalogo_COR80') + '/'
dist = json.load(open(C + 'distinte.json'))
lista = json.load(open(C + 'profili_lista.json'))
acc_d = json.load(open(C + 'accessori.json'))
vet = json.load(open(C + 'vetrazione.json'))
dxf = json.load(open(os.path.join(ROOT, 'data', 'dxf_sez_cor80.json')))

SERIE = 'COR80'
NOME_SERIE = 'COR80 — Cortizo COR 80 Evolution (finestre 80 mm)'

# ---- ruoli e nomi italiani dei profili ----
TELAI = {'COR-5611': 'Telaio alto finestra, ala 39', 'COR-5613': 'Telaio alto con sormonto 30 mm, ala 39',
         'COR-5635': 'Telaio portafinestra con soglia, ala 39', 'COR-5619': 'Telaio alto, ala 21',
         'COR-7419': 'Telaio alto, ala 21', 'COR-7434': 'Telaio alto con sormonto 30 mm, ala 21',
         'COR-5639': 'Telaio portafinestra con soglia, ala 21'}
ANTE = {'COR-5604': 'Anta a scomparsa 36-38-40', 'COR-5670': 'Anta semivista finestra', 'COR-5690': 'Anta in vista finestra',
        'COR-5672': 'Anta semivista portafinestra', 'COR-5692': 'Anta in vista portafinestra'}
ANTE_INV = {'COR-5607': 'Anta semifissa a scomparsa (inversora)', 'COR-5676': 'Anta semifissa semivista (inversora)',
            'COR-5678': 'Anta semifissa semivista portafinestra', 'COR-5695': 'Anta semifissa in vista (inversora)',
            'COR-5697': 'Anta semifissa in vista portafinestra'}
INVERSORI = {'COR-5641': 'Inversore interno', 'COR-6642': 'Inversore esterno', 'COR-6643': 'Inversore ridotto',
             'COR-5643': 'Inversore anta in vista', 'COR-6744': 'Inversore ridotto anta in vista',
             'COR-5645': 'Inversore anta semivista ridotta', 'COR-6747': 'Inversore ridotto anta semivista ridotta'}
FERMAVETRI = {'COR-7088': 'Fermavetro esterno anta a scomparsa (nero)', 'COR-2017': 'Fermavetro clip 33 mm',
              'COR-2094': 'Fermavetro clip 29,5 mm', 'COR-7090': 'Fermavetro per fissi 26 mm',
              'COR-8082': 'Fermavetro metallico anta a scomparsa', 'COR-2093': 'Fermavetro clip 8 mm',
              'COR-2019': 'Fermavetro clip 12 mm', 'COR-2065': 'Fermavetro clip 16,5 mm', 'COR-2018': 'Fermavetro clip 19 mm',
              'COR-2117': 'Fermavetro clip 22 mm', 'COR-2015': 'Fermavetro clip 26 mm', 'COR-2016': 'Fermavetro clip 38 mm',
              'COR-2122': 'Fermavetro clip 42 mm', 'COR-2119': 'Fermavetro clip 47 mm', 'COR-7011': 'Fermavetro per fissi 22 mm',
              'COR-7098': 'Fermavetro per fissi 18 mm', 'COR-7518': 'Fermavetro per fissi 29,5 mm', 'COR-7517': 'Fermavetro per fissi 33 mm'}
ALTRI = {'COR-7561': 'Traverso finestra, ala 21', 'COR-5600': 'Complemento centrale telaio', 'COR-5590': 'Soglia 80 mm',
         'COR-6645': 'Copertura maniglia centrata', 'COR-6644': 'Copertura maniglia centrata piana',
         'COR-5573': "Divisore d'anta semivista", 'COR-5598': "Divisore d'anta in vista", 'COR-6798': "Divisore d'anta in vista portafinestra",
         'COR-5563': "Divisore d'anta a scomparsa 36-38-40", 'COR-8055': "Copertura (tapeta) divisore d'anta a scomparsa"}

# ---- tipologie: metadati per pagina ----
# fam: O scomparsa, S semivista, V in vista, R semivista ridotta; ferr: regole Maico A-R (solo ante con canale euro in vista)
META = {
 298: dict(id='COR80_FISSO_ALA39', cod='TF39', nome='Telaio fisso — ala 39 mm', forma='F', fam='F39', tel='COR-5611', anta=None, tav='tavCOR80_F39', dren_tel='telaio'),
 299: dict(id='COR80_1A_SCOMPARSA', cod='1AO80', nome="Finestra 1 anta A-R — anta a scomparsa (ala 39)", forma='1', fam='O', tel='COR-5611', anta='COR-5604', tav='tavCOR80_O', anta_h='H-54', anta_l='L-54', dren_anta='antaTravO'),
 300: dict(id='COR80_2A_SCOMPARSA', cod='2AO80', nome="Finestra 2 ante A-R — anta a scomparsa, inversore (ala 39)", forma='2', fam='O', tel='COR-5611', anta='COR-5604', tav='tavCOR80_O', anta_h='H-54', anta_l2='L/2-30', stulp=True, dren_anta='antaTravO'),
 302: dict(id='COR80_1A_SEMIVISTA', cod='1AS80', nome="Finestra 1 anta A-R — anta semivista (ala 39)", forma='1', fam='S', tel='COR-5611', anta='COR-5670', tav='tavCOR80_S', anta_h='H-54', anta_l='L-54'),
 303: dict(id='COR80_2A_SEMIVISTA', cod='2AS80', nome="Finestra 2 ante A-R — anta semivista, inversore (ala 39)", forma='2', fam='S', tel='COR-5611', anta='COR-5670', tav='tavCOR80_S', anta_h='H-54', anta_l2='L/2-30', stulp=True),
 304: dict(id='COR80_2A_SEMIVISTA_INVRID', cod='2RS80', nome="Finestra 2 ante A-R — anta semivista, inversore ridotto (ala 39)", forma='2', fam='S', tel='COR-5611', anta='COR-5670', tav='tavCOR80_S', anta_h='H-54', anta_l2='L/2-13', stulp=True),
 305: dict(id='COR80_PF1_SEMIVISTA', cod='P1S80', nome="Portafinestra 1 anta con soglia — anta semivista (ala 39)", forma='P1', fam='S', tel='COR-5635', anta='COR-5672', tav='tavCOR80_S', anta_h='H-73.6', anta_l='L-73.6', dren_x=150),
 306: dict(id='COR80_PF2_SEMIVISTA', cod='P2S80', nome="Portafinestra 2 ante con soglia — anta semivista, inversore (ala 39)", forma='P2', fam='S', tel='COR-5635', anta='COR-5672', tav='tavCOR80_S', anta_h='H-73.6', anta_l2='L/2-39.8', stulp=True, dren_x=150),
 307: dict(id='COR80_PF2_SEMIVISTA_INVRID', cod='P2RS80', nome="Portafinestra 2 ante con soglia — anta semivista, inversore ridotto (ala 39)", forma='P2', fam='S', tel='COR-5635', anta='COR-5672', tav='tavCOR80_S', anta_h='H-73.6', anta_l2='L/2-22.8', stulp=True, dren_x=150),
 311: dict(id='COR80_FISSO_ALA21', cod='TF21', nome='Telaio fisso — ala 21 mm', forma='F', fam='F21', tel='COR-7419', anta=None, tav='tavCOR80_F21', dren_tel='telaio21'),
 312: dict(id='COR80_1A_VISTA', cod='1AV80', nome="Finestra 1 anta A-R — anta in vista (ala 21)", forma='1', fam='V', tel='COR-5619', anta='COR-5690', tav='tavCOR80_V', anta_h='H-54', anta_l='L-54', dren_tel='telaio21'),
 313: dict(id='COR80_2A_VISTA', cod='2AV80', nome="Finestra 2 ante A-R — anta in vista, inversore (ala 21)", forma='2', fam='V', tel='COR-5619', anta='COR-5690', tav='tavCOR80_V', anta_h='H-54', anta_l2='L/2-30', stulp=True, dren_tel='telaio21'),
 314: dict(id='COR80_2A_VISTA_INVRID', cod='2RV80', nome="Finestra 2 ante A-R — anta in vista, inversore ridotto (ala 21)", forma='2', fam='V', tel='COR-5619', anta='COR-5690', tav='tavCOR80_V', anta_h='H-54', anta_l2='L/2-13', stulp=True, dren_tel='telaio21'),
 315: dict(id='COR80_1A_FISSOINF_VISTA', cod='1FV80', nome="Finestra 1 anta A-R + fisso inferiore — anta in vista (ala 21)", forma='1', fam='V', tel='COR-7419', anta='COR-5690', tav='tavCOR80_V', anta_h='H1-32.6', anta_l='L-54', fisso_inf=True, dren_tel='telaio21'),
 316: dict(id='COR80_2A_FISSOINF_VISTA', cod='2FV80', nome="Finestra 2 ante A-R + fisso inferiore — anta in vista, inversore (ala 21)", forma='2', fam='V', tel='COR-7419', anta='COR-5690', tav='tavCOR80_V', anta_h='H1-32.6', anta_l2='L/2-30', stulp=True, fisso_inf=True, dren_tel='telaio21'),
 317: dict(id='COR80_2A_FISSOINF_VISTA_INVRID', cod='2RFV80', nome="Finestra 2 ante A-R + fisso inferiore — anta in vista, inversore ridotto (ala 21)", forma='2', fam='V', tel='COR-7419', anta='COR-5690', tav='tavCOR80_V', anta_h='H1-32.6', anta_l2='L/2-13', stulp=True, fisso_inf=True, dren_tel='telaio21'),
 318: dict(id='COR80_PF1_VISTA', cod='P1V80', nome="Portafinestra 1 anta A-R con soglia — anta in vista (ala 21)", forma='P1', fam='V', tel='COR-5639', anta='COR-5692', tav='tavCOR80_V', anta_h='H-73.6', anta_l='L-73.6', dren_x=150, dren_tel='telaio21'),
 319: dict(id='COR80_PF2_VISTA', cod='P2V80', nome="Portafinestra 2 ante A-R con soglia — anta in vista, inversore (ala 21)", forma='P2', fam='V', tel='COR-5639', anta='COR-5692', tav='tavCOR80_V', anta_h='H-73.6', anta_l2='L/2-39.8', stulp=True, dren_x=150, dren_tel='telaio21'),
 320: dict(id='COR80_PF2_VISTA_INVRID', cod='P2RV80', nome="Portafinestra 2 ante A-R con soglia — anta in vista, inversore ridotto (ala 21)", forma='P2', fam='V', tel='COR-5639', anta='COR-5692', tav='tavCOR80_V', anta_h='H-73.6', anta_l2='L/2-22.8', stulp=True, dren_x=150, dren_tel='telaio21'),
 322: dict(id='COR80_1A_SEMIVISTA_RID', cod='1AR80', nome="Finestra 1 anta A-R — anta semivista ridotta (ala 21)", forma='1', fam='R', tel='COR-5619', anta='COR-5604', tav='tavCOR80_R', anta_h='H-54', anta_l='L-54', dren_tel='telaio21'),
 323: dict(id='COR80_2A_SEMIVISTA_RID', cod='2AR80', nome="Finestra 2 ante A-R — anta semivista ridotta, inversore (ala 21)", forma='2', fam='R', tel='COR-5619', anta='COR-5604', tav='tavCOR80_R', anta_h='H-54', anta_l2='L/2-30', stulp=True, dren_tel='telaio21'),
 324: dict(id='COR80_2A_SEMIVISTA_RID_INVRID', cod='2RR80', nome="Finestra 2 ante A-R — anta semivista ridotta, inversore ridotto (ala 21)", forma='2', fam='R', tel='COR-5619', anta='COR-5604', tav='tavCOR80_R', anta_h='H-54', anta_l2='L/2-13', stulp=True, dren_tel='telaio21'),
 325: dict(id='COR80_1A_FISSOINF_SEMIVISTA_RID', cod='1FR80', nome="Finestra 1 anta A-R + fisso inferiore — anta semivista ridotta (ala 21)", forma='1', fam='R', tel='COR-7419', anta='COR-5604', tav='tavCOR80_R', anta_h='H1-32.6', anta_l='L-54', fisso_inf=True, dren_tel='telaio21'),
 326: dict(id='COR80_2A_FISSOINF_SEMIVISTA_RID', cod='2FR80', nome="Finestra 2 ante A-R + fisso inferiore — anta semivista ridotta, inversore (ala 21)", forma='2', fam='R', tel='COR-7419', anta='COR-5604', tav='tavCOR80_R', anta_h='H1-32.6', anta_l2='L/2-30', stulp=True, fisso_inf=True, dren_tel='telaio21'),
 327: dict(id='COR80_2A_FISSOINF_SEMIVISTA_RID_INVRID', cod='2RFR80', nome="Finestra 2 ante A-R + fisso inferiore — anta semivista ridotta, inversore ridotto (ala 21)", forma='2', fam='R', tel='COR-7419', anta='COR-5604', tav='tavCOR80_R', anta_h='H1-32.6', anta_l2='L/2-13', stulp=True, fisso_inf=True, dren_tel='telaio21'),
}
# ---- divisore d'anta (p.301/308/321/328): per anta divisa; La/Ha = anta, Ha1 = parte superiore, Ha2 = inferiore (Ha1+Ha2 = Ha) ----
# fv_o: fermavetri orizzontali (4 per anta), fv_v: verticali (2 sopra + 2 sotto); gu: guarnizioni TOTALI dell'anta divisa (sostituiscono quelle dell'anta intera)
DIV = {
 ('S', 'fin'): dict(art='COR-5573', mis='La-95', fv_o='La-104', fv_v1='Ha1-105.6', fv_v2='Ha2-105.6', vetro_l='La-116', vetro_h1='Ha1-77.6', vetro_h2='Ha2-77.6',
                    gu=[('430026', '4La+2Ha', True), ('416657', '4La+2Ha', False), ('377701', '4La+2Ha', False)], acc=[('418181', 2), ('423756', 4)], rif='p.308'),
 ('S', 'pb'):  dict(art='COR-5573', mis='La-191', fv_o='La-200', fv_v1='Ha1-153.6', fv_v2='Ha2-153.6', vetro_l='La-212', vetro_h1='Ha1-125.6', vetro_h2='Ha2-125.6',
                    gu=[('430026', '4La+2Ha', True), ('416657', '4La+2Ha', False), ('377701', '2La+2Ha', False)], acc=[('418181', 2), ('423756', 4)], rif='p.308'),
 ('V', 'fin'): dict(art='COR-5598', mis='La-95', fv_o='La-104', fv_v1='Ha1-105.5', fv_v2='Ha2-105.5', vetro_l='La-116', vetro_h1='Ha1-77.6', vetro_h2='Ha2-77.6',
                    gu=[('430025', '4La+2Ha', True), ('416657', '4La+2Ha', False), ('307000', '4La+2Ha', False)], acc=[('418181', 2), ('384970', 4)], rif='p.321'),
 ('V', 'pb'):  dict(art='COR-6798', mis='La-151', fv_o='La-160', fv_v1='Ha1-133.5', fv_v2='Ha2-133.5', vetro_l='La-172', vetro_h1='Ha1-105.6', vetro_h2='Ha2-105.6',
                    gu=[('430025', '4La+2Ha', True), ('416657', '4La+2Ha', False), ('307000', '2La+2Ha', False)], acc=[('418181', 2), ('384970', 4)], rif='p.321'),
 # anta a scomparsa: divisore COR-5563 + tapeta COR-8055; il catalogo non ridefinisce i fermavetri COR-7088/8082 verticali:
 # spezzati a Ha1-92 / Ha2-92 (= Ha-134 dell'anta intera meno i 50 mm del divisore) — DA VERIFICARE
 ('O', 'fin'): dict(art='COR-5563', mis='La-77', tapeta=('COR-8055', 'La-119'), fv_o=None, fv_v1='Ha1-92', fv_v2='Ha2-92', vetro_l='La-85', vetro_h1='Ha1-55.5', vetro_h2='Ha2-55.5',
                    gu=[('416607', '2La', False), ('416617', '4La+2Ha', False), ('374003', '4La+2Ha', False)], acc=[('397950', 1), ('347906', 4), ('823919', 2), ('814245', 4)], rif='p.301', fv_nota=True),
 ('R', 'fin'): dict(art='COR-5563', mis='La-77', tapeta=('COR-8055', 'La-119'), fv_o=None, fv_v1='Ha1-92', fv_v2='Ha2-92', vetro_l='La-85', vetro_h1='Ha1-55.5', vetro_h2='Ha2-55.5',
                    gu=[('416607', '2La', False), ('416617', '4La+2Ha', False), ('374003', '4La+2Ha', False)], acc=[('397950', 1), ('347906', 4), ('407923', 4), ('823595', 8), ('823919', 2), ('814245', 4)], rif='p.328', fv_nota=True),
}
# ---- maniglia centrata (opzione delle 2 ante con inversore ridotto): copertura Ha-4, kit tappi, adesivo (Ha-124)/500+1 ----
MANC = {'S': dict(art='COR-6645', tappi='426645'), 'V': dict(art='COR-6644', tappi='426647'), 'R': dict(art='COR-6645', tappi='426645')}

FAM_NOME = {'O': 'anta a scomparsa', 'S': 'anta semivista', 'V': 'anta in vista', 'R': 'anta semivista ridotta', 'F39': 'fisso', 'F21': 'fisso'}

def desc_pezzo(art, mis, m):
    """descrizione italiana + codice sc + angoli, dal codice profilo e dalla formula"""
    mm = mis.replace(' ', '')
    if art in TELAI:
        return ('Traverso stipite', 'TELL', '45-45') if mm == 'L' else ('Montante stipite', 'TELH', '45-45')
    if art in ANTE:
        if mm.startswith('L'): return ('Traverso battente', 'ANTL', '45-45')
        return ('Montante battente', 'ANTH', '45-45')
    if art in ANTE_INV:
        return ('Montante battente centrale (anta semifissa, inversora)', 'ANTC', '45-45')
    if art in INVERSORI:
        return (INVERSORI[art] + ' (su anta semifissa)', 'INVH', '90-90')
    if art in FERMAVETRI:
        oriz = mm.startswith('L')
        fisso = bool(m.get('fisso_inf')) and (('H2' in mm) or (oriz and re.fullmatch(r'L(/2)?-(70|48\.6)', mm)))
        batt = bool(m.get('fisso_inf')) and not fisso
        suff = ' fisso' if fisso else (' battente' if batt else '')
        return (('Fermavetro orizz.' if oriz else 'Fermavetro vert.') + suff, ('FVFL' if fisso else 'FERL') if oriz else ('FVFH' if fisso else 'FERH'), '90-90')
    if art == 'COR-7561':
        return ('Traverso T fisso inferiore', 'TELT', '90-90') if mm.startswith('L') else ('Montante T fisso inferiore', 'TELM', '90-90')
    if art == 'COR-5600':
        return ('Complemento centrale telaio (fisso inferiore) orizz.', 'COML', '90-90') if mm.startswith('L') else ('Complemento centrale telaio (fisso inferiore) vert.', 'COMH', '90-90')
    return (lista.get(art, {}).get('desc_es', art), 'ALTR', '90-90')

def espandi(mis, vetri):
    """'2Lv+2Hv' -> '2*(L-170)+2*(H-170)' con le formule del vetro; Lv1/Hv1 = vetro 1, Lv2/Hv2 = vetro 2"""
    s = mis.replace(' ', '')
    def rep(m):
        n = m.group(1); tag = m.group(2); idx = m.group(3)
        v = vetri[int(idx) - 1] if idx else vetri[0]
        f = v['l'] if tag == 'L' else v['h']
        return f"{n}*({f})"
    s = re.sub(r'(\d+)([LH])v(\d?)', rep, s)
    return s

def build_tip(d):
    n = d['pagina']; m = META[n]
    prof = []
    for p in d['profili']:
        desc, sc, ang = desc_pezzo(p['art'], p['mis'], m)
        e = {'art': p['art'], 'desc': desc, 'pz': p['pz'], 'mis': p['mis'], 'ang': ang, 'sc': sc}
        if p['art'] in FERMAVETRI:
            e['fv'] = True
            if sc in ('FVFL', 'FVFH'): e['tav'] = 'tavCOR80_F21' if m['fam'] != 'F39' else 'tavCOR80_F39'
        prof.append(e)
    acc = [{'art': a['art'], 'desc': acc_d['accessori'].get(a['art'], 'Accessorio (cat. p.%d)' % n), 'pz': a['pz']} for a in d['accessori']]
    gua = []
    for g in d['guarnizioni']:
        mis = espandi(g['mis'], d['vetro'])
        e = {'art': g['art'], 'desc': acc_d['guarnizioni'].get(g['art'], 'Guarnizione (cat. p.%d)' % n), 'mis': mis}
        if g['art'].startswith('4300') and re.search(r'[LH]v1?(?!\d)', g['mis']) and m['anta']:
            e['gv'] = True; e['desc'] = 'Interna vetro (anta)'   # dalla tavola di vetrazione in base allo spessore
        gua.append(e)
    vetro = [{'pz': v['pz'], 'l': v['l'], 'h': v['h'], 'anta': bool(m['anta']) and 'H2' not in (v['h'] or '')} for v in d['vetro']]
    t = {'id': m['id'], 'serie': SERIE, 'nome': m['nome'], 'cod': m['cod'],
         'rif': f"COR 80 Evolution p.{n} (catalogo Cortizo 12/2025, ala {d['ala']} mm)", 'forma': m['forma'],
         'famiglia': m['fam'], 'telaio_rif': m['tel'], 'anta_rif': m['anta'] or m['tel'], 'vetro_tav': m['tav'],
         'ferr': m['fam'] in ('S', 'V'), 'stulp': bool(m.get('stulp')), 'sopraluce': bool(m.get('fisso_inf')), 'fisso_inf': bool(m.get('fisso_inf')),
         'anta_h': m.get('anta_h'), 'anta_l': m.get('anta_l'), 'anta_l2': m.get('anta_l2'),
         'dren_x': m.get('dren_x', 100), 'dren_anta': m.get('dren_anta', 'antaTrav'), 'dren_telaio': m.get('dren_tel', 'telaio'),
         'profili': prof, 'accessori': acc, 'guarnizioni': gua, 'vetro': vetro, 'opzioni': d.get('opzioni', []), 'titolo_es': d['titolo_es']}
    av = ["Serie nuova (Cortizo COR 80 Evolution): distinta dal catalogo 12/2025, senza riscontro di produzione."]
    if t['ferr']: av.append("Ferramenta Maico A-R con le regole di C75S: quote Y/Z e facce DA TARARE sui profili Cortizo (tutte le lavorazioni sono marcate).")
    elif m['fam'] in ('O', 'R'): av.append("Anta a scomparsa: lavorazioni ferramenta non emesse (come C82S); solo drenaggi/aerazioni da catalogo.")
    if m.get('fisso_inf'): av.append("Inserire H2 = altezza del fisso inferiore (filo esterno telaio); H1 = H − H2 è la parte apribile.")
    if m.get('stulp'): av.append("Due ante con inversore sull'anta semifissa: trattate come 'stulp' per gli scontri Maico (DA TARARE).")
    if d.get('nota'): av.append(d['nota'])
    if d.get('opzioni'):
        nt = [o['nota'] for o in d['opzioni'] if 'nota' in o]
        if nt: av.append(' '.join(nt))
        if any(o.get('art') == 'COR-6645' or o.get('art') == 'COR-6644' for o in d['opzioni']): av.append('Opzione maniglia centrata (copertura COR-6645/6644 Ha−4, kit tappi, adesivo): casella "maniglia centrata"; le quote Maico della maniglia restano quelle standard (DA TARARE).')
    if m['anta']:
        dv = DIV.get((m['fam'], 'pb' if m['forma'] in ('P1', 'P2') else 'fin'))
        if dv:
            t['divisore'] = {k: v for k, v in dv.items()}
            t['divisore']['desc'] = ALTRI.get(dv['art'], "Divisore d'anta")
            av.append(f"Opzione divisore d'anta (cat. {dv['rif']}): inserire Ha2 = altezza della parte inferiore dell'anta; fermavetri, vetri e guarnizioni dell'anta ricalcolati." + (' Fermavetri verticali COR-7088/8082 spezzati a Ha1-92 / Ha2-92: DA VERIFICARE.' if dv.get('fv_nota') else ''))
    if 'inversore ridotto' in m['nome'] and m['fam'] in MANC:
        mc = MANC[m['fam']]
        t['opz_maniglia'] = {'art': mc['art'], 'desc': ALTRI[mc['art']], 'mis': 'Ha-4', 'tappi': mc['tappi'], 'adesivo': '238297', 'adesivo_formula': '(Ha-124)/500+1'}
    t['avviso'] = ' '.join(av)
    return t

# ---- costruttore a griglia (composta) COR80: telaio ala 21 COR-7419 + traverso COR-7561 (pagine "fisso inferiore" p.311/315/316/325/326) ----
# Tutte le detrazioni sono derivate da quelle pagine: [lato telaio, lato traverso/montante T]. Nessun riscontro di produzione.
COMPOSTA_BASE = dict(
    telaio='COR-7419', trav='COR-7561', comp='COR-5600',
    trv_len=[30.5, 9.1],            # traverso L-61 (30,5 per lato telaio); montante T tra traverso e telaio H2-39,6 -> 9,1 lato traverso
    anta=[27, 5.6],                 # anta L-54 (27 lato telaio); Ha = H1-32,6 -> 5,6 lato traverso
    due_ante_c=3,                   # 2 ante: La = L/2-30 -> 3 al centro (inversore)
    fv_fis=[[35, 13.6], [55, 33.6]],  # fermavetri fisso: orizz. L-70 / L/2-48,6; vert. H-110 (p.311) / H2-88,6
    vetro_fis=[[41, 19.6], [41, 19.6]],  # vetro fisso L-82 / H2-60,6
    comp_ded=[[35, 35], [35, 73.6]],  # complemento COR-5600: orizz. L-70; vert. H1-108,6 (35 telaio + 73,6 traverso: derivato)
    dren_x=100, tavF='tavCOR80_F21',
    acc_telaio=[('396710', 4), ('366733', 4), ('296838', 4)],
    acc_trav=[('418181', 2), ('423756', 4)], acc_comp=[('455600', 2)], acc_fis=[('347780', 4)],
    gask_perimetro=[('320023', 'perimetro')],
)
COMPOSTA = {
 'V': dict(COMPOSTA_BASE, anta_art='COR-5690', inv='COR-5643', inv_ded=80, tav='tavCOR80_V', fv_anta=[104, 144], vetro_anta=[116, 116],
           acc_anta=[('426630', 4), ('426632', 4), ('416600', 4), ('296838', 4), ('455603', 6)],
           acc_2a=[('426630', 8), ('426632', 8), ('416600', 8), ('296838', 8), ('455603', 10), ('455642', 1)],
           gask_anta=[('416617', 'batt2'), ('446610', 'cella'), ('377701', 'anta')], gask_vetro_ext='416657', gask_fis_ext='240124'),
 'R': dict(COMPOSTA_BASE, anta_art='COR-5604', inv='COR-5645', inv_ded=78, tav='tavCOR80_R', fv_anta=[62, 62], vetro_anta=[85, 85],
           acc_anta=[('416614', 4), ('416600', 4), ('823925', 4), ('347906', 2), ('407923', 4), ('823595', 8)],
           acc_2a=[('416614', 8), ('416600', 8), ('823925', 8), ('347906', 4), ('407923', 8), ('823595', 16), ('455646', 1)],
           gask_anta=[('416617', 'batt3'), ('456607', 'cella'), ('446610', 'cella'), ('320038', 'anta'), ('374003', 'anta')], gask_vetro_ext='240138', gask_fis_ext='240124'),
}
def build_composta(fam):
    c = COMPOSTA[fam]
    nome = {'V': 'anta in vista', 'R': 'anta semivista ridotta'}[fam]
    return {'id': f'COR80_COMPOSTA_{fam}', 'serie': SERIE, 'nome': f'COSTRUTTORE — telaio a griglia, {nome} (ala 21)', 'cod': f'CM{fam}80',
            'rif': 'motore di composizione COR80 (detrazioni derivate da p.311/315/316/325/326 del catalogo)', 'forma': 'M', 'famiglia': fam,
            'telaio_rif': c['telaio'], 'anta_rif': c['anta_art'], 'vetro_tav': c['tav'], 'ferr': False, 'stulp': False, 'sopraluce': False,
            'composta_cor80': c, 'profili': [], 'accessori': [], 'guarnizioni': [], 'vetro': [],
            'avviso': f"Composta COR80 ({nome}): telaio COR-7419 con traversi/montanti T COR-7561 e complementi COR-5600 sui lati telaio delle celle apribili; celle F / anta DX-SX / vasistas / 2 ante (inversore {c['inv']}), senza portefinestre. Detrazioni DERIVATE dalle pagine 'fisso inferiore' del catalogo (mai prodotte): validare la prima distinta. Lavorazioni: solo drenaggi/aerazioni [DA TARARE]; ferramenta delle celle non emessa (come C75S).",
            'varianti': {'telaio': {'standard': c['telaio'], 'alternative': ['COR-7434']}, 'anta': {'standard': c['anta_art'], 'alternative': []}, 'traverso': {'standard': c['trav'], 'alternative': []}}}

tipologie = [build_composta('V'), build_composta('R')] + [build_tip(d) for d in dist]
ids = [t['id'] for t in tipologie]; assert len(ids) == len(set(ids))
cods = [t['cod'] for t in tipologie]; assert len(cods) == len(set(cods))

# ---- profili: anagrafica, altezze, sezioni ----
used = sorted({p['art'] for t in tipologie for p in t['profili']} | {'COR-5613', 'COR-7434', 'COR-6645', 'COR-6644', 'COR-5573', 'COR-5598', 'COR-6798', 'COR-5563', 'COR-8055', 'COR-7090', 'COR-7011', 'COR-7098', 'COR-2093', 'COR-2019', 'COR-2065', 'COR-2018', 'COR-2117', 'COR-2015', 'COR-2016', 'COR-2122', 'COR-2119'})
TUTTI = {}
for dct, tipo, forma in ((TELAI, 'telaio', 'L'), (ANTE, 'anta', 'A'), (ANTE_INV, 'anta', 'A'), (INVERSORI, 'inversore', 'T'), (FERMAVETRI, 'fermavetro', 'L'), (ALTRI, 'traverso', 'T')):
    for k, v in dct.items(): TUTTI[k] = (v, tipo, forma)
altezze, profili_ana, dxf_sez = {}, {}, {}
for art in used:
    nome, tipo, forma = TUTTI.get(art, (lista.get(art, {}).get('desc_es', art), 'accessorio', 'L'))
    s = dxf.get(art)
    w, h = (s['w'], s['h']) if s else (80, 50)
    info = lista.get(art, {})
    profili_ana[art] = {'tipo': tipo, 'forma': forma, 'w': w, 'h': h, 'nome': nome + (' (Cortizo)' if tipo != 'accessorio' else ''), 'peso_g_m': info.get('peso_g_m'), 'serie': SERIE}
    altezze[art] = h
    if s:
        dxf_sez[art] = {'d': s['d'], 'x': 0, 'y': 0, 'w': w, 'h': h, 'cam': {'x': 0, 'y': 0, 'w': w, 'h': h},
                        'cam_nota': 'camera = ingombro totale del DXF Cortizo (da tarare sulla libreria macchina)'}

# ---- vetrazione: per ogni spessore la coppia (fermavetro, guarnizione interna) preferendo guarnizione 5-4-6-7-8 ----
G_INT = {4.0: '430024', 5.0: '430025', 6.0: '430026', 7.0: '430027', 8.0: '430028'}
PREF = [5.0, 4.0, 6.0, 7.0, 8.0]
def tavola_recto(tab, profili, ext, solo=None):
    righe = {}
    for code, v in tab.items():
        if solo and code not in solo: continue
        for sp, gk in v['righe']:
            k = str(sp); cand = righe.setdefault(k, [])
            cand.append((PREF.index(gk) if gk in PREF else 9, {'A': gk, 'g': G_INT.get(gk, '?'), 'B': v['A'], 'fv': code, 'ext': ext}))
    out = {}
    for k, cand in righe.items():
        cand.sort(key=lambda x: (x[0], -x[1]['B']))
        out[k] = cand[0][1]
    return {'profili': profili, 'righe': out}
vetrazione = {
    'tavCOR80_V': tavola_recto(vet['vista']['tab'], vet['vista']['profili'], '416657'),
    'tavCOR80_S': tavola_recto(vet['semivista']['tab'], vet['semivista']['profili'], '416657'),
    'tavCOR80_F39': tavola_recto(vet['fisso_ala39']['tab'], vet['fisso_ala39']['profili'], '240124'),
    'tavCOR80_F21': tavola_recto(vet['fisso_ala21']['tab'], vet['fisso_ala21']['profili'], '240124'),
    'tavCOR80_O': {'profili': ['COR-5604', 'COR-5607'], 'righe': {str(sp): {'A': gk, 'g': g, 'B': 3.5, 'fv': 'COR-7088', 'ext': None} for sp, gk, g in vet['scomparsa']['righe']}},
    'tavCOR80_R': {'profili': [], 'righe': {str(sp): {'A': gk, 'g': g, 'B': 3.5, 'fv': 'COR-8082', 'ext': '240138'} for sp, gk, g in vet['semivista_ridotta']['righe']}},
}
for k, v in vetrazione.items(): v['nota'] = 'A = guarnizione interna (mm), g = codice guarnizione interna (nero), B = larghezza fermavetro, fv = fermavetro, ext = guarnizione esterna'

# ---- drenaggi (catalogo p.382-391): quote Y/Z/facce per analogia con C75S, DA TARARE ----
drain = {SERIE: {
    'telaio':   {'w': '#1', 'v1': '5', 'v2': '30', 'y': 38.8, 'z': 3, 'f': '3', 'ut': '12', 'prof': 2, 'bordo': 75, 'passo': 1000,
                 'desc': 'Drenaggio telaio ala 39 asola 5x30 (troquel) [DA TARARE]', 'cap': ['920100', 'Deflettore drenaggio telaio']},
    'telaio21': {'w': '#1', 'v1': '5', 'v2': '30', 'y': 21.2, 'z': 3, 'f': '3', 'ut': '12', 'prof': 2, 'bordo': 75, 'passo': 1000,
                 'desc': 'Drenaggio telaio ala 21 asola 5x30 (troquel) [DA TARARE]', 'cap': ['920100', 'Deflettore drenaggio telaio']},
    'traversoT': {'w': '#1', 'v1': '5', 'v2': '30', 'y': 38.8, 'z': 3, 'f': '3', 'ut': '12', 'prof': 2, 'bordo': 75, 'passo': 1000,
                  'desc': 'Drenaggio traverso COR-7561 asola 5x30 [DA TARARE]', 'cap': ['920100', 'Deflettore drenaggio telaio']},
    'antaTrav':  {'w': '#1', 'v1': '5', 'v2': '15', 'y': 12, 'z': -19, 'f': '4', 'ut': '12', 'prof': 2, 'desc': 'Drenaggio anta asola 15x5 (a mano) [DA TARARE]'},
    'antaTravO': {'w': '#1', 'v1': '5', 'v2': '25', 'y': 12, 'z': -19, 'f': '4', 'ut': '12', 'prof': 2, 'desc': 'Drenaggio anta a scomparsa 25x4 con fermavetro (a mano; fresa d5 al posto di d4) [DA TARARE]'},
    'antaMont':  {'w': '#0', 'v1': '2.5', 'v2': '', 'y': 12, 'z': -19, 'f': '4', 'ut': '12', 'prof': 2, 'desc': 'Aerazione montante anta D5 a 100 dal filo superiore (150 portefinestre) [DA TARARE]'},
    'nota': 'Catalogo p.390-391: asole telaio 5x30 min. 2 per barra, interasse <=1000, a 75 dagli estremi, asse a 38,8 (ala 39) / 21,2 (ala 21) dal bordo. Ante (p.382-385): 2 asole 15x5 sul traverso inferiore a 100 dagli angoli, 2 fori D5 di aerazione sui montanti a 100 dall\'alto (150 sulle portefinestre). Facce/Y/Z per analogia con C75S: DA TARARE.'
}}

# ---- libreria operativa COR80: valori di C75S con le facce 1 e 4 specchiate rispetto all'asse a +40 (taratura FSTLine 10/09/2026) ----
LAV_BASE_C75S = {
    'fx_foro':      dict(w='#0', v1='3.75', v2='', y=62.999, z=-3,    f='4', ut='12', descr='FX D7.5 (040NI000)'),
    'fx_lamatura':  dict(w='#0', v1='6.75', v2='', y=11,     z=-20.5, f='1', ut='2',  descr='FX lamatura D13.5 (040NI000)'),
    'cern_d7':      dict(w='#0', v1='3.5',  v2='', y=9.5,    z=2,     f='2', ut='17', descr='Cerniera angolare D7 (S030/E030)'),
    'cern_d3':      dict(w='#0', v1='1.5',  v2='', y=9.5,    z=2,     f='2', ut='7',  descr='Cerniera angolare D3 (S030/E030)'),
    'cern_centrale':dict(w='#0', v1='1.5',  v2='', y=9,      z=-21.5, f='1', ut='4',  descr='Cerniera centrale D3 (C100)'),
    'sc_alzaanta':  dict(w='#0', v1='1.5',  v2='', y=10,     z=-20.5, f='1', ut='4',  descr='Scontro alza-anta D3'),
    'sc_nottolino': dict(w='#0', v1='1.5',  v2='', y=8,      z=-21.5, f='1', ut='4',  descr='Scontro nottolino D3'),
    'sc_angolo':    dict(w='#0', v1='1.5',  v2='', y=9,      z=-20.5, f='1', ut='4',  descr='Scontro angolo D3'),
    'mart_d10':     dict(w='#0', v1='5',    v2='', y=30,     z=3,     f='3', ut='8',  descr='Martellina D10 (G001)'),
    'mart_d12':     dict(w='#0', v1='6',    v2='', y=30,     z=3,     f='3', ut='8',  descr='Martellina D12 (G001)'),
    'mart_scasso':  dict(w='#1', v1='12',   v2='62', y=64,   z=-12,   f='1', ut='3',  descr='Martellina scasso 12x62 (G001)'),
}
ASSE_SPECCHIO = 40   # profondità profilo 80: Y -> 80 - Y sulle facce 1 e 4
def specchia(d):
    d = dict(d)
    if d['f'] in ('1', '4'): d['y'] = round(2*ASSE_SPECCHIO - d['y'], 3); d['descr'] += ' (Y specchiata)'
    return d
lav_def = {SERIE: {k: specchia(v) for k, v in LAV_BASE_C75S.items()}}
for tipo, d in drain[SERIE].items():
    if isinstance(d, dict) and d.get('w'):
        lav_def[SERIE]['dren_'+tipo] = specchia(dict(w=d['w'], v1=d['v1'], v2=d['v2'], y=d['y'], z=d['z'], f=d['f'], ut=d['ut'], descr=d['desc']))
lav_def[SERIE]['_nota'] = None
del lav_def[SERIE]['_nota']

libreria = [
    {'id': 'CO01', 'el': 'telaio', 'serie': SERIE, 'prof': ['COR-5611', 'COR-5613', 'COR-5635'], 'tipo': 'cnc', 'geo': 'asola', 'dim': '5x30', 'quota': 'Y 38.8 · Z 3 · F3 (da tarare)', 'pos': '75 dagli estremi, interasse <=1000, min 2', 'ut': 'fresa d.5 (ut.12)', 'rif': 'p.390', 'stato': 'da_tarare', 'nome': 'Drenaggio telaio ala 39'},
    {'id': 'CO02', 'el': 'telaio', 'serie': SERIE, 'prof': ['COR-5619', 'COR-7419', 'COR-7434', 'COR-5639'], 'tipo': 'cnc', 'geo': 'asola', 'dim': '5x30', 'quota': 'Y 21.2 · Z 3 · F3 (da tarare)', 'pos': '75 dagli estremi, interasse <=1000, min 2', 'ut': 'fresa d.5 (ut.12)', 'rif': 'p.391', 'stato': 'da_tarare', 'nome': 'Drenaggio telaio ala 21'},
    {'id': 'CO03', 'el': 'traverso', 'serie': SERIE, 'prof': ['COR-7561'], 'tipo': 'cnc', 'geo': 'asola', 'dim': '5x30', 'quota': 'Y 38.8 (da tarare)', 'pos': 'come telaio', 'ut': 'fresa d.5 (ut.12)', 'rif': 'p.391', 'stato': 'da_tarare', 'nome': 'Drenaggio traverso fisso inferiore'},
    {'id': 'CO04', 'el': 'anta', 'serie': SERIE, 'prof': ['COR-5670', 'COR-5690', 'COR-5672', 'COR-5692'], 'tipo': 'cnc', 'geo': 'asola', 'dim': '15x5', 'quota': 'Y 11.5-12.5 dal bordo esterno · F4 (da tarare)', 'pos': 'traverso inferiore: 100 dagli angoli (150 portefinestre)', 'ut': 'fresa d.5 (ut.12)', 'rif': 'p.383-384', 'stato': 'da_tarare', 'nome': 'Drenaggio anta in vista / semivista'},
    {'id': 'CO05', 'el': 'anta', 'serie': SERIE, 'prof': ['COR-5604', 'COR-5607'], 'tipo': 'cnc', 'geo': 'asola', 'dim': '25x4 (con fermavetro COR-7088)', 'quota': 'a 60° sul fermavetro (da tarare)', 'pos': 'traverso inferiore: 100 dagli angoli', 'ut': 'a mano (catalogo)', 'rif': 'p.382/385', 'stato': 'da_tarare', 'nome': 'Drenaggio anta a scomparsa'},
    {'id': 'CO06', 'el': 'anta', 'serie': SERIE, 'prof': ['ante'], 'tipo': 'cnc', 'geo': 'foro', 'dim': 'D5', 'quota': 'Y 11.5-13.5 dal bordo esterno (da tarare)', 'pos': 'montanti: 100 dal filo superiore (150 portefinestre)', 'ut': 'fresa d.5 (ut.12)', 'rif': 'p.382-385', 'stato': 'da_tarare', 'nome': 'Aerazione montanti anta'},
    {'id': 'CO07', 'el': 'anta', 'serie': SERIE, 'prof': ['COR-5670', 'COR-5690', 'COR-5672', 'COR-5692'], 'tipo': 'cnc', 'geo': 'ferramenta', 'dim': 'Maico Multi-Matic (regole C75S)', 'quota': 'Y/Z/facce di B23122C: DA TARARE', 'pos': 'cremonese, scontri, cerniere, forbice, martellina come C75S', 'ut': 'vari', 'rif': 'doc. Maico 750135', 'stato': 'da_tarare', 'nome': 'Ferramenta A-R (stessa di C75S)'},
    {'id': 'CO08', 'el': 'telaio', 'serie': SERIE, 'prof': ['telai'], 'tipo': 'cnc', 'geo': 'fori', 'dim': 'FX D7.5 + lamatura D13.5', 'quota': 'come C75S: DA TARARE', 'pos': '150 dagli estremi, passo <=900', 'ut': 'ut.12 / ut.2', 'rif': 'schema aziendale', 'stato': 'da_tarare', 'nome': 'Fissaggi telaio in vista'},
    {'id': 'CO09', 'el': 'telaio', 'serie': SERIE, 'prof': ['telai', 'ante'], 'tipo': 'banco', 'geo': 'squadrette', 'dim': 'tetón/ensamblar (tab. p.158-161)', 'quota': '—', 'pos': '4 angoli', 'ut': 'troquel 447998 / cianfrinatrice', 'rif': 'p.158-161', 'stato': 'banco', 'nome': 'Squadrette'},
]

P = {
    'serie_info': {SERIE: {'nome': NOME_SERIE, 'porta': False, 'sigla': 'COR 80 EVOLUTION', 'syst': SERIE, 'in_vista': True, 'tip_profili': True, 'da_tarare': True, 'vetro_default': '28',

                           'nota': 'Cortizo COR 80 Evolution 12/2025. Telai ala 39 (COR-5611/5635) e ala 21 (COR-5619/7419/5639). Ante: a scomparsa COR-5604, semivista COR-5670/5672, in vista COR-5690/5692, semivista ridotta COR-5604+COR-8082. Ferramenta Maico come C75S.'}},
    'varianti_porte': {SERIE: {'ala': {'COR-5611': 'COR-5613', 'COR-5619': 'COR-7434', 'COR-7419': 'COR-7434'}, 'telaio_int': 'COR-5611', 'nome_ala': 'con sormonto 30 mm (solape)'}},
    'tipologie': tipologie, 'altezze': altezze, 'profili_ana': profili_ana, 'dxf_sez': dxf_sez, 'vetrazione': vetrazione,
    'drain': drain, 'libreria': libreria, 'lav_def': lav_def,
    'ruota180': {SERIE: {'*': True}},   # barre caricate ruotate di 180° rispetto ai DXF Cortizo (richiesta 10/09/2026): agisce sui disegni
    'cor80_note': {'acc_desc': dict(acc_d['accessori'], **acc_d['guarnizioni']),
                   'fonte': 'Catalogo Cortizo COR 80 EVOLUTION 12/2025 (sez. 1 profili, 6 vetrazione, 7 distinte, 8 assemblaggi, 9 dettagli di fabbricazione) + DXF Cortizo "SinCotas"',
                   'non_incluso': ['vasistas', 'composta con portefinestre / ala 39 / inversore ridotto', 'importatore job XML', 'telai con enganches / apertura esterna', 'ante tubolari'],
                   'da_tarare': ['facce/versi/Y/Z di tutte le lavorazioni', 'camera macchina (cam) dei profili', 'libreria macchina W:\\LMT_65\\CAM\\COR80 (SYST COR80)']},
}
json.dump(P, open(os.path.join(ROOT, 'src', 'dati_cor80.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('tipologie', len(tipologie), '| profili', len(profili_ana), '| sezioni', len(dxf_sez), '| tavole', list(vetrazione), '->', 'src/dati_cor80.json', os.path.getsize(os.path.join(ROOT, 'src', 'dati_cor80.json')) // 1024, 'KB')
for t in tipologie[:3] + tipologie[14:15]:
    print(' ', t['cod'], t['id'], [(p['art'], p['pz'], p['mis'], p['sc']) for p in t['profili']][:8])
    print('    gu:', [(g['art'], g['mis'], g.get('gv')) for g in t['guarnizioni']][:6])
