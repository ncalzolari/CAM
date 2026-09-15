# Patch 3 (08/09/2026): opzioni COR80 "divisore d'anta" (Ha2) e "maniglia centrata". Applicata una volta; assert sulle occorrenze.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, 'src', 'app_logic.js'); TPL = os.path.join(ROOT, 'src', 'app_template.html')
js = open(JS, encoding='utf-8').read(); tpl = open(TPL, encoding='utf-8').read()
def rep(old, new, n=1):
    global js
    c = js.count(old); assert c == n, f'attese {n} occorrenze, trovate {c}: {old[:70]!r}'
    js = js.replace(old, new)

# 1. template: campi opzione dopo H2
old = """              <div style="font-size:.68rem;color:var(--acciaio)">H1 = H − H2 (parte porta). Formule di catalogo AluK 8.05/8.15.</div></div>"""
new = old + """
            <div id="box-div" style="display:none"><label>Divisore d'anta — Ha2 = altezza parte inferiore dell'anta (mm; vuoto = nessun divisore)</label>
              <input id="r-hdiv" class="mis" placeholder="es. 600">
              <div style="font-size:.68rem;color:var(--acciaio)">Ha1 = Ha − Ha2 (parte superiore). Fermavetri, vetri e guarnizioni dell'anta ricalcolati dalla tavola "divisore" del catalogo.</div></div>
            <div id="box-manc" style="display:none"><label><input type="checkbox" id="r-manc" style="width:auto"> Maniglia centrata (copertura inversore Ha−4 + kit tappi + adesivo)</label></div>"""
assert tpl.count(old) == 1; tpl = tpl.replace(old, new)

# 2. aggiornaSezioni: visibilità dei box
rep("  const bh2 = $('#box-h2'); if(bh2) bh2.style.display = (t && t.sopraluce) ? 'block' : 'none';",
    "  const bh2 = $('#box-h2'); if(bh2) bh2.style.display = (t && t.sopraluce) ? 'block' : 'none';\n"
    "  const bdv = $('#box-div'); if(bdv) bdv.style.display = (t && t.divisore) ? 'block' : 'none';\n"
    "  const bmc = $('#box-manc'); if(bmc) bmc.style.display = (t && t.opz_maniglia) ? 'block' : 'none';")

# 3. leggiRigaCorrente: lettura e validazione
rep("  const ferr = t.porta ? {cern:$('#r-cern').value, ncern:parseInt($('#r-ncern').value,10)||0, serr:$('#r-serr').value} : null;",
    "  const ferr = t.porta ? {cern:$('#r-cern').value, ncern:parseInt($('#r-ncern').value,10)||0, serr:$('#r-serr').value} : null;\n"
    "  const hdiv = t.divisore ? (parseFloat(String($('#r-hdiv').value).replace(',','.'))||null) : null;\n"
    "  if(hdiv!==null){ const ha = valuta(t.anta_h||'H-43', L, H, {h2}); if(!(ha && hdiv>=150 && hdiv<=ha-150)){\n"
    "    if(!quiet) $('#esito').textContent = `Divisore d'anta: Ha2 deve stare tra 150 e ${ha? Math.round(ha-150) : '?'} mm (altezza anta ${ha? Math.round(ha) : '?'}).`; return null; } }\n"
    "  const manc = t.opz_maniglia ? !!$('#r-manc').checked : null;")
rep("    traverso:$('#r-traverso').value, vetro:$('#r-vetro').value, base, L, H, q, h2, ferr};",
    "    traverso:$('#r-traverso').value, vetro:$('#r-vetro').value, base, L, H, q, h2, ferr, hdiv, manc};")

# 4. modificaRiga: ripristino campi
rep("  if(r.h2) $('#r-h2').value = r.h2;",
    "  if(r.h2) $('#r-h2').value = r.h2;\n  if($('#r-hdiv')) $('#r-hdiv').value = r.hdiv||'';\n  if($('#r-manc')) $('#r-manc').checked = !!r.manc;")

# 5. disegnaRighe: mostra le opzioni nella riga
rep("${r.battuta?'<br>'+(r.battuta==='stulp'?'stulp':'nodo stretto'):''}",
    "${r.battuta?'<br>'+(r.battuta==='stulp'?'stulp':'nodo stretto'):''}${r.hdiv?'<br>divisore Ha2='+r.hdiv:''}${r.manc?'<br>maniglia centrata':''}")

# 6. motore: applica le opzioni alla tipologia della riga
rep("    if(r.mano) t = Object.assign({}, t, {nome: t.nome+' — '+r.mano.toUpperCase()});",
    "    if(r.mano) t = Object.assign({}, t, {nome: t.nome+' — '+r.mano.toUpperCase()});\n"
    "    if(r.hdiv>0 && t.divisore) t = conDivisore(t, r);\n"
    "    if(r.manc && t.opz_maniglia) t = conManigliaCentrata(t, r);")
rep("// ---------- motore di calcolo ----------\nfunction calcolaCommessa(){",
    """// ---------- opzioni COR80: divisore d'anta e maniglia centrata (catalogo Cortizo p.301/308/321/328, p.304/307/314/317/320/324/327) ----------
function formulaAnta(t, f, hdiv){
  // 'La-95', 'Ha1-105.6', '4La+2Ha' -> formula in L/H per valuta(): La = anta (1 anta: anta_l; 2 ante: anta_l2), Ha = anta_h, Ha2 = hdiv, Ha1 = Ha-Ha2
  const La = `(${t.anta_l||t.anta_l2||'L-43'})`, Ha = `(${t.anta_h||'H-43'})`;
  const Ha1 = `(${Ha}-${hdiv})`, Ha2 = `(${hdiv})`;
  return String(f).replace(/\\s/g,'').replace(/Ha1/g, Ha1).replace(/Ha2/g, Ha2).replace(/Ha/g, Ha).replace(/La/g, La).replace(/(\\d)\\(/g, '$1*(');
}
function conDivisore(t, r){
  const d = t.divisore, n = (t.forma==='2'||t.forma==='P2') ? 2 : 1, F = f=>formulaAnta(t, f, r.hdiv);
  const prof = [];
  t.profili.forEach(p=>{
    if(p.fv && p.sc==='FERL' && d.fv_o){ prof.push(Object.assign({}, p, {pz: 4*n, mis: F(d.fv_o), desc: 'Fermavetro orizz. (anta divisa)'})); return; }
    if(p.fv && p.sc==='FERH'){
      prof.push(Object.assign({}, p, {pz: 2*n, mis: F(d.fv_v1), desc: 'Fermavetro vert. sup. (anta divisa)'}));
      prof.push(Object.assign({}, p, {pz: 2*n, mis: F(d.fv_v2), desc: 'Fermavetro vert. inf. (anta divisa)', sc: 'FERI'})); return; }
    prof.push(p);
  });
  prof.push({art: d.art, desc: d.desc, pz: n, mis: F(d.mis), ang: '90-90', sc: 'DIVL'});
  if(d.tapeta) prof.push({art: d.tapeta[0], desc: "Copertura divisore d'anta", pz: n, mis: F(d.tapeta[1]), ang: '90-90', sc: 'TAPL'});
  const vetro = [];
  t.vetro.forEach(v=>{
    if(!v.anta){ vetro.push(v); return; }
    vetro.push({pz: v.pz, l: F(d.vetro_l), h: F(d.vetro_h1), anta: true});
    vetro.push({pz: v.pz, l: F(d.vetro_l), h: F(d.vetro_h2), anta: true});
  });
  const gua = t.guarnizioni.filter(g=>!d.gu.some(x=>x[0]===g.art) && !g.gv);   // le guarnizioni dell'anta divisa sostituiscono quelle dell'anta intera
  d.gu.forEach(([art, f, gv])=>{
    const orig = t.guarnizioni.find(g=>g.art===art || (gv && g.gv));
    gua.push({art, desc: orig ? orig.desc : (((DATI.cor80_note||{}).acc_desc||{})[art] || 'Guarnizione divisore'), mis: n>1 ? `${n}*(${F(f)})` : F(f), gv: !!gv});
  });
  const acc = t.accessori.concat(d.acc.map(([art, pz])=>({art, desc: ((DATI.cor80_note||{}).acc_desc||{})[art] || `Accessorio divisore ${art}`, pz: pz*n})));
  return Object.assign({}, t, {nome: t.nome+` — DIVISORE Ha2=${r.hdiv}`, profili: prof, vetro, guarnizioni: gua, accessori: acc});
}
function conManigliaCentrata(t, r){
  const m = t.opz_maniglia, F = f=>formulaAnta(t, f, 0);
  const prof = t.profili.concat([{art: m.art, desc: m.desc, pz: 1, mis: F(m.mis), ang: '90-90', sc: 'MANC'}]);
  const ha = valuta(t.anta_h||'H-43', r.L, r.H, r) || 0;
  const nAd = Math.floor((ha-124)/500)+1;
  const acc = t.accessori.concat([{art: m.tappi, desc: 'Kit tappi copertura maniglia centrata', pz: 1},
                                  {art: m.adesivo, desc: `Adesivo cianoacrilato (${m.adesivo_formula})`, pz: nAd>0 ? nAd : 1}]);
  return Object.assign({}, t, {nome: t.nome+' — MANIGLIA CENTRATA', profili: prof, accessori: acc});
}

// ---------- motore di calcolo ----------
function calcolaCommessa(){""")
open(JS, 'w', encoding='utf-8').write(js); open(TPL, 'w', encoding='utf-8').write(tpl)
print('patch 3 applicata')
