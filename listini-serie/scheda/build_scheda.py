#!/usr/bin/env python3
"""Scheda tecnica della porta base D67 (P1IA67) che genera il listino base.
Dati: scheda/porta_base_1000x2200.json (esportato dal programma listini per la misura 1000x2200),
immagini: ritagli del catalogo tecnico AluK D67-D77 v4C (scheda/img). Output: ../Scheda_Porta_Base_D67.html"""
import json, base64, os, html
H = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(os.path.join(H, 'porta_base_1000x2200.json')))
img = lambda n: 'data:image/png;base64,' + base64.b64encode(open(os.path.join(H, 'img', n), 'rb').read()).decode()
L, Hh = 1000, 2200
p, c, co = D['par'], D['coef'], D['costo']
e = html.escape
f2 = lambda v: f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
f3 = lambda v: f"{v:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.')
pct = lambda v: f"{v*100:.0f} %"

# ---- calcolo passo-passo (stessa formula del programma) ----
kg_tt = p['eur_kg_tt'] + p['add_kg']; kg_n = p['eur_kg_n'] + p['add_kg']
list_tt = co['kgT'] * kg_tt; list_n = co['kgN'] * kg_n
net_tt = list_tt * (1 - p['sc_prof']); net_n = list_n * (1 - p['sc_prof'])
acc_list = co['gua'] + c['acc']; acc_net = acc_list * (1 - p['sc_acc'])
mat = net_tt + net_n + acc_net; mat_sfrido = mat * (1 + p['sfrido'])
mano = D['ore'] * p['eur_h']
costo = mat_sfrido + co['ferr'] + mano
listino = costo * (1 + p['ricarico'])
assert abs(costo - co['costo']) < 0.05 and abs(listino - co['listino']) < 0.1, (costo, listino)

# ---- prospetto SVG (scala 1:10 circa) ----
sc = 0.22; W, HH = L*sc, Hh*sc; ox, oy = 128, 40
tel = 47*sc; anta_w, anta_h = (L-94)*sc, (Hh-55)*sc; sog = 8*sc
vet_w, vet_h = (L-258)*sc, (Hh-219)*sc; fv = 82*sc
ah = Hh-55; cern = [256, ah/2, ah-244]      # asse dal filo superiore dell'anta
def dim_v(x, y1, y2, txt, side=1):
    return (f'<line class="dim" x1="{x}" y1="{y1}" x2="{x}" y2="{y2}"/><line class="dim" x1="{x-4}" y1="{y1}" x2="{x+4}" y2="{y1}"/><line class="dim" x1="{x-4}" y1="{y2}" x2="{x+4}" y2="{y2}"/>'
            f'<text class="dimt" transform="translate({x-6*side},{(y1+y2)/2}) rotate(-90)" text-anchor="middle">{txt}</text>')
def dim_h(y, x1, x2, txt):
    return (f'<line class="dim" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"/><line class="dim" x1="{x1}" y1="{y-4}" x2="{x1}" y2="{y+4}"/><line class="dim" x1="{x2}" y1="{y-4}" x2="{x2}" y2="{y+4}"/>'
            f'<text class="dimt" x="{(x1+x2)/2}" y="{y-5}" text-anchor="middle">{txt}</text>')
svg = [f'<svg viewBox="0 0 {ox+W+150} {oy+HH+70}" class="prospetto" role="img" aria-label="Prospetto porta 1000 per 2200">']
svg.append(f'<rect class="telaio" x="{ox}" y="{oy}" width="{W}" height="{HH}"/>')
svg.append(f'<rect class="anta" x="{ox+tel}" y="{oy+tel}" width="{anta_w}" height="{anta_h}"/>')
svg.append(f'<rect class="soglia" x="{ox+tel}" y="{oy+tel+anta_h}" width="{anta_w}" height="{sog}"/>')
svg.append(f'<rect class="vetro" x="{ox+tel+fv}" y="{oy+tel+fv}" width="{vet_w}" height="{vet_h}"/>')
svg.append(f'<rect class="ferm" x="{ox+tel+fv-8*sc}" y="{oy+tel+fv-8*sc}" width="{vet_w+16*sc}" height="{vet_h+16*sc}"/>')
# verso di apertura (interna, cerniere a sinistra)
svg.append(f'<polyline class="verso" points="{ox+tel+anta_w},{oy+tel} {ox+tel},{oy+tel+anta_h/2} {ox+tel+anta_w},{oy+tel+anta_h}"/>')
for i, yc in enumerate(cern):
    y = oy+tel+yc*sc; svg.append(f'<rect class="cern" x="{ox+tel-9}" y="{y-9}" width="18" height="18" rx="2"/>')
    svg.append(f'<text class="lab" x="{ox+tel-14}" y="{y+4}" text-anchor="end">C{i+1}</text>')
ym = oy+tel+(1050)*sc
svg.append(f'<rect class="serr" x="{ox+tel+anta_w-6}" y="{ym-40}" width="6" height="80"/><circle class="cern" cx="{ox+tel+anta_w-30}" cy="{ym}" r="7"/><text class="lab" x="{ox+tel+anta_w-42}" y="{ym+4}" text-anchor="end">maniglia 1050</text>')
svg.append(dim_h(oy-14, ox, ox+W, f'L = {L}'))
svg.append(dim_h(oy+HH+30, ox+tel, ox+tel+anta_w, f'anta L−94 = {L-94}'))
svg.append(dim_h(oy+HH+52, ox+tel+fv, ox+tel+fv+vet_w, f'vetro L−258 = {L-258}'))
svg.append(dim_v(ox-26, oy, oy+HH, f'H = {Hh}'))
svg.append(dim_v(ox-66, oy+tel, oy+tel+anta_h, f'anta H−55 = {Hh-55}'))
svg.append(dim_v(ox-106, oy+tel+fv, oy+tel+fv+vet_h, f'vetro H−219 = {Hh-219}'))
x2 = ox+W+18
svg.append(dim_v(x2, oy+tel, oy+tel+256*sc, '256', -1))
svg.append(dim_v(x2, oy+tel+256*sc, oy+tel+cern[1]*sc, f'{round(cern[1]-256)}', -1))
svg.append(dim_v(x2, oy+tel+cern[1]*sc, oy+tel+cern[2]*sc, f'{round(cern[2]-cern[1])}', -1))
svg.append(dim_v(x2, oy+tel+cern[2]*sc, oy+tel+anta_h, '244', -1))
svg.append(f'<text class="lab" x="{x2+18}" y="{oy+tel+cern[0]*sc+4}">C1</text><text class="lab" x="{x2+18}" y="{oy+tel+cern[1]*sc+4}">C2</text><text class="lab" x="{x2+18}" y="{oy+tel+cern[2]*sc+4}">C3</text>')
svg.append(f'<text class="lab" x="{ox+tel+anta_w/2}" y="{oy+tel+anta_h+sog+14}" text-anchor="middle">soglia automatica 732043 (anta 906 → fascia 830-930)</text>')
svg.append('</svg>')
SVG = ''.join(svg)

def tabella(head, rows, cls=''):
    ths = ''.join(('<th class="n">' if h.endswith('*') else '<th>') + e(h.rstrip('*')) + '</th>' for h in head)
    def td(v):
        if isinstance(v, str): return '<td>' + v + '</td>'
        return '<td class="n">' + (f2(v) if isinstance(v, float) else str(v)) + '</td>'
    body = ''.join('<tr>' + ''.join(td(v) for v in r) + '</tr>' for r in rows)
    return f'<table class="{cls}"><thead><tr>{ths}</tr></thead><tbody>{body}</tbody></table>'

IMG = {'U51200': 'crop_U51200.png', 'U51320': 'crop_U51320.png', 'K1486': 'crop_K1486.png', 'N48823': 'crop_N48823.png'}
prof_rows = []
for r in D['prof']:
    prof_rows.append([f'<code>{r["art"]}</code>', e(r['desc']), r['pz'], f'<code>{e(r["mis"])}</code>', r['len'], f'<span class="chip {"tt" if r["cl"]=="tt" else "nn"}">{"taglio termico" if r["cl"]=="tt" else "non isolato"}</span>', f3(r['kg_m']), f3(r['pz']*r['len']/1000*r['kg_m'])])
gua_rows = [[f'<code>{g["art"]}</code>', e(g['desc']), f'<code>{e(g["mis"])}</code>', f2(g['m']), f2(g['pr']), f2(g['m']*g['pr'])] for g in D['gua']]
acc_rows = [[f'<code>{a["art"]}</code>', e(a['desc']), a['pz'] or '—', f2(a['pr']), f2(a['pz']*a['pr']) if a['pz'] else '—'] for a in D['acc']]
kit_rows = [[f'<code>{e(k["cod"])}</code>', e(k['desc']), k['q'], f2(k['pr']), pct(k['sc']), f2(k['netto']), f2(k['q']*k['netto']), e(k['fonte'])] for k in D['kit']]

page = f'''<title>Scheda Porta Base D67</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{--paper:#f7f6f2;--ink:#1d2024;--mute:#5d6470;--rule:#d7d3ca;--soft:#ecebe5;--acc:#c0261f;--tt:#1f5f8b;--tt-bg:#dfeaf3;--nn:#6a5a1a;--nn-bg:#f1ead0;--vetro:#d6e6ef;--anta:#ffffff;--tel:#cfcdc6;--code-bg:#efede7}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--paper:#191b1e;--ink:#ebe9e3;--mute:#a4a9b2;--rule:#3a3e45;--soft:#24272c;--acc:#e0564e;--tt:#8bbde3;--tt-bg:#1e3446;--nn:#d9c274;--nn-bg:#3a3319;--vetro:#233a48;--anta:#2a2d33;--tel:#4a4e56;--code-bg:#26292e}}}}
:root[data-theme="dark"]{{--paper:#191b1e;--ink:#ebe9e3;--mute:#a4a9b2;--rule:#3a3e45;--soft:#24272c;--acc:#e0564e;--tt:#8bbde3;--tt-bg:#1e3446;--nn:#d9c274;--nn-bg:#3a3319;--vetro:#233a48;--anta:#2a2d33;--tel:#4a4e56;--code-bg:#26292e}}
body{{background:var(--paper);color:var(--ink);font-family:"Source Sans 3",system-ui,sans-serif;font-size:15px;line-height:1.5;padding-block:32px 64px;padding-inline:clamp(16px,4vw,40px)}}
.wrap{{max-width:1040px;margin:0 auto}}
h1,h2,h3{{font-family:"Barlow Condensed","Arial Narrow",sans-serif;text-wrap:balance;margin:0;line-height:1.1}}
h1{{font-size:44px;font-weight:700;letter-spacing:.01em}} h2{{font-size:26px;font-weight:600;margin-top:44px;padding-top:12px;border-top:2px solid var(--ink)}} h3{{font-size:19px;font-weight:600;margin-top:22px}}
.eyebrow{{font-family:"JetBrains Mono",monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--acc)}}
.sub{{color:var(--mute);max-width:70ch;margin-top:8px}}
.testata{{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;border-bottom:1px solid var(--rule);padding-bottom:18px}}
.fatti{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px 22px;margin-top:22px}}
.fatti div{{border-left:2px solid var(--rule);padding-left:10px}} .fatti b{{display:block;font-family:"Barlow Condensed",sans-serif;font-size:22px;font-weight:600;line-height:1.1}} .fatti span{{font-size:12px;color:var(--mute);text-transform:uppercase;letter-spacing:.06em}}
.duo{{display:grid;grid-template-columns:minmax(280px,420px) 1fr;gap:28px;align-items:start}} @media (max-width:760px){{.duo{{grid-template-columns:1fr}}}}
.prospetto{{width:100%;max-width:100%;height:auto;display:block}}
.prospetto .telaio{{fill:var(--tel);stroke:var(--ink);stroke-width:1}} .prospetto .anta{{fill:var(--anta);stroke:var(--ink);stroke-width:1}} .prospetto .vetro{{fill:var(--vetro);stroke:none}} .prospetto .ferm{{fill:none;stroke:var(--mute);stroke-width:.8;stroke-dasharray:3 2}}
.prospetto .soglia{{fill:var(--acc);opacity:.85}} .prospetto .verso{{fill:none;stroke:var(--mute);stroke-width:.8;stroke-dasharray:4 3}} .prospetto .cern{{fill:var(--acc)}} .prospetto .serr{{fill:var(--ink)}}
.prospetto .dim{{stroke:var(--mute);stroke-width:.7}} .prospetto .dimt,.prospetto .lab{{font-family:"JetBrains Mono",monospace;font-size:9px;fill:var(--ink)}}
table{{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}} th,td{{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}} th{{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);font-weight:600}} td.n,th.n{{text-align:right}} tbody tr:last-child td{{border-bottom:1px solid var(--ink)}}
.scroll{{overflow-x:auto}} code{{font-family:"JetBrains Mono",monospace;font-size:13px;background:var(--code-bg);padding:1px 5px;border-radius:3px}}
.chip{{display:inline-block;font-size:11px;font-weight:600;letter-spacing:.04em;padding:1px 7px;border-radius:2px;white-space:nowrap}} .chip.tt{{background:var(--tt-bg);color:var(--tt)}} .chip.nn{{background:var(--nn-bg);color:var(--nn)}}
.profili{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:22px;margin-top:16px}} .profili figure{{margin:0;background:#fff;border:1px solid var(--rule);padding:8px}} .profili img{{max-width:100%;display:block}} .profili figcaption{{font-size:13px;color:var(--mute);margin-top:6px;color:#3b3f45}}
.formula{{font-family:"JetBrains Mono",monospace;font-size:13px;background:var(--soft);padding:14px 16px;border-left:3px solid var(--acc);white-space:pre-wrap;line-height:1.6}}
.tot td{{font-weight:600}} .nota{{font-size:13.5px;color:var(--mute);max-width:75ch}} ul{{padding-left:20px}} li{{margin:4px 0}}
.legenda{{display:flex;gap:18px;flex-wrap:wrap;font-size:13px;color:var(--mute);margin-top:6px}} .legenda i{{display:inline-block;width:12px;height:12px;vertical-align:-1px;margin-right:5px;border:1px solid var(--ink)}}
</style>
<div class="wrap">
<header class="testata">
 <div><div class="eyebrow">Listini altre serie · tipologia base · {e(D['t']['id'])}</div>
 <h1>Porta base D67, un'anta, apertura interna</h1>
 <p class="sub">Come è costruita la porta che genera il listino base: profili, guarnizioni, accessori, kit ferramenta e calcolo del costo. Esempio numerico sulla misura {L} × {Hh} mm. Riferimento catalogo AluK D67 pag. 8.07 (14.10.2024); prezzi listino AluK 15.06.2026.</p></div>
 <div class="eyebrow">codice griglia {e(D['t']['id'].split('_')[0])} · P1IA67</div>
</header>

</div>

<h2>1. Prospetto e regole dimensionali</h2>
<div class="duo">
 <div>{SVG}<div class="legenda"><span><i style="background:var(--tel)"></i>stipite</span><span><i style="background:var(--anta)"></i>anta</span><span><i style="background:var(--vetro)"></i>vetro</span><span><i style="background:var(--acc)"></i>cerniere / soglia</span></div></div>
 <div>
  <h3>Misure derivate da L × H (luce esterna telaio)</h3>
  <ul>
   <li><b>Stipite</b>: traverso <code>L</code>, montanti <code>H</code>, tagli 45°/90° (montanti 90-45 e 45-90).</li>
   <li><b>Anta</b> U51320 su quattro lati a 45°: traversi <code>L−94</code>, montanti <code>H−55</code>. Anta 47 mm dentro il telaio sui lati e in alto; 8 mm di aria in basso per la soglia automatica.</li>
   <li><b>Vetro</b> 1 lastra <code>L−258 × H−219</code>, spessore 28 mm. Fermavetri N48823: orizzontali <code>L−242</code>, verticali <code>H−247</code>, a 90°.</li>
   <li><b>Portaspazzolino</b> K1486 <code>L−148</code> sul traverso inferiore anta, con spazzolino 809944 lungo <code>L</code>.</li>
   <li><b>Cerniere a stelo H51300-B1</b> (nere): 2 se altezza anta ≤ 1300, 3 se ≤ 2400, altrimenti 4. Asse a 256 dal filo superiore anta e 244 dal filo inferiore, intermedie equidistanti; sul telaio +6 mm. Qui anta {Hh-55} → 3 cerniere.</li>
   <li><b>Serratura</b> Performa 3 catenacci + scrocco E35, maniglia a 1050 dal filo inferiore anta; incontri centrale e deviatori sullo stipite.</li>
   <li><b>Soglia automatica</b> scelta per larghezza anta (<code>L−94</code>): fasce 530-630 … 1130-1230, articoli 732040 ÷ 732046, con spazzolino K1488.</li>
  </ul>
 </div>
</div>

<h2>2. Profili</h2>
<div class="scroll">{tabella(['Articolo','Elemento','Pz','Misura','mm a 1000×2200*','Classe','kg/m*','kg totali*'], prof_rows)}</div>

<div class="profili">
 <figure><img src="{img(IMG['U51200'])}" alt="Sezione stipite U51200"><figcaption>U51200 stipite porta apertura interna, 67 × 66 mm. Squadrette V42002 (interna) e 710410 + spina 710409 (esterna).</figcaption></figure>
 <figure><img src="{img(IMG['U51320'])}" alt="Sezione battente U51320"><figcaption>U51320 battente porta apertura interna, 67 × 96 mm. Squadrette V42003 (interna) e 730036 (esterna).</figcaption></figure>
 <figure><img src="{img(IMG['K1486'])}" alt="Sezione portaspazzolino K1486"><figcaption>K1486 portaspazzolino, 28,2 × 20,4 mm, con tappi 732090.</figcaption></figure>
 <figure><img src="{img(IMG['N48823'])}" alt="Fermavetro N48823"><figcaption>N48823 fermavetro squadrato cava K, A = 23 mm per vetro 28 mm. <img src="{img('crop_FV_legenda.png')}" alt="Quota A del fermavetro" style="max-width:140px;display:inline-block;vertical-align:middle;margin-left:8px"></figcaption></figure>
</div>

<h2>3. Guarnizioni</h2>
<div class="scroll">{tabella(['Articolo','Guarnizione','Sviluppo','m a 1000×2200*','€/m listino*','€ listino*'], gua_rows)}</div>
<p class="nota">Totale guarnizioni a listino {f2(co['gua'])} €; nel calcolo entrano con lo sconto accessori {pct(p['sc_acc'])}.</p>

<h2>4. Accessori fissi della tipologia</h2>
<div class="scroll">{tabella(['Articolo','Accessorio','Pz','€/pz listino*','€ listino*'], acc_rows)}</div>
<p class="nota">Totale accessori a listino {f2(c['acc'])} € per porta, indipendente dalla misura. Le voci senza quantità (regolatori, tappi copriforo, antiscardine) sono opzionali o dipendono dalla posa e non sono conteggiate.</p>

<h2>5. Kit ferramenta per la misura {L} × {Hh}</h2>
<div class="scroll">{tabella(['Codice','Componente','Q.tà','€/pz listino*','Sconto','€/pz netto*','€ netto*','Fonte'], kit_rows)}</div>
<p class="nota">Totale ferramenta netta {f2(co['ferr'])} €. Le voci a listino AluK (blocco FP «{e(D['t']['kit_blocco'])}», cerniere) hanno lo sconto accessori {pct(p['sc_acc'])}; il pacchetto serratura, cilindro e maniglia è a prezzo netto fornitore senza sconto ulteriore. La ferramenta non subisce sfrido.</p>

<h2>6. Come si arriva al prezzo di listino</h2>
<div class="formula">costo = [ (kg TT × €/kg TT verniciato + kg N × €/kg N verniciato) × (1 − sconto profili)
        + (guarnizioni + accessori a listino) × (1 − sconto accessori) ] × (1 + sfrido)
        + ferramenta netta + ore × €/h
listino = costo × (1 + ricarico)</div>
<h3>Parametri in vigore</h3>
<div class="scroll"><table><tbody>
<tr><td>€/kg profili taglio termico (grezzo + verniciatura 20)</td><td class="n">{f2(p['eur_kg_tt'])} + {f2(p['add_kg'])} = {f2(kg_tt)}</td><td>€/kg profili non isolati (grezzo + verniciatura 20)</td><td class="n">{f2(p['eur_kg_n'])} + {f2(p['add_kg'])} = {f2(kg_n)}</td></tr>
<tr><td>Sconto acquisto profili</td><td class="n">{pct(p['sc_prof'])}</td><td>Sconto acquisto accessori e guarnizioni</td><td class="n">{pct(p['sc_acc'])}</td></tr>
<tr><td>Sfrido</td><td class="n">{pct(p['sfrido'])}</td><td>Manodopera</td><td class="n">{D['ore']} h × {f2(p['eur_h'])} €/h</td></tr>
<tr><td>Ricarico</td><td class="n">{pct(p['ricarico'])}</td><td>Coefficienti kg TT (cost., per mm L, per mm H)</td><td class="n">{c['tt'][0]:.4f} · {c['tt'][1]:.5f} · {c['tt'][2]:.5f}</td></tr>
</tbody></table></div>
<h3>Esempio {L} × {Hh}</h3>
<div class="scroll"><table><thead><tr><th>Voce</th><th class="n">Quantità</th><th class="n">Listino €</th><th class="n">Netto €</th></tr></thead><tbody>
<tr><td>Profili taglio termico</td><td class="n">{f3(co['kgT'])} kg × {f2(kg_tt)} €/kg</td><td class="n">{f2(list_tt)}</td><td class="n">{f2(net_tt)}</td></tr>
<tr><td>Profili non isolati</td><td class="n">{f3(co['kgN'])} kg × {f2(kg_n)} €/kg</td><td class="n">{f2(list_n)}</td><td class="n">{f2(net_n)}</td></tr>
<tr><td>Guarnizioni + accessori</td><td class="n">{f2(co['gua'])} + {f2(c['acc'])}</td><td class="n">{f2(acc_list)}</td><td class="n">{f2(acc_net)}</td></tr>
<tr><td>Materiale con sfrido {pct(p['sfrido'])}</td><td class="n">{f2(mat)} × {1+p['sfrido']:.2f}</td><td></td><td class="n">{f2(mat_sfrido)}</td></tr>
<tr><td>Ferramenta (kit sopra)</td><td></td><td></td><td class="n">{f2(co['ferr'])}</td></tr>
<tr><td>Manodopera</td><td class="n">{D['ore']} h × {f2(p['eur_h'])}</td><td></td><td class="n">{f2(mano)}</td></tr>
<tr class="tot"><td>Costo</td><td></td><td></td><td class="n">{f2(costo)}</td></tr>
<tr class="tot"><td>Listino = costo × {1+p['ricarico']:.2f}</td><td></td><td></td><td class="n">{f2(listino)}</td></tr>
</tbody></table></div>
<p class="nota">Il listino a griglia si ottiene ripetendo lo stesso calcolo su ogni coppia L × H; i pesi dei profili e le guarnizioni sono lineari in L e H, la soglia e le cerniere cambiano a scalini con la larghezza e l'altezza dell'anta.</p>

<h2>7. Varianti e altre serie</h2>
<ul>
 <li><b>Con zoccolo</b>: battente inferiore U51340 (96 mm) al posto di U51320, cerniere a 274 dal basso; soglia automatica invariata.</li>
 <li><b>Soglia K1769</b> (con o senza zoccolo): soglia in alluminio non isolata K1769 0,92 kg/m, tappi 732086, senza soglia automatica.</li>
 <li><b>Apertura esterna</b>: stessa costruzione con profili U51201 / U51320 in variante esterna e blocco FP 360-02; la soglia standard resta quella automatica.</li>
 <li><b>Due ante</b>: anta <code>L/2−37,5</code>, seconda anta con catenacci 732089 e aste K1777 (0,46 kg/m), 2 soglie automatiche, 6 cerniere a 2145 di anta.</li>
 <li><b>D77</b>: identica logica con U52200 / U52320 (serie 315, {f2(16.15)} €/kg grezzo) e riuso dei blocchi FP D67 per il kit.</li>
</ul>
<p class="nota">Punti ancora da confermare: attribuzione voci del blocco FP (ricavate dalla libreria FP_CAM D67, non opzionali), lunghezza aste K1777 nelle due ante, articolo V59106 senza prezzo su D77.</p>
</div>
'''
out = os.path.join(H, '..', 'Scheda_Porta_Base_D67.html'); open(out, 'w').write(page); print(out, len(page))
