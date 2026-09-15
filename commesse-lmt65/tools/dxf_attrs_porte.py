"""Estrae i blocchi ATTDEF (testo) dai DXF di libreria macchina D67/D77: descrizione (DESC), densita'
(DENS), larghezza vetro (PANE_WIDTH), spessore vetro min/max (GLASS_MIN/MAX), lunghezza barra di stock
(BL01), parametri di ottimizzazione taglio (OPTI), offset giunzione (JX/WX/JY/WY), e soprattutto i punti
di riferimento FP_LCS_ORIG / FP_LCS_HOT / FP_LCS_INTERN (origine e verso lato caldo/interno del profilo
cosi' come lo intende FP Pro) e VC_START/VC_END (estremi della camera virtuale). dxf2svg.py ignora questi
ATTDEF (legge solo LINE/ARC/CIRCLE/LWPOLYLINE per il disegno) -> serve questo script separato.
Produce data/dxf_attrs_porte.json. Non tocca dxf2svg.py ne' dati_porte.json: e' un'estrazione a se',
da usare per tarare porte_ferr/profili_ana quando serve (vedi CLAUDE.md/dossier)."""
import glob, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_attdefs(fn):
    L = open(fn, encoding='latin1').read().splitlines()
    out = {}
    i = 0
    while i < len(L):
        if L[i].strip() == '0' and i + 1 < len(L) and L[i + 1].strip() == 'ATTDEF':
            i += 2
            d = {}
            while i < len(L) and L[i].strip() != '0':
                c = L[i].strip(); v = L[i + 1].strip(); i += 2
                d[c] = v
            tag = d.get('2', '')
            x, y = float(d.get('10', 0)), float(d.get('20', 0))
            if ':' in tag:
                k, v = tag.split(':', 1)
                out[k] = v
            elif tag:
                out[tag] = [round(x, 3), round(y, 3)]
        else:
            i += 1
    return out

def verso(orig, pt):
    if not orig or not pt: return None
    dx, dy = round(pt[0] - orig[0], 1), round(pt[1] - orig[1], 1)
    if abs(dx) > abs(dy): return '+X' if dx > 0 else '-X'
    if abs(dy) > 0: return '+Y' if dy > 0 else '-Y'
    return None

if __name__ == '__main__':
    res = {}
    n_tot = 0
    # K1490/K1490-2A esistono identici in entrambe le cartelle (soglia condivisa D67/D77):
    # chiave "serie/codice" per non perdere/sovrascrivere nessuna delle due copie.
    for serie in ('D67', 'D77'):
        for fn in sorted(glob.glob(os.path.join(ROOT, 'data', 'dxf', serie, '*.DXF'))):
            n_tot += 1
            cod = os.path.basename(fn)[:-4]
            a = parse_attdefs(fn)
            if not a: continue
            orig = a.get('FP_LCS_ORIG')
            entry = {'serie': serie, **a}
            if orig:
                entry['verso_hot'] = verso(orig, a.get('FP_LCS_HOT'))
                entry['verso_intern'] = verso(orig, a.get('FP_LCS_INTERN'))
            res[f'{serie}/{cod}'] = entry
    json.dump(res, open(os.path.join(ROOT, 'data', 'dxf_attrs_porte.json'), 'w', encoding='utf-8'),
               ensure_ascii=False, indent=1)
    print(f'{len(res)} profili con ATTDEF su {n_tot} file totali -> data/dxf_attrs_porte.json')
    for key, e in sorted(res.items()):
        cod = key.split('/', 1)[1]
        print(f"  {cod:10s} [{e['serie']}] DESC={e.get('DESC','-'):38s} DENS={e.get('DENS','-'):>6s}  "
              f"HOT={e.get('verso_hot','-'):>3s} INTERN={e.get('verso_intern','-'):>3s}"
              + (f"  PANE_WIDTH={e['PANE_WIDTH']}" if 'PANE_WIDTH' in e else ''))
