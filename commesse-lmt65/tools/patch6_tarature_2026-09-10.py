# Patch 6 (10/09/2026): pannello "Tarature lavorazioni" — regole per serie/profilo/faccia/lavorazione con spostamenti
# ΔX/ΔY/ΔZ e cambio faccia, modificabili nel programma (salvate nel browser e nell'archivio dati). Assert sulle occorrenze.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, 'src', 'app_logic.js'); TPL = os.path.join(ROOT, 'src', 'app_template.html'); CJ = os.path.join(ROOT, 'src', 'cor80_logic.js')
js = open(JS, encoding='utf-8').read(); tpl = open(TPL, encoding='utf-8').read(); cj = open(CJ, encoding='utf-8').read()
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, f'attese {n} occorrenze, trovate {c}: {old[:70]!r}'
    return s.replace(old, new)

# ---- template: pulsante e sezione ----
tpl = rep(tpl, '        <button id="btn-libreria">Libreria lavorazioni</button>\n',
               '        <button id="btn-libreria">Libreria lavorazioni</button>\n        <button id="btn-tarature">Tarature lavorazioni</button>\n')
tpl = rep(tpl, '  <section id="sez-distinta" style="display:none">',
'''  <section id="sez-tarature" style="display:none">
    <h2>Tarature lavorazioni <span style="font-weight:400;text-transform:none">(correzioni per serie / profilo / faccia, applicate al calcolo)</span></h2>
    <div class="corpo" style="padding-bottom:0">
      <button id="btn-chiudi-tarature" class="primario">← Torna alla commessa</button>
      <button id="btn-nuova-taratura">+ Aggiungi regola</button>
      <span class="nota-piccola">Le regole valgono per tutte le lavorazioni che corrispondono a serie, profilo (* = tutti), faccia (* = tutte) e testo della lavorazione (vuoto = tutte): ΔX lungo la barra, ΔY e ΔZ nella sezione, in mm; "Nuova faccia" sposta la lavorazione su un'altra faccia. Dallo schema pezzo, ⚙ accanto a una lavorazione precompila la regola. Dopo una modifica premi di nuovo "Calcola commessa". Le regole restano salvate in questo browser e vengono incluse in "Esporta archivio dati" (dati_serie.js).</span>
    </div>
    <div class="corpo" style="overflow-x:auto">
      <table id="tab-tarature" style="min-width:900px">
        <thead><tr><th>Serie</th><th>Profilo</th><th>Faccia</th><th>Lavorazione (contiene)</th><th>ΔX</th><th>ΔY</th><th>ΔZ</th><th>Nuova faccia</th><th>Nota</th><th></th></tr></thead>
        <tbody></tbody>
      </table>
      <div id="tarature-vuoto" class="nota-piccola" style="padding:.5rem 0">Nessuna regola. Esempio: serie COR80, profilo COR-5619, faccia 4, lavorazione "FX D7.5", ΔY +20, ΔZ −5.</div>
    </div>
  </section>

  <section id="sez-distinta" style="display:none">''')

# ---- JS: regole, applicazione, pannello ----
js = rep(js, "// ---------- secondo foglio: libreria lavorazioni ----------",
'''// ---------- tarature lavorazioni: regole modificabili nel programma ----------
// DATI.tarature = {id: {serie, prof, f, filtro, dx, dy, dz, f2, nota}}; la copia salvata nel browser (localStorage) ha la precedenza.
let TARATURE = (function(){
  try{ const s = localStorage.getItem('tarature'); if(s) return JSON.parse(s); }catch(e){}
  return Object.assign({}, DATI.tarature||{});
})();
DATI.tarature = TARATURE;
function salvaTarature(){ DATI.tarature = TARATURE; try{ localStorage.setItem('tarature', JSON.stringify(TARATURE)); }catch(e){} }
function descrBase(d){ return String(d||'').replace(/\\s*[\\[(](DA TARARE|Y specchiata|tar\\.[^\\])]*)[\\])]/g,'').split(' (')[0].trim(); }
function applicaTarature(serie, art, lav){
  const regole = Object.entries(TARATURE);
  if(!regole.length || !lav) return lav;
  lav.forEach(l=>{
    regole.forEach(([id,r])=>{
      if(r.serie && r.serie!=='*' && r.serie!==serie) return;
      if(r.prof && r.prof!=='*' && r.prof!==art) return;
      if(r.f && r.f!=='*' && String(r.f)!==String(l.f)) return;
      if(r.filtro && !String(l.descr||'').toLowerCase().includes(String(r.filtro).toLowerCase())) return;
      const dx=parseFloat(r.dx)||0, dy=parseFloat(r.dy)||0, dz=parseFloat(r.dz)||0;
      if(dx) l.x = Math.round((parseFloat(l.x)+dx)*1000)/1000;
      if(dy) l.y = Math.round((parseFloat(l.y)+dy)*1000)/1000;
      if(dz) l.z = Math.round(((parseFloat(l.z)||0)+dz)*1000)/1000;
      if(r.f2 && r.f2!=='' && r.f2!=='*') l.f = String(r.f2);
      l.descr = (l.descr||'') + ` [tar.${id}]`;
    });
  });
  return lav;
}
function nuovaTaratura(pre){
  const id = 't' + Date.now().toString(36);
  TARATURE[id] = Object.assign({serie:'*', prof:'*', f:'*', filtro:'', dx:0, dy:0, dz:0, f2:'', nota:''}, pre||{});
  salvaTarature(); apriTarature(); disegnaTarature();
  const inp = document.querySelector(`#tab-tarature [data-id="${id}"][data-k="dy"]`); if(inp) inp.focus();
}
function rimuoviTaratura(id){ delete TARATURE[id]; salvaTarature(); disegnaTarature(); }
function disegnaTarature(){
  const tb = document.querySelector('#tab-tarature tbody'); if(!tb) return;
  const serie = ['*', ...new Set(DATI.tipologie.map(t=>t.serie))];
  const sel = (id,k,v,opts,lab)=>`<select data-id="${id}" data-k="${k}">${opts.map(o=>`<option value="${o}" ${String(o)===String(v)?'selected':''}>${lab?lab(o):o}</option>`).join('')}</select>`;
  const inp = (id,k,v,w,ph)=>`<input data-id="${id}" data-k="${k}" value="${String(v==null?'':v).replace(/"/g,'&quot;')}" style="width:${w}" placeholder="${ph||''}">`;
  tb.innerHTML = Object.entries(TARATURE).map(([id,r])=>`<tr>
    <td>${sel(id,'serie',r.serie,serie,o=>o==='*'?'tutte':o)}</td><td>${inp(id,'prof',r.prof,'7rem','* = tutti')}</td>
    <td>${sel(id,'f',r.f,['*','1','2','3','4'],o=>o==='*'?'tutte':'F'+o)}</td><td>${inp(id,'filtro',r.filtro,'14rem','vuoto = tutte')}</td>
    <td>${inp(id,'dx',r.dx,'4.5rem')}</td><td>${inp(id,'dy',r.dy,'4.5rem')}</td><td>${inp(id,'dz',r.dz,'4.5rem')}</td>
    <td>${sel(id,'f2',r.f2||'',['','1','2','3','4'],o=>o===''?'— nessuno':'F'+o)}</td><td>${inp(id,'nota',r.nota,'12rem')}</td>
    <td><button class="spoglio" data-del="${id}" title="Elimina">✕</button></td></tr>`).join('');
  const v = document.querySelector('#tarature-vuoto'); if(v) v.style.display = Object.keys(TARATURE).length ? 'none' : 'block';
  tb.querySelectorAll('[data-id]').forEach(el=>el.addEventListener('change', ()=>{
    const r = TARATURE[el.dataset.id]; if(!r) return;
    r[el.dataset.k] = ['dx','dy','dz'].includes(el.dataset.k) ? (parseFloat(String(el.value).replace(',','.'))||0) : el.value.trim();
    salvaTarature();
  }));
  tb.querySelectorAll('[data-del]').forEach(b=>b.addEventListener('click', ()=>rimuoviTaratura(b.dataset.del)));
}
function apriTarature(){
  if(_sezSalvate===null){
    _sezSalvate = [];
    document.querySelectorAll('section').forEach(s=>{ if(s.id==='sez-tarature') return; _sezSalvate.push([s, s.style.display]); s.style.display='none'; });
  } else { const lib = document.querySelector('#sez-libreria'); if(lib) lib.style.display='none'; }
  const sz = document.querySelector('#sez-tarature'); if(sz) sz.style.display='block';
  disegnaTarature(); window.scrollTo(0,0);
}
function chiudiTarature(){
  const sz = document.querySelector('#sez-tarature'); if(sz) sz.style.display='none';
  (_sezSalvate||[]).forEach(([s,d])=>{ s.style.display = d; }); _sezSalvate = null; window.scrollTo(0,0);
}
document.addEventListener('click', e=>{
  const b = e.target.closest && e.target.closest('[data-tar]'); if(!b) return;
  e.preventDefault(); const pl = document.querySelector('#popup-lav'); if(pl) pl.style.display='none';
  nuovaTaratura(JSON.parse(decodeURIComponent(b.dataset.tar)));
});

// ---------- secondo foglio: libreria lavorazioni ----------''')

# applicazione: tipologie (dopo la specchiatura), composta COR80, composta C75S/C82S
js = rep(js, "          specchiaY(t.serie, lav);\n", "          specchiaY(t.serie, lav); applicaTarature(t.serie, art, lav);\n")
js = rep(js, "  const spingi=(art,desc,sc,mm,tag,lav)=>{ if(mm==null||mm<=0){erroriFormule.push(`${t.cod}: ${desc} nullo`);return;}\n    const [al,ar]=angoliJob(tag);\n    pezzi.push({art,desc,mm:Math.round(mm*10)/10,al,ar,unita,tip:t.nome,tcod:t.cod,\n      cod:`${t.cod}-${sc}`,serie:t.serie,lav:lav||[]}); };",
             "  const spingi=(art,desc,sc,mm,tag,lav)=>{ if(mm==null||mm<=0){erroriFormule.push(`${t.cod}: ${desc} nullo`);return;}\n    const [al,ar]=angoliJob(tag);\n    pezzi.push({art,desc,mm:Math.round(mm*10)/10,al,ar,unita,tip:t.nome,tcod:t.cod,\n      cod:`${t.cod}-${sc}`,serie:t.serie,lav:applicaTarature(t.serie, art, lav||[])}); };")
cj = rep(cj, "  const tara = lav=>{ specchiaY(t.serie, lav||[]);", "  const tara = lav=>{ specchiaY(t.serie, lav||[]); applicaTarature(t.serie, art_corrente, lav||[]);")
cj = rep(cj, "  const spingi=(art,desc,sc,mm,tag,lav)=>{ if(mm==null||mm<=0){erroriFormule.push(`${t.cod}: ${desc} nullo`);return;}\n    const [al,ar]=angoliJob(tag);\n    pezzi.push({art,desc,mm:Math.round(mm*10)/10,al,ar,unita,tip:t.nome,tcod:t.cod,\n      cod:`${t.cod}-${sc}`,serie:t.serie,lav:tara(lav)}); };",
             "  let art_corrente = null;\n  const spingi=(art,desc,sc,mm,tag,lav)=>{ if(mm==null||mm<=0){erroriFormule.push(`${t.cod}: ${desc} nullo`);return;}\n    const [al,ar]=angoliJob(tag); art_corrente = art;\n    pezzi.push({art,desc,mm:Math.round(mm*10)/10,al,ar,unita,tip:t.nome,tcod:t.cod,\n      cod:`${t.cod}-${sc}`,serie:t.serie,lav:tara(lav)}); };")

# schema pezzo: ⚙ per precompilare la regola
js = rep(js, "      return `<div style=\"font-size:.72rem\"><b class=\"num\">${geo}</b> a X ${l.x} · Y ${l.y} · Z ${l.z||0} · ut.${l.ut} <span style=\"color:var(--acciaio)\">${l.descr||''}</span></div>`;",
             "      const tar = encodeURIComponent(JSON.stringify({serie:p.serie, prof:p.art, f:String(l.f), filtro:descrBase(l.descr), nota:`${p.art} F${l.f} ${descrBase(l.descr)}`}));\n      return `<div style=\"font-size:.72rem\"><b class=\"num\">${geo}</b> a X ${l.x} · Y ${l.y} · Z ${l.z||0} · ut.${l.ut} <span style=\"color:var(--acciaio)\">${l.descr||''}</span> <a href=\"#\" data-tar=\"${tar}\" class=\"no-stampa\" title=\"Aggiungi una regola di taratura per questa lavorazione\" style=\"text-decoration:none\">⚙</a></div>`;")
# pulsanti
js = rep(js, "const bl=$('#btn-libreria'); if(bl) bl.addEventListener('click', apriLibreria);",
             "const bl=$('#btn-libreria'); if(bl) bl.addEventListener('click', apriLibreria);\nconst bt=$('#btn-tarature'); if(bt) bt.addEventListener('click', apriTarature);\nconst bct=$('#btn-chiudi-tarature'); if(bct) bct.addEventListener('click', chiudiTarature);\nconst bnt=$('#btn-nuova-taratura'); if(bnt) bnt.addEventListener('click', ()=>nuovaTaratura());")
open(JS,'w',encoding='utf-8').write(js); open(TPL,'w',encoding='utf-8').write(tpl); open(CJ,'w',encoding='utf-8').write(cj)
print('patch 6 applicata')
