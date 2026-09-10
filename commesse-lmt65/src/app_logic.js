;
// archivio dati esterno (dati_serie.js accanto al programma): integra o sostituisce le voci interne
if(typeof window!=='undefined' && window.DATI_ESTERNI){
  const E = window.DATI_ESTERNI;
  Object.keys(E).forEach(k=>{
    if(k==='tipologie' && Array.isArray(E[k])){
      E[k].forEach(te=>{ const i = DATI.tipologie.findIndex(t=>t.id===te.id);
        if(i>=0) DATI.tipologie[i]=te; else DATI.tipologie.push(te); });
    } else if(k==='libreria' && Array.isArray(E[k])){
      E[k].forEach(le=>{ const i = DATI.libreria.findIndex(l=>l.id===le.id);
        if(i>=0) DATI.libreria[i]=le; else DATI.libreria.push(le); });
    } else if(E[k] && typeof E[k]==='object' && !Array.isArray(E[k]) && DATI[k] && typeof DATI[k]==='object' && !Array.isArray(DATI[k])){
      Object.assign(DATI[k], E[k]);
    } else DATI[k]=E[k];
  });
}

"use strict";
// ---------- utilità ----------
const $ = s => document.querySelector(s);
const fmt = n => (Math.round(n*10)/10).toLocaleString('it-IT');
const righe = [];

function valuta(formula, L, H, r){
  // "L-42", "L/2-9", "H-29.5", "2L+4H", "L+3H" -> mm ; porte con sopraluce: H1 = parte porta, H2 = sopraluce (r.h2)
  let s = String(formula).replace(/,/g,'.').replace(/\s/g,'');
  if(!/^[0-9LH+\-*/().]+$/.test(s)) return null;
  const H2 = (r && r.h2>0) ? r.h2 : 0, H1 = H - H2;
  if(/H[12]/.test(s) && !(H2>0)) return null;
  s = s.replace(/H1/g,'A').replace(/H2/g,'B').replace(/L\/2/g,'(L/2)').replace(/(\d)([LHAB])/g,'$1*$2');
  try{ const v = Function('L','H','A','B',`return (${s});`)(L,H,H1,H2); return (isFinite(v)&&v>0)?v:null; }
  catch(e){ return null; }
}
const SERIE_INFO = DATI.serie_info || {};
function isPorta(serie){ return !!(SERIE_INFO[serie] && SERIE_INFO[serie].porta); }
function serieInVista(serie){ return serie==='C75S' || !!(SERIE_INFO[serie] && SERIE_INFO[serie].in_vista); }   // FX + ferramenta Maico in vista
function tipProfili(serie){ return !!(SERIE_INFO[serie] && SERIE_INFO[serie].tip_profili); }                    // telaio/anta/vetro definiti dalla tipologia (come le porte)
function specchiaY(serie, lav){   // serie_info[serie].specchio_y = {facce:['1','4'], asse:40}: Y -> 2*asse - Y sulle facce indicate (COR80: taratura FSTLine 10/09/2026)
  const sp = SERIE_INFO[serie] && SERIE_INFO[serie].specchio_y; if(!sp) return lav;
  lav.forEach(l=>{ if(sp.facce.includes(String(l.f))){ l.y = Math.round((2*sp.asse - parseFloat(l.y))*1000)/1000; l.descr = (l.descr||'') + (/specchiat/.test(l.descr||'') ? '' : ' (Y specchiata)'); } });
  return lav;
}
function angoliJob(t){ // "45-45" -> [135,135], "45-90" -> [135,90], "90-45"->[90,135]
  const [a,b] = String(t).split('-').map(x=>parseInt(x,10));
  return [a===45?135:90, b===45?135:90];
}
function codiceProfilo(serie, r, art, desc){
  const vp = (DATI.varianti_porte||{})[serie];
  if(vp){ return (r.telaio==='ala' && vp.ala[art]) ? vp.ala[art] : art; }
  const v = DATI.varianti[serie];
  if(v && art===v.standard && r.telaio && r.telaio!==v.standard) return r.telaio;   // telaio scelto
  if(art==='B23122C' && r.anta && r.anta!=='B23122C' && !/centrale/.test(desc)) return r.anta; // anta scelta
  if(/T centrale/i.test(desc) && r.traverso) return r.traverso;                      // traverso scelto
  return art;
}
function posizioniDrenaggio(lun, bordo=150, passo=450){
  const utile = lun - 2*bordo;
  if(utile<=0) return [Math.round(lun/2)];
  const n = Math.max(2, Math.ceil(utile/passo)+1);
  const p = utile/(n-1);
  return Array.from({length:n},(_,i)=>Math.round((bordo+i*p)*10)/10);
}


// ---------- grafica: prospetto tipologia ----------

function latiLavorati(serie){
  const dren = !document.querySelector('#c-dren') || document.querySelector('#c-dren').checked;
  const inVista = serieInVista(serie||'C75S');
  return { giu: dren, tutti: dren && inVista };   // giu: drenaggio; tutti: fissaggi FX in vista
}
function bandeTelaio(W, A, t, lati){
  const G = '#CDE8D8', GS = '#0F6B3C';
  let h = '';
  const poly = (pts,lato)=>`<polygon points="${pts}" fill="${G}" stroke="${GS}" stroke-width=".8" data-lato="${lato}" style="cursor:pointer"/>`;
  if(lati.tutti){
    h += poly(`0,0 ${W},0 ${W-t},${t} ${t},${t}`,'su');
    h += poly(`0,0 ${t},${t} ${t},${A-t} 0,${A}`,'sx');
    h += poly(`${W},0 ${W},${A} ${W-t},${A-t} ${W-t},${t}`,'dx');
  }
  if(lati.giu || lati.tutti)
    h += poly(`0,${A} ${W},${A} ${W-t},${A-t} ${t},${A-t}`,'giu');
  return h;
}
function svgProspetto(forma, L, H, scala, mano, serie){
  mano = mano||'dx';
  const s = scala || Math.min(210/L, 210/H);
  const W = L*s, A = H*s, t = Math.max(4, 60*s); // spessore telaio a video
  let inner = '';
  const anta = (x,y,w,h,verso)=>{ // ali di apertura verso la maniglia
    const cerniera = verso==='dx'? x+w : x, man = verso==='dx'? x : x+w;
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#DEEAF2" stroke="#5C6B76" stroke-width="1" data-lato="anta" style="cursor:pointer"/>
      <path d="M ${cerniera} ${y} L ${man} ${y+h/2} L ${cerniera} ${y+h}" fill="none" stroke="#5C6B76" stroke-width="1" stroke-dasharray="4 3" pointer-events="none"/>`;
  };
  const fisso = (x,y,w,h)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#EAF1F5" stroke="#5C6B76" stroke-width="1"/>
      <line x1="${x}" y1="${y}" x2="${x+w}" y2="${y+h}" stroke="#B6C2CB" stroke-width="1"/>
      <line x1="${x+w}" y1="${y}" x2="${x}" y2="${y+h}" stroke="#B6C2CB" stroke-width="1"/>`;
  const iw = W-2*t, ih = A-2*t;
  if(forma==='F') inner = fisso(t,t,iw,ih);
  const vasistas = (x,y,w,h)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#DEEAF2" stroke="#5C6B76" stroke-width="1"/>
      <path d="M ${x} ${y+h} L ${x+w/2} ${y} L ${x+w} ${y+h}" fill="none" stroke="#5C6B76" stroke-width="1" stroke-dasharray="4 3"/>`;
  if(forma==='V') inner = vasistas(t,t,iw,ih);
  if(forma==='1') inner = anta(t,t,iw,ih,mano);
  if(forma==='2'||forma==='P2') inner = anta(t,t,iw/2-1,ih,'dx') + anta(t+iw/2+1,t,iw/2-1,ih,'sx');
  if(forma==='P1') inner = anta(t,t,iw,ih,mano);
  if(forma==='1F') inner = anta(t,t,iw/2-2,ih,mano) +
     `<rect x="${t+iw/2-2}" y="${t}" width="4" height="${ih}" fill="#8A98A3"/>` + fisso(t+iw/2+2,t,iw/2-2,ih);
  const soglia = (forma==='P1'||forma==='P2')? `<rect x="0" y="${A-3}" width="${W}" height="3" fill="#8A98A3"/>` : '';
  return `<svg width="${W.toFixed(0)}" height="${A.toFixed(0)}" viewBox="0 0 ${W} ${A}" role="img">
    <rect x="0" y="0" width="${W}" height="${A}" fill="#C9CFD4" stroke="#1B2328" stroke-width="1.5"/>
    <rect x="${t}" y="${t}" width="${iw}" height="${ih}" fill="#fff"/>
    ${bandeTelaio(W, A, t, latiLavorati(serie))}
    ${inner}${soglia}</svg>`;
}
// ---------- grafica: sezione schematica profilo ----------
function svgSezione(cod){
  if(DATI.sezioni_img && DATI.sezioni_img[cod])
    return `<div><img src="${DATI.sezioni_img[cod]}" alt="Sezione ${cod}" style="max-width:100%;max-height:120px">
      <div class="num" style="font-size:.7rem"><b>${cod}</b></div></div>`;
  const a = DATI.profili_ana[cod]; if(!a) return `<span class="num">${cod}</span>`;
  const dxs = (DATI.dxf_sez||{})[cod];
  if(dxs && dxs.d && dxs.x===0){                      // sezione reale dal DXF di macchina (serie porte)
    const sc = Math.min(110/dxs.w, 110/dxs.h);
    return `<div><svg width="${(dxs.w*sc+4).toFixed(0)}" height="${(dxs.h*sc+4).toFixed(0)}" viewBox="-2 -2 ${(dxs.w+4).toFixed(1)} ${(dxs.h+4).toFixed(1)}">
      <path d="${dxs.d}" fill="none" stroke="#1B2328" stroke-width="${(0.9/sc).toFixed(2)}"/></svg>
      <div class="num" style="font-size:.7rem"><b>${cod}</b> · ${a.w}×${a.h}</div><div style="font-size:.68rem">${a.nome}</div></div>`;
  }
  const s = Math.min(86/a.w, 52/(a.h+(a.z||0)));
  const w=a.w*s, h=a.h*s, z=(a.z||0)*s;
  let corpo='';
  if(a.forma==='Z') corpo = `<rect x="1" y="${1+z}" width="${w}" height="${h}" class="pr"/>
     <rect x="${w-14}" y="1" width="15" height="${z+2}" class="pr"/>`;
  else if(a.forma==='A') corpo = `<rect x="1" y="8" width="${w}" height="${h}" class="pr"/>
     <rect x="6" y="1" width="${w*0.35}" height="9" class="pr"/>`;
  else if(a.forma==='T') corpo = `<rect x="${w/2-7}" y="1" width="14" height="${h}" class="pr"/>
     <rect x="1" y="${h-12}" width="${w}" height="12" class="pr"/>`;
  else corpo = `<rect x="1" y="1" width="${w}" height="${h}" class="pr"/>
     <rect x="1" y="1" width="12" height="${h*0.55}" class="pr"/>`;
  return `<div><svg width="${(w+4).toFixed(0)}" height="${(h+z+6).toFixed(0)}">
    <style>.pr{fill:#E4E8EB;stroke:#1B2328;stroke-width:1.3}</style>${corpo}</svg>
    <div class="num" style="font-size:.7rem"><b>${cod}</b> · ${a.w}×${a.h+(a.z||0)}</div>
    <div style="font-size:.68rem">${a.nome}</div></div>`;
}
// ---------- vetrazione ----------
function tavolaVetro(codProfilo, key){
  if(key && DATI.vetrazione[key]) return DATI.vetrazione[key];
  for(const k of Object.keys(DATI.vetrazione)) if(/^tav[A-Z]/.test(k) && DATI.vetrazione[k].profili.includes(codProfilo)) return DATI.vetrazione[k];
  if(DATI.vetrazione.tav702.profili.includes(codProfilo)) return DATI.vetrazione.tav702;
  return DATI.vetrazione.tav701;
}
function risolviVetro(mm, codProfilo, key){
  const tav = tavolaVetro(codProfilo, key);
  return tav.righe[String(mm)] || null;
}





// ---------- libreria operativa: definizioni delle lavorazioni per serie, con eccezioni per profilo ----------
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
const LAV_DEF_DATI = JSON.parse(JSON.stringify(DATI.lav_def||{}));   // copia immutabile dei DATI di partenza (dati_*.json + dati_serie.js)
function costruisciLavDef(){
  const clone = o=>JSON.parse(JSON.stringify(o)); const out = {};
  Object.keys(DATI.drain||{}).forEach(s=>{ out[s] = {}; Object.entries(DATI.drain[s]).forEach(([tipo,d])=>{
    if(d && typeof d==='object' && d.w) out[s]['dren_'+tipo] = {w:d.w, v1:d.v1, v2:d.v2||'', y:d.y, z:d.z||0, f:d.f, ut:d.ut, descr:d.desc}; }); });
  Object.keys(LAV_DEF_BASE).forEach(s=>{ out[s] = Object.assign(out[s]||{}, clone(LAV_DEF_BASE[s])); });
  const fondi = (dst, src)=>{ Object.entries(src||{}).forEach(([s,def])=>{ dst[s]=dst[s]||{}; Object.entries(def||{}).forEach(([k,v])=>{
    if(k.startsWith('@')){ dst[s][k]=dst[s][k]||{}; Object.entries(v||{}).forEach(([kk,vv])=>{ dst[s][k][kk]=Object.assign({}, dst[s][k][kk]||{}, vv); }); }
    else dst[s][k]=Object.assign({}, dst[s][k]||{}, v); }); }); return dst; };
  fondi(out, LAV_DEF_DATI);
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

// ---------- tarature lavorazioni: regole modificabili nel programma ----------
// DATI.tarature = {id: {serie, prof, f, filtro, dx, dy, dz, f2, nota}}; la copia salvata nel browser (localStorage) ha la precedenza.
let TARATURE = (function(){
  try{ const s = localStorage.getItem('tarature'); if(s) return JSON.parse(s); }catch(e){}
  return Object.assign({}, DATI.tarature||{});
})();
DATI.tarature = TARATURE;
function salvaTarature(){ DATI.tarature = TARATURE; try{ localStorage.setItem('tarature', JSON.stringify(TARATURE)); }catch(e){} }
function descrBase(d){ return String(d||'').replace(/\s*[\[(](DA TARARE|Y specchiata|tar\.[^\])]*)[\])]/g,'').split(' (')[0].trim(); }
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

// ---------- secondo foglio: libreria lavorazioni ----------
let _sezSalvate = null;
function apriLibreria(){
  _sezSalvate = [];
  document.querySelectorAll('section').forEach(s=>{
    if(s.id==='sez-libreria') return;
    _sezSalvate.push([s, s.style.display]);
    s.style.display = 'none';
  });
  const lib = document.querySelector('#sez-libreria');
  if(lib) lib.style.display = 'block';
  disegnaLavDef();
  window.scrollTo(0,0);
}
function chiudiLibreria(){
  const lib = document.querySelector('#sez-libreria');
  if(lib) lib.style.display = 'none';
  (_sezSalvate||[]).forEach(([s,d])=>{ s.style.display = d; });
  _sezSalvate = null;
  window.scrollTo(0,0);
}

// ---------- libreria lavorazioni: schemi ----------
function svgLavSchema(l){
  const W=320, Hh=64, bar={x:8,y:18,w:W-16,h:30};
  let glifi='';
  const glifo=(cx)=>{
    if(l.geo.startsWith('foro')||l.geo==='fori')
      return `<circle cx="${cx}" cy="${bar.y+bar.h/2}" r="4" fill="none" stroke="#BE1622" stroke-width="1.6"/>`;
    if(l.geo.includes('asola'))
      return `<rect x="${cx-9}" y="${bar.y+bar.h/2-3}" width="18" height="6" rx="3" fill="none" stroke="#BE1622" stroke-width="1.6"/>`;
    if(l.geo==='intestatura'||l.geo.includes('sagoma'))
      return `<path d="M ${cx-8} ${bar.y} L ${cx+8} ${bar.y+bar.h} M ${cx-8} ${bar.y+bar.h} L ${cx+8} ${bar.y}" stroke="#BE1622" stroke-width="1.6" fill="none"/>`;
    return `<rect x="${cx-8}" y="${bar.y+6}" width="16" height="${bar.h-12}" fill="none" stroke="#BE1622" stroke-width="1.4" stroke-dasharray="3 2"/>`;
  };
  if(/150 dagli angoli/.test(l.pos)){
    [40, W/2, W-40].forEach(x=>glifi+=glifo(x));
    glifi += `<text x="40" y="${Hh-4}" font-size="9" fill="#5C6B76" text-anchor="middle">150</text>
      <text x="${W/2}" y="${Hh-4}" font-size="9" fill="#5C6B76" text-anchor="middle">passo ≤450</text>
      <text x="${W-40}" y="${Hh-4}" font-size="9" fill="#5C6B76" text-anchor="middle">150</text>`;
  } else if(/350 dal filo/.test(l.pos)){
    glifi += glifo(70) + `<text x="70" y="${Hh-4}" font-size="9" fill="#5C6B76" text-anchor="middle">350 dal filo sup.</text>
      <line x1="${bar.x}" y1="${bar.y-6}" x2="70" y2="${bar.y-6}" stroke="#5C6B76" stroke-width=".8"/>`;
  } else if(/teste|estremita/.test(l.pos)){
    glifi += glifo(bar.x+14) + glifo(bar.x+bar.w-14);
  } else if(/angoli/.test(l.pos)){
    [bar.x+12, bar.x+bar.w-12].forEach(x=>glifi+=glifo(x));
  } else {
    glifi += glifo(W/2);
  }
  return `<svg class="lav-schema" width="100%" viewBox="0 0 ${W} ${Hh}">
    <rect x="${bar.x}" y="${bar.y}" width="${bar.w}" height="${bar.h}" fill="#EDEFF1" stroke="#1B2328"/>
    ${glifi}
    <text x="${W-6}" y="12" font-size="9" fill="#5C6B76" text-anchor="end">${l.dim}</text>
  </svg>`;
}
const NOMI_STATO={tarato:'tarato', da_tarare:'da tarare', indicativo:'indicativo', banco:'banco'};
function disegnaLibreria(filtro){
  const el = $('#out-libreria'); if(!el) return;
  const gruppi = {telaio:'LAVORAZIONI LEGATE AL TELAIO', traverso:'LAVORAZIONI LEGATE A MONTANTI E TRAVERSI', anta:'LAVORAZIONI LEGATE ALLE ANTE'};
  let h='';
  for(const [g, titolo] of Object.entries(gruppi)){
    if(filtro && filtro!=='tutte' && filtro!==g) continue;
    const voci = DATI.libreria.filter(l=>l.el===g);
    h += `<h3 style="font-size:.78rem;letter-spacing:.1em;color:var(--rosso);margin:.9rem 0 .5rem">${titolo}</h3><div class="lav-griglia">`;
    voci.forEach(l=>{
      h += `<div class="lav-card">
        <h4>${l.id} — ${l.nome}<span class="lav-stato st-${l.stato}">${NOMI_STATO[l.stato]}</span></h4>
        ${svgLavSchema(l)}
        <div class="meta"><b>${l.serie}</b> · ${l.prof.join(', ')} · ${l.tipo==='banco'?'operazione di banco':'CNC — '+l.ut}<br>
        Quota: ${l.quota} · Posizione: ${l.pos}<br>Rif. catalogo: tav. ${l.rif}</div></div>`;
    });
    h += '</div>';
  }
  el.innerHTML = h;
}

// ---------- drenaggi da catalogo (tav. 9.11 C75S / 9.12 C82S-CS) ----------
const DRAIN = DATI.drain;
function lavDrenaggio(serie, tipo, x){
  const s = DRAIN[serie]||DRAIN['C75S']; const d = s[tipo] || DRAIN['C75S'][tipo] || {};
  return Object.assign({x}, lavDef('dren_'+tipo, serie), {v3:String(d.prof||2)});
}
function capDrenaggio(serie, accessori, n){
  const d = (DRAIN[serie]||DRAIN['C75S']).telaio;
  if(d.cap) registraAccessorio(accessori, d.cap[0], d.cap[1], n, null);
}


// ---------- FERRAMENTA IN VISTA C75S: regole derivate dal pilota FP Pro (provaxml) ----------
function posFX(L){ // 150 dagli estremi + intermedi, passo max 900
  const span=L-300; const n=Math.max(1, Math.ceil(span/900)); const p=span/n;
  return Array.from({length:n+1},(_,i)=>Math.round((150+i*p)*10)/10);
}
const LAV_FX = [ {w:'#0',v1:'3.75',v2:'',y:62.999,z:-3,f:'4',ut:'12',descr:'FX D7.5 (040NI000)'},
                 {w:'#0',v1:'6.75',v2:'',y:11,z:-20.5,f:'1',ut:'2',descr:'FX lamatura D13.5 (040NI000)'} ];
const LAV_CERN = { d7:{w:'#0',v1:'3.5',v2:'',y:9.5,z:2,f:'2',ut:'17',descr:'Cerniera angolare D7 (S030/E030)'},
                   d3:{w:'#0',v1:'1.5',v2:'',y:9.5,z:2,f:'2',ut:'7',descr:'Cerniera angolare D3 (S030/E030)'} };
function lavFX(L){ const out=[]; posFX(L).forEach(x=>['fx_foro','fx_lamatura'].forEach(k=>out.push(Object.assign({x}, lavDef(k))))); return out; }
function lavDrenTelaioFP(L, serie){ // stesse posizioni dei FX, spostate di 2 mm verso l'interno
  const p=posFX(L); return p.map((x,i)=> lavDrenaggio(serie,'telaio', i===0? x+2 : (i===p.length-1? x-2 : x))); }
function lavCerniere(L, specchio){
  const s=[23.5,93.5], e=[25.5,95.5];           // asimmetria 2 mm come FP Pro
  const a = specchio? e : s, b = specchio? s : e;
  const out=[];
  a.forEach(x=>out.push(Object.assign({x},lavDef('cern_d7'))));
  [37.5,51.5,65.5,79.5].forEach(x=>out.push(Object.assign({x:x+(specchio?2:0)},lavDef('cern_d3'))));
  b.forEach(x=>out.push(Object.assign({x:Math.round((L-x)*10)/10},lavDef('cern_d7'))));
  [37.5,51.5,65.5,79.5].forEach(x=>out.push(Object.assign({x:Math.round((L-x-(specchio?0:2))*10)/10},lavDef('cern_d3'))));
  return out;
}


// ---------- MAICO Multi-Matic (doc. 750135): cremonese e altezza maniglia per HBB ----------
function cremoneseMaico(HBB){
  const t=[[430,125],[660,190],[840,300],[1090,400],[1340,500],[1590,500],[1700,500],[1950,1050],[2200,1050],[2450,1050]];
  for(const [gr,hm] of t) if(HBB<=gr) return {gr,hm};
  return {gr:2450,hm:1050};
}
function lavMartellina(hAnta, hm){ // X = altezza maniglia + 18 dal fondo anta (verificato sul pilota)
  const xm = (hm || hmStandard(hAnta)) + 18;
  return [
    Object.assign({x:xm-21.5}, lavDef('mart_d10')),
    Object.assign({x:xm+21.5}, lavDef('mart_d10')),
    Object.assign({x:xm},      lavDef('mart_d12')),
    Object.assign({x:xm},      lavDef('mart_scasso'))
  ];
}


// ---------- SCONTRI MAICO (doc. 750135 p.27) calibrati su produzione: quota + 27, HBB = anta - 20 ----------
const HM_AMMESSE = DATI.maico.hm_ammesse;
const SCONTRI_A = DATI.maico.scontri_A;
function scontriPer(gr, hm){ return SCONTRI_A[`${gr}/${hm}`] || SCONTRI_A[String(gr)] || []; }
function hmStandard(hAnta){ return cremoneseMaico(hAnta-20).hm; }
function hmAmmesse(hAnta){ return HM_AMMESSE[cremoneseMaico(hAnta-20).gr] || []; }
const OFF_SC = 27, CORNER_SC = 142;
const SC_PAIR16 = (x)=>[Object.assign({x:x-8}, lavDef('sc_alzaanta')), Object.assign({x:x+8}, lavDef('sc_alzaanta'))];
const SC_SINGLE = (x)=>Object.assign({x}, lavDef('sc_nottolino'));
const SC_PAIR54 = (x)=>[Object.assign({x:x-27}, lavDef('sc_angolo')), Object.assign({x:x+27}, lavDef('sc_angolo'))];
function lavScontriMontanteManiglia(Ltel, hAnta, hm){
  const hbb = hAnta-20; const gr = cremoneseMaico(hbb).gr; const A = scontriPer(gr, hm||cremoneseMaico(hbb).hm);
  const out=[]; A.forEach((a,i)=>{                                    // dal filo superiore
    if(i===0) out.push(...SC_PAIR16(Math.round((Ltel-27.5-a)*10)/10));
    else out.push(SC_SINGLE(Math.round((Ltel-26.5-a)*10)/10)); });
  return out;
}
function lavScontriMontanteCerniere(Ltel, hAnta){
  const out=[SC_SINGLE(Math.round((Ltel-CORNER_SC)*10)/10)];       // scontro d'angolo in alto
  if(hAnta-20 > 800) out.push(SC_SINGLE(Math.round((Ltel/2-0.5)*10)/10)); // chiusura centrale lato cerniere a meta'
  return out;
}
function lavScontriTraverso(Ltel, inferiore, manoDx, lAnta){
  // scontro d'angolo (coppia a 54): in basso lato maniglia, in alto lato cerniere
  const xc = 143.5;
  const dalSx = inferiore ? manoDx : !manoDx;
  const out = SC_PAIR54(dalSx ? xc : Math.round((Ltel-xc+1.5)*10)/10);
  const lbb = (lAnta||0)-20;
  if(inferiore && lbb>800){                       // chiusura centrale orizzontale inferiore
    const C = lbb<=1280 ? 565 : 800;
    out.push(SC_SINGLE(Math.round((C+27)*10)/10));
  }
  return out;
}


function aggiornaHM(forza){
  const tP = DATI.tipologie.find(x=>x.id===$('#r-tip').value);
  if(tP && tP.porta){                                            // porte: altezza maniglia AM dal filo inferiore anta (manuale AluK: 1050)
    if(forza || !$('#r-hm').value || parseFloat($('#r-hm').value)<600) $('#r-hm').value = 1050;
    $('#info-hm').innerHTML = `<div style="font-size:.72rem;line-height:1.5">AM = asse maniglia/serratura dal filo inferiore dell'anta.<br>Standard AluK: <b class="num">1050</b> (manuale lavorazioni 10.71-10.84)</div>`;
    return;
  }
  const H = parseFloat($('#r-h').value)||1400, L = parseFloat($('#r-l').value)||1200;
  const hAnta = (tP && tP.anta_h) ? (valuta(tP.anta_h, L, H, {h2: parseFloat($('#r-h2').value)||0}) || H-43) : H-43;
  const std = hmStandard(hAnta), amm = hmAmmesse(hAnta), gr = cremoneseMaico(hAnta-20).gr;
  if(forza || !$('#r-hm').value) $('#r-hm').value = std;
  const hm = parseFloat($('#r-hm').value);
  const ok = amm.includes(hm);
  $('#info-hm').innerHTML = `<div style="font-size:.72rem;line-height:1.5">Anta ${hAnta} → HBB ${hAnta-20} → cremonese <b>${gr}</b><br>
    Standard Maico: <b class="num">${amm.join(' / ')}</b><br>
    ${ok ? '<span class="ok">altezza ammessa</span>' : '<span class="attenzione">fuori standard: richiede cremonese variabile</span>'}</div>`;
}


// ---------- scontro forbice sul traverso superiore (fasce dal file Maico aziendale) ----------
// quota provata in produzione: forbice 1300 (FFB 1051-1650) -> 506 + 28.5
// altre fasce: quote DA CONFERMARE alla prima produzione con quelle larghezze
const FORBICE_QUOTA = DATI.maico.forbice_quota;
function forbicePer(lAnta){
  const ffb = lAnta - 20;
  if(ffb<=400) return 400; if(ffb<=600) return 600; if(ffb<=800) return 800;
  if(ffb<=1050) return 1050; return 1300;   // fascia aziendale estesa a 1650
}
function lavScontroForbice(Ltel, lAnta, manoDx){
  const q = FORBICE_QUOTA[forbicePer(lAnta)];
  if(q==null) return [];
  const x = manoDx ? Math.round((q+28.5)*10)/10 : Math.round((Ltel-q-28.5)*10)/10; // dal lato cerniere
  return [SC_SINGLE(x)];
}

// ---------- tipologia composta: editor matrice ----------
const matC = {cols:2, rows:1, ws:[], hs:[], celle:[], giunte:[], giunteO:[]};
const CICLO = ['F','ADX','ASX','VAS','2A'];
const CICLO_PF = ['F','ADX','ASX','VAS','2A','PFDX','PFSX','PF2'];
const NOMI_CELLA = {F:'FISSO', ADX:'ANTA DX', ASX:'ANTA SX', VAS:'VASISTAS', '2A':'2 ANTE',
                    PFDX:'P.FIN. DX', PFSX:'P.FIN. SX', PF2:'P.FIN. 2A'};
const isPF = v => v && v.startsWith('PF');
function isComposta(){ const t = DATI.tipologie.find(x=>x.id===$('#r-tip').value); return !!(t && t.forma==='M'); }
function compostaSenzaPF(){ const t = DATI.tipologie.find(x=>x.id===$('#r-tip').value); return !!(t && t.composta_cor80); }   // COR80: niente celle portafinestra
function ripartisci(tot, n){
  const q = Math.floor(tot/n*10)/10, arr = Array(n).fill(q);
  arr[n-1] = Math.round((tot - q*(n-1))*10)/10; return arr;
}
function rigeneraMatrice(daCampi){
  matC.cols = Math.max(1, Math.min(5, parseInt($('#m-cols').value,10)||1));
  matC.rows = Math.max(1, Math.min(5, parseInt($('#m-rows').value,10)||1));
  const L = parseFloat($('#r-l').value)||1200, H = parseFloat($('#r-h').value)||1400;
  if(daCampi){
    const ws = $('#m-ws').value.split(/[;,\s]+/).map(Number).filter(x=>x>0);
    const hs = $('#m-hs').value.split(/[;,\s]+/).map(Number).filter(x=>x>0);
    matC.ws = ws.length===matC.cols ? ws : ripartisci(L, matC.cols);
    matC.hs = hs.length===matC.rows ? hs : ripartisci(H, matC.rows);
  } else {
    matC.ws = ripartisci(L, matC.cols);
    matC.hs = ripartisci(H, matC.rows);
  }
  $('#m-ws').value = matC.ws.join(' ; ');
  $('#m-hs').value = matC.hs.join(' ; ');
  const gdef = $('#m-giunta').value==='raddoppio' ? 'R' : 'T';
  const vg = matC.giunte;
  matC.giunte = Array.from({length:Math.max(0,matC.cols-1)},(_,j)=> vg[j]||gdef);
  const vgo = matC.giunteO||[];
  matC.giunteO = Array.from({length:Math.max(0,matC.rows-1)},(_,j)=> vgo[j]||gdef);
  // celle: conservo quelle esistenti dove possibile
  const vecchie = matC.celle;
  matC.celle = Array.from({length:matC.rows},(_,r)=>
    Array.from({length:matC.cols},(_,c)=>{
      let v = (vecchie[r]&&vecchie[r][c])||'F';
      if(isPF(v) && (r!==matC.rows-1 || compostaSenzaPF())) v='F';    // portefinestre solo nella riga inferiore (mai in COR80)
      return v; }));
  disegnaGriglia(); aggiornaAnteprima();
}

function miniSezione(prof, titolo){
  const dx = (DATI.dxf_sez||{})[prof];
  if(!dx) return '';
  const S=120, mg=8, a=S-2*mg;
  const sc = Math.min(a/dx.w, a/dx.h);
  const bw=dx.w*sc, bh=dx.h*sc, bx=mg+(a-bw)/2, by=mg+(a-bh)/2;
  return `<div style="text-align:center">
    <svg width="${S}" height="${S}" viewBox="0 0 ${S} ${S}" style="border:1px solid var(--linea); background:#fff">
      <g transform="translate(${bx},${by+bh}) scale(${sc},${-sc}) translate(${-dx.x},${-dx.y})">
        <path d="${dx.d}" fill="none" stroke="#5C6B76" stroke-width="${(0.9/sc).toFixed(2)}"/></g>
    </svg>
    <div style="font-size:.68rem"><b class="num">${prof}</b> — ${titolo}</div>
  </div>`;
}
function disegnaProfiliT(){
  const box = $('#info-profiliT'); if(!box) return;
  const tC = DATI.tipologie.find(x=>x.id===$('#r-tip').value);
  if(tC && tC.composta_cor80){ box.innerHTML = miniSezione(tC.composta_cor80.trav,'montanti e traversi T') + miniSezione(tC.composta_cor80.comp,'complemento telaio (celle apribili)'); return; }
  const c82 = ($('#r-serie').value||'').startsWith('C82');
  box.innerHTML = c82
    ? miniSezione('B23610C','montanti e traversi T')
    : miniSezione('B23609C','montante T') + miniSezione('B23608C','traverso T');
}
function ciclaCella(r, c){
  const lista = (r===matC.rows-1 && !compostaSenzaPF()) ? CICLO_PF : CICLO;
  matC.celle[r][c] = lista[(lista.indexOf(matC.celle[r][c])+1)%lista.length];
  disegnaGriglia(); aggiornaAnteprima();
}
function commutaGiunto(j){
  matC.giunte[j] = matC.giunte[j]==='T' ? 'R' : 'T';
  disegnaGriglia(); aggiornaAnteprima();
}
function commutaGiuntoO(j){
  matC.giunteO[j] = matC.giunteO[j]==='T' ? 'R' : 'T';
  disegnaGriglia(); aggiornaAnteprima();
}
function disegnaGriglia(){
  const g = $('#m-griglia'); if(g) g.innerHTML = '';
}
// ---------- prospetto della matrice ----------
function svgProspettoMatrice(ws, hs, celle, scala, giunte, serie, interattivo, giunteO){
  if(!Array.isArray(giunte)) giunte = Array.from({length:Math.max(0,ws.length-1)},()=> giunte==='raddoppio'?'R':'T');
  if(!Array.isArray(giunteO)) giunteO = Array.from({length:Math.max(0,hs.length-1)},()=> 'T');
  const L = ws.reduce((a,b)=>a+b,0), H = hs.reduce((a,b)=>a+b,0);
  const s = scala || Math.min(210/L, 210/H);
  const W=L*s, A=H*s, t=Math.max(3,50*s), m=Math.max(2,60*s/2);
  let inner='';
  let y=0;
  for(let r=0;r<hs.length;r++){
    let x=0;
    for(let c=0;c<ws.length;c++){
      const x0=x*s+(c===0?t:m/2), y0=y*s+(r===0?t:m/2);
      const w=ws[c]*s-(c===0?t:m/2)-(c===ws.length-1?t:m/2);
      const h=hs[r]*s-(r===0?t:m/2)-(r===hs.length-1?t:m/2);
      const v=celle[r][c];
      if(v==='F') inner += `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="#EAF1F5" stroke="#5C6B76"/>
        <line x1="${x0}" y1="${y0}" x2="${x0+w}" y2="${y0+h}" stroke="#B6C2CB"/>
        <line x1="${x0+w}" y1="${y0}" x2="${x0}" y2="${y0+h}" stroke="#B6C2CB"/>`;
      else if(v==='2A') inner += `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="#DEEAF2" stroke="#5C6B76"/>
        <path d="M ${x0+w/2} ${y0} L ${x0} ${y0+h/2} L ${x0+w/2} ${y0+h} M ${x0+w/2} ${y0} L ${x0+w} ${y0+h/2} L ${x0+w/2} ${y0+h}" fill="none" stroke="#5C6B76" stroke-dasharray="4 3"/>
        <line x1="${x0+w/2}" y1="${y0}" x2="${x0+w/2}" y2="${y0+h}" stroke="#8A98A3" stroke-width="2"/>`;
      else if(v==='VAS') inner += `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="#DEEAF2" stroke="#5C6B76"/>
        <path d="M ${x0} ${y0+h} L ${x0+w/2} ${y0} L ${x0+w} ${y0+h}" fill="none" stroke="#5C6B76" stroke-width="1" stroke-dasharray="4 3"/>`;
      else if(v==='PF2') inner += `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="#DEEAF2" stroke="#5C6B76"/>
        <line x1="${x0+w/2}" y1="${y0}" x2="${x0+w/2}" y2="${y0+h}" stroke="#1B2328" stroke-width="1.5"/>
        <path d="M ${x0} ${y0} L ${x0+w/2} ${y0+h/2} L ${x0} ${y0+h}" fill="none" stroke="#5C6B76" stroke-width="1" stroke-dasharray="4 3"/>
        <path d="M ${x0+w} ${y0} L ${x0+w/2} ${y0+h/2} L ${x0+w} ${y0+h}" fill="none" stroke="#5C6B76" stroke-width="1" stroke-dasharray="4 3"/>
        <rect x="${x0}" y="${y0+h-3}" width="${w}" height="3" fill="#8A98A3"/>`;
      else { const pf = isPF(v);
        const va = v==='PFDX'?'ADX':(v==='PFSX'?'ASX':v);
        const cern = va==='ADX'? x0+w : x0, man = va==='ADX'? x0 : x0+w;
        if(pf) inner += `<rect x="${x0}" y="${y0+h-3}" width="${w}" height="3" fill="#8A98A3"/>`;
        inner += `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="#DEEAF2" stroke="#5C6B76"/>
        <path d="M ${cern} ${y0} L ${man} ${y0+h/2} L ${cern} ${y0+h}" fill="none" stroke="#5C6B76" stroke-dasharray="4 3"/>`; }
      if(interattivo){
        inner += `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="rgba(0,0,0,0)" data-cella="${r},${c}" style="cursor:pointer"/>
        <text x="${x0+3}" y="${y0+11}" font-size="9" font-weight="700" fill="#1B2328" pointer-events="none">${NOMI_CELLA[v]||v}</text>`;
      }
      x += ws[c];
    }
    y += hs[r];
  }
  // linee traversi/montanti
  let seg='';
  let hitGiunti='';
  let ax=0; for(let c=0;c<ws.length-1;c++){ ax+=ws[c];
    if(interattivo) hitGiunti += `<rect x="${ax*s-8}" y="0" width="16" height="${A}" fill="rgba(0,0,0,0)" data-giunto="${c}" style="cursor:pointer"/>`;
    if(giunte[c]==='R')
      seg += `<rect x="${ax*s-t-1}" y="0" width="${t}" height="${A}" fill="#C9CFD4" stroke="#1B2328"/>
              <rect x="${ax*s+1}" y="0" width="${t}" height="${A}" fill="#C9CFD4" stroke="#1B2328"/>`;
    else seg += `<rect x="${ax*s-m/2}" y="${t}" width="${m}" height="${A-2*t}" fill="#8A98A3"/>`; }
  let ay=0; for(let r=0;r<hs.length-1;r++){ ay+=hs[r];
    if(interattivo) hitGiunti += `<rect x="0" y="${ay*s-8}" width="${W}" height="16" fill="rgba(0,0,0,0)" data-giuntoo="${r}" style="cursor:pointer"/>`;
    if(giunteO[r]==='R')
      seg += `<rect x="0" y="${ay*s-t-1}" width="${W}" height="${t}" fill="#C9CFD4" stroke="#1B2328"/>
              <rect x="0" y="${ay*s+1}" width="${W}" height="${t}" fill="#C9CFD4" stroke="#1B2328"/>`;
    else seg += `<rect x="${t}" y="${ay*s-m/2}" width="${W-2*t}" height="${m}" fill="#8A98A3"/>`; }
  return `<svg width="${W.toFixed(0)}" height="${A.toFixed(0)}" viewBox="0 0 ${W} ${A}">
    <rect width="${W}" height="${A}" fill="#C9CFD4" stroke="#1B2328" stroke-width="1.5"/>
    <rect x="${t}" y="${t}" width="${W-2*t}" height="${A-2*t}" fill="#fff"/>${seg}${bandeTelaio(W, A, t, latiLavorati(serie))}
    ${inner}${hitGiunti}</svg>`;
}
// ---------- motore di composizione (C75S e C82S) ----------
// detrazioni per lato derivate dal catalogo: [lato telaio, lato traverso]
const DED = DATI.ded;
function apribile(v){ return v==='ADX'||v==='ASX'||v==='2A'||v==='VAS'||isPF(v); }
function violaVincoloC82(celle, giunte, giunteO){
  if(!Array.isArray(giunte)) giunte = Array.from({length:99},()=> giunte==='raddoppio'?'R':'T');
  for(let r=0;r<celle.length;r++) for(let c=0;c<celle[r].length;c++){
    if(!apribile(celle[r][c])) continue;
    if(giunte[c]!=='R' && c+1<celle[r].length && apribile(celle[r][c+1])) return `celle ${r+1}.${c+1} e ${r+1}.${c+2}`;
    if(r+1<celle.length && (!giunteO || giunteO[r]!=='R') && apribile(celle[r+1][c])) return `celle ${r+1}.${c+1} e ${r+2}.${c+1}`;
  }
  return null;
}
function accessorioBlocal(r, t, accessori){
  if(r.blocal && ['1','1F','2','P1','P2'].includes(t.forma)){
    registraAccessorio(accessori,'1490 Savio','Serratura BLOCAL (opzione) — lavorazioni da tarare',1,null);
    registraAccessorio(accessori,'Incontro 1490','Incontro serratura BLOCAL',1,null);
  }
}
function componiMatrice(r, t, agg){
  let giunteO = r.mat.giunteO;
  if(!Array.isArray(giunteO)) giunteO = Array.from({length:Math.max(0,r.mat.hs.length-1)},()=> 'T');
  // gruppi di righe: telai sovrapposti dove il giunto orizzontale e' R
  const gr=[]; let i0=0;
  for(let i=0;i<r.mat.hs.length;i++){
    if(i===r.mat.hs.length-1 || giunteO[i]==='R'){ gr.push([i0,i]); i0=i+1; }
  }
  if(gr.length>1){
    gr.forEach(([a,b],g)=>{
      const sub = {telaio:r.telaio, anta:r.anta, vetro:r.vetro, battuta:r.battuta, mano:r.mano, hm:r.hm, blocal:r.blocal,
        mat:{ws:r.mat.ws, hs:r.mat.hs.slice(a,b+1), celle:r.mat.celle.slice(a,b+1),
             giunte:r.mat.giunte, giunteO:[]}};
      componiMatrice(sub, t, Object.assign({}, agg, {unita: agg.unita+'-O'+(g+1)}));
    });
    return;
  }
  let giunte = r.mat.giunte;
  if(!Array.isArray(giunte)) giunte = Array.from({length:Math.max(0,r.mat.ws.length-1)},
    ()=> r.mat.giunta==='raddoppio'?'R':'T');
  // gruppi di colonne uniti da montante T, separati dove ci sono telai affiancati
  const gruppi=[]; let inizio=0;
  for(let c=0;c<r.mat.ws.length;c++){
    if(c===r.mat.ws.length-1 || giunte[c]==='R'){ gruppi.push([inizio,c]); inizio=c+1; }
  }
  if(gruppi.length===1) return componiMatriceBase(r, t, agg);
  gruppi.forEach(([a,b],g)=>{
    const sub = {telaio:r.telaio, anta:r.anta, vetro:r.vetro,
      mat:{ws:r.mat.ws.slice(a,b+1), hs:r.mat.hs,
           celle:r.mat.celle.map(riga=>riga.slice(a,b+1)), giunte:[]}};
    componiMatriceBase(sub, t, Object.assign({}, agg, {unita: agg.unita+'-U'+(g+1)}));
  });
}
if(typeof componiMatriceCOR80!=='function'){ window.componiMatriceCOR80 = function(){ return; }; }
function componiMatriceBase(r, t, agg){
  if(t.composta_cor80) return componiMatriceCOR80(r, t, agg);
  const includiFV_m = $('#c-fermavetro-si').value !== 'no';
  const {pezzi, accessori, guarnizioni, vetri, erroriFormule, conDren, unita} = agg;
  const ws=r.mat.ws, hs=r.mat.hs, celle=r.mat.celle;
  const D = DED[t.serie] || DED['C75S'];
  const telaio = r.telaio||'B23008C', anta = 'B23122C', trav = D.trav;
  LAV_CTX.serie = t.serie; LAV_CTX.art = telaio;
  const risA = risolviVetro(r.vetro, anta), risT = risolviVetro(r.vetro, telaio);
  const fvA = risA? risA.fv : null, fvT = risT? risT.fv : null;
  const L = ws.reduce((a,b)=>a+b,0), H = hs.reduce((a,b)=>a+b,0);
  const spingi=(art,desc,sc,mm,tag,lav)=>{ if(mm==null||mm<=0){erroriFormule.push(`${t.cod}: ${desc} nullo`);return;}
    const [al,ar]=angoliJob(tag);
    pezzi.push({art,desc,mm:Math.round(mm*10)/10,al,ar,unita,tip:t.nome,tcod:t.cod,
      cod:`${t.cod}-${sc}`,serie:t.serie,lav:applicaTarature(t.serie, art, lav||[])}); };
  // perimetro (con soglia ribassata se la riga inferiore è a portefinestre)
  const rigaInf = celle[hs.length-1] || [];
  const conPF = rigaInf.some(v=>isPF(v));
  const tuttaPF = conPF && rigaInf.every(v=>isPF(v));
  const sogliaArt = t.serie==='C75S' ? 'B23401' : 'B23402';
  [1,2].forEach(k=>{
    if(k===1 && tuttaPF){                                     // sotto: soglia al posto dello stipite
      spingi(sogliaArt,'Soglia ribassata',`SOGL01`,L-46,'90-90');
      registraAccessorio(accessori,'Kit soglia','Fissaggi/tappi soglia (macro 010NOR/050ALU)',1,null);
      return;
    }
    let lav=[];
    if(conDren&&k===1){ const pos=posizioniDrenaggio(L);
      LAV_CTX.art = telaio; lav=pos.map(x=>lavDrenaggio(t.serie,'telaio',x)); capDrenaggio(t.serie,accessori,pos.length); }
    spingi(telaio,'Traverso stipite',`TELL0${k}`,L,'45-45',lav); });
  [1,2].forEach(k=>spingi(telaio,'Montante stipite',`TELH0${k}`,H, tuttaPF?(k===1?'45-90':'90-45'):'45-45'));
  if(conPF && !tuttaPF){                                      // soglia parziale sotto le sole celle PF
    let c0=null;
    for(let c=0;c<=rigaInf.length;c++){
      const pf = c<rigaInf.length && isPF(rigaInf[c]);
      if(pf && c0===null) c0=c;
      if(!pf && c0!==null){
        const span = ws.slice(c0,c).reduce((a,b)=>a+b,0);
        spingi(sogliaArt,'Soglia ribassata parziale — DA VERIFICARE',`SOGL${c0+1}`,span,'90-90');
        c0=null; }
    }
  }
  registraAccessorio(accessori,'V40022/V40037','Squadretta est. stipite',4,null);
  registraAccessorio(accessori,'V43017','Squadretta int. stipite',4,null);
  accessorioBlocal(r, t, accessori);
  registraAccessorio(accessori,'V46028','Squadretta di all. est. stipite',4,null);
  // montanti verticali interni (passanti)
  for(let c=0;c<ws.length-1;c++) spingi(D.mont||trav,'Montante T interno',`TRVV0${c+1}`,H-2*D.trvV_tel,'90-90');
  // traversi orizzontali interni (interrotti tra i montanti)
  for(let rr=0;rr<hs.length-1;rr++) for(let c=0;c<ws.length;c++){
    const dS = c===0? D.trvO[0]:D.trvO[1], dD = c===ws.length-1? D.trvO[0]:D.trvO[1];
    const lunT = ws[c]-dS-dD;
    let lavT=[];
    if(conDren){ const pos=posizioniDrenaggio(lunT);
      const tipoT = (DRAIN[t.serie]||{}).traversoT ? 'traversoT' : 'telaio';
      LAV_CTX.art = trav; lavT=pos.map(x=>lavDrenaggio(t.serie,tipoT,x)); capDrenaggio(t.serie,accessori,pos.length); }
    spingi(trav,'Traverso T interno',`TRVO${rr+1}${c+1}`,lunT,'90-90',lavT); }
  // celle
  for(let rr=0;rr<hs.length;rr++) for(let c=0;c<ws.length;c++){
    const v=celle[rr][c], id=`C${rr+1}${c+1}`;
    const bordi={sx:c===0, dx:c===ws.length-1, su:rr===0, giu:rr===hs.length-1}; // true = telaio
    const d=(tel)=>tel?0:1;
    const spanW=ws[c], spanH=hs[rr];
    if(v==='F'){
      const fo=spanW-D.fermFisO[d(bordi.sx)]-D.fermFisO[d(bordi.dx)];
      const fv=spanH-D.fermFisV[d(bordi.su)]-D.fermFisV[d(bordi.giu)];
      if(fvT){ spingi(fvT,'Fermavetro orizz. fisso',`${id}-FVFL`,fo,'90-90');
               spingi(fvT,'Fermavetro orizz. fisso',`${id}-FVFL`,fo,'90-90');
               spingi(fvT,'Fermavetro vert. fisso',`${id}-FVFH`,fv,'90-90');
               spingi(fvT,'Fermavetro vert. fisso',`${id}-FVFH`,fv,'90-90'); }
      if(D.b23906){
        const ao=spanW-D.aggO[d(bordi.sx)]-D.aggO[d(bordi.dx)];
        const av=spanH-D.aggV[d(bordi.su)]-D.aggV[d(bordi.giu)];
        spingi('B23906','Compensatore fisso orizz.',`${id}-AGGL`,ao,'90-90');
        spingi('B23906','Compensatore fisso orizz.',`${id}-AGGL`,ao,'90-90');
        spingi('B23906','Compensatore fisso vert. (DA VALIDARE)',`${id}-AGGH`,av,'90-90');
        spingi('B23906','Compensatore fisso vert. (DA VALIDARE)',`${id}-AGGH`,av,'90-90');
      }
      vetri.push({q:1,l:Math.round(spanW-D.vetFis[d(bordi.sx)]-D.vetFis[d(bordi.dx)]),
                  h:Math.round(spanH-D.vetFis[d(bordi.su)]-D.vetFis[d(bordi.giu)]),
                  sp:r.vetro,tip:`${t.nome} ${id} fisso`,unita});
      const per=2*spanW+2*spanH;
      if(risT) guarnizioni[risT.g+'|Interna vetro (vetro '+r.vetro+' mm)']=(guarnizioni[risT.g+'|Interna vetro (vetro '+r.vetro+' mm)']||0)+per;
    } else {
      const cellaPF = isPF(v);
      const bordoSoglia = cellaPF && bordi.giu;
      const aw=spanW-D.anta[d(bordi.sx)]-D.anta[d(bordi.dx)];
      const ah=spanH-D.anta[d(bordi.su)]-(bordoSoglia? 8.5 : D.anta[d(bordi.giu)]);
      const goccDed = t.serie==='C75S' ? 69 : 141;
      LAV_CTX.art = anta;
      if(v==='2A' || v==='PF2'){
        const pzS=spanW/2-D.anta[d(bordi.sx)]+12, pzD=spanW/2-D.anta[d(bordi.dx)]+12;
        spingi(anta,'Traverso battente sx',`${id}-ANTL`,pzS,'45-45',
          agg.conAnte? posizioniDrenaggio(pzS).map(x=>lavDrenaggio(t.serie,'antaTrav',x)) : []);
        spingi(anta,'Traverso battente sx',`${id}-ANTL`,pzS,'45-45');
        spingi(anta,'Traverso battente dx',`${id}-ANTL`,pzD,'45-45',
          agg.conAnte? posizioniDrenaggio(pzD).map(x=>lavDrenaggio(t.serie,'antaTrav',x)) : []);
        spingi(anta,'Traverso battente dx',`${id}-ANTL`,pzD,'45-45');
        for(let k=0;k<3;k++) spingi(anta,'Montante battente',`${id}-ANTH`,ah,'45-45',
          agg.conAnte? [lavDrenaggio(t.serie,'antaMont',Math.round((ah-350)*10)/10)] : []);
        spingi('B23100C','Montante battente centrale (stulp)',`${id}-ANTC`,ah-32,'45-45');
        spingi('N23637C','Aggiuntivo per B23100C',`${id}-AGGC`,ah-63,'90-90');
        if(fvA){ const eS=pzS-D.fermBattO[d(bordi.sx)]-49, eD=pzD-49-D.fermBattO[d(bordi.dx)];
                 [eS,eS,eD,eD].forEach(p=>spingi(fvA,'Fermavetro orizz. battente',`${id}-FVBL`,p,'90-90'));
                 const ev=ah-D.fermBattV[d(bordi.su)]-D.fermBattV[d(bordi.giu)]-((bordoSoglia&&t.serie==='C75S')?0.5:0);
                 for(let k=0;k<4;k++) spingi(fvA,'Fermavetro vert. battente',`${id}-FVBH`,ev,'90-90'); }
        vetri.push({q:1,l:Math.round(pzS-106),h:Math.round(ah-106),sp:r.vetro,tip:`${t.nome} ${id} anta sx`,unita});
        vetri.push({q:1,l:Math.round(pzD-106),h:Math.round(ah-106),sp:r.vetro,tip:`${t.nome} ${id} anta dx`,unita});
        registraAccessorio(accessori,'V40014','Squadretta int. battente',8,null);
        registraAccessorio(accessori,'V40022/V40037','Squadretta est. battente',8,null);
        registraAccessorio(accessori,'V46005','Squadretta di all. est. battente',8,null);
        registraAccessorio(accessori,'V52014','Tappi interni per due ante T-Z',1,null);
        registraAccessorio(accessori,'V52055','Tappi esterni due ante',1,null);
        if(cellaPF){ spingi('K50','Gocciolatoio',`${id}-GOCC`,pzS-goccDed,'90-90');
                     spingi('K50','Gocciolatoio',`${id}-GOCC`,pzD-goccDed,'90-90'); }
      } else {
        spingi(anta,'Traverso battente',`${id}-ANTL`,aw,'45-45',
          agg.conAnte? posizioniDrenaggio(aw).map(x=>lavDrenaggio(t.serie,'antaTrav',x)) : []);
        spingi(anta,'Traverso battente',`${id}-ANTL`,aw,'45-45');
        [1,2].forEach(()=>spingi(anta,'Montante battente',`${id}-ANTH`,ah,'45-45',
          agg.conAnte? [lavDrenaggio(t.serie,'antaMont',Math.round((ah-350)*10)/10)] : []));
        if(fvA && includiFV_m){ const eo=aw-D.fermBattO[d(bordi.sx)]-D.fermBattO[d(bordi.dx)];
                 const ev=ah-D.fermBattV[d(bordi.su)]-D.fermBattV[d(bordi.giu)]-((bordoSoglia&&t.serie==='C75S')?0.5:0);
                 spingi(fvA,'Fermavetro orizz. battente',`${id}-FVBL`,eo,'90-90');
                 spingi(fvA,'Fermavetro orizz. battente',`${id}-FVBL`,eo,'90-90');
                 spingi(fvA,'Fermavetro vert. battente',`${id}-FVBH`,ev,'90-90');
                 spingi(fvA,'Fermavetro vert. battente',`${id}-FVBH`,ev,'90-90'); }
        vetri.push({q:1,l:Math.round(aw-106),h:Math.round(ah-106),sp:r.vetro,tip:`${t.nome} ${id} ${NOMI_CELLA[v]}`,unita});
        registraAccessorio(accessori,'V40014','Squadretta int. battente',4,null);
        registraAccessorio(accessori,'V40022/V40037','Squadretta est. battente',4,null);
        registraAccessorio(accessori,'V46005','Squadretta di all. est. battente',4,null);
        if(cellaPF) spingi('K50','Gocciolatoio',`${id}-GOCC`,aw-goccDed,'90-90');
      }
      const per=2*spanW+2*spanH;
      if(risA) guarnizioni[risA.g+'|Interna vetro (vetro '+r.vetro+' mm)']=(guarnizioni[risA.g+'|Interna vetro (vetro '+r.vetro+' mm)']||0)+per;
      guarnizioni['V09049|Elemento isolante']=(guarnizioni['V09049|Elemento isolante']||0)+per;
    }
    registraAccessorio(accessori,'V62008','Supporto vetro',null,null);
  }
  if(r.blocal && celle.flat().some(v=> isPF(v) || v==='ADX' || v==='ASX' || v==='2A')){
    registraAccessorio(accessori,'1490 Savio','Serratura BLOCAL (opzione) — lavorazioni da tarare',1,null);
    registraAccessorio(accessori,'Incontro 1490','Incontro serratura BLOCAL',1,null);
  }
}

// ---------- selettori tipologia ----------
function iniziaSelettori(){
  const serie = [...new Set(DATI.tipologie.map(t=>t.serie))];
  $('#r-serie').innerHTML = serie.map(s=>`<option value="${s}">${(SERIE_INFO[s]&&SERIE_INFO[s].nome)||s}</option>`).join('');
  $('#r-h2').addEventListener('input', aggiornaAnteprima);
  aggiornaTipologie();
  $('#r-serie').addEventListener('change', aggiornaTipologie);
  $('#r-tip').addEventListener('change', ()=>{mostraAvvisoTip(); if(isPorta($('#r-serie').value) || tipProfili($('#r-serie').value)) aggiornaSelettoriProfili(); else aggiornaSezioni();});
  ['#r-telaio','#r-anta','#r-traverso','#r-vetro','#r-base','#r-battuta','#r-mano'].forEach(id=>
    $(id).addEventListener('change', aggiornaSezioni));
  ['#r-l','#r-h','#r-cod'].forEach(id=>$(id).addEventListener('input', ()=>{
    if(isComposta()) rigeneraMatrice(false); else aggiornaAnteprima(); }));
  ['#m-cols','#m-rows'].forEach(id=>$(id).addEventListener('input', ()=>rigeneraMatrice(false)));
  $('#r-hm').addEventListener('input', ()=>aggiornaHM(false));
  $('#r-h').addEventListener('input', ()=>{ if($('#box-hm').style.display==='block') aggiornaHM(true); });
  $('#m-giunta').addEventListener('change', ()=>{
    const g = $('#m-giunta').value==='raddoppio' ? 'R' : 'T';
    matC.giunte = matC.giunte.map(()=>g);
    disegnaGriglia(); aggiornaAnteprima(); });
  ['#m-ws','#m-hs'].forEach(id=>$(id).addEventListener('change', ()=>rigeneraMatrice(true)));
}
function aggiornaSelettoriProfili(){
  const s = $('#r-serie').value, v = DATI.varianti[s];
  if(isPorta(s) || tipProfili(s)){
    const t = DATI.tipologie.find(x=>x.id===$('#r-tip').value) || {};
    const vp = DATI.varianti_porte[s];
    const tel = t.telaio_rif || vp.telaio_int, ala = vp.ala[tel];
    $('#r-telaio').innerHTML = `<option value="std">${tel} — standard</option>` + (ala? `<option value="ala">${ala} — ${vp.nome_ala||'con ala 32 mm'}</option>` : '');
    $('#r-anta').innerHTML = `<option value="${t.anta_rif||''}">${t.anta_rif||'—'} — anta della tipologia</option>`;
    $('#r-traverso').innerHTML = `<option value="">—</option>`;
    const tav = tavolaVetro(t.anta_rif||'', t.vetro_tav);
    const spess = Object.keys(tav.righe).sort((a,b)=>a-b);
    const vd = (SERIE_INFO[s]||{}).vetro_default;
    const def = vd ? (spess.includes(vd) ? vd : spess.reduce((a,b)=>Math.abs(b-vd)<Math.abs(a-vd)?b:a)) : spess.includes('30')? '30' : spess.includes('46')? '46' : spess[0];
    $('#r-vetro').innerHTML = spess.map(m=>`<option value="${m}" ${m===def?'selected':''}>${m} mm</option>`).join('');
    aggiornaSezioni(); return;
  }
  $('#r-telaio').innerHTML = `<option value="${v.standard}">${v.standard} — standard</option>
    <option value="${v.z}">${v.z} — a Z</option>`;
  $('#r-anta').innerHTML = `<option value="B23122C">B23122C — unica anta di serie</option>`;
  const defT = DATI.traversi_default[s];
  $('#r-traverso').innerHTML = `<option value="${defT}">${defT} — traverso di serie</option>`;
  const spess = [...new Set([...Object.keys(DATI.vetrazione.tav701.righe),
                             ...Object.keys(DATI.vetrazione.tav702.righe)])].sort((a,b)=>a-b);
  $('#r-vetro').innerHTML = spess.map(m=>`<option value="${m}" ${m==='35'?'selected':''}>${m} mm</option>`).join('');
  aggiornaSezioni();
}
function sogliaSerie(){ return $('#r-serie').value==='C75S' ? 'B23401' : 'B23402'; }
function aggiornaSezioni(){
  const t = DATI.tipologie.find(x=>x.id===$('#r-tip').value);
  $('#box-matrice').style.display = isComposta() ? 'block' : 'none';
  const cg = $('#ctrl-griglia'); if(cg) cg.style.display = (t && t.forma==='M') ? 'block' : 'none';
  const bt = $('#box-traverso'); if(bt) bt.style.display = (t && t.forma==='M') ? 'none' : '';
  if(t && t.forma==='M') disegnaProfiliT();
  if(isComposta()) rigeneraMatrice(matC.ws.length>0);  // conserva interassi già impostati
  const porta = t && t.porta;
  const tipP = t && tipProfili(t.serie);
  const apribile = t && ['1','P1','1F','2','P2'].includes(t.forma) && t.ferr!==false;
  $('#box-blocal').style.display = (t && !porta && !tipP && ['1','1F','2','P1','P2','M'].includes(t.forma)) ? 'block' : 'none';
  $('#box-hm').style.display = apribile ? 'block' : 'none';
  if(bt && (porta || tipP)) bt.style.display = 'none';
  const bh2 = $('#box-h2'); if(bh2) bh2.style.display = (t && t.sopraluce) ? 'block' : 'none';
  const bdv = $('#box-div'); if(bdv) bdv.style.display = (t && t.divisore) ? 'block' : 'none';
  const bmc = $('#box-manc'); if(bmc) bmc.style.display = (t && t.opz_maniglia) ? 'block' : 'none';
  const bfp = $('#box-ferr-porta'); if(bfp) bfp.style.display = porta ? 'block' : 'none';
  if(apribile) aggiornaHM();
  const conMano = t && ['1','P1','1F'].includes(t.forma);
  $('#box-mano').style.display = conMano ? 'block' : 'none';
  if(conMano) $('#svg-mano').innerHTML =
    `<div style="padding:.2rem">${svgProspetto(t.forma==='1F'?'1F':'1', 300, 300, 0.18, $('#r-mano').value, $('#r-serie').value)}</div>`;
  const conStulp = t && DATI.stulp_map[t.id];
  $('#box-battuta').style.display = conStulp ? 'block' : 'none';
  if(conStulp) $('#svg-battuta').innerHTML =
    svgSezione($('#r-battuta').value==='stulp' ? 'B23505C' : 'B23100C');
  const isPB = t && DATI.pb_telaio[t.id];
  $('#box-base').style.display = isPB ? 'block' : 'none';
  if(isPB) $('#svg-base').innerHTML = $('#r-base').value==='soglia'
      ? svgSezione(sogliaSerie()) : svgSezione($('#r-telaio').value);
  if(porta || tipP){
    const vp = DATI.varianti_porte[t.serie], telP = t.telaio_rif || vp.telaio_int;
    const codTel = $('#r-telaio').value==='ala' ? (vp.ala[telP]||telP) : telP;
    $('#svg-telaio').innerHTML = svgSezione(codTel);
    $('#svg-anta').innerHTML = svgSezione(t.anta_rif);
    const mmP = $('#r-vetro').value, rP = risolviVetro(mmP, t.anta_rif, t.vetro_tav);
    $('#info-vetro').innerHTML = `<div style="font-size:.72rem;line-height:1.5"><b>Vetro ${mmP} mm</b> (${porta ? 'tav. 7.0'+(t.serie==='D67'?'4':'5') : 'tavola '+(t.vetro_tav||'')})<br>
      Fermavetro: <b class="num">${rP? rP.fv:'—'}</b> · guarn. interna <span class="num">${rP? rP.g:'n.d.'}</span><br>
      ${porta ? `<span style="color:var(--acciaio)">squadrato ${rP&&rP.fv_sq?rP.fv_sq:'—'} · tubolare ${rP&&rP.fv_tub?rP.fv_tub:'—'} · clips ${rP&&rP.fv_clip?rP.fv_clip:'—'}</span>`
              : `<span style="color:var(--acciaio)">guarn. esterna ${rP&&rP.ext?rP.ext:'—'} · fermavetro ${rP&&rP.B?rP.B:'—'} mm</span>`}</div>`;
    aggiornaAnteprima(); return;
  }
  $('#svg-telaio').innerHTML = svgSezione($('#r-telaio').value);
  $('#svg-anta').innerHTML = svgSezione($('#r-anta').value);
  $('#svg-traverso').innerHTML = svgSezione($('#r-traverso').value);
  const mm = $('#r-vetro').value;
  const rT = risolviVetro(mm, $('#r-telaio').value), rA = risolviVetro(mm, $('#r-anta').value);
  $('#info-vetro').innerHTML = `<div style="font-size:.72rem;line-height:1.5">
    <b>Vetro ${mm} mm</b><br>
    Anta: ferm. <b class="num">${rA? rA.fv:'—'}</b> · guarn. <span class="num">${rA? rA.g:'n.d.'}</span><br>
    Telaio: ferm. <b class="num">${rT? rT.fv:'—'}</b> · guarn. <span class="num">${rT? rT.g:'n.d.'}</span>
    ${(!rT||!rA)?'<br><span class="attenzione">spessore fuori tavola per uno dei profili</span>':''}</div>`;
  aggiornaAnteprima();
}
function aggiornaAnteprima(){
  const t = DATI.tipologie.find(x=>x.id===$('#r-tip').value); if(!t) return;
  const L = parseFloat($('#r-l').value)||1200, H = parseFloat($('#r-h').value)||1400;
  let forma = t.forma;
  if(forma==='M'){ $('#prospetto').innerHTML = svgProspettoMatrice(matC.ws.length?matC.ws:[L], matC.hs.length?matC.hs:[H], matC.celle.length?matC.celle:[['F']], null, matC.giunte, $('#r-serie').value, true, matC.giunteO);
    $('#prospetto-dati').textContent = `[${($('#r-cod').value.trim()||t.cod)}] ${L} × ${H} mm — ${matC.cols}×${matC.rows}`; return; }
  if(DATI.pb_telaio[t.id] && $('#r-base').value==='telaio')
    forma = forma==='P1' ? '1' : '2';   // porta con telaio a terra: come finestra, senza soglia
  $('#prospetto').innerHTML = svgProspetto(forma, L, H, null, $('#r-mano').value, $('#r-serie').value);
  $('#prospetto-dati').textContent = `[${($('#r-cod').value.trim()||t.cod)}] ${L} × ${H} mm`;
}
function aggiornaTipologie(){
  const s = $('#r-serie').value;
  $('#r-tip').innerHTML = DATI.tipologie.filter(t=>t.serie===s && !t.nascosta)
    .map(t=>`<option value="${t.id}">[${t.cod}] ${t.nome}</option>`).join('');
  mostraAvvisoTip(); aggiornaSelettoriProfili(); aggiornaAnteprima();
}
function mostraAvvisoTip(){
  const t = DATI.tipologie.find(x=>x.id===$('#r-tip').value);
  $('#r-avviso').innerHTML = (t && t.avviso) ? `<div class="avviso">${t.avviso}</div>` : '';
  if(t) $('#r-cod').value = t.cod;
}

// ---------- righe commessa ----------
function leggiRigaCorrente(quiet){
  const t = DATI.tipologie.find(x=>x.id===$('#r-tip').value);
  const L = parseFloat($('#r-l').value.replace(',','.'));
  const H = parseFloat($('#r-h').value.replace(',','.'));
  const q = parseInt($('#r-q').value,10) || 1;
  if(!t || !(L>200) || !(H>200)){
    if(!quiet) $('#esito').textContent = 'Controlla tipologia, misure (mm) e quantità.';
    return null;
  }
  const base = DATI.pb_telaio[t.id] ? $('#r-base').value : null;
  const battuta = DATI.stulp_map[t.id] ? $('#r-battuta').value : null;
  const mano = ['1','P1','1F'].includes(t.forma) ? $('#r-mano').value : null;
  const hm = ['1','P1','1F','2','P2'].includes(t.forma) ? (parseFloat($('#r-hm').value)||null) : null;
  const blocal = $('#r-blocal').checked || false;
  const h2 = t.sopraluce ? (parseFloat(String($('#r-h2').value).replace(',','.'))||null) : null;
  if(t.sopraluce && !(h2>50 && h2<H-300)){
    if(!quiet) $('#esito').textContent = (t.porta ? 'Porta con sopraluce: inserisci H2 (altezza sopraluce, mm)' : 'Inserisci H2 (altezza del fisso inferiore, mm)') + ' tra 50 e H-300.';
    return null;
  }
  const ferr = t.porta ? {cern:$('#r-cern').value, ncern:parseInt($('#r-ncern').value,10)||0, serr:$('#r-serr').value} : null;
  const hdiv = t.divisore ? (parseFloat(String($('#r-hdiv').value).replace(',','.'))||null) : null;
  if(hdiv!==null){ const ha = valuta(t.anta_h||'H-43', L, H, {h2}); if(!(ha && hdiv>=150 && hdiv<=ha-150)){
    if(!quiet) $('#esito').textContent = `Divisore d'anta: Ha2 deve stare tra 150 e ${ha? Math.round(ha-150) : '?'} mm (altezza anta ${ha? Math.round(ha) : '?'}).`; return null; } }
  const manc = t.opz_maniglia ? !!$('#r-manc').checked : null;
  let mat = null;
  if(t.forma==='M'){
    if(t.serie==='C82S-CS'){
      const viol = violaVincoloC82(matC.celle, matC.giunte, matC.giunteO);
      if(viol){ $('#esito').textContent =
        `Vincolo C82S: due apribili adiacenti con montante/traverso in mezzo non sono realizzabili (${viol}). Metti un fisso tra loro.`; return null; }
    }
    const sw = matC.ws.reduce((a,b)=>a+b,0), sh = matC.hs.reduce((a,b)=>a+b,0);
    if(Math.abs(sw-L)>1 || Math.abs(sh-H)>1){
      $('#esito').textContent = `Le larghezze colonne devono sommare a L (${sw} ≠ ${L}) e le altezze a H (${sh} ≠ ${H}).`; return null; }
    mat = JSON.parse(JSON.stringify({ws:matC.ws, hs:matC.hs, celle:matC.celle, giunte:matC.giunte, giunteO:matC.giunteO}));
  }
  const codTip = ($('#r-cod').value.trim()||t.cod).replace(/[^A-Za-z0-9_\-]/g,'').toUpperCase();
  return {tid:t.id, codTip, mat, battuta, mano, hm, blocal, telaio:$('#r-telaio').value, anta:$('#r-anta').value,
    traverso:$('#r-traverso').value, vetro:$('#r-vetro').value, base, L, H, q, h2, ferr, hdiv, manc};
}
function aggiungiRiga(){
  const r = leggiRigaCorrente(false);
  if(!r) return;
  if(modificaIdx!==null && righe[modificaIdx]){
    const q = parseInt($('#r-q').value,10); if(q>0) r.q = q;
    righe[modificaIdx] = r;
    $('#esito').textContent = `Riga ${modificaIdx+1} aggiornata.`;
    annullaModifica();
  } else {
    righe.push(r);
    $('#esito').textContent='';
  }
  disegnaRighe();
}
function disegnaRighe(){
  const tb = $('#tab-righe tbody');
  tb.innerHTML = righe.map((r,i)=>{
    if(r.tipo==='composta'){
      const mini = `<span class="mini-prosp">${svgMatrice(r.m, Math.min(34/r.L,34/r.H))}</span>`;
      return `<tr><td class="n">${i+1}</td><td>${r.m.serie}</td>
        <td>${mini} <span class="num"><b>${r.codTip}</b></span> Composizione ${r.m.cols}×${r.m.rows}</td>
        <td class="num" style="font-size:.78rem">${r.telaio}<br>v.${r.vetro}</td>
        <td class="n">${r.L}</td><td class="n">${r.H}</td>
        <td class="n"><input type="number" min="1" class="q-riga num" data-i="${i}" value="${r.q}" style="width:3.2rem;text-align:right"></td>
        <td class="no-stampa"><button class="spoglio" onclick="rimuovi(${i})" title="Elimina">✕</button></td></tr>`;
    }
    const t = DATI.tipologie.find(x=>x.id===r.tid);
    const mini = `<span class="mini-prosp">${ r.mat
      ? svgProspettoMatrice(r.mat.ws, r.mat.hs, r.mat.celle, Math.min(34/r.L,34/r.H), r.mat.giunte||r.mat.giunta, r.serie||t.serie, false, r.mat.giunteO)
      : svgProspetto(t.forma, r.L, r.H, Math.min(34/r.L,34/r.H), r.mano||'dx', r.serie||t.serie)}</span>`;
    return `<tr><td class="n">${i+1}</td><td>${t.serie}</td><td>${mini} <span class="num"><b>${r.codTip||t.cod}</b></span> ${t.nome}</td>
      <td class="num" style="font-size:.78rem">${r.telaio}<br>${r.anta} · v.${r.vetro}${r.base?'<br>'+(r.base==='telaio'?'tel. a terra':'soglia'):''}${r.battuta?'<br>'+(r.battuta==='stulp'?'stulp':'nodo stretto'):''}${r.hdiv?'<br>divisore Ha2='+r.hdiv:''}${r.manc?'<br>maniglia centrata':''}${r.mano?' · '+r.mano.toUpperCase():''}${r.hm?' · man. '+r.hm:''}${r.h2?'<br>H2 '+r.h2:''}${r.ferr?'<br>'+r.ferr.cern+(r.ferr.ncern?'×'+r.ferr.ncern:'')+' · '+r.ferr.serr:''}</td>
      <td class="n">${r.L}</td><td class="n">${r.H}</td>
      <td class="n"><input type="number" min="1" class="q-riga num" data-i="${i}" value="${r.q}" style="width:3.2rem;text-align:right"></td>
      <td class="no-stampa"><button class="spoglio" onclick="modificaRiga(${i})" title="Modifica">✎</button>
        <button class="spoglio" onclick="rimuovi(${i})" title="Elimina">✕</button></td></tr>`;
  }).join('');
  document.querySelectorAll('.q-riga').forEach(inp=>inp.addEventListener('input', ()=>{
    const v = parseInt(inp.value,10);
    if(v>0) righe[+inp.dataset.i].q = v;
  }));
  $('#vuoto').style.display = righe.length? 'none':'block';
}
window.rimuovi = i => { righe.splice(i,1); if(modificaIdx===i) annullaModifica(); disegnaRighe(); };

let modificaIdx = null;
window.modificaRiga = function(i){
  const r = righe[i];
  const t = DATI.tipologie.find(x=>x.id===r.tid);
  if(!t) return;
  const fire = (sel)=>{ const e=$(sel); if(e && e.dispatchEvent) e.dispatchEvent(new Event(sel==='#r-hm'||sel==='#r-l'||sel==='#r-h'?'input':'change')); };
  $('#r-serie').value = t.serie; fire('#r-serie');
  $('#r-tip').value = r.tid; fire('#r-tip');
  $('#r-l').value = r.L; $('#r-h').value = r.H; fire('#r-h');
  if(r.telaio) $('#r-telaio').value = r.telaio;
  if(r.anta) $('#r-anta').value = r.anta;
  if(r.traverso) $('#r-traverso').value = r.traverso;
  $('#r-vetro').value = r.vetro||'29';
  if(r.base) $('#r-base').value = r.base;
  if(r.battuta) $('#r-battuta').value = r.battuta;
  if(r.mano) $('#r-mano').value = r.mano;
  if(r.hm){ $('#r-hm').value = r.hm; fire('#r-hm'); }
  if(r.h2) $('#r-h2').value = r.h2;
  if($('#r-hdiv')) $('#r-hdiv').value = r.hdiv||'';
  if($('#r-manc')) $('#r-manc').checked = !!r.manc;
  if(r.ferr){ $('#r-cern').value = r.ferr.cern; $('#r-ncern').value = r.ferr.ncern||0; $('#r-serr').value = r.ferr.serr; }
  const bl = $('#r-blocal'); if(bl) bl.checked = !!r.blocal;
  $('#r-cod').value = r.codTip||'';
  $('#r-q').value = r.q;
  if(r.mat){
    matC.cols = r.mat.ws.length; matC.rows = r.mat.hs.length;
    matC.ws = r.mat.ws.slice(); matC.hs = r.mat.hs.slice();
    matC.celle = r.mat.celle.map(x=>x.slice());
    matC.giunte = (r.mat.giunte||[]).slice();
    matC.giunteO = (r.mat.giunteO||[]).slice();
    $('#m-cols').value = matC.cols; $('#m-rows').value = matC.rows;
    $('#m-ws').value = matC.ws.join(' ; '); $('#m-hs').value = matC.hs.join(' ; ');
    disegnaGriglia(); aggiornaAnteprima();
  }
  modificaIdx = i;
  const ba = $('#btn-aggiungi');
  if(ba) ba.textContent = `Salva modifiche riga ${i+1}`;
  $('#esito').textContent = `Modifica della riga ${i+1} (${r.codTip||t.cod}): correggi i campi e premi "Salva modifiche".`;
  window.scrollTo(0,0);
};

function annullaModifica(){
  modificaIdx = null;
  const ba = $('#btn-aggiungi'); if(ba) ba.textContent = 'Aggiungi alla commessa';
}

// ---------- opzioni COR80: divisore d'anta e maniglia centrata (catalogo Cortizo p.301/308/321/328, p.304/307/314/317/320/324/327) ----------
function formulaAnta(t, f, hdiv){
  // 'La-95', 'Ha1-105.6', '4La+2Ha' -> formula in L/H per valuta(): La = anta (1 anta: anta_l; 2 ante: anta_l2), Ha = anta_h, Ha2 = hdiv, Ha1 = Ha-Ha2
  const La = `(${t.anta_l||t.anta_l2||'L-43'})`, Ha = `(${t.anta_h||'H-43'})`;
  const Ha1 = `(${Ha}-${hdiv})`, Ha2 = `(${hdiv})`;
  return String(f).replace(/\s/g,'').replace(/Ha1/g, Ha1).replace(/Ha2/g, Ha2).replace(/Ha/g, Ha).replace(/La/g, La).replace(/(\d)\(/g, '$1*(');
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
function calcolaCommessa(){
  const pezzi=[], erroriFormule=[], accessori={}, guarnizioni={}, vetri=[];
  const conDren = $('#c-dren').checked, conForo8 = $('#c-foro8').checked;
  const includiFV = $('#c-fermavetro-si').value==='si';

  righe.forEach((r,idx)=>{
    if(r.tipo==='composta'){
      for(let u=0; u<r.q; u++){
        const d = distintaComposta(r.m, {dren: conDren});
        d.pezzi.forEach((p,pi)=>pezzi.push(Object.assign({},p,{unita:`R${idx+1}.${u+1}`,
          tip:'Composizione', tcod:r.codTip, serie:r.m.serie,
          cod:`${r.codTip}-${p.sc}${String(pi+1).padStart(2,'0')}`, desc:p.desc})));
        d.vetri.forEach(v=>vetri.push(Object.assign({},v,{unita:`R${idx+1}.${u+1} ${v.unita}`})));
        Object.entries(d.accessori).forEach(([k,v])=>{const [a,de]=k.split('|');registraAccessorio(accessori,a,de,v.pz,null);});
        Object.entries(d.guarnizioni).forEach(([k,mm])=>{guarnizioni[k]=(guarnizioni[k]||0)+mm;});
      }
      return;
    }
    let t = DATI.tipologie.find(x=>x.id===r.tid);
    let notaBase = '';
    if(r.battuta==='stulp' && DATI.stulp_map[r.tid]){
      const ts = DATI.tipologie.find(x=>x.id===DATI.stulp_map[r.tid]);
      t = Object.assign({}, ts, {nome: t.nome+' — STULP', cod: t.cod, forma: t.forma});
    } else if(r.battuta==='montante'){
      t = Object.assign({}, t, {nome: t.nome+' — NODO STRETTO'});
    }
    if(r.base==='telaio' && DATI.pb_telaio[r.tid]){
      const tf = DATI.tipologie.find(x=>x.id===DATI.pb_telaio[r.tid]);
      t = Object.assign({}, tf, {nome: t.nome+' — TELAIO A TERRA', cod: t.cod, forma: tf.forma});
      notaBase = ' (telaio a terra)';
    }
    if(r.codTip) t = Object.assign({}, t, {cod: r.codTip});
    if(r.mano) t = Object.assign({}, t, {nome: t.nome+' — '+r.mano.toUpperCase()});
    if(r.hdiv>0 && t.divisore) t = conDivisore(t, r);
    if(r.manc && t.opz_maniglia) t = conManigliaCentrata(t, r);
    if(r.mat){
      for(let u=0; u<r.q; u++)
        componiMatrice(r, t, {pezzi, accessori, guarnizioni, vetri, erroriFormule,
          conDren, conAnte: conForo8, unita:`R${idx+1}.${u+1}`});
      return;
    }
    for(let u=0; u<r.q; u++){
      const unita = `R${idx+1}.${u+1}`;
      accessorioBlocal(r, t, accessori);
      t.profili.forEach(p=>{
        let art = codiceProfilo(t.serie, r, p.art, p.desc);
        const isFV = art.startsWith('N458') || p.fv===true;
        if(isFV){
          // i fermavetri stanno sull'anta, salvo quelli del vetro fisso e del telaio fisso
          const suFisso = /fisso/i.test(p.desc) || t.forma==='F';
          const codRif = t.porta ? (t.anta_rif||r.anta) : (t.anta_rif ? (suFisso && t.telaio_rif ? t.telaio_rif : t.anta_rif) : (suFisso ? (r.telaio||'B23008C') : (r.anta||'B23122C')));
          const ris = risolviVetro(r.vetro, codRif, suFisso ? p.tav : (p.tav||t.vetro_tav));
          if(!ris){ erroriFormule.push(`${t.nome}: vetro ${r.vetro} mm fuori tavola per ${codRif}`); return; }
          if(!ris.fv || ris.fv==='-'){ erroriFormule.push(`${t.nome}: nessun fermavetro a catalogo per vetro ${r.vetro} mm (${codRif})`); return; }
          if(!includiFV){ registraAccessorio(accessori, ris.fv, p.desc+' (da tagliare a parte)', p.pz, valuta(p.mis,r.L,r.H,r)); return; }
          art = ris.fv;
        }
        const mm = valuta(p.mis, r.L, r.H, r);
        if(mm===null){ erroriFormule.push(`${t.nome}: ${p.desc} = "${p.mis}"`); return; }
        const [al,ar] = angoliJob(p.ang);
        const traversoTelaio = /Traverso stipite/.test(p.desc) && p.pz===2;
        const traversoAnta = /Traverso battente/.test(p.desc);
        const montanteAnta = /Montante battente/.test(p.desc);
        for(let k=0;k<p.pz;k++){
          const codPezzo = `${t.cod}-${p.sc}${String(k+1).padStart(2,'0')}`;
          const lav=[]; LAV_CTX.serie = t.serie; LAV_CTX.art = art;
          const inVista = serieInVista(t.serie);
          const ferrAR = ['1','2','P1','P2'].includes(t.forma) && t.ferr!==false;   // ferramenta A-R solo su battenti (ferr:false = anta a scomparsa)
          const conStulp = r.battuta==='stulp' || /stulp/i.test(t.nome||'') || t.stulp===true;
          const montanteTelaio = /Montante stipite/.test(p.desc) && !/T centrale/.test(p.desc);
          if(inVista && conDren && (traversoTelaio || montanteTelaio || (/Traverso stipite/.test(p.desc)))){
            lav.push(...lavFX(mm));                                   // fissaggi su tutti i lati telaio
          }
          if(conDren && traversoTelaio && k===0){                     // drenaggio: traverso inferiore
            const dT = (DRAIN[t.serie]||{})[t.dren_telaio||'telaio'] || {};
            const dl = dT.bordo ? posizioniDrenaggio(mm, dT.bordo, dT.passo||450).map(x=>lavDrenaggio(t.serie, t.dren_telaio||'telaio', x))
                     : inVista ? lavDrenTelaioFP(mm, t.serie) : posizioniDrenaggio(mm).map(x=>lavDrenaggio(t.serie,'telaio',x));
            if(/2 ante|due ante/i.test(t.nome) && r.battuta==='stulp' &&
               !dl.some(l=>Math.abs(l.x-mm/2)<5))                     // scarico sotto il nodo stulp
              dl.push(lavDrenaggio(t.serie,'telaio', Math.round(mm/2*10)/10));
            lav.push(...dl); capDrenaggio(t.serie, accessori, dl.length);
          }
          if(inVista && conForo8 && ferrAR && montanteTelaio){          // cerniere angolari lato cerniere
            const dueAnte = /2 ante|due ante/i.test(t.nome);
            const latoCerniere = dueAnte || ((r.mano||'dx')==='dx' ? k===1 : k===0);
            if(latoCerniere) lav.push(...lavCerniere(mm, k===0));
            if(!dueAnte){                                              // scontri Maico (1 anta)
              const hAnta = valuta(t.anta_h||'H-43', r.L, r.H, r);
              lav.push(...(latoCerniere ? lavScontriMontanteCerniere(mm, hAnta) : lavScontriMontanteManiglia(mm, hAnta, r.hm)));
            } else if(conStulp){                                       // due ante stulp (doc 750135 pp.27-34)
              const hbb = valuta(t.anta_h||'H-43', r.L, r.H, r) - 20;
              const attivo = (r.mano||'dx')==='dx' ? k===1 : k===0;
              if(attivo){
                lav.push(SC_SINGLE(Math.round((mm-142)*10)/10));       // scontro d'angolo in alto
                const Bs = hbb<=1280 ? [565] : hbb<=1700 ? [800] : hbb<=2200 ? [800,1506] : [800,1506,1977];
                if(hbb>800) Bs.forEach((b,i)=> lav.push(SC_SINGLE(Math.round((mm-(b+(i===0?25.5:24.5)))*10)/10)));
              } else {                                                   // cerniera centrale sul semifisso (sempre)
                [mm/2-19, mm/2+19].forEach(x=> lav.push(Object.assign({x:Math.round(x*10)/10}, lavDef('cern_centrale'))));
              }
            }
          }
          if(inVista && conForo8 && ferrAR && traversoTelaio && !/2 ante|due ante/i.test(t.nome)){
            lav.push(...lavScontriTraverso(mm, k===0, (r.mano||'dx')==='dx', valuta(t.anta_l||'L-43', r.L, r.H, r)));
            if(k===1) lav.push(...lavScontroForbice(mm, valuta(t.anta_l||'L-43', r.L, r.H, r), (r.mano||'dx')==='dx'));
          }
          if(inVista && conForo8 && ferrAR && traversoTelaio && /2 ante|due ante/i.test(t.nome) && conStulp){
            const s = (r.mano||'dx')==='dx' ? 1 : -1;                  // specchio per mano
            const ax = mm/2;                                           // asse stulp
            if(k===0){                                                 // traverso inferiore
              lav.push(...SC_PAIR54(Math.round((ax-123*s)*10)/10));    // scontro d'angolo anta attiva al nodo
              lav.push(SC_SINGLE(Math.round((ax+74.8*s)*10)/10));      // scontro catenaccio inferiore semifisso
            } else {                                                   // traverso superiore
              lav.push(...SC_PAIR54(Math.round((ax+124.5*s)*10)/10));  // scontro d'angolo al nodo (lato semifisso)
              lav.push(SC_SINGLE(Math.round((ax-46.8*s)*10)/10));      // scontro catenaccio superiore
              const ffbAnta = valuta(t.anta_l2||'L/2-24', r.L, r.H, r) - 20;
              if(ffbAnta > 800){                                       // scontro forbice semifisso (ante larghe)
                const q = FORBICE_QUOTA[forbicePer(ffbAnta+20)];
                if(q!=null) lav.push(SC_SINGLE(s>0 ? Math.round((q+28.5)*10)/10 : Math.round((mm-q-28.5)*10)/10));
              }
            }
          }
          if(t.porta){ lav.push(...lavPorta(t, r, p, k, mm, conDren, conForo8, accessori)); }
          if(!t.porta && conForo8 && traversoAnta && k < p.pz/2){       // drenaggio anta: 168 dagli estremi
            const xd = t.dren_x||168;
            [xd, Math.round((mm-xd)*10)/10].forEach(x=>lav.push(lavDrenaggio(t.serie, t.dren_anta||'antaTrav', x)));
          }
          if(conForo8 && traversoAnta && k===2 && p.pz>=4 &&           // sfiato semifissa: traverso SUP, 200 dal nodo
             /2 ante|due ante/i.test(t.nome) && conStulp){             // (schema drenaggi aziendale; FP non lo faceva)
            const xSf = (r.mano||'dx')==='dx' ? Math.round((mm-200)*10)/10 : 200;
            lav.push(lavDrenaggio(t.serie, t.dren_anta||'antaTrav', xSf));
          }
          if(!t.porta && conForo8 && montanteAnta)                     // 218 dal basso
            { const xm = t.dren_x||218; lav.push(lavDrenaggio(t.serie,'antaMont', (k%2===0)? xm : Math.round((mm-xm)*10)/10)); }
          if(inVista && conForo8 && ferrAR && montanteAnta){            // martellina sull'anta attiva, lato maniglia
            const kMan = (r.mano||'dx')==='dx' ? 1 : 0;
            if(k===kMan) lav.push(...lavMartellina(mm, r.hm));
          }
          specchiaY(t.serie, lav); applicaTarature(t.serie, art, lav);
          if(SERIE_INFO[t.serie] && SERIE_INFO[t.serie].da_tarare) lav.forEach(l=>{ if(!/DA TARARE/.test(l.descr)) l.descr += ' [DA TARARE]'; });
          pezzi.push({art, desc:p.desc, mm:Math.round(mm*10)/10, al, ar, unita,
                      tip:t.nome, tcod:t.cod, cod:codPezzo, serie:t.serie, lav});
        }
      });
      t.accessori.forEach(a=>registraAccessorio(accessori, a.art, a.desc, a.pz, null));
      t.guarnizioni.forEach(g=>{
        const mm = valuta(g.mis, r.L, r.H, r);
        let art = g.art, desc = g.desc;
        if(/^809119/.test(g.art) || (t.porta && /^interna vetro/i.test(g.desc)) || g.gv===true){  // guarnizione interna vetro -> dalla tavola di vetrazione
          const ris = risolviVetro(r.vetro, (t.porta||t.anta_rif) ? (t.anta_rif||r.anta) : (r.anta||'B23122C'), t.vetro_tav);
          if(ris){ art = ris.g; desc = `Interna vetro (vetro ${r.vetro} mm)`; }
        }
        const chiave = art+'|'+desc;
        guarnizioni[chiave] = (guarnizioni[chiave]||0) + (mm? mm:0);
      });
      t.vetro.forEach(v=>{
        const l=valuta(v.l,r.L,r.H,r), h=valuta(v.h,r.L,r.H,r);
        vetri.push({q:v.pz, l:l?Math.round(l):v.l, h:h?Math.round(h):v.h, sp:r.vetro, tip:t.nome, unita});
      });
    }
  });
  return {pezzi, accessori, guarnizioni, vetri, erroriFormule};
}
function registraAccessorio(reg, art, desc, pz, mm){
  const k = art+'|'+desc;
  if(!reg[k]) reg[k]={pz:0, mm:0};
  if(pz) reg[k].pz += pz;
  if(mm) reg[k].mm += mm;
}

// ---------- ottimizzazione barre (FFD) ----------
function ottimizza(pezzi){
  const stock = parseFloat($('#c-barra').value)||6500;
  const lama = parseFloat($('#c-lama').value)||6;
  const perProfilo = {};
  pezzi.forEach(p=>{ (perProfilo[p.art]=perProfilo[p.art]||[]).push(p); });
  const barre=[];
  Object.entries(perProfilo).forEach(([art, lista])=>{
    lista.sort((a,b)=>b.mm-a.mm);
    const aperte=[];
    lista.forEach(p=>{
      let b = aperte.find(x=>x.resto >= p.mm + lama);
      if(!b){ b={art, resto:stock, pezzi:[], stock}; aperte.push(b); barre.push(b); }
      b.pezzi.push(p); b.resto -= (p.mm + lama);
    });
  });
  return barre;
}


// ---------- schema grafico del singolo pezzo con lavorazioni ----------

// facce nel job vs facce fisiche in macchina: alcuni profili sono caricati ruotati di 180
// (conferma operatore su B23122C: fori martellina job F3 = reale F2; scasso job F1 = reale F4)
const FACCIA_FISICA = DATI.faccia_fisica;
function facciaFisica(prof, f){ return (FACCIA_FISICA[prof]||{})[f] || f; }
function sezioneFacciaSvg(f, col, lav, maxY, prof){
  const S=104, mg=10, a=S-2*mg;
  const dx = (DATI.dxf_sez||{})[prof];
  const VT='#2E9E44', VTS='#1B6B2E';
  let disegno='', bx=mg, by=mg, bwd=a, bhd=a, sc=a/75;
  let cam = null;
  if(dx){
    sc = Math.min(a/dx.w, a/dx.h);
    bwd = dx.w*sc; bhd = dx.h*sc;
    bx = mg + (a-bwd)/2; by = mg + (a-bhd)/2;
    disegno = `<g transform="translate(${bx},${by+bhd}) scale(${sc},${-sc}) translate(${-dx.x},${-dx.y})">
      <path d="${dx.d}" fill="none" stroke="#5C6B76" stroke-width="${(0.9/sc).toFixed(2)}"/></g>`;
    const c = dx.cam || {x:dx.x,y:dx.y,w:dx.w,h:dx.h};
    cam = { L: bx+(c.x-dx.x)*sc, R: bx+(c.x-dx.x+c.w)*sc,
            T: by+bhd-(c.y-dx.y+c.h)*sc, B: by+bhd-(c.y-dx.y)*sc };
  } else {
    disegno = `<rect x="${bx}" y="${by}" width="${bwd}" height="${bhd}" fill="#EDEFF1" stroke="#8A98A3" stroke-width="1"/>`;
    cam = {L:bx, R:bx+bwd, T:by, B:by+bhd};
  }
  // camera rettangolare FP (rif. operatore): origini per faccia sullo spigolo camera, scala reale mm
  const F = {
    '1': {lx1:bx, ly:cam.T,  lx2:bx+bwd, vert:false, zx:cam.R, zy:cam.T, dir:-1, nx:0, ny:1},
    '4': {lx1:bx, ly:cam.B,  lx2:bx+bwd, vert:false, zx:cam.L, zy:cam.B, dir:+1, nx:0, ny:-1},
    '3': {ly1:by, lx:bx,     ly2:by+bhd, vert:true,  zx:bx,    zy:cam.B, dir:-1, nx:1, ny:0},
    '2': {ly1:by, lx:bx+bwd, ly2:by+bhd, vert:true,  zx:bx+bwd,zy:cam.T, dir:+1, nx:-1, ny:0}
  }[f] || {lx1:bx, ly:cam.T, lx2:bx+bwd, vert:false, zx:cam.R, zy:cam.T, dir:-1, nx:0, ny:1};
  let g;
  if(!F.vert)
    g = `<line x1="${F.lx1}" y1="${F.ly-F.ny*3}" x2="${F.lx2}" y2="${F.ly-F.ny*3}" stroke="${col}" stroke-width="3.2" stroke-linecap="square" opacity=".9"/>`;
  else
    g = `<line x1="${F.lx-F.nx*3}" y1="${F.ly1}" x2="${F.lx-F.nx*3}" y2="${F.ly2}" stroke="${col}" stroke-width="3.2" stroke-linecap="square" opacity=".9"/>`;
  g += `<circle cx="${F.zx-F.nx*3}" cy="${F.zy-F.ny*3}" r="2.4" fill="#fff" stroke="${col}" stroke-width="1.3"/>
    <text x="${F.zx-F.nx*9}" y="${F.zy-F.ny*9+2.5}" font-size="7" fill="${col}" text-anchor="middle">0</text>`;
  const P=(x,y)=>`${x.toFixed(1)},${y.toFixed(1)}`;
  (lav||[]).forEach(l=>{
    const ymm = Math.abs(parseFloat(l.y));
    let cx, cy;
    if(!F.vert){ cx = Math.max(bx+1, Math.min(bx+bwd-1, F.zx + F.dir*ymm*sc)); cy = F.ly; }
    else { cy = Math.max(by+1, Math.min(by+bhd-1, F.zy + F.dir*ymm*sc)); cx = F.lx; }
    const wmm = l.v2 ? parseFloat(l.v1) : 2*parseFloat(l.v1);
    const w = Math.max(3, wmm*sc);
    const pen = Math.min((F.vert? bwd : bhd)*0.38, 20), cod = 8;
    const e = F.vert? {x:0,y:1} : {x:1,y:0}, n = {x:F.nx, y:F.ny};
    const poly = (w2,d0,d1)=>`${P(cx-e.x*w2+n.x*d0, cy-e.y*w2+n.y*d0)} ${P(cx+e.x*w2+n.x*d0, cy+e.y*w2+n.y*d0)} ${P(cx+e.x*w2+n.x*d1, cy+e.y*w2+n.y*d1)} ${P(cx-e.x*w2+n.x*d1, cy-e.y*w2+n.y*d1)}`;
    g += `<polygon points="${poly(w/2,0,pen)}" fill="${VT}" stroke="${VTS}" stroke-width=".8" opacity=".95"/>`;
    g += `<polygon points="${poly(w/2+1.2,-cod,0)}" fill="${VT}" stroke="${VTS}" stroke-width=".8" opacity=".65"/>`;
    g += `<line x1="${cx-n.x*(cod+4)}" y1="${cy-n.y*(cod+4)}" x2="${cx+n.x*(pen+3)}" y2="${cy+n.y*(pen+3)}" stroke="${VTS}" stroke-width=".9" stroke-dasharray="3 2"/>`;
  });
  return `<svg width="${S}" height="${S}" viewBox="0 0 ${S} ${S}" style="flex:0 0 auto">
    ${disegno}${g}
    <text x="${S/2}" y="${S-1}" font-size="8" fill="#5C6B76" text-anchor="middle">${prof||''} · F${f}</text>
  </svg>`;
}
function svgPezzoLav(p){
  const NOMI_F = {'1':'Faccia 1 — superiore','2':'Faccia 2 — destra','3':'Faccia 3 — sinistra','4':'Faccia 4 — inferiore'};
  const FCOL = {'1':'#1B2328','2':'#5C6B76','3':'#0F6B3C','4':'#8A5A00'};
  const L = p.mm, W = 660, mg = 14, s = (W - 2*mg)/L;
  const perFaccia = {};
  p.lav.forEach(l=>{ const df = facciaFisica(p.art, l.f); (perFaccia[df]=perFaccia[df]||[]).push(l); });
  let out = '';
  ['1','2','3','4'].forEach(f=>{
    const lav = perFaccia[f]; if(!lav) return;
    const col = FCOL[f] || '#BE1622';
    const maxY = Math.max(...lav.map(l=>Math.abs(parseFloat(l.y))||0), 40);
    const hb = 52, y0 = 16, HB = y0 + hb + 22;
    const ys = (yv)=> y0 + (Math.abs(parseFloat(yv))/(maxY*1.25)) * hb;
    let g='', q='';
    lav.forEach((l,i)=>{
      const x = mg + l.x*s, yy = ys(l.y);
      if(l.v2){ const w = Math.max(6, parseFloat(l.v2)*s);
        g += `<rect x="${x-w/2}" y="${yy-3.5}" width="${w}" height="7" rx="3.5" fill="none" stroke="${col}" stroke-width="1.8"/>`;
      } else {
        const rr = Math.min(Math.max(2.5, parseFloat(l.v1)*s), 7);
        g += `<circle cx="${x}" cy="${yy}" r="${rr}" fill="none" stroke="${col}" stroke-width="1.8"/>`;
      }
      q += `<text x="${x}" y="${i%2? y0-4 : y0+hb+13}" font-size="8.5" fill="#5C6B76" text-anchor="middle">${l.x}</text>`;
    });
    const righe = lav.map(l=>{
      const geo = l.v2? `${l.v1}×${l.v2}` : `Ø${Math.round(20*parseFloat(l.v1))/10}`;
      const tar = encodeURIComponent(JSON.stringify({serie:p.serie, prof:p.art, f:String(l.f), filtro:descrBase(l.descr), nota:`${p.art} F${l.f} ${descrBase(l.descr)}`}));
      return `<div style="font-size:.72rem"><b class="num">${geo}</b> a X ${l.x} · Y ${l.y} · Z ${l.z||0} · ut.${l.ut} <span style="color:var(--acciaio)">${l.descr||''}</span> <a href="#" data-tar="${tar}" class="no-stampa" title="Aggiungi una regola di taratura per questa lavorazione" style="text-decoration:none">⚙</a></div>`;
    }).join('');
    out += `<div style="margin-bottom:.55rem">
      <div style="font-size:.72rem; font-weight:700; color:${col}; letter-spacing:.04em">${NOMI_F[f]||('Faccia '+f)} — ${lav.length} lavoraz.</div>
      <div style="display:flex; gap:.4rem; align-items:flex-start; flex-wrap:wrap">
        ${sezioneFacciaSvg(f, col, lav, maxY, p.art)}
        <div style="flex:1 1 280px; min-width:240px">
          <svg width="100%" viewBox="0 0 ${W} ${HB}" style="background:#fff;border:1px solid var(--linea)">
            <rect x="${mg}" y="${y0}" width="${W-2*mg}" height="${hb}" fill="#F2F7F4" stroke="${col}" stroke-width="1.2"/>
            ${g}${q}
            <text x="${mg}" y="${y0-4}" font-size="8.5" fill="#1B2328">0</text>
            <text x="${W-mg}" y="${y0-4}" font-size="8.5" fill="#1B2328" text-anchor="end">${p.mm}</text>
          </svg>
          <div style="display:flex;flex-wrap:wrap;gap:.05rem .9rem;margin-top:.15rem">${righe}</div>
        </div>
      </div>
    </div>`;
  });
  return `<div style="background:#fff;border:1px solid var(--linea);padding:.5rem .6rem">${out}</div>`;
}



// ---------- importatore job XML (FP Pro / macchina) ----------
function importaJobTesto(testo){
  const esiti = {righe:[], composte:[], avvisi:[]};
  const gruppi = {};
  const reBar = /<BAR>([\s\S]*?)<\/BAR>/g;
  let mb;
  while((mb = reBar.exec(testo))){
    const b = mb[1];
    const prof = (b.match(/<CODE>([^<]*)<\/CODE>/)||[])[1]||'';
    const syst = (b.match(/<SYST>([^<]*)<\/SYST>/)||[])[1]||'';
    const reCut = /<CUT>([\s\S]*?)<\/CUT>/g;
    let mc;
    while((mc = reCut.exec(b))){
      const c = mc[1];
      const il = parseFloat((c.match(/<IL>([^<]*)<\/IL>/)||[])[1]||'0');
      const lbl = [...c.matchAll(/<LBL>([^<]*)<\/LBL>/g)].map(x=>x[1].trim());
      const serr = (lbl[3]||'').replace(/\.(L|H)$/,'');
      const ruolo = lbl[2]||'';
      if(!serr) continue;
      (gruppi[serr] = gruppi[serr] || {pezzi:[], syst:new Set()}).pezzi.push({prof, il, ruolo});
      gruppi[serr].syst.add(syst);
    }
  }
  for(const [serr, g] of Object.entries(gruppi)){
    const P = g.pezzi;
    const has = c => P.some(p=>p.prof===c);
    if(P.some(p=>p.ruolo==='MNT'||p.ruolo==='TRV')){
      esiti.composte.push(`${serr} (${P.length} pezzi, con montanti/traversi T)`); continue;
    }
    const serie = (has('B23007C')||has('B23021C')||has('B23022C')||has('B23610C')) ? 'C82S-CS' : 'C75S';
    const tel = [...new Set(P.filter(p=>p.ruolo==='TEL' && !/B2340/.test(p.prof)).map(p=>p.il))].sort((a,b)=>a-b);
    const bat = [...new Set(P.filter(p=>p.ruolo==='BAT').map(p=>p.il))].sort((a,b)=>a-b);
    const soglia = has('B23401')||has('B23402');
    const nAnte = Math.round(P.filter(p=>p.ruolo==='BAT' && (p.prof==='B23122C') && p.il===Math.max(...bat,0)).length / 2);
    let H=null, L=null;
    if(bat.length){                               // H dall'anta: montante anta = H-43
      const hCand = Math.max(...bat) + 43;
      H = tel.find(x=>Math.abs(x-hCand)<0.6) || hCand;
      L = tel.find(x=>Math.abs(x-H)>0.6) || tel[0];
    } else if(tel.length>=2){ L=tel[0]; H=tel[1]; esiti.avvisi.push(`${serr}: fisso, L/H assegnate per dimensione (verifica)`); }
    else if(tel.length===1){ L=H=tel[0]; }
    if(!L||!H){ esiti.avvisi.push(`${serr}: misure non ricavabili, saltato`); continue; }
    const stulp = has('B23505C');
    const b23100 = has('B23100');
    let tid, battuta=null, base=null;
    const pref = serie==='C75S' ? 'C75S' : 'C82S';
    if(!bat.length) tid = `${pref}_TELAIO_FISSO`;
    else if(nAnte>=2){ tid = `${pref}_FIN_2ANTE`; battuta = stulp?'stulp':(b23100?'b23100':'stulp'); }
    else tid = soglia ? `${pref}_PB_1ANTA` : `${pref}_FIN_1ANTA`;
    if(soglia){ tid = nAnte>=2 ? `${pref}_PB_2ANTE` : `${pref}_PB_1ANTA`; base='soglia'; }
    const t = DATI.tipologie.find(x=>x.id===tid);
    if(!t){ esiti.avvisi.push(`${serr}: tipologia ${tid} non trovata, saltato`); continue; }
    const v = t.varianti||{};
    esiti.righe.push({tid, codTip: serr.replace(/[^A-Za-z0-9_\-]/g,'').toUpperCase()||t.cod,
      mat:null, battuta, mano:'dx', hm:null, blocal:false,
      telaio: v.telaio? v.telaio.standard:null, anta: v.anta? v.anta.standard:null,
      traverso: v.traverso? v.traverso.standard:null, vetro:'29', base,
      L: Math.round(L*10)/10, H: Math.round(H*10)/10, q:1});
  }
  return esiti;
}

function esportaArchivioDati(){
  const testa = "// Archivio dati Commesse LMT65 - Nord Infissi\n" +
    "// Sezioni: tipologie[] (id, serie, forma, profili, varianti) - ded (detrazioni e articoli T per serie)\n" +
    "//          drain (drenaggi per serie) - maico (scontri, maniglie, forbici) - faccia_fisica (orientamento profili)\n" +
    "//          dxf_sez (sezioni profili) - libreria[] (lavorazioni) - vetri, sezioni_img\n" +
    "// Per una serie nuova: aggiungere voci in tipologie, ded, drain, dxf_sez con la stessa struttura.\n" +
    "// Salvare come dati_serie.js nella cartella del programma: viene letto all'avvio e fuso con i dati interni.\n";
  const blob = new Blob([testa + 'window.DATI_ESTERNI = ' + JSON.stringify(DATI, null, 1) + ';\n'], {type:'text/javascript'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'dati_serie.js'; a.click();
  URL.revokeObjectURL(a.href);
}
function iniziaImporta(){
  const btn = $('#btn-importa'), fi = $('#file-importa');
  if(!btn || !fi) return;
  btn.addEventListener('click', ()=>fi.click());
  fi.addEventListener('change', ()=>{
    const f = fi.files && fi.files[0]; if(!f) return;
    const fr = new FileReader();
    fr.onload = ()=>{
      const buf = new Uint8Array(fr.result);
      let testo;
      if(buf[0]===0xFF && buf[1]===0xFE) testo = new TextDecoder('utf-16le').decode(buf);
      else if(buf[0]===0xFE && buf[1]===0xFF) testo = new TextDecoder('utf-16be').decode(buf);
      else testo = new TextDecoder('utf-8').decode(buf);
      const e = importaJobTesto(testo);
      e.righe.forEach(r=>righe.push(r));
      disegnaRighe();
      let msg = `Importati ${e.righe.length} serramenti dal job.`;
      if(e.composte.length) msg += ` Composte da ricostruire nel COSTRUTTORE: ${e.composte.join('; ')}.`;
      if(e.avvisi.length) msg += ` Avvisi: ${e.avvisi.join(' | ')}`;
      msg += ' Verifica vetro (importato 29 di default), mano e maniglia, poi Calcola.';
      $('#esito').textContent = msg;
      fi.value = '';
    };
    fr.readAsArrayBuffer(f);
  });
}

// ---------- popup lavorazioni dall'anteprima ----------
function pezziRigaCorrente(){
  const r0 = leggiRigaCorrente(true);
  if(!r0) return null;
  righe.push(r0);
  let calc;
  try{ calc = calcolaCommessa(); } finally { righe.pop(); }
  const pref = 'R'+righe.length+1; // ultima riga aggiunta = indice righe.length (dopo il pop: righe.length+1)
  const prefix = 'R'+(righe.length+1);
  return calc.pezzi.filter(p=>p.unita===prefix || p.unita.startsWith(prefix+'.') || p.unita.startsWith(prefix+'-'));
}
function apriPopupLav(lato){
  const pezzi = pezziRigaCorrente();
  if(!pezzi) return;
  const perLato = {
    giu: p=>/Traverso stipite/.test(p.desc)&&/01$/.test(p.cod) || /Soglia/.test(p.desc),
    su:  p=>/Traverso stipite/.test(p.desc)&&/02$/.test(p.cod),
    sx:  p=>/Montante stipite/.test(p.desc)&&/01$/.test(p.cod),
    dx:  p=>/Montante stipite/.test(p.desc)&&/02$/.test(p.cod),
    anta:p=>/battente|Stulp|centrale/i.test(p.desc)
  };
  const sel = (pezzi.filter(perLato[lato]||(()=>false)));
  const nomi = {giu:'Traverso inferiore', su:'Traverso superiore', sx:'Montante sinistro', dx:'Montante destro', anta:'Anta'};
  let corpo = '';
  const daMostrare = sel.length? sel : [];
  if(!daMostrare.length) corpo = '<p style="font-size:.8rem">Nessun pezzo trovato per questo lato.</p>';
  daMostrare.forEach(p=>{
    corpo += `<div style="margin-bottom:.6rem"><div style="font-size:.78rem;margin-bottom:.2rem">
      <b class="num">${p.cod}</b> — ${p.desc} · ${p.art} · <span class="num">${fmt(p.mm)} mm</span> · ${p.al===135?'45':'90'}°/${p.ar===135?'45':'90'}°</div>
      ${p.lav.length? svgPezzoLav(p) : '<div style="font-size:.74rem;color:var(--acciaio)">Nessuna lavorazione su questo pezzo (solo taglio).</div>'}</div>`;
  });
  $('#popup-lav-titolo').textContent = nomi[lato]||lato;
  $('#popup-lav-corpo').innerHTML = corpo;
  const pl = $('#popup-lav');
  pl.style.display = 'flex';
  if(!pl.dataset.pronto){
    pl.dataset.pronto = '1';
    pl.addEventListener('click', e=>{ if(e.target===pl) pl.style.display='none'; });
    const pc = $('#popup-lav-chiudi');
    if(pc) pc.addEventListener('click', ()=>{ pl.style.display='none'; });
  }
}
function iniziaPopupLav(){
  const pr = $('#prospetto');
  if(pr) pr.addEventListener('click', e=>{
    let n = e.target;
    while(n && n.getAttribute && !n.getAttribute('data-cella') && !n.getAttribute('data-giunto') && !n.getAttribute('data-giuntoo') && !n.getAttribute('data-lato')) n = n.parentNode;
    if(!n || !n.getAttribute) return;
    const cella = n.getAttribute('data-cella'), giunto = n.getAttribute('data-giunto'),
          giuntoO = n.getAttribute('data-giuntoo'), lato = n.getAttribute('data-lato');
    if(cella){ const [r,c] = cella.split(',').map(Number); ciclaCella(r, c); return; }
    if(giunto!==null && giunto!==undefined && giunto!==''){ commutaGiunto(+giunto); return; }
    if(giuntoO!==null && giuntoO!==undefined && giuntoO!==''){ commutaGiuntoO(+giuntoO); return; }
    if(lato) apriPopupLav(lato);
  });
  const pl = $('#popup-lav');
  if(pl) pl.addEventListener('click', e=>{ if(e.target===pl) pl.style.display='none'; });
  const pc = $('#popup-lav-chiudi');
  if(pc) pc.addEventListener('click', ()=>{ $('#popup-lav').style.display='none'; });
}


// ---------- importazione ordine da job XML (FP Pro / formato macchina) ----------
function importaJobTesto(testo){
  const pulito = testo.replace(/^\uFEFF/,'').replace(/encoding="UTF-16(LE|BE)?"/i,'encoding="UTF-8"');
  const dom = new DOMParser().parseFromString(pulito, 'text/xml');
  if(dom.getElementsByTagName('parsererror').length)
    throw new Error('XML non valido: ' + dom.getElementsByTagName('parsererror')[0].textContent.slice(0,120));
  const gruppi = {};
  [...dom.getElementsByTagName('BAR')].forEach(bar=>{
    const syst = (bar.getElementsByTagName('SYST')[0]||{}).textContent || '';
    let prof = '';
    for(const fig of bar.children){ if(fig.tagName==='CODE'){ prof = fig.textContent; break; } }
    [...bar.getElementsByTagName('CUT')].forEach(cut=>{
      const il = parseFloat((cut.getElementsByTagName('IL')[0]||{}).textContent || '0');
      const lbls = [...cut.getElementsByTagName('LBL')].map(e=>e.textContent.trim());
      const ruolo = (lbls[2]||'').trim();
      const serr = ((lbls[3]||'').trim() || '?').replace(/\.(L|H)$/,'');
      (gruppi[serr] = gruppi[serr] || {syst:{}, pezzi:[]}).pezzi.push({prof, il, ruolo});
      gruppi[serr].syst[syst] = (gruppi[serr].syst[syst]||0)+1;
    });
  });
  const esiti = {ok:[], saltati:[]};
  for(const [serr, g] of Object.entries(gruppi)){
    const serie = Object.keys(g.syst).sort((a,b)=>g.syst[b]-g.syst[a]).find(s=>s.startsWith('C7')||s.startsWith('C8')) || 'C75S';
    const serieApp = serie.startsWith('C82') ? 'C82S-CS' : 'C75S';
    const tel = g.pezzi.filter(p=>p.ruolo==='TEL');
    const bat = g.pezzi.filter(p=>p.ruolo==='BAT');
    const mnt = g.pezzi.filter(p=>p.ruolo==='MNT'), trv = g.pezzi.filter(p=>p.ruolo==='TRV');
    const stulp = g.pezzi.some(p=>/B23505/.test(p.prof));
    const soglia = g.pezzi.some(p=>/B2340[12]/.test(p.prof));
    const b100 = g.pezzi.some(p=>/B23100/.test(p.prof));
    if(!tel.length){ esiti.saltati.push(serr+' (senza telaio)'); continue; }
    const lung = [...new Set(tel.map(p=>p.il))].sort((a,b)=>a-b);
    let L, H;
    if(lung.length===1){ L = H = lung[0]; }
    else {
      const montBat = Math.max(0, ...bat.map(p=>p.il));
      H = lung.find(v=>Math.abs(v-(montBat+43))<2) || Math.max(...lung);
      L = lung.find(v=>v!==H) || H;
    }
    if(mnt.length || trv.length){ esiti.saltati.push(`${serr} ${L}x${H} (composta: ricostruiscila nel COSTRUTTORE)`); continue; }
    let tid = null, battuta = null;
    const pre = serieApp==='C75S' ? 'C75S' : 'C82S';
    if(!bat.length) tid = pre+'_TELAIO_FISSO';
    else if(stulp || b100){ tid = pre+'_FIN_2ANTE'; battuta = stulp?'stulp':'b23100'; }
    else tid = soglia ? pre+'_PB_1ANTA' : pre+'_FIN_1ANTA';
    if(soglia && (stulp||b100)) tid = pre+'_PB_2ANTE';
    const t = DATI.tipologie.find(x=>x.id===tid);
    if(!t){ esiti.saltati.push(`${serr} (${tid} non in archivio)`); continue; }
    const uguale = righe.find(r=>r.tid===tid && r.L===L && r.H===H && r.battuta===battuta);
    if(uguale) uguale.q += 1;
    else righe.push({tid, codTip: serr.replace(/[^A-Za-z0-9_\-]/g,'').toUpperCase().slice(0,10)||t.cod,
      mat:null, battuta, mano:'dx', hm:null, blocal:false,
      telaio: (DATI.varianti_telaio?.[t.serie]?.standard) || $('#r-telaio').value,
      anta: $('#r-anta').value, traverso: $('#r-traverso').value,
      vetro: $('#r-vetro').value, base: soglia?'soglia':null, L, H, q:1});
    esiti.ok.push(`${serr} → ${t.nome} ${L}×${H}`);
  }
  disegnaRighe();
  $('#esito').innerHTML = `<b>Import:</b> ${esiti.ok.length} serramenti caricati.` +
    (esiti.saltati.length? `<br>Non importati (${esiti.saltati.length}): ${esiti.saltati.join('; ')}` : '') +
    `<br><span class="nota-piccola">Verifica vetro, mano e maniglia: il job non li contiene. Vasistas importati come 1 anta.</span>`;
  return esiti;
}

function esportaArchivioDati(){
  const testa = "// Archivio dati Commesse LMT65 - Nord Infissi\n" +
    "// Sezioni: tipologie[] (id, serie, forma, profili, varianti) - ded (detrazioni e articoli T per serie)\n" +
    "//          drain (drenaggi per serie) - maico (scontri, maniglie, forbici) - faccia_fisica (orientamento profili)\n" +
    "//          dxf_sez (sezioni profili) - libreria[] (lavorazioni) - vetri, sezioni_img\n" +
    "// Per una serie nuova: aggiungere voci in tipologie, ded, drain, dxf_sez con la stessa struttura.\n" +
    "// Salvare come dati_serie.js nella cartella del programma: viene letto all'avvio e fuso con i dati interni.\n";
  const blob = new Blob([testa + 'window.DATI_ESTERNI = ' + JSON.stringify(DATI, null, 1) + ';\n'], {type:'text/javascript'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'dati_serie.js'; a.click();
  URL.revokeObjectURL(a.href);
}
function iniziaImporta(){
  const btn = $('#btn-importa'), inp = $('#file-importa');
  if(!btn || !inp) return;
  btn.addEventListener('click', ()=>inp.click());
  inp.addEventListener('change', ()=>{
    const f = inp.files && inp.files[0]; if(!f) return;
    const fr = new FileReader();
    fr.onload = ()=>{
      const buf = new Uint8Array(fr.result);
      let testo;
      if((buf[0]===0xFF&&buf[1]===0xFE) || buf[1]===0) testo = new TextDecoder('utf-16le').decode(fr.result);
      else if(buf[0]===0xFE&&buf[1]===0xFF) testo = new TextDecoder('utf-16be').decode(fr.result);
      else testo = new TextDecoder('utf-8').decode(fr.result);
      try{ importaJobTesto(testo); }
      catch(e){ $('#esito').textContent = 'File non riconosciuto come job macchina: '+e.message; }
      inp.value='';
    };
    fr.readAsArrayBuffer(f);
  });
}

// ---------- uscite a video ----------
function mostra(){
  const calc = calcolaCommessa();
  if(!calc.pezzi.length){ $('#esito').textContent='Aggiungi almeno una riga.'; return null; }
  const barre = ottimizza(calc.pezzi);

  // distinta
  let idxPezzo = 0; const schemi = {};
  const perProfilo = {};
  calc.pezzi.forEach(p=>{ (perProfilo[p.art]=perProfilo[p.art]||[]).push(p); });
  let h = '<table><thead><tr><th>Profilo</th><th>Descrizione</th><th>Unità</th><th class="n">Lungh. (mm)</th><th class="n">Angoli</th><th>Lavorazioni</th></tr></thead><tbody>';
  Object.entries(perProfilo).forEach(([art,lista])=>{
    h += `<tr class="gruppo"><td colspan="6">${art} — ${lista.length} pezzi, ${fmt(lista.reduce((s,p)=>s+p.mm,0))} mm</td></tr>`;
    lista.forEach(p=>{
      const conLav = p.lav.length>0;
      const idp = 'plav'+(idxPezzo++);
      if(conLav) schemi[idp] = p;
      h += `<tr${conLav? ` class="riga-lav" data-p="${idp}" title="Tocca per vedere le lavorazioni"`:''}>
        <td class="num">${art}</td><td><span class="num"><b>${p.cod}</b></span> ${p.desc}<br><span class="nota-piccola">[${p.tcod}] ${p.tip}</span></td>
        <td class="num">${p.unita}</td><td class="n">${fmt(p.mm)}</td>
        <td class="n">${p.al===135?'45':'90'}°/${p.ar===135?'45':'90'}°</td>
        <td>${conLav? `<span class="lav-badge">${p.lav.length} lav ▾</span>` : '—'}</td></tr>`;
      if(conLav) h += `<tr class="riga-schema" id="${idp}" style="display:none"><td colspan="6">${svgPezzoLav(p)}</td></tr>`;
    });
  });
  h += '</tbody></table>';
  if(calc.erroriFormule.length)
    h = `<div class="avviso">Formule non calcolabili (verifica a catalogo): ${calc.erroriFormule.join(' · ')}</div>` + h;
  $('#out-distinta').innerHTML = h; $('#sez-distinta').style.display='block';
  document.querySelectorAll('.riga-lav').forEach(tr=>tr.addEventListener('click', ()=>{
    const det = document.getElementById(tr.dataset.p);
    if(det) det.style.display = det.style.display==='none' ? 'table-row' : 'none';
  }));

  // barre
  const stock = parseFloat($('#c-barra').value)||6500;
  let hb=''; let nb=0;
  barre.forEach(b=>{ nb++;
    const usati = b.stock - b.resto;
    hb += `<div class="barra-viz"><div class="etichetta">
      <span><b>${b.art}</b> — barra ${nb} (${fmt(b.stock)} mm)</span>
      <span class="num">sfrido ${fmt(b.resto)} mm</span></div><div class="asta">`;
    b.pezzi.forEach(p=>{ hb += `<div class="pezzo" style="width:${(p.mm/b.stock*100).toFixed(2)}%">${Math.round(p.mm)}</div>`; });
    hb += `</div></div>`;
  });
  $('#out-barre').innerHTML = hb; $('#sez-barre').style.display='block';

  // fabbisogno
  const conteggioBarre = {};
  barre.forEach(b=>conteggioBarre[b.art]=(conteggioBarre[b.art]||0)+1);
  let hf = '<table><thead><tr><th>Voce</th><th>Descrizione</th><th class="n">Quantità</th></tr></thead><tbody>';
  hf += `<tr class="gruppo"><td colspan="3">Profili (barre da ${fmt(stock)} mm)</td></tr>`;
  Object.entries(conteggioBarre).forEach(([art,n])=>{
    hf += `<tr><td class="num">${art}</td><td>barre a magazzino</td><td class="n">${n}</td></tr>`;});
  hf += '<tr class="gruppo"><td colspan="3">Accessori</td></tr>';
  Object.entries(calc.accessori).forEach(([k,v])=>{ const [art,desc]=k.split('|');
    const q = v.pz? v.pz+' pz' : '—'; const extra = v.mm? ` (${fmt(v.mm)} mm)` : '';
    hf += `<tr><td class="num">${art}</td><td>${desc}${extra}</td><td class="n">${q}</td></tr>`;});
  hf += '<tr class="gruppo"><td colspan="3">Guarnizioni</td></tr>';
  Object.entries(calc.guarnizioni).forEach(([k,mm])=>{ const [art,desc]=k.split('|');
    hf += `<tr><td class="num">${art}</td><td>${desc}</td><td class="n">${(mm/1000).toFixed(1)} m</td></tr>`;});
  hf += '<tr class="gruppo"><td colspan="3">Vetri</td></tr>';
  calc.vetri.forEach(v=>{
    hf += `<tr><td class="num">${v.q}×</td><td>${v.tip} — ${v.unita} (sp. ${v.sp} mm)</td><td class="n">${fmt(v.l)} × ${fmt(v.h)}</td></tr>`;});
  hf += '</tbody></table>';
  $('#out-fabb').innerHTML = hf; $('#sez-fabb').style.display='block';
  $('#esito').textContent = `${calc.pezzi.length} pezzi su ${barre.length} barre.`;
  return {calc, barre};
}

// ---------- generazione file JOB ----------
function xmlLav(l, x){
  return macchina(l.w, l.descr, x, l.y, (l.z||0), l.f, l.v1, l.v2, l.v3, l.ut);
}
function macchina(w, descr, x, y, z, faccia, v1, v2, v3, ut){
  return `          <MACHINING WCODE="${w}" OFFSET="${x}" OFFSETY="${y}" OFFSETZ="${z}" FORMULAX="" FORMULAY="" FORMULAZ="" FACE="${faccia}" TIPOLAV="" VAR1="${v1}" VAR2="${v2}" VAR3="${v3}" VAR4="" VAR5="" ANGLE="0" VERPERC="0" P1X="0" P1Y="0" P1Z="0" P2X="0" P2Y="0" P2Z="0" P3X="0" P3Y="0" P3Z="0" INVERSEPATHONMULTIPLANES="0" EMPTYGROVE="0" BREAKSHAVING="0" CODUTENSILE="${ut}" CILINLAV="2" OFFSETFIN="0" CODUTEFIN="0" CILLAVFIN="0" DESCRIPTION="${descr}" SGRAVANZ="0" SGRUSCITA="0" SRGLAV="0" SGRROT="0" VARPROFSGR="0" FINAVANZ="0" FINUSCITA="0" FINLAV="0" FINROT="0" VARPROFFIN="0" EXECUTIONLEVEL="1" IDCATEGORY="1" POSDEF="" ENABLELOAD="" IDMACHINING="0" CLAMPNEAR="0" STARTCONNECTION="0" ENDCONNECTION="0" TIPOSTAZIONE="Lavorazione" STATION_ID="" NUMEROSOTTOLAVORAZIONI="1" NUMEROFORIANUBATRICE="0" NUMEROANUBATURE="0" SGRTIPO="2" FINTIPO="0" STATION_EXTRA_DATA="10">\r\n            <FORBIDDENSPACES />\r\n            <PIANI>\r\n              <PIANO START="0" THICK="2" AVANZAMENTO="0" ROTAZIONE="0" />\r\n            </PIANI>\r\n          </MACHINING>`;
}
function xmlPezzo(num, p, commessa){
  const h = DATI.altezze[p.art]||50;
  const n45 = (p.al===135?1:0)+(p.ar===135?1:0);
  const ol = Math.round((p.mm - n45*h)*1000)/1000;
  const lav = p.lav.map(l=>xmlLav(l, l.x)).join('\r\n');
  const blocco = lav? `\r\n        <MACHININGS>\r\n${lav}\r\n        </MACHININGS>` : '\r\n        <MACHININGS />';
  return `      <CUT>\r\n        <NUM>${num}</NUM>\r\n        <NUMEXE>0</NUMEXE>\r\n        <TINA />\r\n        <ANGL>${p.al}</ANGL>\r\n        <ANGR>${p.ar}</ANGR>\r\n        <AB1>90</AB1>\r\n        <AB2>90</AB2>\r\n        <IL>${p.mm}</IL>\r\n        <OL>${ol}</OL>\r\n        <TRML>0</TRML>\r\n        <TL1>0</TL1>\r\n        <TAL>90</TAL>\r\n        <TRMR>0</TRMR>\r\n        <TL2>0</TL2>\r\n        <TAR>90</TAR>\r\n        <TLON>0</TLON>\r\n        <TRON>0</TRON>\r\n        <TLMTON>0</TLMTON>\r\n        <TRMTON>0</TRMTON>\r\n        <MARGIN1>0</MARGIN1>\r\n        <MARGIN2>0</MARGIN2>\r\n        <BCOD>${commessa}.${p.unita}</BCOD>\r\n        <EXTERNAL_ID>0</EXTERNAL_ID>\r\n        <CSNA />\r\n        <CSNU />\r\n        <ORCD>genIA</ORCD>\r\n        <ORDCDQTY>1</ORDCDQTY>\r\n        <DESC>${commessa}.${p.unita}.${p.cod}</DESC>\r\n        <CID />\r\n        <IDQUADRO />\r\n        <FRNU />\r\n        <STAT>0</STAT>\r\n        <SUBAREA_BARRA>0</SUBAREA_BARRA>\r\n        <PEZZO_RIFATTO>0</PEZZO_RIFATTO>\r\n        <RT>\r\n          <Vx />\r\n          <Vy />\r\n          <T />\r\n        </RT>\r\n        <AREA>0</AREA>\r\n        <STOP>0</STOP>\r\n        <PRINT_LABEL>1</PRINT_LABEL>\r\n        <LBL>${commessa} ${p.unita} ${p.cod}</LBL>${blocco}\r\n      </CUT>`;
}
function xmlBarra(b, num, serie, commessa){
  const stock = b.stock;
  const cuts = b.pezzi.map((p,i)=>xmlPezzo(i+1,p,commessa)).join('\r\n');
  const h = DATI.altezze[b.art]||50;
  return `    <BAR>\r\n      <BRAN>FP_PRO</BRAN>\r\n      <SYST>${serie}</SYST>\r\n      <CODE>${b.art}</CODE>\r\n      <DESC>${commessa}.${b.art}</DESC>\r\n      <DICL />\r\n      <DOCL />\r\n      <LEN>${stock}</LEN>\r\n      <LENR>0</LENR>\r\n      <H>${h}</H>\r\n      <MLT>-1</MLT>\r\n      <POS>0</POS>\r\n      <ICL />\r\n      <OCL />\r\n      <SCRI>0</SCRI>\r\n      <SCRF>0</SCRF>\r\n      <LREUSAB>0</LREUSAB>\r\n      <SCRP>0</SCRP>\r\n      <CTIM>0</CTIM>\r\n      <CTSP>0</CTSP>\r\n      <SVL>0</SVL>\r\n      <IVL>0</IVL>\r\n      <VROT>0</VROT>\r\n      <VU1S>0</VU1S>\r\n      <VU1D>0</VU1D>\r\n      <VU2S>0</VU2S>\r\n      <VU2D>0</VU2D>\r\n      <SCP>0</SCP>\r\n      <BRS>0</BRS>\r\n      <IFS>0</IFS>\r\n      <BS1L>0</BS1L>\r\n      <BS1R>0</BS1R>\r\n      <BS2L>0</BS2L>\r\n      <BS2R>0</BS2R>\r\n      <PRPZ>0</PRPZ>\r\n      <PRMA>0</PRMA>\r\n      <PRMB>0</PRMB>\r\n      <PRMO>0</PRMO>\r\n      <PRMV>0</PRMV>\r\n      <STMV>0</STMV>\r\n      <MXBN>0</MXBN>\r\n      <W>${h}</W>\r\n      <ENTH>0</ENTH>\r\n      <COLOR />\r\n      <DXF />\r\n      <REV>0</REV>\r\n      <INNESTABILE>0</INNESTABILE>\r\n      <NUM>${num}</NUM>\r\n      <PRIORITA>0</PRIORITA>\r\n      <STATOBARRA>0</STATOBARRA>\r\n      <STATOCONGELATO>0</STATOCONGELATO>\r\n      <MODELLO_CON_ERRORI>0</MODELLO_CON_ERRORI>\r\n      <ID_ESTERNO />\r\n      <OFFESET_X>0</OFFESET_X>\r\n      <OFFESET_Y>0</OFFESET_Y>\r\n      <OFFESET_Z>0</OFFESET_Z>\r\n      <OFFESET_YCLOSE>0</OFFESET_YCLOSE>\r\n      <VIRTPLATE />\r\n${cuts}\r\n      <AREE_ROVINATE />\r\n      <TIMES />\r\n      <TEMPI_CN_START />\r\n      <TEMPI_CN_END />\r\n    </BAR>`;
}
function generaJob(){
  const r = mostra(); if(!r) return;
  const commessa = ($('#c-codice').value.trim()||'COMMESSA').replace(/[^A-Za-z0-9_\-\.]/g,'_');
  const seriePer = {}; r.calc.pezzi.forEach(p=>seriePer[p.art]=p.serie);
  const barsXml = r.barre.map((b,i)=>xmlBarra(b, i+1, (seriePer[b.art]||'C75S').replace('C82S-CS','C82S_CS'), commessa)).join('\r\n');
  const doc = `<?xml version="1.0" encoding="UTF-16"?>\r\n<JOB>\r\n  <JINF>\r\n    <NUM>0</NUM>\r\n  </JINF>\r\n  <BODY>\r\n${barsXml}\r\n  </BODY>\r\n  <JOBIMAGES />\r\n</JOB>\r\n`;
  // UTF-16LE con BOM
  const buf = new Uint8Array(2 + doc.length*2);
  buf[0]=0xFF; buf[1]=0xFE;
  for(let i=0;i<doc.length;i++){ const c=doc.charCodeAt(i); buf[2+2*i]=c&255; buf[3+2*i]=c>>8; }
  scarica(new Blob([buf],{type:'application/xml'}), `JOB_${commessa}.xml`);
  $('#esito').textContent = `File JOB_${commessa}.xml generato: importalo in FSTLine e verifica a video prima di produrre.`;
}
function scarica(blob, nome){
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = nome; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href), 3000);
}

// ---------- salva / apri commessa ----------
function salvaCommessa(){
  const dati = {codice:$('#c-codice').value, rif:$('#c-rif').value, barra:$('#c-barra').value,
    lama:$('#c-lama').value, fermavetroSi:$('#c-fermavetro-si').value,
    dren:$('#c-dren').checked, foro8:$('#c-foro8').checked, righe};
  scarica(new Blob([JSON.stringify(dati,null,1)],{type:'application/json'}),
    `commessa_${($('#c-codice').value||'senza_nome').replace(/\W/g,'_')}.json`);
}
function apriCommessa(file){
  const fr = new FileReader();
  fr.onload = () => { try{
    const d = JSON.parse(fr.result);
    $('#c-codice').value=d.codice||''; $('#c-rif').value=d.rif||'';
    $('#c-barra').value=d.barra||'6500'; $('#c-lama').value=d.lama||'6';
    $('#c-fermavetro-si').value=d.fermavetroSi||'si';
    $('#c-dren').checked=!!d.dren; $('#c-foro8').checked=!!d.foro8;
    righe.length=0; (d.righe||[]).forEach(x=>righe.push(x));
    disegnaRighe(); $('#esito').textContent='Commessa caricata.';
  }catch(e){ $('#esito').textContent='File commessa non leggibile.'; } };
  fr.readAsText(file);
}

// ---------- avvio ----------
iniziaSelettori(); disegnaRighe(); disegnaLibreria('tutte');
iniziaPopupLav();
const be=$('#btn-esporta-dati'); if(be) be.addEventListener('click', esportaArchivioDati);
[['#g-mont-piu',1,0],['#g-mont-meno',-1,0],['#g-trav-piu',0,1],['#g-trav-meno',0,-1]].forEach(([id,dc,dr])=>{
  const b=$(id); if(b) b.addEventListener('click', ()=>{
    $('#m-cols').value = Math.max(1, (parseInt($('#m-cols').value,10)||1)+dc);
    $('#m-rows').value = Math.max(1, (parseInt($('#m-rows').value,10)||1)+dr);
    rigeneraMatrice(false); aggiornaAnteprima();
  });
});
iniziaImporta();
iniziaImporta();
const bl=$('#btn-libreria'); if(bl) bl.addEventListener('click', apriLibreria);
const bt=$('#btn-tarature'); if(bt) bt.addEventListener('click', apriTarature);
const ls=$('#lib-serie'); if(ls) ls.addEventListener('change', disegnaLavDef);
const lr=$('#btn-lib-ripristina'); if(lr) lr.addEventListener('click', ()=>{ if(confirm('Ripristinare le definizioni di serie (si perdono le modifiche fatte in questo browser)?')) ripristinaLavDef(); });
const bct=$('#btn-chiudi-tarature'); if(bct) bct.addEventListener('click', chiudiTarature);
const bnt=$('#btn-nuova-taratura'); if(bnt) bnt.addEventListener('click', ()=>nuovaTaratura());
const bc=$('#btn-chiudi-libreria'); if(bc) bc.addEventListener('click', chiudiLibreria);
document.querySelectorAll('.filtro-lav').forEach(b=>b.addEventListener('click', ()=>{
  document.querySelectorAll('.filtro-lav').forEach(x=>x.classList.remove('primario'));
  b.classList.add('primario');
  disegnaLibreria(b.dataset.el);
}));
$('#btn-aggiungi').addEventListener('click', aggiungiRiga);
$('#btn-calcola').addEventListener('click', mostra);
$('#btn-job').addEventListener('click', generaJob);
$('#btn-stampa').addEventListener('click', ()=>{ mostra(); window.print(); });
$('#btn-salva').addEventListener('click', salvaCommessa);
$('#btn-apri-btn').addEventListener('click', ()=>$('#btn-apri').click());
$('#btn-apri').addEventListener('change', e=>{ if(e.target.files[0]) apriCommessa(e.target.files[0]); e.target.value=''; });



// ---------- porte D67/D77: lavorazioni (segnaposto, vedi modulo porte) ----------
if(typeof lavPorta!=='function'){ window.lavPorta = function(){ return []; }; }
