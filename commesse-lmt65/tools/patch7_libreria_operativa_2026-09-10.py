# Patch 7 (10/09/2026): la libreria diventa la definizione operativa delle lavorazioni, per serie, con eccezioni per profilo.
# DATI.lav_def[serie][chiave] = {w, v1, v2, y, z, f, ut, descr}; DATI.lav_def[serie]['@'+profilo][chiave] = campi che sovrascrivono.
# I motori leggono lavDef(chiave) nel contesto (serie, profilo) del pezzo; i valori C75S di default sono quelli di produzione
# (regressione identica). Pagina Libreria: tabella modificabile, salvata in localStorage ed esportata con l'archivio dati.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, 'src', 'app_logic.js'); TPL = os.path.join(ROOT, 'src', 'app_template.html'); CJ = os.path.join(ROOT, 'src', 'cor80_logic.js')
js = open(JS, encoding='utf-8').read(); tpl = open(TPL, encoding='utf-8').read(); cj = open(CJ, encoding='utf-8').read()
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, f'attese {n} occorrenze, trovate {c}: {old[:70]!r}'
    return s.replace(old, new)

# ---- 1. definizioni di base + contesto + lettura ----
js = rep(js, "// ---------- tarature lavorazioni: regole modificabili nel programma ----------",
'''// ---------- libreria operativa: definizioni delle lavorazioni per serie, con eccezioni per profilo ----------
// Valori C75S = regole di produzione calibrate sul pilota FP Pro (sez. 5 del dossier). v1 = raggio del foro (#0) o larghezza asola (#1), v2 = lunghezza asola.
const LAV_DEF_BASE = { C75S: {
  fx_foro:      {w:'#0', v1:'3.75', v2:'', y:62.999, z:-3,    f:'4', ut:'12', descr:'FX D7.5 (040NI000)'},
  fx_lamatura:  {w:'#0', v1:'6.75', v2:'', y:11,     z:-20.5, f:'1', ut:'2',  descr:'FX lamatura D13.5 (040NI000)'},
  cern_d7:      {w:'#0', v1:'3.5',  v2:'', y:9.5,    z:2,     f:'2', ut:'17', descr:'Cerniera angolare D7 (S030/E030)'},
  cern_d3:      {w:'#0', v1:'1.5',  v2:'', y:9.5,    z:2,     f:'2', ut:'7',  descr:'Cerniera angolare D3 (S030/E030)'},
  cern_centrale:{w:'#0', v1:'1.5',  v2:'', y:9,      z:-21.5, f:'1', ut:'4',  descr:'Cerniera centrale D3 (C100)'},
  sc_alzaanta:  {w:'#0', v1:'1.5',  v2:'', y:10,     z:-20.5, f:'1', ut:'4',  descr:'Scontro alza-anta D3'},
  sc_nottolino: {w:'#0', v1:'1.5',  v2:'', y:8,      z:-21.5, f:'1', ut:'4',  descr:'Scontro nottolino D3'},
  sc_angolo:    {w:'#0', v1:'1.5',  v2:'', y:9,      z:-20.5, f:'1', ut:'4',  descr:'Scontro angolo D3'},
  mart_d10:     {w:'#0', v1:'5',    v2:'', y:30,     z:3,     f:'3', ut:'8',  descr:'Martellina D10 (G001)'},
  mart_d12:     {w:'#0', v1:'6',    v2:'', y:30,     z:3,     f:'3', ut:'8',  descr:'Martellina D12 (G001)'},
  mart_scasso:  {w:'#1', v1:'12',   v2:'62', y:64,   z:-12,   f:'1', ut:'3',  descr:'Martellina scasso 12x62 (G001)'},
}};
const NOMI_LAV = {fx_foro:'Fissaggio telaio Ø7,5', fx_lamatura:'Fissaggio telaio: lamatura Ø13,5', cern_d7:'Cerniera angolare Ø7', cern_d3:'Cerniera angolare Ø3',
  cern_centrale:'Cerniera centrale 2 ante Ø3', sc_alzaanta:'Scontro alza-anta (coppia int. 16)', sc_nottolino:'Scontro nottolino / chiusura', sc_angolo:"Scontro d'angolo (coppia int. 54)",
  mart_d10:'Martellina fori Ø10', mart_d12:'Martellina foro Ø12', mart_scasso:'Martellina scasso', dren_telaio:'Drenaggio telaio', dren_telaio21:'Drenaggio telaio ala 21',
  dren_traversoT:'Drenaggio traverso T', dren_antaTrav:'Drenaggio traverso anta', dren_antaTravO:'Drenaggio anta a scomparsa', dren_antaMont:'Drenaggio / aerazione montante anta'};
function costruisciLavDef(){
  const clone = o=>JSON.parse(JSON.stringify(o)); const out = {};
  Object.keys(DATI.drain||{}).forEach(s=>{ out[s] = {}; Object.entries(DATI.drain[s]).forEach(([tipo,d])=>{
    if(d && typeof d==='object' && d.w) out[s]['dren_'+tipo] = {w:d.w, v1:d.v1, v2:d.v2||'', y:d.y, z:d.z||0, f:d.f, ut:d.ut, descr:d.desc}; }); });
  Object.keys(LAV_DEF_BASE).forEach(s=>{ out[s] = Object.assign(out[s]||{}, clone(LAV_DEF_BASE[s])); });
  const fondi = (dst, src)=>{ Object.entries(src||{}).forEach(([s,def])=>{ dst[s]=dst[s]||{}; Object.entries(def||{}).forEach(([k,v])=>{
    if(k.startsWith('@')){ dst[s][k]=dst[s][k]||{}; Object.entries(v||{}).forEach(([kk,vv])=>{ dst[s][k][kk]=Object.assign({}, dst[s][k][kk]||{}, vv); }); }
    else dst[s][k]=Object.assign({}, dst[s][k]||{}, v); }); }); return dst; };
  fondi(out, DATI.lav_def);
  try{ const s = localStorage.getItem('lav_def'); if(s) fondi(out, JSON.parse(s)); }catch(e){}
  return out;
}
let LAV_DEF = costruisciLavDef(); DATI.lav_def = LAV_DEF;
function salvaLavDef(){ DATI.lav_def = LAV_DEF; try{ localStorage.setItem('lav_def', JSON.stringify(LAV_DEF)); }catch(e){} }
const LAV_CTX = {serie:'C75S', art:null};   // pezzo in lavorazione: impostato dai motori prima di generare le lavorazioni
function lavDef(chiave, serie, art){
  serie = serie||LAV_CTX.serie; art = art||LAV_CTX.art;
  const S = LAV_DEF[serie]||{}; const base = S[chiave] || (LAV_DEF.C75S||{})[chiave] || {};
  const ov = (art && S['@'+art] && S['@'+art][chiave]) || null;
  const d = Object.assign({}, base, ov||{});
  return {w:d.w||'#0', v1:String(d.v1), v2:(d.v2==null?'':String(d.v2)), v3:String(d.v3||2), y:parseFloat(d.y), z:parseFloat(d.z)||0, f:String(d.f), ut:String(d.ut),
          descr:(d.descr||chiave) + (ov ? ` [lib.${art}]` : '')};
}
function profiliSerie(serie){
  const s = new Set();
  DATI.tipologie.filter(t=>t.serie===serie).forEach(t=>(t.profili||[]).forEach(p=>{ if(!p.fv && !/^N458|^FV/.test(p.art)) s.add(p.art); }));
  const v = (DATI.varianti||{})[serie]; if(v){ if(v.standard) s.add(v.standard); if(v.z) s.add(v.z); }
  const vp = (DATI.varianti_porte||{})[serie]; if(vp && vp.ala) Object.values(vp.ala).forEach(a=>s.add(a));
  const cs = DATI.composta && DATI.composta[serie]; if(cs){ if(cs.mullone) s.add(cs.mullone); }
  Object.keys(LAV_DEF[serie]||{}).forEach(k=>{ if(k.startsWith('@')) s.add(k.slice(1)); });
  return [...s].sort();
}
function disegnaLavDef(){
  const sel = $('#lib-serie'); const tb = document.querySelector('#tab-lavdef tbody'); if(!sel || !tb) return;
  if(!sel.options.length){ [...new Set(DATI.tipologie.map(t=>t.serie))].forEach(s=>{ const o=document.createElement('option'); o.value=s; o.textContent=(SERIE_INFO[s]&&SERIE_INFO[s].nome)||s; sel.appendChild(o); }); }
  const serie = sel.value; const S = LAV_DEF[serie]||{}; const prof = profiliSerie(serie);
  const chiavi = Object.keys(S).filter(k=>!k.startsWith('@')).sort((a,b)=>(a.startsWith('dren')?1:0)-(b.startsWith('dren')?1:0) || a.localeCompare(b));
  const campi = ['descr','w','v1','v2','y','z','f','ut'];
  const cella = (k, art, campo, v, eredita)=>{
    const id = `data-k="${k}" data-campo="${campo}" ${art?`data-art="${art}"`:''}`;
    if(campo==='w') return `<select ${id}><option value="" ${v==null||v===''?'selected':''}>${eredita?'(eredita)':''}</option><option value="#0" ${v==='#0'?'selected':''}>#0 foro</option><option value="#1" ${v==='#1'?'selected':''}>#1 asola</option></select>`;
    if(campo==='f') return `<select ${id}><option value="" ${v==null||v===''?'selected':''}>${eredita?'(eredita)':''}</option>${['1','2','3','4'].map(o=>`<option value="${o}" ${String(v)===o?'selected':''}>F${o}</option>`).join('')}</select>`;
    const w = campo==='descr' ? '15rem' : '4.6rem';
    return `<input ${id} value="${v==null?'':String(v).replace(/"/g,'&quot;')}" style="width:${w}" placeholder="${eredita?'eredita':''}">`;
  };
  let h = '';
  chiavi.forEach(k=>{
    const d = S[k];
    h += `<tr><td><b>${NOMI_LAV[k]||k}</b><br><span class="nota-piccola">${k}</span></td>${campi.map(c=>`<td>${cella(k,null,c,d[c],false)}</td>`).join('')}
      <td><button class="spoglio" data-ecc="${k}" title="Aggiungi un'eccezione per un profilo">+ profilo</button></td></tr>`;
    Object.keys(S).filter(a=>a.startsWith('@') && S[a][k]).sort().forEach(a=>{
      const art = a.slice(1), o = S[a][k];
      h += `<tr style="background:#F5F7F9"><td style="padding-left:1.2rem">↳ <select data-k="${k}" data-art="${art}" data-campo="__art">${prof.map(p=>`<option ${p===art?'selected':''}>${p}</option>`).join('')}${prof.includes(art)?'':`<option selected>${art}</option>`}</select></td>
        ${campi.map(c=>`<td>${cella(k,art,c,o[c],true)}</td>`).join('')}<td><button class="spoglio" data-del-ecc="${k}" data-art="${art}" title="Elimina eccezione">✕</button></td></tr>`;
    });
  });
  tb.innerHTML = h || `<tr><td colspan="10" class="nota-piccola">Nessuna definizione per questa serie (le porte D67/D77 usano i parametri di DATI.porte_ferr).</td></tr>`;
  const num = c=>['y','z'].includes(c);
  tb.querySelectorAll('[data-campo]').forEach(el=>el.addEventListener('change', ()=>{
    const k=el.dataset.k, c=el.dataset.campo, art=el.dataset.art;
    if(c==='__art'){ const nuovo = el.value; if(nuovo===art) return; LAV_DEF[serie]['@'+nuovo] = LAV_DEF[serie]['@'+nuovo]||{}; LAV_DEF[serie]['@'+nuovo][k] = LAV_DEF[serie]['@'+art][k]; delete LAV_DEF[serie]['@'+art][k]; salvaLavDef(); disegnaLavDef(); return; }
    const v = el.value.trim();
    if(art){ const o = LAV_DEF[serie]['@'+art][k]; if(v==='') delete o[c]; else o[c] = num(c) ? (parseFloat(v.replace(',','.'))||0) : v; }
    else { LAV_DEF[serie][k][c] = num(c) ? (parseFloat(v.replace(',','.'))||0) : v; }
    salvaLavDef();
  }));
  tb.querySelectorAll('[data-ecc]').forEach(b=>b.addEventListener('click', ()=>{
    const k=b.dataset.ecc; const art = prof.find(p=>!(LAV_DEF[serie]['@'+p]&&LAV_DEF[serie]['@'+p][k])) || prof[0] || 'PROFILO';
    LAV_DEF[serie]['@'+art] = LAV_DEF[serie]['@'+art]||{}; LAV_DEF[serie]['@'+art][k] = LAV_DEF[serie]['@'+art][k]||{}; salvaLavDef(); disegnaLavDef(); }));
  tb.querySelectorAll('[data-del-ecc]').forEach(b=>b.addEventListener('click', ()=>{
    const k=b.dataset.delEcc, art=b.dataset.art; delete LAV_DEF[serie]['@'+art][k]; if(!Object.keys(LAV_DEF[serie]['@'+art]).length) delete LAV_DEF[serie]['@'+art]; salvaLavDef(); disegnaLavDef(); }));
}
function ripristinaLavDef(){ try{ localStorage.removeItem('lav_def'); }catch(e){} LAV_DEF = costruisciLavDef(); DATI.lav_def = LAV_DEF; disegnaLavDef(); }

// ---------- tarature lavorazioni: regole modificabili nel programma ----------''')

# ---- 2. i motori leggono dalla libreria ----
js = rep(js, "function lavDrenaggio(serie, tipo, x){\n  const s = DRAIN[serie]||DRAIN['C75S']; const d = s[tipo];\n  return {x, w:d.w, v1:d.v1, v2:d.v2, v3:String(d.prof), y:d.y, z:(d.z||0), f:d.f, ut:d.ut, descr:d.desc};\n}",
             "function lavDrenaggio(serie, tipo, x){\n  const s = DRAIN[serie]||DRAIN['C75S']; const d = s[tipo] || DRAIN['C75S'][tipo] || {};\n  return Object.assign({x}, lavDef('dren_'+tipo, serie), {v3:String(d.prof||2)});\n}")
js = rep(js, "function lavFX(L){ const out=[]; posFX(L).forEach(x=>LAV_FX.forEach(s=>out.push(Object.assign({x,v3:'2'},s)))); return out; }",
             "function lavFX(L){ const out=[]; posFX(L).forEach(x=>['fx_foro','fx_lamatura'].forEach(k=>out.push(Object.assign({x}, lavDef(k))))); return out; }")
js = rep(js, ",v3:'2'},LAV_CERN.d7)", "},lavDef('cern_d7'))", 2)
js = rep(js, ",v3:'2'},LAV_CERN.d3)", "},lavDef('cern_d3'))", 2)
js = rep(js, """  return [
    {x:xm-21.5, w:'#0',v1:'5',v2:'',v3:'2',y:30,z:3,f:'3',ut:'8',descr:'Martellina D10 (G001)'},
    {x:xm+21.5, w:'#0',v1:'5',v2:'',v3:'2',y:30,z:3,f:'3',ut:'8',descr:'Martellina D10 (G001)'},
    {x:xm,      w:'#0',v1:'6',v2:'',v3:'2',y:30,z:3,f:'3',ut:'8',descr:'Martellina D12 (G001)'},
    {x:xm,      w:'#1',v1:'12',v2:'62',v3:'2',y:64,z:-12,f:'1',ut:'3',descr:'Martellina scasso 12x62 (G001)'}
  ];""", """  return [
    Object.assign({x:xm-21.5}, lavDef('mart_d10')),
    Object.assign({x:xm+21.5}, lavDef('mart_d10')),
    Object.assign({x:xm},      lavDef('mart_d12')),
    Object.assign({x:xm},      lavDef('mart_scasso'))
  ];""")
js = rep(js, """const SC_PAIR16 = (x)=>[{x:x-8,w:'#0',v1:'1.5',v2:'',v3:'2',y:10,z:-20.5,f:'1',ut:'4',descr:'Scontro alza-anta D3'},
                        {x:x+8,w:'#0',v1:'1.5',v2:'',v3:'2',y:10,z:-20.5,f:'1',ut:'4',descr:'Scontro alza-anta D3'}];
const SC_SINGLE = (x)=>({x,w:'#0',v1:'1.5',v2:'',v3:'2',y:8,z:-21.5,f:'1',ut:'4',descr:'Scontro nottolino D3'});
const SC_PAIR54 = (x)=>[{x:x-27,w:'#0',v1:'1.5',v2:'',v3:'2',y:9,z:-20.5,f:'1',ut:'4',descr:'Scontro angolo D3'},
                        {x:x+27,w:'#0',v1:'1.5',v2:'',v3:'2',y:9,z:-20.5,f:'1',ut:'4',descr:'Scontro angolo D3'}];""",
"""const SC_PAIR16 = (x)=>[Object.assign({x:x-8}, lavDef('sc_alzaanta')), Object.assign({x:x+8}, lavDef('sc_alzaanta'))];
const SC_SINGLE = (x)=>Object.assign({x}, lavDef('sc_nottolino'));
const SC_PAIR54 = (x)=>[Object.assign({x:x-27}, lavDef('sc_angolo')), Object.assign({x:x+27}, lavDef('sc_angolo'))];""")
js = rep(js, """                [mm/2-19, mm/2+19].forEach(x=> lav.push({x:Math.round(x*10)/10, w:'#0',v1:'1.5',v2:'',v3:'2',
                  y:9, z:-21.5, f:'1', ut:'4', descr:'Cerniera centrale D3 (C100)'}));""",
"""                [mm/2-19, mm/2+19].forEach(x=> lav.push(Object.assign({x:Math.round(x*10)/10}, lavDef('cern_centrale'))));""")
# contesto: tipologie
js = rep(js, "          const codPezzo = `${t.cod}-${p.sc}${String(k+1).padStart(2,'0')}`;\n          const lav=[];",
             "          const codPezzo = `${t.cod}-${p.sc}${String(k+1).padStart(2,'0')}`;\n          const lav=[]; LAV_CTX.serie = t.serie; LAV_CTX.art = art;")
# contesto: composta C75S/C82S
js = rep(js, "  const telaio = r.telaio||'B23008C', anta = 'B23122C', trav = D.trav;",
             "  const telaio = r.telaio||'B23008C', anta = 'B23122C', trav = D.trav;\n  LAV_CTX.serie = t.serie; LAV_CTX.art = telaio;")
js = rep(js, "      lav=pos.map(x=>lavDrenaggio(t.serie,'telaio',x)); capDrenaggio(t.serie,accessori,pos.length); }",
             "      LAV_CTX.art = telaio; lav=pos.map(x=>lavDrenaggio(t.serie,'telaio',x)); capDrenaggio(t.serie,accessori,pos.length); }")
js = rep(js, "      lavT=pos.map(x=>lavDrenaggio(t.serie,tipoT,x)); capDrenaggio(t.serie,accessori,pos.length); }",
             "      LAV_CTX.art = trav; lavT=pos.map(x=>lavDrenaggio(t.serie,tipoT,x)); capDrenaggio(t.serie,accessori,pos.length); }")
js = rep(js, "      const goccDed = t.serie==='C75S' ? 69 : 141;", "      const goccDed = t.serie==='C75S' ? 69 : 141;\n      LAV_CTX.art = anta;")
# contesto: composta COR80
cj = rep(cj, "  const telaio = codiceProfilo(t.serie, r, C.telaio, ''), anta = C.anta_art, trav = C.trav;",
             "  const telaio = codiceProfilo(t.serie, r, C.telaio, ''), anta = C.anta_art, trav = C.trav;\n  LAV_CTX.serie = t.serie; LAV_CTX.art = telaio;")
cj = rep(cj, "    if(conDren&&k===1){ const pos=posDren(L); lav=pos.map(x=>lavDrenaggio(t.serie,'telaio21',x));",
             "    if(conDren&&k===1){ LAV_CTX.art = telaio; const pos=posDren(L); lav=pos.map(x=>lavDrenaggio(t.serie,'telaio21',x));")
cj = rep(cj, "    if(conDren){ const pos=posDren(lunT); lavT=pos.map(x=>lavDrenaggio(t.serie,'traversoT',x));",
             "    if(conDren){ LAV_CTX.art = trav; const pos=posDren(lunT); lavT=pos.map(x=>lavDrenaggio(t.serie,'traversoT',x));")
cj = rep(cj, "      const sash=(lab, awS, n)=>{                       // n = indice per i codici pezzo",
             "      const sash=(lab, awS, n)=>{                       // n = indice per i codici pezzo\n        LAV_CTX.art = anta;")
# pulsanti e apertura
js = rep(js, "  const lib = document.querySelector('#sez-libreria');\n  if(lib) lib.style.display = 'block';\n  window.scrollTo(0,0);\n}",
             "  const lib = document.querySelector('#sez-libreria');\n  if(lib) lib.style.display = 'block';\n  disegnaLavDef();\n  window.scrollTo(0,0);\n}")
js = rep(js, "const bt=$('#btn-tarature'); if(bt) bt.addEventListener('click', apriTarature);",
             "const bt=$('#btn-tarature'); if(bt) bt.addEventListener('click', apriTarature);\nconst ls=$('#lib-serie'); if(ls) ls.addEventListener('change', disegnaLavDef);\nconst lr=$('#btn-lib-ripristina'); if(lr) lr.addEventListener('click', ()=>{ if(confirm('Ripristinare le definizioni di serie (si perdono le modifiche fatte in questo browser)?')) ripristinaLavDef(); });")

# ---- 3. template ----
tpl = rep(tpl, '''      <div class="azioni no-stampa" style="margin-bottom:.8rem">
        <button class="filtro-lav primario" data-el="tutte">Tutte</button>''',
'''      <h3 style="font-size:.8rem;letter-spacing:.1em;color:var(--rosso);margin:.2rem 0 .4rem">DEFINIZIONI DELLE LAVORAZIONI — serie
        <select id="lib-serie" style="width:auto;display:inline-block;margin:0 .5rem"></select>
        <button id="btn-lib-ripristina" class="spoglio" style="font-size:.7rem">ripristina valori di serie</button></h3>
      <div class="nota-piccola" style="margin-bottom:.5rem">Questa è la libreria che il programma usa davvero: per ogni lavorazione i valori della serie (W = #0 foro / #1 asola; v1 = raggio del foro o larghezza dell'asola; v2 = lunghezza asola; Y, Z in mm; faccia; utensile). "+ profilo" aggiunge un'eccezione per un profilo: compila solo i campi da cambiare, gli altri ereditano dalla serie. Le posizioni lungo la barra (X) restano regole di produzione (Maico, catalogo). Le modifiche restano salvate in questo browser e vanno nell'archivio dati (dati_serie.js); dopo una modifica premi di nuovo "Calcola commessa".</div>
      <div style="overflow-x:auto;margin-bottom:1rem"><table id="tab-lavdef" style="min-width:1000px">
        <thead><tr><th>Lavorazione</th><th>Descrizione nel job</th><th>W</th><th>v1</th><th>v2</th><th>Y</th><th>Z</th><th>Faccia</th><th>Utensile</th><th></th></tr></thead><tbody></tbody></table></div>
      <h3 style="font-size:.8rem;letter-spacing:.1em;color:var(--rosso);margin:.2rem 0 .4rem">SCHEDE DI CATALOGO</h3>
      <div class="azioni no-stampa" style="margin-bottom:.8rem">
        <button class="filtro-lav primario" data-el="tutte">Tutte</button>''')
open(JS,'w',encoding='utf-8').write(js); open(TPL,'w',encoding='utf-8').write(tpl); open(CJ,'w',encoding='utf-8').write(cj)
print('patch 7 applicata')
