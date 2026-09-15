# Sezioni profili Cortizo COR 80 Evolution: DXF "SinCotas" -> data/dxf_sez_cor80.json
# Legge SOLO la sezione ENTITIES (i DXF Cortizo contengono blocchi/oggetti con coordinate spurie),
# layer 0 / 00_ALUMINIO + 00_POLIAMIDAS (barrette di poliammide), ignora HATCH. Coordinate arrotondate a 0,1 mm. Stessa uscita di dxf2svg.py (d, w, h, x=0, y=0, n).
import math, os, sys, json, glob, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'dxf', 'COR80')
LAYERS_OK = {'0', '00_ALUMINIO', '00_POLIAMIDAS'}

def entities(fn):
    L = open(fn, encoding='latin1').read().splitlines()
    try: s = L.index('ENTITIES')
    except ValueError: return []
    i = s; out = []
    while i < len(L) - 1:
        if L[i].strip() == '0':
            typ = L[i + 1].strip(); i += 2; d = collections.defaultdict(list)
            while i < len(L) - 1 and L[i].strip() != '0':
                d[L[i].strip()].append(L[i + 1].strip()); i += 2
            if typ == 'ENDSEC': break
            out.append((typ, d))
        else: i += 1
    return out

def arc_pts(cx, cy, r, a1, a2):
    if a2 < a1: a2 += 360
    pts = []; a = a1
    while a < a2:
        pts.append((cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))); a += 5
    pts.append((cx + r * math.cos(math.radians(a2)), cy + r * math.sin(math.radians(a2))))
    return pts

def segments(ents):
    """-> lista di primitive ('L',x1,y1,x2,y2) / ('A',x1,y1,x2,y2,r,large,sweep) / ('C',cx,cy,r) e punti per bbox"""
    path = []; pts = []
    for typ, d in ents:
        layer = d['8'][0] if d['8'] else '0'
        if layer not in LAYERS_OK: continue
        f = lambda k, j=0: float(d[k][j])
        if typ == 'LINE':
            x1, y1, x2, y2 = f('10'), f('20'), f('11'), f('21')
            path.append(('L', x1, y1, x2, y2)); pts += [(x1, y1), (x2, y2)]
        elif typ == 'ARC':
            cx, cy, r, a1, a2 = f('10'), f('20'), f('40'), f('50'), f('51')
            p = arc_pts(cx, cy, r, a1, a2); pts += p
            sweep = (a2 - a1) % 360
            path.append(('A', p[0][0], p[0][1], p[-1][0], p[-1][1], r, 1 if sweep > 180 else 0, 0))
        elif typ == 'CIRCLE':
            cx, cy, r = f('10'), f('20'), f('40')
            path.append(('C', cx, cy, r)); pts += [(cx - r, cy - r), (cx + r, cy + r)]
        elif typ == 'LWPOLYLINE':
            xs = [float(v) for v in d['10']]; ys = [float(v) for v in d['20']]
            bul = [float(v) for v in d['42']] if d['42'] else []
            closed = d['70'] and (int(d['70'][0]) & 1)
            n = len(xs); rng = range(n if closed else n - 1)
            for k in rng:
                a = (xs[k], ys[k]); b = (xs[(k + 1) % n], ys[(k + 1) % n])
                bg = bul[k] if k < len(bul) else 0.0
                if abs(bg) < 1e-9:
                    path.append(('L', a[0], a[1], b[0], b[1])); pts += [a, b]
                else:  # arco da bulge
                    th = 4 * math.atan(bg); ch = math.dist(a, b); r = abs(ch / (2 * math.sin(th / 2))) if ch else 0
                    path.append(('A', a[0], a[1], b[0], b[1], r, 1 if abs(th) > math.pi else 0, 0 if bg > 0 else 1)); pts += [a, b]
        elif typ == 'SPLINE':  # approssimazione: poligonale sui fit/control points
            xs = [float(v) for v in d['10']]; ys = [float(v) for v in d['20']]
            for k in range(len(xs) - 1):
                path.append(('L', xs[k], ys[k], xs[k + 1], ys[k + 1])); pts += [(xs[k], ys[k]), (xs[k + 1], ys[k + 1])]
    return path, pts

def svg(fn):
    path, pts = segments(entities(fn))
    if not pts: return None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    T = lambda x, y: (round(x - x0, 1), round(y1 - y, 1))  # y DXF verso l'alto -> svg verso il basso
    out = []
    for p in path:
        if p[0] == 'L':
            a = T(p[1], p[2]); b = T(p[3], p[4]); out.append(f"M{a[0]} {a[1]}L{b[0]} {b[1]}")
        elif p[0] == 'A':
            a = T(p[1], p[2]); b = T(p[3], p[4]); r = round(p[5], 2)
            # il flip verticale inverte il verso dell'arco
            out.append(f"M{a[0]} {a[1]}A{r} {r} 0 {p[6]} {1 - p[7]} {b[0]} {b[1]}")
        elif p[0] == 'C':
            c = T(p[1], p[2]); r = round(p[3], 2)
            out.append(f"M{c[0] - r} {c[1]}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0")
    return dict(d=''.join(out), w=round(x1 - x0, 1), h=round(y1 - y0, 1), x=0, y=0, n=len(path))

if __name__ == '__main__':
    res = {}
    for fn in sorted(glob.glob(os.path.join(SRC, '*.dxf'))):
        k = os.path.basename(fn).replace('_SinCotas', '')[:-4].replace(' ', '')
        s = svg(fn)
        if s: res[k] = s; print(f"{k:12} {s['w']:7} x {s['h']:6}  n={s['n']}")
        else: print(k, 'VUOTO')
    json.dump(res, open(os.path.join(ROOT, 'data', 'dxf_sez_cor80.json'), 'w'))
    print(len(res), 'sezioni ->', 'data/dxf_sez_cor80.json')
