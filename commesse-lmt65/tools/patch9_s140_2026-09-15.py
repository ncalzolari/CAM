#!/usr/bin/env python3
"""Patch 9 (15/09/2026): serie AluK S140 nel programma commesse.
- assemble.py: unione di src/dati_s140.json (generato da tools/build_s140.py dalle tipologie del listino);
- app_logic.js: prospetto degli scorrevoli (forma 'S:<schema>', X = anta mobile, O/F = specchiatura fissa) e accessori
  del kit ferramenta per anta mobile in funzione della misura (t.kit_s140: meccanismo per altezza anta, asta per larghezza)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def patch(path, old, new, n=1):
    s = open(path, encoding='utf-8').read(); c = s.count(old); assert c == n, f'{path}: attese {n} occorrenze, trovate {c}: {old[:70]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new))
A = os.path.join(ROOT, 'tools', 'assemble.py'); L = os.path.join(ROOT, 'src', 'app_logic.js')
patch(A, "merge(D, json.load(open(F+'dati_cor80.json')))   # Cortizo COR 80 Evolution\n",
         "merge(D, json.load(open(F+'dati_cor80.json')))   # Cortizo COR 80 Evolution\nmerge(D, json.load(open(F+'dati_s140.json')))    # AluK S140 (tipologie del listino)\n")
patch(L, """  const soglia = (forma==='P1'||forma==='P2')? `<rect x="0" y="${A-3}" width="${W}" height="3" fill="#8A98A3"/>` : '';""",
"""  if(String(forma).startsWith('S:')){                                   // scorrevoli S140: schema X = anta mobile, O/F = specchiatura fissa
    const sch = forma.slice(2), n = sch.length, cw = (iw-2*(n-1))/n;
    const scorr = (x,y,w,h,verso)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#DEEAF2" stroke="#5C6B76" stroke-width="1"/>
      <path d="M ${verso==='dx'?x+w*0.25:x+w*0.75} ${y+h/2} L ${verso==='dx'?x+w*0.75:x+w*0.25} ${y+h/2}" fill="none" stroke="#5C6B76" stroke-width="1.5" marker-end="url(#frecciaS)"/>`;
    inner = `<defs><marker id="frecciaS" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#5C6B76"/></marker></defs>` +
      [...sch].map((c,i)=>{ const x = t+i*(cw+2); return c==='X' ? scorr(x,t,cw,ih,i<n/2?'dx':'sx') : fisso(x,t,cw,ih); }).join('');
  }
  const soglia = (forma==='P1'||forma==='P2'||String(forma).startsWith('S:'))? `<rect x="0" y="${A-3}" width="${W}" height="3" fill="#8A98A3"/>` : '';""")
patch(L, "      t.accessori.forEach(a=>registraAccessorio(accessori, a.art, a.desc, a.pz, null));\n      t.guarnizioni.forEach(g=>{",
"""      t.accessori.forEach(a=>registraAccessorio(accessori, a.art, a.desc, a.pz, null));
      if(t.kit_s140) kitS140Accessori(t, r, accessori);                // S140: ferramenta per anta mobile in funzione della misura
      t.guarnizioni.forEach(g=>{""")
patch(L, "// ---------- motore di calcolo ----------\nfunction calcolaCommessa(){",
"""// ---------- S140: kit ferramenta per anta mobile (stesse regole del programma listini: meccanismo per altezza anta, asta per larghezza anta) ----------
function kitS140Accessori(t, r, accessori){
  const K = t.kit_s140; const aw = valuta(K.anta_l, r.L, r.H, r)||0, ah = valuta(K.anta_h, r.L, r.H, r)||0; let scelta = false;
  K.righe.forEach(x=>{
    if(x.fascia_h && !(ah>=x.fascia_h[0] && ah<=x.fascia_h[1])) return;
    if(x.fascia){ if(x.fascia_h==null && scelta) return; if(!(aw>=x.fascia[0] && aw<=x.fascia[1])) return; if(x.fascia_h==null) scelta = true; }
    registraAccessorio(accessori, x.cod, x.desc + ' [anta ' + Math.round(aw) + 'x' + Math.round(ah) + ']', x.q, null);
  });
}
// ---------- motore di calcolo ----------
function calcolaCommessa(){""")
print('patch 9 applicata')
