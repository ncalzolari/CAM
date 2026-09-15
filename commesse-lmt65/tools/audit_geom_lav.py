# Verifica geometrica delle lavorazioni S140/D67/D77: per ogni combinazione unica (profilo, faccia, Y)
# generata dal programma (vedi tests/audit_lav_extract.js), controlla se il marker che lo schema-pezzo
# disegna cade abbastanza vicino al tracciato DXF reale del profilo, o se e' "nel vuoto" (bug segnalato
# dall'utente 2026-09-15 su S140 U10140: squadretta/ventilazione anta usavano un placeholder w/2 senza
# base geometrica). Uso:
#   node tests/audit_lav_extract.js > /tmp/audit_lav.json
#   python3 tools/audit_geom_lav.py /tmp/audit_lav.json
import json, re, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S140 = json.load(open(f'{ROOT}/data/dxf_sez_s140.json'))
PORTE = json.load(open(f'{ROOT}/data/dxf_sez_porte.json'))
AUDIT = json.load(open(sys.argv[1] if len(sys.argv) > 1 else '/tmp/audit_lav.json'))

TOK = re.compile(r'([MLA])([^MLA]*)')

def parse_path(d):
    """Ritorna lista di subpath, ciascuno lista di punti (x,y). Gli archi sono approssimati
    con un piccolo numero di punti sull'arco (sufficiente: raggi tipici 0.3-0.5mm).
    Il tracciato esportato da dxf2svg/dxf_s140 ha un comando M ridondante prima di ogni
    singolo segmento L/A (un'entita' LINE/ARC per comando): quando M ripete il punto finale
    del segmento precedente NON e' l'inizio di un nuovo sottopercorso, ma la prosecuzione
    dello stesso contorno chiuso."""
    subpaths = []
    cur = None
    cx = cy = 0.0
    EPS = 1e-3
    for m in TOK.finditer(d):
        cmd, rest = m.group(1), m.group(2).split()
        nums = [float(x) for x in rest]
        if cmd == 'M':
            nx, ny = nums[0], nums[1]
            if cur is not None and abs(nx-cx) < EPS and abs(ny-cy) < EPS:
                cx, cy = nx, ny  # continuazione dello stesso contorno: non aprire un nuovo subpath
                continue
            if cur and len(cur) > 1: subpaths.append(cur)
            cx, cy = nx, ny
            cur = [(cx, cy)]
        elif cmd == 'L':
            cx, cy = nums[0], nums[1]
            cur.append((cx, cy))
        elif cmd == 'A':
            rx, ry, rot, laf, swf, x2, y2 = nums
            # approssima l'arco con punti intermedi (raggio piccolo: pochi segmenti bastano)
            x1, y1 = cx, cy
            # arco circolare semplice (rx==ry atteso qui, fillet DXF)
            steps = 4
            # centro approssimato risolvendo geometria arco (assunzione rx=ry, sweep piccolo <=90deg)
            mxp, myp = (x1+x2)/2, (y1+y2)/2
            dx_, dy_ = x2-x1, y2-y1
            dist = math.hypot(dx_, dy_)
            h = math.sqrt(max(rx*rx - (dist/2)**2, 0))
            nx, ny = -dy_/dist if dist else 0, dx_/dist if dist else 0
            sign = 1 if (laf == swf) else -1
            if laf == '1': sign = -sign
            ccx, ccy = mxp + sign*h*nx, myp + sign*h*ny
            a1 = math.atan2(y1-ccy, x1-ccx); a2 = math.atan2(y2-ccy, x2-ccx)
            if swf == '1' and a2 < a1: a2 += 2*math.pi
            if swf == '0' and a2 > a1: a2 -= 2*math.pi
            for i in range(1, steps+1):
                a = a1 + (a2-a1)*i/steps
                cur.append((ccx+rx*math.cos(a), ccy+ry*math.sin(a)))
            cx, cy = x2, y2
    if cur and len(cur) > 1: subpaths.append(cur)
    return subpaths

def dist_point_segment(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx_, dy_ = bx-ax, by-ay
    l2 = dx_*dx_ + dy_*dy_
    if l2 == 0: return math.hypot(px-ax, py-ay)
    t = max(0, min(1, ((px-ax)*dx_ + (py-ay)*dy_) / l2))
    return math.hypot(px-(ax+t*dx_), py-(ay+t*dy_))

def dist_to_outline(pt, subpaths):
    best = float('inf')
    for sp in subpaths:
        n = len(sp)
        for i in range(n):
            a, b = sp[i], sp[(i+1) % n]
            d = dist_point_segment(pt, a, b)
            if d < best: best = d
    return best

def get_dx(art):
    if art in S140: return S140[art]
    if art in PORTE: return PORTE[art]
    return None

CACHE = {}
def polys_for(art):
    if art in CACHE: return CACHE[art]
    dx = get_dx(art)
    if dx is None:
        CACHE[art] = None; return None
    sp = parse_path(dx['d'])
    CACHE[art] = (dx, sp)
    return CACHE[art]

# F1 = superiore (top edge, dir=-1, zx=cam.R -> mm_x = dx.x+dx.w-ymm, mm_y = dx.y+dx.h)  [non ruotato]
# F4 = inferiore (bottom edge, dir=+1, zx=cam.L -> mm_x = dx.x+ymm,        mm_y = dx.y)         [non ruotato]
# F3 = sinistra  (left edge,  dir=-1, zy=cam.B -> mm_y = dx.y+dx.h-ymm,   mm_x = dx.x)          [non ruotato]
# F2 = destra    (right edge, dir=+1, zy=cam.T -> mm_y = dx.y+ymm,        mm_x = dx.x+dx.w)      [non ruotato]
# NB: rot=False per tutti i profili S140/D67/D77 (nessuna voce in DATI.ruota180 per queste serie)
# Il marker nello schema-pezzo viene disegnato esattamente SUL filo della faccia (cy=F.ly, il lato
# della bounding box), non affondato nel materiale: replichiamo lo stesso punto esatto e verifichiamo
# se il tracciato reale del profilo passa abbastanza vicino (spessore parete tipico 1.2-3mm).
SOGLIA_VUOTO = 2.0  # mm: oltre questa distanza dal tracciato piu' vicino, il marker e' "nel vuoto"

def marker_mm(dx, f, ymm):
    w, h = dx['w'], dx['h']; x0, y0 = dx['x'], dx['y']
    ymm = min(max(ymm, 0), max(w, h))
    if f == '1':
        mx = min(max(x0+w-ymm, x0), x0+w); my = y0 + h
    elif f == '4':
        mx = min(max(x0+ymm, x0), x0+w); my = y0
    elif f == '3':
        my = min(max(y0+h-ymm, y0), y0+h); mx = x0
    elif f == '2':
        my = min(max(y0+ymm, y0), y0+h); mx = x0 + w
    else:
        mx, my = x0+w/2, y0+h/2
    return (mx, my)

results = []
seen = set()
for l in AUDIT['lav']:
    key = (l['art'], l['f'], l['y'])
    if key in seen: continue
    seen.add(key)
    pf = polys_for(l['art'])
    if pf is None:
        results.append({**l, 'status':'NO_DXF'}); continue
    dx, sp = pf
    pt = marker_mm(dx, l['f'], abs(float(l['y'])))
    d = dist_to_outline(pt, sp)
    ok = d <= SOGLIA_VUOTO
    results.append({**l, 'status':'OK' if ok else 'VUOTO', 'pt':pt, 'dist':round(d,2), 'bbox':[dx['x'],dx['y'],dx['w'],dx['h']]})

vuoti = [r for r in results if r['status']=='VUOTO']
noD = [r for r in results if r['status']=='NO_DXF']
oks = [r for r in results if r['status']=='OK']
print(f"totale coppie uniche: {len(results)}  OK: {len(oks)}  VUOTO: {len(vuoti)}  NO_DXF: {len(noD)}")
print()
print("=== NEL VUOTO ===")
for r in vuoti:
    print(f"  {r['art']:8s} F{r['f']} y={r['y']:>7} dist={r['dist']:>6}mm pt={tuple(round(v,1) for v in r['pt'])} bbox={r['bbox']}  {r['descr']}")
print()
print("=== NO_DXF (profilo senza sezione disegnata) ===")
for r in noD:
    print(f"  {r['art']:8s} F{r['f']} y={r['y']:>7}  {r['descr']}")

out_path = sys.argv[2] if len(sys.argv) > 2 else '/tmp/audit_geom_results.json'
json.dump(results, open(out_path, 'w'), indent=1)
print(f"\ndettaglio -> {out_path}")
