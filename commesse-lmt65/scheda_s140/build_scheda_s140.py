#!/usr/bin/env python3
"""Scheda tecnica descrittiva AluK S140 (alzante scorrevole L&S / scorrevole in linea R).
Dati: ../src/dati_s140.json (tipologie, profili, sezioni DXF reali, vetrazione) + finiture da
../../listini-serie/dati_listini_serie.json. Nessun costo: solo come è costruito il prodotto
(prospetto, sezioni profilo, caratteristiche, accessori/ferramenta, colore, vetro).
Output: ../Scheda_S140.html"""
import json, os, re, html

H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(H)
D = json.load(open(os.path.join(ROOT, 'src', 'dati_s140.json'), encoding='utf-8'))
CAT = json.load(open(os.path.join(ROOT, 'data', 'catalogo_S140', 'catalogo_S140.json'), encoding='utf-8'))
LST = json.load(open(os.path.join(ROOT, '..', 'listini-serie', 'dati_listini_serie.json'), encoding='utf-8'))
FIN = LST['serie']['S140']['finiture']
TIP = {t['id']: t for t in D['tipologie']}
e = html.escape

def ev(expr, L, Hh):
    s = re.sub(r'\bL\b', str(L), expr); s = re.sub(r'\bH\b', str(Hh), s)
    return eval(s)

# ---------------- 1. Prospetto: tipologia XX, misura d'esempio 2900x2400 ----------------
L, Hh = 2900, 2400
xx = TIP['S140_LS_XX']
anta_l = ev(xx['anta_l'], L, Hh); anta_h = ev(xx['anta_h'], L, Hh)
vetro = xx['vetro'][0]; vetro_l = ev(vetro['l'], L, Hh); vetro_h = ev(vetro['h'], L, Hh)
sc = 0.115; W, HH = L * sc, Hh * sc; ox, oy = 150, 40
tel = 10  # bordo telaio disegnato a spessore fisso (sightline reale ~7 mm, non leggibile in scala)
aw, ah = anta_l * sc, anta_h * sc
fvL = (anta_l - vetro_l) / 2 * sc; fvH = (anta_h - vetro_h) / 2 * sc
vw, vh = aw - 2 * fvL, ah - 2 * fvH
ya = oy + (HH - ah) / 2

def dim_h(y, x1, x2, txt):
    return (f'<line class="dim" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"/><line class="dim" x1="{x1}" y1="{y-4}" x2="{x1}" y2="{y+4}"/><line class="dim" x1="{x2}" y1="{y-4}" x2="{x2}" y2="{y+4}"/>'
            f'<text class="dimt" x="{(x1+x2)/2}" y="{y-5}" text-anchor="middle">{txt}</text>')
def dim_v(x, y1, y2, txt, side=1):
    return (f'<line class="dim" x1="{x}" y1="{y1}" x2="{x}" y2="{y2}"/><line class="dim" x1="{x-4}" y1="{y1}" x2="{x+4}" y1="{y1}" x2="{x+4}" y2="{y1}"/><line class="dim" x1="{x-4}" y1="{y2}" x2="{x+4}" y2="{y2}"/>'
            f'<text class="dimt" transform="translate({x-6*side},{(y1+y2)/2}) rotate(-90)" text-anchor="middle">{txt}</text>')

svg = [f'<svg viewBox="0 0 {ox+W+60} {oy+HH+56}" class="prospetto" role="img" aria-label="Prospetto XX alzante scorrevole 2 ante mobili, 2900 per 2400 mm">']
svg.append(f'<rect class="telaio" x="{ox}" y="{oy}" width="{W}" height="{HH}"/>')
for i in (0, 1):
    x0 = ox + tel + i * (aw - 6)  # leggera sovrapposizione centrale (labirinto)
    svg.append(f'<rect class="anta" x="{x0}" y="{ya}" width="{aw}" height="{ah}"/>')
    svg.append(f'<rect class="vetro" x="{x0+fvL}" y="{ya+fvH}" width="{vw}" height="{vh}"/>')
    svg.append(f'<rect class="ferm" x="{x0+fvL-3}" y="{ya+fvH-3}" width="{vw+6}" height="{vh+6}"/>')
    ymid = ya + ah / 2
    xarrow = x0 + aw / 2 + (18 if i == 0 else -18)
    dirn = 1 if i == 0 else -1
    svg.append(f'<polyline class="verso" points="{xarrow-10*dirn},{ymid-8} {xarrow+10*dirn},{ymid} {xarrow-10*dirn},{ymid+8}"/>')
svg.append(f'<rect class="soglia" x="{ox}" y="{ya+ah}" width="{W}" height="{tel}"/>')
svg.append(dim_h(oy - 12, ox, ox + W, f'L = {L}'))
svg.append(dim_h(oy + HH + 22, ox + tel, ox + tel + aw, f'anta L/2−7 = {round(anta_l)}'))
svg.append(dim_h(oy + HH + 40, ox + tel + fvL, ox + tel + fvL + vw, f'vetro = {round(vetro_l)}'))
svg.append(dim_v(ox - 22, oy, oy + HH, f'H = {Hh}'))
svg.append(dim_v(ox - 44, ya, ya + ah, f'anta H−86,5 = {round(anta_h)}'))
svg.append(f'<text class="lab" x="{ox+W/2}" y="{ya+ah/2+3}" text-anchor="middle">labirinto centrale</text>')
svg.append(f'<text class="lab" x="{ox+W/2}" y="{ya+ah+tel+14}" text-anchor="middle">binario N10630 · soglia standard (telaio a filo)</text>')
svg.append('</svg>')
SVG = ''.join(svg)

# ---------------- 2. Sezioni profilo: dai DXF reali (dxf_sez) ----------------
SEZ_ORD = [
    ('U10020', 'Telaio 2 binari (XX)'), ('U10000', 'Telaio 1 binario (OX, fisso apribile)'),
    ('U10060', 'Telaio 3 binari, interno'), ('U10061', 'Telaio 3 binari'),
    ('U10140', 'Anta standard'), ('U10120', 'Montante centrale anta, slim'),
    ('U10600', 'Montante stipite (soluzione OX)'), ('U10601', 'Aggiuntivo montante/ripostiglio'),
    ('U10400', 'Soglia ribassata — XX'), ('U10401', 'Soglia ribassata — OX'),
    ('U10402', 'Soglia ribassata — interno XXX/4A/6A'), ('U10403', 'Soglia ribassata — esterno XXX/4A/6A'),
    ('N10630', 'Binario'), ('N10901', 'Profilo di finitura laterale'), ('N10902', 'Gocciolatoio'),
    ('N10903', 'Profilo di finitura'), ('N10904', 'Profilo aggiuntivo'), ('N10905', 'Profilo aggiuntivo'),
    ('N10906', 'Profilo aggiuntivo'), ('N10909', 'Profilo scatto labirinto'),
    ('V31013', 'Labirinto standard'), ('V31015', 'Labirinto slim'),
    ('V31208', 'Cover telaio (PVC)'), ('V31210', 'Cover anta (PVC)'), ('800167', 'Cover finitura labirinto'),
]
def sez_svg(art):
    s = D['dxf_sez'].get(art)
    if not s: return '<div class="nosez">sezione DXF non disponibile</div>'
    w, hh = s['w'], s['h']; scc = min(96 / w, 96 / hh) if w and hh else 1
    return (f'<svg viewBox="0 -2 {w+4} {hh+4}" width="{round(w*scc)}" height="{round(hh*scc)}" preserveAspectRatio="xMidYMid meet">'
            f'<path d="{s["d"]}" fill="none" stroke="var(--acc)" stroke-width="{max(0.5, 1/scc)}"/></svg>')
sez_cards = []
for art, nome in SEZ_ORD:
    pa = D['profili_ana'].get(art, {})
    kg = pa.get('peso_g_m', 0) / 1000
    sez_cards.append(f'<figure><div class="sezbox">{sez_svg(art)}</div><figcaption><code>{art}</code> {e(nome)}'
                      f'<span class="kg">{f"{kg:.2f} kg/m" if kg else ""}</span></figcaption></figure>')
SEZIONI = ''.join(sez_cards)

# ---------------- 3. Caratteristiche: gruppi / famiglie ----------------
GRUPPI_ORD, seen = [], set()
for t in D['tipologie']:
    g = t['gruppo']
    if g not in seen: seen.add(g); GRUPPI_ORD.append(g)
gruppi_rows = []
for g in GRUPPI_ORD:
    items = [t for t in D['tipologie'] if t['gruppo'] == g]
    varianti = sorted({(('montante slim' if 'U10120' in [p['art'] for p in it['profili']] else 'montante standard') + ' · ' +
                         ('soglia ribassata' if 'U10400' not in [p['art'] for p in it['profili']] and any('U104' in p['art'] for p in it['profili']) else 'soglia standard'))
                        for it in items})
    gruppi_rows.append(f'<tr><td><b>{e(g.split("—")[0].strip())}</b><div class="nota" style="margin:0">{e(g.split("—",1)[1].strip() if "—" in g else "")}</div></td>'
                        f'<td class="n">{len(items)}</td><td class="n">{items[0]["ore"]:.1f} h</td><td class="n">{items[0]["specchiature"]}</td></tr>')
GRUPPI = ''.join(gruppi_rows)

# ---------------- 4. Accessori e ferramenta (senza costi) ----------------
def acc_rows_from(t):
    return ''.join(f'<tr><td><code>{e(a["art"])}</code></td><td>{e(a["desc"])}</td><td class="n">{a["pz"] or "—"}</td></tr>' for a in t['accessori'])
def gua_rows_from(t):
    return ''.join(f'<tr><td><code>{e(g["art"])}</code></td><td>{e(g["desc"])}</td><td><code>{e(g["mis"])}</code></td></tr>' for g in t['guarnizioni'])
def kit_rows_from(t):
    rows = []
    for r in t['kit_s140']['righe']:
        fascia = f'anta {r["fascia"][0]}–{r["fascia"][1]} mm (L)' if r.get('fascia') else (f'anta {r["fascia_h"][0]}–{r["fascia_h"][1]} mm (H)' if r.get('fascia_h') else 'sempre')
        rows.append(f'<tr><td><code>{e(r["cod"])}</code></td><td>{e(r["desc"])}</td><td class="n">{r["q"]}</td><td>{e(fascia)}</td></tr>')
    return ''.join(rows)
xx, rxx = TIP['S140_LS_XX'], TIP['S140_R_XX']
KIT_LS = kit_rows_from(xx); KIT_R = kit_rows_from(rxx)
ACC = acc_rows_from(xx); GUA = gua_rows_from(xx)

# ---------------- 5. Colore ----------------
FINITURE = ''.join(f'<span class="chip-fin">{e(f["agg"])} — {e(f["nome"])}</span>' for f in FIN)

# ---------------- 6. Vetro ----------------
def vet_rows(tav):
    righe = D['vetrazione'][tav]['righe']
    out = []
    for mm in sorted(righe, key=float):
        r = righe[mm]
        out.append(f'<tr><td class="n">{mm}</td><td><code>{e(r["fv"])}</code></td><td><code>{e(r["g"])}</code></td><td><code>{e(r["ext"])}</code></td></tr>')
    return ''.join(out)
VET_A = vet_rows('tavS140A'); VET_F = vet_rows('tavS140F')

page = f'''<title>Scheda AluK S140</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{--paper:#f7f6f2;--ink:#1d2024;--mute:#5d6470;--rule:#d7d3ca;--soft:#ecebe5;--acc:#c0261f;--vetro:#d6e6ef;--anta:#ffffff;--tel:#cfcdc6;--code-bg:#efede7}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--paper:#191b1e;--ink:#ebe9e3;--mute:#a4a9b2;--rule:#3a3e45;--soft:#24272c;--acc:#e0564e;--vetro:#233a48;--anta:#2a2d33;--tel:#4a4e56;--code-bg:#26292e}}}}
:root[data-theme="dark"]{{--paper:#191b1e;--ink:#ebe9e3;--mute:#a4a9b2;--rule:#3a3e45;--soft:#24272c;--acc:#e0564e;--vetro:#233a48;--anta:#2a2d33;--tel:#4a4e56;--code-bg:#26292e}}
body{{background:var(--paper);color:var(--ink);font-family:"Source Sans 3",system-ui,sans-serif;font-size:15px;line-height:1.5;padding-block:32px 64px;padding-inline:clamp(16px,4vw,40px)}}
.wrap{{max-width:1080px;margin:0 auto}}
h1,h2,h3{{font-family:"Barlow Condensed","Arial Narrow",sans-serif;text-wrap:balance;margin:0;line-height:1.1}}
h1{{font-size:42px;font-weight:700;letter-spacing:.01em}} h2{{font-size:25px;font-weight:600;margin-top:42px;padding-top:12px;border-top:2px solid var(--ink)}} h3{{font-size:18px;font-weight:600;margin-top:20px}}
.eyebrow{{font-family:"JetBrains Mono",monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--acc)}}
.sub{{color:var(--mute);max-width:70ch;margin-top:8px}}
.testata{{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;border-bottom:1px solid var(--rule);padding-bottom:18px}}
table{{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}} th,td{{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}} th{{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);font-weight:600}} td.n,th.n{{text-align:right}}
.scroll{{overflow-x:auto}} code{{font-family:"JetBrains Mono",monospace;font-size:13px;background:var(--code-bg);padding:1px 5px;border-radius:3px}}
.duo{{display:grid;grid-template-columns:minmax(300px,460px) 1fr;gap:28px;align-items:start}} @media (max-width:760px){{.duo{{grid-template-columns:1fr}}}}
.prospetto{{width:100%;max-width:100%;height:auto;display:block;background:#fff;border:1px solid var(--rule)}}
.prospetto .telaio{{fill:var(--tel);stroke:var(--ink);stroke-width:1}} .prospetto .anta{{fill:var(--anta);stroke:var(--ink);stroke-width:1}} .prospetto .vetro{{fill:var(--vetro);stroke:none}} .prospetto .ferm{{fill:none;stroke:var(--mute);stroke-width:.8;stroke-dasharray:3 2}}
.prospetto .soglia{{fill:var(--tel)}} .prospetto .verso{{fill:none;stroke:var(--acc);stroke-width:1.4}}
.prospetto .dim{{stroke:var(--mute);stroke-width:.7}} .prospetto .dimt,.prospetto .lab{{font-family:"JetBrains Mono",monospace;font-size:9px;fill:var(--ink)}}
.legenda{{display:flex;gap:18px;flex-wrap:wrap;font-size:13px;color:var(--mute);margin-top:6px}} .legenda i{{display:inline-block;width:12px;height:12px;vertical-align:-1px;margin-right:5px;border:1px solid var(--ink)}}
.profili{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:14px;margin-top:16px}}
.profili figure{{margin:0;background:#fff;border:1px solid var(--rule);padding:10px;display:flex;flex-direction:column;align-items:center;gap:6px}}
.sezbox{{min-height:100px;display:flex;align-items:center;justify-content:center}} .nosez{{font-size:12px;color:var(--mute);text-align:center;padding:1em}}
.profili figcaption{{font-size:12.5px;color:var(--mute);text-align:center;line-height:1.4}} .profili figcaption code{{display:block;color:var(--ink);font-size:13px;margin-bottom:1px}}
.kg{{display:block;font-family:"JetBrains Mono",monospace;font-size:11px}}
.nota{{font-size:13.5px;color:var(--mute);max-width:75ch}}
.fin-lista{{display:flex;flex-wrap:wrap;gap:6px 10px;margin-top:10px}} .chip-fin{{font-size:12.5px;background:var(--soft);border:1px solid var(--rule);border-radius:3px;padding:3px 8px;white-space:nowrap}}
</style>
<div class="wrap">
<header class="testata">
 <div><div class="eyebrow">Serie S140 · alzante scorrevole L&amp;S · scorrevole in linea R</div>
 <h1>AluK S140</h1>
 <p class="sub">Come è costruito il sistema: prospetto, sezioni profilo, caratteristiche, ferramenta, colori e vetrazione disponibili. Nessun costo: per i prezzi vedi il programma listini. Fonte: catalogo AluK S140 v5A (02.01.2026) e distinte di taglio ufficiali (sez. 8).</p></div>
 <div class="eyebrow">36 tipologie · 10 famiglie</div>
</header>

<h2>1. Prospetto — esempio XX, alzante scorrevole 2 ante mobili</h2>
<div class="duo">
 <div>{SVG}<div class="legenda"><span><i style="background:var(--tel)"></i>telaio / soglia</span><span><i style="background:var(--anta)"></i>anta</span><span><i style="background:var(--vetro)"></i>vetro</span><span><i style="background:none;border-color:var(--acc)"></i>verso di scorrimento</span></div></div>
 <div>
  <h3>Misura d'esempio 2900 × 2400 mm</h3>
  <ul>
   <li><b>Telaio</b> a 2 binari (U10020): traverso <code>L</code>, montanti <code>H</code>.</li>
   <li><b>Ante</b> (U10140) 2, uguali: <code>L/2−7</code> × <code>H−86,5</code> = {round(anta_l)} × {round(anta_h)} mm, sovrapposte al centro nel labirinto.</li>
   <li><b>Vetro</b> 2 lastre <code>L/2−143</code> × <code>H−222,5</code> = {round(vetro_l)} × {round(vetro_h)} mm, spessore di base 28 mm (fino a 48 mm, vedi § 6).</li>
   <li><b>Binario</b> N10630 <code>L−104</code>, kit alzante scorrevole H10600 + meccanismo per fascia altezza anta (vedi § 4).</li>
   <li>Ogni gruppo (§ 3) è disponibile anche con <b>montante slim</b> U10120 al posto del montante standard e <b>soglia ribassata</b> U10400/U10401/U10402+U10403 al posto della soglia standard a filo telaio.</li>
  </ul>
 </div>
</div>

<h2>2. Sezioni profilo</h2>
<p class="nota">Sezioni reali dai DXF del catalogo AluK S140, non in scala fra loro (ogni riquadro è ridimensionato singolarmente).</p>
<div class="profili">{SEZIONI}</div>
<p class="nota">Il codice del telaio a 2 binari era stato trascritto "U10022" dal testo del catalogo: l'utente ha confermato che il codice corretto è <code>U10020</code> (coerente con il file DXF ricevuto, 140 mm di larghezza), corretto in tutte le fonti dati.</p>

<h2>3. Caratteristiche — famiglie e varianti</h2>
<div class="scroll"><table><thead><tr><th>Gruppo</th><th class="n">Varianti</th><th class="n">Ore lavorazione</th><th class="n">Specchiature</th></tr></thead><tbody>{GRUPPI}</tbody></table></div>
<p class="nota">36 tipologie totali = 10 gruppi × (montante standard/slim) × (soglia standard/ribassata), dove applicabile. "Specchiature" = numero di vetrate della tipologia, usato per calcolare le ore di lavorazione (4,5 h a specchiatura).</p>

<h2>4. Accessori e ferramenta</h2>
<h3>Kit ferramenta — alzante scorrevole (L&amp;S), per fascia anta</h3>
<div class="scroll"><table><thead><tr><th>Codice</th><th>Componente</th><th class="n">Q.tà</th><th>Fascia di applicazione</th></tr></thead><tbody>{KIT_LS}</tbody></table></div>
<h3>Kit ferramenta — scorrevole in linea (R), fisso</h3>
<div class="scroll"><table><thead><tr><th>Codice</th><th>Componente</th><th class="n">Q.tà</th><th>Fascia di applicazione</th></tr></thead><tbody>{KIT_R}</tbody></table></div>
<h3>Accessori di montaggio (esempio tipologia XX)</h3>
<div class="scroll"><table><thead><tr><th>Articolo</th><th>Accessorio</th><th class="n">Pz</th></tr></thead><tbody>{ACC}</tbody></table></div>
<h3>Guarnizioni (esempio tipologia XX)</h3>
<div class="scroll"><table><thead><tr><th>Articolo</th><th>Guarnizione</th><th>Sviluppo</th></tr></thead><tbody>{GUA}</tbody></table></div>

<h2>5. Colore</h2>
<p class="nota">Finiture disponibili (cartella AluK, aggregazione standard 20 = RAL 7016 opaco cartella cat. B). Elenco completo delle finiture della serie, senza costi.</p>
<div class="fin-lista">{FINITURE}</div>

<h2>6. Vetro</h2>
<h3>Anta (tavola A) — spessore vetro e componenti</h3>
<div class="scroll"><table><thead><tr><th class="n">Spessore mm</th><th>Fermavetro</th><th>Guarnizione interna</th><th>Guarnizione esterna</th></tr></thead><tbody>{VET_A}</tbody></table></div>
<h3>Fisso (tavola F) — spessore vetro e componenti</h3>
<div class="scroll"><table><thead><tr><th class="n">Spessore mm</th><th>Fermavetro</th><th>Guarnizione interna</th><th>Guarnizione esterna</th></tr></thead><tbody>{VET_F}</tbody></table></div>
<p class="nota">Spessore vetro ammesso 28-48 mm a passi di 2 mm; il fermavetro cambia famiglia (N10820-N10823) ogni 6 mm circa. Guarnizione interna 809119/809120/809121/809122 secondo lo spessore. Guarnizione esterna V03000 per tutti gli spessori.</p>
</div>
'''
out = os.path.join(ROOT, 'Scheda_S140.html'); open(out, 'w', encoding='utf-8').write(page)
print(out, len(page), 'bytes |', len(SEZ_ORD), 'sezioni |', len(GRUPPI_ORD), 'gruppi |', len(FIN), 'finiture')
