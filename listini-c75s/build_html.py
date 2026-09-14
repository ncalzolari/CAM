#!/usr/bin/env python3
# Versione HTML del generatore di listini a griglia: stessi dati e stesse formule di genera_listini.py,
# parametri e ferramenta modificabili a video, griglie ricalcolate al volo, scarico degli xlsx (SheetJS, formule vive).
# Produce Listini_C75S.html (autonomo, download diretti) e Listini_C75S_web.html (Artifact: download via capability).
import json, os, io, contextlib, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
with contextlib.redirect_stdout(io.StringIO()):   # importare lo script rigenera anche gli xlsx (li tiene allineati)
    import genera_listini as g

DATI = {
  "param": g.PARAM, "fonte": g.FONTE, "art_tt": g.ART_TT, "art_n": g.ART_N, "pesi": g.PESI, "prz": g.PRZ,
  "tip": {k: {"nome": t["nome"], "ore": t["ore"], "profili": t["profili"], "acc": t["acc"],
              "guarn": [[round(p, 6), m] for p, m in t["guarn"]], "L": t["L"], "H": t["H"],
              "anta": t.get("anta"), "due": bool(t.get("due"))} for k, t in g.TIP.items()},
  "kit": [[d, crit, ranges, q] for d, crit, ranges, q in g.KIT_ANTA],
  "fisse_anta": [[d, c or "", q, m] for d, c, q, m in g.FERR_FISSE_ANTA],
  "semifissa": [[d, c or "", q, m] for d, c, q, m in g.FERR_SEMIFISSA],
  "netto": {c: round(p, 4) for c, p in g.NETTO.items()},
  "ordine": ["FISSO", "F1", "F2", "PF1", "PF2"],
}

HTML = r'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Listini C75S</title>
<style>
  :root{--fondo:#EDEFF1;--carta:#fff;--inchiostro:#1B2328;--acciaio:#5C6B76;--linea:#D4D9DD;--rosso:#BE1622;--rosso-scuro:#8F1019;--verde:#1F7A4D;--giallo:#B77800;--mono:"Consolas","Cascadia Mono",ui-monospace,monospace}
  *{box-sizing:border-box;margin:0}
  html{font-size:15px}
  body{background:var(--fondo);color:var(--inchiostro);font-family:"Segoe UI",system-ui,-apple-system,sans-serif;padding:0 0 4rem}
  header{background:var(--inchiostro);color:#fff;padding:1.1rem 1.6rem;display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap}
  header h1{font-size:1.25rem;font-weight:600}
  header h1 b{background:var(--rosso);padding:.1em .45em;margin-right:.5rem;letter-spacing:.05em}
  header .sotto{color:#9FB0BC;font-size:.85rem}
  main{max-width:1280px;margin:1.4rem auto;padding:0 1.2rem;display:grid;gap:1.2rem}
  section{background:var(--carta);border:1px solid var(--linea)}
  section>h2{font-size:.8rem;text-transform:uppercase;letter-spacing:.12em;color:#fff;background:var(--rosso);padding:.45rem .9rem;font-weight:700}
  section>.corpo{padding:1rem 1.1rem}
  label{display:block;font-size:.78rem;color:var(--acciaio);margin-bottom:.25rem}
  input,select{font:inherit;padding:.4rem .5rem;border:1px solid var(--linea);background:#FBFCFC;width:100%;color:inherit}
  input.giallo{background:#FFF9C4}
  input:focus,select:focus,button:focus-visible{outline:2px solid var(--rosso);outline-offset:1px}
  button{font:inherit;font-weight:600;border:1px solid var(--inchiostro);background:var(--inchiostro);color:#fff;padding:.5rem 1rem;cursor:pointer}
  button:hover{background:#000}
  button.primario{background:var(--rosso);border-color:var(--rosso-scuro)}
  button.primario:hover{background:var(--rosso-scuro)}
  .param{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))}
  .num{font-family:var(--mono);font-variant-numeric:tabular-nums}
  table{border-collapse:collapse;font-size:.85rem}
  th{font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:var(--acciaio);text-align:left;border-bottom:2px solid var(--inchiostro);padding:.35rem .45rem}
  td{border-bottom:1px solid var(--linea);padding:.3rem .45rem;vertical-align:middle}
  td.n,th.n{text-align:right;font-family:var(--mono)}
  .scroll{overflow-x:auto}
  table.griglia td,table.griglia th{text-align:right;font-family:var(--mono);padding:.25rem .4rem;white-space:nowrap}
  table.griglia th.h,table.griglia td.h{background:#F4F6F7;font-weight:700}
  table.griglia td.sel{background:#FCE8E9;font-weight:700}
  .nota{font-size:.78rem;color:var(--acciaio)}
  .azioni{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;margin:.6rem 0}
  .tabs{display:flex;gap:.3rem;flex-wrap:wrap;margin-bottom:.8rem}
  .tabs button{background:#fff;color:var(--inchiostro)}
  .tabs button.attiva{background:var(--rosso);color:#fff;border-color:var(--rosso-scuro)}
  .ok{color:var(--verde);font-weight:600}
  .avviso{background:#FCF4E4;border-left:4px solid var(--giallo);padding:.5rem .8rem;font-size:.85rem;margin:.5rem 0}
  #esito{min-height:1.2em;font-size:.85rem}
  .riq{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fit,minmax(18rem,1fr))}
  table.griglia td.neg{color:var(--rosso);font-weight:700}
  table.griglia td.bassa{background:#FCF4E4}
  #sez-margine{border-color:var(--inchiostro)}
  #sez-margine>h2{background:var(--inchiostro)}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
</head>
<body>
<header><h1><b>LMT 65</b> Listini a griglia AluK C75S</h1><span class="sotto">senza vetro · RAL 7016 · stesse formule di genera_listini.py · <span id="fonte"></span></span></header>
<main>
<section><h2>Parametri (modificabili: tutte le griglie si ricalcolano)</h2><div class="corpo">
  <div class="param" id="param"></div>
  <div class="azioni"><button class="primario" id="btn-ricalcola">Ricalcola</button><button id="btn-reset" class="spoglio" style="background:none;color:var(--rosso);border:none;padding:0">ripristina valori di consegna</button>
    <span class="nota">Le griglie si ricalcolano a ogni modifica (anche mentre scrivi); le modifiche restano salvate in questo browser. Prezzi profili: taglio termico = codici B (art. <span id="art-tt"></span>), normali = N/K e fermavetri (art. <span id="art-n"></span>).</span></div>
</div></section>

<section><h2>Tipologia</h2><div class="corpo">
  <div class="tabs" id="tabs"></div>
  <div class="riq">
    <div><h3 style="font-size:.8rem;letter-spacing:.1em;color:var(--rosso);margin-bottom:.4rem">COEFFICIENTI</h3><table id="tab-coef"></table></div>
    <div><h3 style="font-size:.8rem;letter-spacing:.1em;color:var(--rosso);margin-bottom:.4rem">FERRAMENTA MAICO — kit per la misura interrogata</h3><div class="nota" style="margin-bottom:.3rem">Kit dipendente da FFB/FFH (anta − 20) secondo il poolfile WinPlus del 14/09/2026; prezzi dal netto 2025. Prezzo, codice e quantità delle voci fisse sono modificabili (celle gialle) e valgono per tutte le misure.</div><div class="scroll"><table id="tab-ferr"></table></div></div>
    <div><h3 style="font-size:.8rem;letter-spacing:.1em;color:var(--rosso);margin-bottom:.4rem">INTERROGAZIONE MISURA</h3>
      <div class="param" style="grid-template-columns:1fr 1fr"><div><label>L (mm)</label><input id="q-l" type="number" step="10"></div><div><label>H (mm)</label><input id="q-h" type="number" step="10"></div></div>
      <table id="tab-q" style="margin-top:.5rem;width:100%"></table></div>
  </div>
  <div class="azioni" style="margin-top:1rem"><button class="primario" id="btn-listino-xlsx">Scarica listino di vendita (xlsx, un foglio per tipologia)</button><button id="btn-csv">Scarica CSV del listino di questa tipologia</button><span id="esito"></span></div>
  <div class="nota">Le esportazioni contengono solo i prezzi di listino. L'xlsx completo con costi, coefficienti e ferramenta si scarica dalla sezione riservata.</div>
  <h3 style="font-size:.8rem;letter-spacing:.1em;color:var(--rosso);margin:.6rem 0 .4rem" id="tit-listino"></h3>
  <div class="scroll"><table class="griglia" id="grid-listino"></table></div>
  <h3 style="font-size:.8rem;letter-spacing:.1em;color:var(--rosso);margin:1rem 0 .4rem">COSTO SERRAMENTO (materiale scontato + sfrido + ferramenta + manodopera)</h3>
  <div class="scroll"><table class="griglia" id="grid-costo"></table></div>
  <p class="nota" style="margin-top:.6rem">Derivati dalle distinte catalogo AluK C75S sez. 8 e pesi kg/m catalogo v3. Manodopera: 1h telaio + 1h/anta + 20' ferramenta/anta + 20'/vetro. Prezzi a 0 in ferramenta = da inserire (ignorati finché vuoti). Scrivendo un codice Maico nella riga, il prezzo viene preso dal netto 2025 incorporato (__NNETTO__ codici); se il codice non c'è, il prezzo si inserisce a mano.</p>
</div></section>
<section id="sez-margine"><h2>Marginalità (riservata)</h2><div class="corpo">
  <div id="mg-chiuso">
    <div class="param" style="grid-template-columns:12rem auto;align-items:end"><div><label>Codice di sblocco</label><input id="mg-codice" type="password" inputmode="numeric" autocomplete="off"></div><div><button class="primario" id="btn-sblocca">Sblocca</button> <span id="mg-msg" class="nota"></span></div></div>
  </div>
  <div id="mg-aperto" hidden>
    <div class="param" style="grid-template-columns:12rem 12rem 1fr auto;align-items:end">
      <div><label>Sconto al cliente sul listino (%)</label><input id="mg-sconto" class="giallo num" type="number" step="0.5" min="0" max="99" value="0"></div>
      <div><label>Costo orario diretto manodopera (€/h)</label><input id="mg-hdir" class="giallo num" type="number" step="0.5" min="0" value="28"></div>
      <div class="nota">Marginalità = (netto cliente − costo) / netto cliente. Netto = listino × (1 − sconto). Il costo è quello della griglia COSTO (materiale scontato + sfrido + ferramenta + manodopera). Spese generali = ore × (tariffa oraria − costo orario diretto); il peso è calcolato sul costo.</div>
      <div><button id="btn-xlsx-completo">Scarica xlsx completo (costi e formule, questa tipologia)</button> <button id="btn-blocca">Blocca</button></div>
    </div>
    <div class="riq" style="margin-top:.8rem">
      <div><h3 style="font-size:.8rem;letter-spacing:.1em;color:var(--rosso);margin-bottom:.4rem">MISURA INTERROGATA</h3><table id="mg-q" style="width:100%"></table></div>
      <div><h3 style="font-size:.8rem;letter-spacing:.1em;color:var(--rosso);margin-bottom:.4rem">SCALETTA SCONTO → MARGINALITÀ (misura interrogata)</h3><div class="scroll"><table class="griglia" id="mg-scala"></table></div></div>
    </div>
    <h3 style="font-size:.8rem;letter-spacing:.1em;color:var(--rosso);margin:1rem 0 .4rem" id="mg-tit"></h3>
    <div class="scroll"><table class="griglia" id="grid-margine"></table></div>
  </div>
</div></section>
</main>
<script>
const DATI = /*__DATI__*/;
const $ = s=>document.querySelector(s);
const PARAM_DEF = [
  ['eur_kg_tt', 'Prezzo profili taglio termico €/kg', 0.01], ['eur_kg_n', 'Prezzo profili normali €/kg', 0.01],
  ['sc_prof', 'Sconto profili (0,43 = 43%)', 0.01], ['sc_acc', 'Sconto accessori/guarnizioni', 0.01],
  ['sfrido', 'Sfrido', 0.01], ['eur_h', 'Tariffa oraria manodopera €/h', 0.5], ['ricarico', 'Ricarico su costo totale (2,13 = +213%)', 0.01]];
let P = Object.assign({}, DATI.param); let tipo = 'F1';
let PRZ_OVR = {};                                   // prezzo €/pz forzato per codice (vale per tutte le misure)
let FISSE = {anta: DATI.fisse_anta.map(r=>r.slice()), semifissa: DATI.semifissa.map(r=>r.slice())};   // [desc, cod, q, prezzo manuale]
try{ const s = localStorage.getItem('listini_param'); if(s) Object.assign(P, JSON.parse(s)); }catch(e){}
try{ const s = localStorage.getItem('listini_przovr'); if(s) PRZ_OVR = JSON.parse(s); }catch(e){}
try{ const s = localStorage.getItem('listini_fisse'); if(s){ const f = JSON.parse(s); ['anta','semifissa'].forEach(k=>{ if(f[k] && f[k].length===FISSE[k].length) FISSE[k] = f[k]; }); } }catch(e){}
function salva(){ try{ localStorage.setItem('listini_param', JSON.stringify(P)); localStorage.setItem('listini_przovr', JSON.stringify(PRZ_OVR)); localStorage.setItem('listini_fisse', JSON.stringify(FISSE)); }catch(e){} }
const prezzoNetto = cod => (cod in PRZ_OVR) ? PRZ_OVR[cod] : (cod in DATI.netto ? DATI.netto[cod] : null);
function dimAnta(k, L, H){ const t = DATI.tip[k]; if(!t.anta) return null; return t.anta.map(f=>{ const [cL,cH,c]=lin(f); return cL*L+cH*H+c; }); }
function kitMaico(k, L, H){                          // -> [{desc, cod, q, pr, fonte, fisso:idx|null}]
  const t = DATI.tip[k]; if(!t.anta) return [];
  const [aw, ah] = dimAnta(k, L, H), ffb = aw-20, ffh = ah-20; const out = [];
  DATI.kit.forEach(([desc, crit, ranges, q])=>{ const v = crit==='ffb' ? ffb : ffh;
    for(const [lo, hi, codes] of ranges){ if(v>=lo && v<=hi){ codes.forEach(c=>{ const pr = prezzoNetto(c); out.push({desc, cod:c, q, pr: pr==null?0:pr, fonte: c in PRZ_OVR ? 'manuale' : (c in DATI.netto ? 'netto 2025' : 'da inserire')}); }); break; } } });
  const fisse = FISSE.anta.map((r,i)=>({r, gruppo:'anta', i})).concat(t.due ? FISSE.semifissa.map((r,i)=>({r, gruppo:'semifissa', i})) : []);
  fisse.forEach(({r, gruppo, i})=>{ const [desc, cod, q, man] = r; const pn = cod ? prezzoNetto(cod) : null;
    const pr = pn!=null ? pn : (man!=null ? man : 0);
    out.push({desc: desc+(cod?'':' — DA INSERIRE'), cod, q, pr, fonte: !cod ? 'da inserire' : (cod in PRZ_OVR ? 'manuale' : (cod in DATI.netto ? 'netto 2025' : (man!=null ? 'manuale' : 'da inserire'))), fisso:{gruppo, i}}); });
  return out;
}
function costoFerr(k, L, H){ return r2(kitMaico(k, L, H).reduce((s,r)=>s+r.q*r.pr, 0)); }
const r2 = x=>Math.round((x+Number.EPSILON)*100)/100;
const fmt = x=>x.toLocaleString('it-IT',{minimumFractionDigits:2, maximumFractionDigits:2});
function lin(expr){ let cL=0,cH=0,c=0; const e = expr.replace(/\s/g,''); const re=/([+-]?)(L|H)(\/2)?|([+-]?\d+(?:\.\d+)?)/g; let m;
  while((m=re.exec(e))){ const s = m[1]==='-'?-1:1; if(m[2]){ const v = m[3]?0.5:1; if(m[2]==='L') cL+=s*v; else cH+=s*v; } else if(m[4]) c+=parseFloat(m[4]); } return [cL,cH,c]; }
function coef(k){ const t = DATI.tip[k]; const tt=[0,0,0], nn=[0,0,0];
  t.profili.forEach(([art,pz,mis])=>{ const [cL,cH,c]=lin(mis); const p=DATI.pesi[art]/1000; const a = art.startsWith('B')?tt:nn; a[0]+=pz*p*c; a[1]+=pz*p*cL; a[2]+=pz*p*cH; });
  let gC=0,gL=0,gH=0; t.guarn.forEach(([pr,mis])=>{ const [cL,cH,c]=lin(mis); const p=pr/1000; gL+=p*cL; gH+=p*cH; gC+=p*c; });
  const acc = t.acc.reduce((s,[a,q])=>s+DATI.prz[a]*q,0);
  return {tt, nn, g:[gC,gL,gH], acc, ore:t.ore, k}; }
function costo(c, L, H){ const kgT=c.tt[0]+c.tt[1]*L+c.tt[2]*H, kgN=c.nn[0]+c.nn[1]*L+c.nn[2]*H, gua=c.g[0]+c.g[1]*L+c.g[2]*H; const ferr = costoFerr(c.k, L, H);
  const co = r2(((kgT*P.eur_kg_tt+kgN*P.eur_kg_n)*(1-P.sc_prof)+(gua+c.acc)*(1-P.sc_acc))*(1+P.sfrido)+ferr+c.ore*P.eur_h);
  return {kgT, kgN, gua, ferr, costo:co, listino:r2(co*(1+P.ricarico))}; }
const range = ([a,b])=>{ const o=[]; for(let v=a; v<=b; v+=100) o.push(v); return o; };
function disegnaParam(){ $('#param').innerHTML = PARAM_DEF.map(([k,lab,st])=>`<div><label>${lab}</label><input class="giallo num" type="number" step="${st}" data-p="${k}" value="${P[k]}"></div>`).join('');
  document.querySelectorAll('[data-p]').forEach(i=>i.addEventListener('input', ()=>{ P[i.dataset.p]=parseFloat(String(i.value).replace(',','.'))||0; salva(); disegnaTipo(); })); }
function disegnaTipo(){
  const t = DATI.tip[tipo], c = coef(tipo);
  $('#tabs').innerHTML = DATI.ordine.map(k=>`<button data-t="${k}" class="${k===tipo?'attiva':''}">${DATI.tip[k].nome}</button>`).join('');
  document.querySelectorAll('[data-t]').forEach(b=>b.addEventListener('click', ()=>{ tipo=b.dataset.t; disegnaTipo(); }));
  const righeC = [['Peso taglio termico costante (kg)',c.tt[0]],['… per mm di L (kg/mm)',c.tt[1]],['… per mm di H (kg/mm)',c.tt[2]],['Peso normali costante (kg)',c.nn[0]],['… per mm di L (kg/mm)',c.nn[1]],['… per mm di H (kg/mm)',c.nn[2]],
    ['Guarnizioni costante (€ listino)',c.g[0]],['… per mm di L (€/mm)',c.g[1]],['… per mm di H (€/mm)',c.g[2]],['Accessori totale (€ listino)',c.acc],['Ore manodopera',c.ore]];
  $('#tab-coef').innerHTML = righeC.map(([l,v])=>`<tr><td>${l}</td><td class="n">${(+v).toFixed(v<0.01?6:3)}</td></tr>`).join('');
  const ql0 = $('#q-l'), qh0 = $('#q-h'); if(!ql0.value || +ql0.value<t.L[0] || +ql0.value>t.L[1]) ql0.value = Math.min(1000, t.L[1]); if(!qh0.value || +qh0.value<t.H[0] || +qh0.value>t.H[1]) qh0.value = Math.max(t.H[0], Math.min(1500, t.H[1]));
  const fr = kitMaico(tipo, +ql0.value, +qh0.value); const ferrTot = costoFerr(tipo, +ql0.value, +qh0.value);
  const da = t.anta ? dimAnta(tipo, +ql0.value, +qh0.value) : null;
  $('#tab-ferr').innerHTML = fr.length ? `<tr><th colspan="6" class="nota" style="text-transform:none;letter-spacing:0">Anta ${da[0].toFixed(1)} × ${da[1].toFixed(1)} → FFB ${(da[0]-20).toFixed(0)} / FFH ${(da[1]-20).toFixed(0)}</th></tr><tr><th>Componente</th><th>Codice</th><th class="n">Q.tà</th><th class="n">€/pz</th><th class="n">Sub.</th><th>Fonte</th></tr>` +
    fr.map((r,i)=>{ const f = r.fisso; return `<tr><td style="font-size:.78rem">${f ? `<input class="giallo" data-fd="${f.gruppo}|${f.i}" value="${String(FISSE[f.gruppo][f.i][0]).replace(/"/g,'&quot;')}" style="width:11rem;font-size:.78rem">` : r.desc}</td>
      <td>${f ? `<input class="giallo num" data-fc="${f.gruppo}|${f.i}" value="${r.cod}" style="width:5.6rem" placeholder="codice">` : `<span class="num">${r.cod}</span>`}</td>
      <td>${f ? `<input class="giallo num" type="number" step="1" data-fq="${f.gruppo}|${f.i}" value="${r.q}" style="width:3.6rem">` : `<span class="num">${r.q}</span>`}</td>
      <td><input class="giallo num" type="number" step="0.01" data-fp="${r.cod||('#'+f.gruppo+'|'+f.i)}" value="${r.pr}" style="width:5.2rem"></td><td class="n">${fmt(r.q*r.pr)}</td><td class="nota">${r.fonte}</td></tr>`; }).join('') +
    `<tr><td><b>TOTALE FERRAMENTA (questa misura)</b></td><td></td><td></td><td></td><td class="n"><b>${fmt(ferrTot)}</b></td><td></td></tr>` : '<tr><td class="nota">Nessuna ferramenta (telaio fisso)</td></tr>';
  const rif = el=>{ const [gr,i] = el.dataset.fd ? el.dataset.fd.split('|') : (el.dataset.fc||el.dataset.fq).split('|'); return FISSE[gr][+i]; };
  document.querySelectorAll('[data-fd]').forEach(i=>i.addEventListener('change', ()=>{ rif(i)[0]=i.value.trim(); salva(); disegnaTipo(); }));
  document.querySelectorAll('[data-fc]').forEach(i=>i.addEventListener('change', ()=>{ const r = rif(i); r[1]=i.value.trim(); salva(); disegnaTipo(); }));
  document.querySelectorAll('[data-fq]').forEach(i=>i.addEventListener('change', ()=>{ rif(i)[2]=parseFloat(i.value)||0; salva(); disegnaTipo(); }));
  document.querySelectorAll('[data-fp]').forEach(i=>i.addEventListener('change', ()=>{ const key = i.dataset.fp; const v = parseFloat(String(i.value).replace(',','.'))||0;
    if(key.startsWith('#')){ const [gr,ix] = key.slice(1).split('|'); FISSE[gr][+ix][3] = v; } else { if(v===DATI.netto[key]) delete PRZ_OVR[key]; else PRZ_OVR[key] = v; } salva(); disegnaTipo(); }));
  const Ls = range(t.L), Hs = range(t.H);
  const qL = +ql0.value, qH = +qh0.value, q = costo(c, qL, qH);
  $('#tab-q').innerHTML = [['kg taglio termico', q.kgT.toFixed(3)+' × '+P.eur_kg_tt+' €/kg'], ['kg normali', q.kgN.toFixed(3)+' × '+P.eur_kg_n+' €/kg'],
    ['Profili scontati', fmt((q.kgT*P.eur_kg_tt+q.kgN*P.eur_kg_n)*(1-P.sc_prof))], ['Guarnizioni + accessori scontati', fmt((q.gua+c.acc)*(1-P.sc_acc))],
    ['Sfrido', fmt(((q.kgT*P.eur_kg_tt+q.kgN*P.eur_kg_n)*(1-P.sc_prof)+(q.gua+c.acc)*(1-P.sc_acc))*P.sfrido)], ['Ferramenta Maico (kit per questa misura)', fmt(q.ferr)], ['Manodopera', c.ore.toFixed(2)+' h = '+fmt(c.ore*P.eur_h)],
    ['<b>COSTO</b>', '<b>'+fmt(q.costo)+'</b>'], ['<b>LISTINO</b>', '<b>'+fmt(q.listino)+'</b>']].map(([a,b])=>`<tr><td>${a}</td><td class="n">${b}</td></tr>`).join('');
  $('#tit-listino').textContent = `LISTINO — ${t.nome} — C75S SENZA VETRO — RAL 7016 (costo +${Math.round(P.ricarico*100)}%)`;
  const griglia = (id, campo)=>{ $(id).innerHTML = '<tr><th class="h">H \\ L</th>'+Ls.map(L=>`<th class="h">${L}</th>`).join('')+'</tr>' +
    Hs.map(H=>`<tr><td class="h">${H}</td>`+Ls.map(L=>`<td class="${L===qL&&H===qH?'sel':''}">${fmt(costo(c,L,H)[campo])}</td>`).join('')+'</tr>').join(''); };
  griglia('#grid-listino','listino'); griglia('#grid-costo','costo');
  disegnaMargine();
}
['#q-l','#q-h'].forEach(id=>$(id).addEventListener('input', disegnaTipo));
$('#btn-ricalcola').addEventListener('click', ()=>{ document.querySelectorAll('[data-p]').forEach(i=>{ P[i.dataset.p]=parseFloat(String(i.value).replace(',','.'))||0; }); salva(); disegnaTipo(); $('#esito').textContent='Griglie ricalcolate.'; });
$('#btn-reset').addEventListener('click', ()=>{ P = Object.assign({}, DATI.param); PRZ_OVR = {}; FISSE = {anta: DATI.fisse_anta.map(r=>r.slice()), semifissa: DATI.semifissa.map(r=>r.slice())}; salva(); disegnaParam(); disegnaTipo(); });
// ---- xlsx con formule vive (stessa struttura di genera_listini.py) ----
function workbook(k){
  const t = DATI.tip[k], c = coef(k), X = XLSX; const wb = X.utils.book_new();
  const Ls = range(t.L), Hs = range(t.H);
  const ws = {}; const set = (r,col,v)=>{ ws[X.utils.encode_cell({r:r-1,c:col-1})] = typeof v==='object' ? v : (typeof v==='number' ? {t:'n', v} : {t:'s', v:String(v)}); };
  const qL = +$('#q-l').value, qH = +$('#q-h').value; const Lrif = (t.L[0]<=qL && qL<=t.L[1]) ? qL : t.L[0], Hrif = (t.H[0]<=qH && qH<=t.H[1]) ? qH : t.H[0];
  const fr = kitMaico(k, Lrif, Hrif).map(r=>[r.desc+(r.cod?` (${r.cod})`:''), r.q, r.pr, null, r.fonte]); const totRow = 2+fr.length;
  const col = j=>X.utils.encode_col(j-1);
  const fCosto = (Lr,Hr,ft)=>{ const C='Coefficienti!$B$', Pp='Parametri!$B$';
    const kgT=`(${C}1+${C}2*${Lr}+${C}3*${Hr})`, kgN=`(${C}4+${C}5*${Lr}+${C}6*${Hr})`, gua=`(${C}7+${C}8*${Lr}+${C}9*${Hr})`;
    return `ROUND(((${kgT}*${Pp}1+${kgN}*${Pp}2)*(1-${Pp}3)+(${gua}+${C}10)*(1-${Pp}4))*(1+${Pp}5)+${ft}+${C}11*${Pp}6,2)`; };
  const griglia = (r0, titolo, f)=>{ set(r0,1,titolo); set(r0+1,1,'H/L'); Ls.forEach((L,j)=>set(r0+1,2+j,L)); Hs.forEach((H,i)=>set(r0+2+i,1,H));
    Hs.forEach((H,i)=>Ls.forEach((L,j)=>{ const Lr=`${col(2+j)}$${r0+1}`, Hr=`$A${r0+2+i}`, ft=`FerrGriglia!${col(2+j)}${2+i}`; set(r0+2+i,2+j,{t:'n', f:f(Lr,Hr,ft), z:'0.00'}); })); return r0+2+Hs.length; };
  const r = griglia(1, `LISTINO — ${t.nome} — C75S SENZA VETRO — RAL 7016 (costo +${Math.round(P.ricarico*100)}%)`, (Lr,Hr,ft)=>`ROUND(${fCosto(Lr,Hr,ft)}*(1+Parametri!$B$7),2)`);
  griglia(r+2, 'COSTO SERRAMENTO (materiale scontato + sfrido + manodopera)', fCosto);
  ws['!ref'] = X.utils.encode_range({s:{r:0,c:0}, e:{r:r+2+2+Hs.length, c:1+Ls.length}}); ws['!cols'] = [{wch:8}].concat(Ls.map(()=>({wch:9})));
  X.utils.book_append_sheet(wb, ws, 'Prezzo');
  const wp = X.utils.aoa_to_sheet([[`Prezzo profili taglio termico €/kg (${DATI.art_tt} CAT.B +ADD — RAL 7016)`, P.eur_kg_tt],[`Prezzo profili normali €/kg (${DATI.art_n} CAT.B +ADD — fermavetri, aggiuntivi, gocciolatoio)`, P.eur_kg_n],
    ['Sconto profili su listino AluK C75S/C82S-CS', P.sc_prof],['Sconto accessori/guarnizioni su listino AluK', P.sc_acc],['Sfrido', P.sfrido],['Tariffa oraria manodopera €/h', P.eur_h],['Ricarico su costo totale', P.ricarico],[],
    ['Celle gialle = valori modificabili: tutte le griglie si ricalcolano.'],[`Prezzi: ${DATI.fonte}. Ferramenta: prezzi nel foglio dedicato.`]]);
  wp['!cols'] = [{wch:70},{wch:12}]; X.utils.book_append_sheet(wb, wp, 'Parametri');
  const wc = X.utils.aoa_to_sheet([['Peso profili taglio termico costante (kg)',c.tt[0]],['Peso taglio termico per mm di L (kg/mm)',c.tt[1]],['Peso taglio termico per mm di H (kg/mm)',c.tt[2]],['Peso profili normali costante (kg)',c.nn[0]],['Peso normali per mm di L (kg/mm)',c.nn[1]],['Peso normali per mm di H (kg/mm)',c.nn[2]],
    ['Guarnizioni costante (€ listino)',c.g[0]],['Guarnizioni per mm di L (€/mm)',c.g[1]],['Guarnizioni per mm di H (€/mm)',c.g[2]],['Accessori totale (€ listino)',c.acc],['Ore manodopera',c.ore],[],
    ['Derivati dalle distinte catalogo AluK C75S sez. 8 e pesi kg/m catalogo v3.'],['Taglio termico = codici B (stipite, anta, battuta centrale, soglia); normali = N/K (aggiuntivo, gocciolatoio, fermavetri).'],[`Prezzi unitari accessori e guarnizioni (pre-sconto): ${DATI.fonte}.`]]);
  wc['!cols'] = [{wch:46},{wch:14}]; X.utils.book_append_sheet(wb, wc, 'Coefficienti');
  const wf = X.utils.aoa_to_sheet([['Componente','Q.tà','Prezzo €/pz','Subtotale €','Fonte','',`Kit Maico per la misura ${Lrif}x${Hrif} (FFB/FFH = anta-20). Le griglie usano il foglio FerrGriglia (kit per ogni misura).`]].concat(fr));
  fr.forEach((r,i)=>{ wf[X.utils.encode_cell({r:i+1,c:3})] = {t:'n', f:`B${i+2}*C${i+2}`, z:'0.00'}; });
  if(fr.length) wf[X.utils.encode_cell({r:totRow-1,c:0})] = {t:'s', v:'TOTALE FERRAMENTA'}; else wf[X.utils.encode_cell({r:1,c:0})] = {t:'s', v:'Nessuna ferramenta (telaio fisso)'};
  wf[X.utils.encode_cell({r:totRow-1,c:3})] = fr.length ? {t:'n', f:`SUM(D2:D${totRow-1})`, z:'0.00'} : {t:'n', v:0};
  wf['!ref'] = X.utils.encode_range({s:{r:0,c:0}, e:{r:totRow, c:4}}); wf['!cols'] = [{wch:44},{wch:6},{wch:11},{wch:12},{wch:12}];
  X.utils.book_append_sheet(wb, wf, 'Ferramenta');
  const wg = X.utils.aoa_to_sheet([['H/L'].concat(Ls)].concat(Hs.map(H=>[H].concat(Ls.map(L=>costoFerr(k,L,H))))).concat([[], ['Costo ferramenta Maico per misura (kit da regole WinPlus + voci fisse). Valori, non formule: rigenerare dalla pagina.']]));
  X.utils.book_append_sheet(wb, wg, 'FerrGriglia');
  return wb;
}
function scarica(dati, nome){   // dati: Uint8Array (xlsx) o stringa (csv)
  const tipoMime = nome.endsWith('.csv') ? 'text/csv;charset=utf-8' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([dati], {type: tipoMime})); a.download = nome; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href), 3000);
  $('#esito').textContent = `File ${nome} generato.`;
}
function xlsxBytes(wb){ return new Uint8Array(XLSX.write(wb, {bookType:'xlsx', type:'array'})); }
function senzaXlsx(){ if(typeof XLSX==='undefined'){ $('#esito').textContent = 'Libreria xlsx non caricata (serve la connessione la prima volta): usa il CSV.'; return true; } return false; }
function workbookListino(){   // solo prezzi di vendita: un foglio per tipologia, valori
  const X = XLSX, wb = X.utils.book_new();
  DATI.ordine.forEach(k=>{ const t = DATI.tip[k], c = coef(k), Ls = range(t.L), Hs = range(t.H);
    const aoa = [[`LISTINO — ${t.nome} — C75S SENZA VETRO — RAL 7016`], ['H/L'].concat(Ls)].concat(Hs.map(H=>[H].concat(Ls.map(L=>costo(c,L,H).listino))));
    aoa.push([], [`Prezzi di listino in €, IVA esclusa. ${DATI.fonte}. Generato il ${new Date().toLocaleDateString('it-IT')}.`]);
    const ws = X.utils.aoa_to_sheet(aoa); Hs.forEach((H,i)=>Ls.forEach((L,j)=>{ const cell = ws[X.utils.encode_cell({r:i+2,c:j+1})]; if(cell) cell.z='0.00'; }));
    ws['!cols'] = [{wch:8}].concat(Ls.map(()=>({wch:9}))); X.utils.book_append_sheet(wb, ws, k); });
  return wb;
}
$('#btn-listino-xlsx').addEventListener('click', ()=>{ if(senzaXlsx()) return; scarica(xlsxBytes(workbookListino()), 'LISTINO_C75S_SENZA_VETRO.xlsx'); });
$('#btn-xlsx-completo').addEventListener('click', ()=>{ if(!mgAperto || senzaXlsx()) return; scarica(xlsxBytes(workbook(tipo)), `${tipo}_SENZA_VETRO_COMPLETO.xlsx`); });
$('#btn-csv').addEventListener('click', ()=>{ const t = DATI.tip[tipo], c = coef(tipo); const Ls = range(t.L), Hs = range(t.H);
  const righe = [['H/L'].concat(Ls)].concat(Hs.map(H=>[H].concat(Ls.map(L=>fmt(costo(c,L,H).listino)))));
  scarica('\ufeff'+righe.map(r=>r.join(';')).join('\r\n'), `${tipo}_LISTINO.csv`); });
// ---- marginalità riservata: codice confrontato per impronta (SHA-256, ripiego FNV-1a), sblocco valido per la sessione ----
const MG_H = '5e2f06eeba88cde592c16bb86d5898064130a5895abd2d3408f967ab3546b69c', MG_F = 2138287407;
function fnv1a(t){ let x = 0x811c9dc5; for(const ch of new TextEncoder().encode(t)){ x ^= ch; x = Math.imul(x, 0x01000193) >>> 0; } return x; }
async function impronta(t){ try{ if(crypto && crypto.subtle){ const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(t)); return [...new Uint8Array(d)].map(b=>b.toString(16).padStart(2,'0')).join(''); } }catch(e){} return null; }
let mgAperto = false; try{ mgAperto = sessionStorage.getItem('mg_aperto')==='1'; }catch(e){}
function mgStato(){ $('#mg-chiuso').hidden = mgAperto; $('#mg-aperto').hidden = !mgAperto; if(mgAperto) disegnaMargine(); }
async function sblocca(){ const t = $('#mg-codice').value.trim(); const h = await impronta(t); const ok = h ? h===MG_H : fnv1a(t)===MG_F;
  if(!ok){ $('#mg-msg').textContent = 'Codice errato.'; $('#mg-codice').value=''; return; }
  mgAperto = true; try{ sessionStorage.setItem('mg_aperto','1'); }catch(e){} $('#mg-msg').textContent=''; $('#mg-codice').value=''; mgStato(); }
$('#btn-sblocca').addEventListener('click', sblocca); $('#mg-codice').addEventListener('keydown', e=>{ if(e.key==='Enter') sblocca(); });
$('#btn-blocca').addEventListener('click', ()=>{ mgAperto = false; try{ sessionStorage.removeItem('mg_aperto'); }catch(e){} mgStato(); });
try{ const sc = localStorage.getItem('mg_sconto'); if(sc!=null) $('#mg-sconto').value = sc; }catch(e){}
$('#mg-sconto').addEventListener('input', ()=>{ try{ localStorage.setItem('mg_sconto', $('#mg-sconto').value); }catch(e){} disegnaMargine(); });
try{ const hd = localStorage.getItem('mg_hdir'); if(hd!=null) $('#mg-hdir').value = hd; }catch(e){}
$('#mg-hdir').addEventListener('input', ()=>{ try{ localStorage.setItem('mg_hdir', $('#mg-hdir').value); }catch(e){} disegnaMargine(); });
const pct = x=>(x*100).toLocaleString('it-IT',{minimumFractionDigits:1, maximumFractionDigits:1})+' %';
function margine(q, sc){ const netto = r2(q.listino*(1-sc)); const m = netto - q.costo; return {netto, m, pm: netto>0 ? m/netto : -1}; }
function disegnaMargine(){
  if(!mgAperto) return;
  const t = DATI.tip[tipo], c = coef(tipo); const sc = (parseFloat(String($('#mg-sconto').value).replace(',','.'))||0)/100;
  const Ls = range(t.L), Hs = range(t.H); const qL = +$('#q-l').value, qH = +$('#q-h').value; const q = costo(c, qL, qH), mg = margine(q, sc);
  const hdir = parseFloat(String($('#mg-hdir').value).replace(',','.'))||0; const mdir = c.ore*hdir, sg = c.ore*(P.eur_h-hdir);
  $('#mg-q').innerHTML = [['Misura', qL+' × '+qH], ['Listino', fmt(q.listino)], ['Sconto', pct(sc)], ['Netto cliente', fmt(mg.netto)], ['Costo', fmt(q.costo)],
    ['&nbsp;&nbsp;di cui manodopera diretta ('+c.ore.toFixed(2)+' h × '+hdir+' €/h)', fmt(mdir)],
    ['&nbsp;&nbsp;<b>di cui spese generali</b> ('+c.ore.toFixed(2)+' h × '+(P.eur_h-hdir).toFixed(2)+' €/h)', '<b>'+fmt(sg)+'</b>'],
    ['&nbsp;&nbsp;peso spese generali sul costo', q.costo>0 ? pct(sg/q.costo) : '-'],
    ['<b>Margine €</b>', '<b>'+fmt(mg.m)+'</b>'], ['<b>Marginalità</b>', '<b>'+pct(mg.pm)+'</b>'], ['Ricarico effettivo sul costo', q.costo>0 ? pct(mg.netto/q.costo-1) : '-']].map(([a,b])=>`<tr><td>${a}</td><td class="n">${b}</td></tr>`).join('');
  const scale = [0,5,10,15,20,25,30,35,40,45,50,55,60];
  $('#mg-scala').innerHTML = '<tr><th class="h">Sconto</th>'+scale.map(x=>`<th class="h">${x}%</th>`).join('')+'</tr>' +
    '<tr><td class="h">Netto</td>'+scale.map(x=>`<td>${fmt(margine(q,x/100).netto)}</td>`).join('')+'</tr>' +
    '<tr><td class="h">Margin.</td>'+scale.map(x=>{ const m=margine(q,x/100); return `<td class="${m.pm<0?'neg':(m.pm<0.2?'bassa':'')}">${pct(m.pm)}</td>`; }).join('')+'</tr>';
  $('#mg-tit').textContent = `MARGINALITÀ % — ${t.nome} — sconto cliente ${pct(sc)}`;
  $('#grid-margine').innerHTML = '<tr><th class="h">H \\ L</th>'+Ls.map(L=>`<th class="h">${L}</th>`).join('')+'</tr>' +
    Hs.map(H=>`<tr><td class="h">${H}</td>`+Ls.map(L=>{ const m = margine(costo(c,L,H), sc); return `<td class="${m.pm<0?'neg':(m.pm<0.2?'bassa':'')}${L===qL&&H===qH?' sel':''}">${pct(m.pm)}</td>`; }).join('')+'</tr>').join('');
}
$('#fonte').textContent = DATI.fonte; $('#art-tt').textContent = DATI.art_tt; $('#art-n').textContent = DATI.art_n;
disegnaParam(); disegnaTipo(); mgStato();
</script>
</body>
</html>
'''
html = HTML.replace('/*__DATI__*/', json.dumps(DATI, ensure_ascii=False)).replace('__NNETTO__', str(len(g.NETTO)))
open(os.path.join(HERE, 'Listini_C75S.html'), 'w', encoding='utf-8').write(html)
# versione web (Artifact): senza doctype/html/head/body, download tramite capability
w = html
for tag in ['<!DOCTYPE html>\n', '<html lang="it">\n', '<head>\n', '<meta charset="utf-8">\n', '<meta name="viewport" content="width=device-width, initial-scale=1">\n', '</head>\n', '<body>\n', '</body>\n', '</html>\n']:
    assert w.count(tag) == 1, tag; w = w.replace(tag, '')
old = """function scarica(dati, nome){   // dati: Uint8Array (xlsx) o stringa (csv)
  const tipoMime = nome.endsWith('.csv') ? 'text/csv;charset=utf-8' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([dati], {type: tipoMime})); a.download = nome; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href), 3000);
  $('#esito').textContent = `File ${nome} generato.`;
}"""
assert w.count(old) == 1
w = w.replace(old, """let __dlCap = null, __dlPronto = false;
if(window.claude && typeof claude.use==='function') claude.use('downloads').then(d=>{ __dlCap = d; __dlPronto = true; }).catch(()=>{ __dlPronto = true; });
let __dlInCorso = false;
function scarica(dati, nome){
  if(!__dlCap){ $('#esito').textContent = __dlPronto ? 'Salvataggio non disponibile in questa vista: usa il file Listini_C75S.html scaricato.' : 'Un attimo: salvataggio in preparazione, riprova.'; return; }
  if(__dlInCorso){ $('#esito').textContent = 'Conferma prima il salvataggio precedente.'; return; }
  __dlInCorso = true; $('#esito').textContent = `Preparo ${nome} (${dati.length} byte)…`;
  __dlCap.save({filename: nome, data: dati}).then(()=>{ $('#esito').textContent = `File ${nome} salvato.`; })
    .catch(e=>{ const c = e && e.code; if(c==='declined'){ $('#esito').textContent = ''; return; }
      $('#esito').textContent = c==='rate_limited' ? 'Attendi: una richiesta di salvataggio è ancora aperta.' : 'Salvataggio non riuscito: ' + ((e && (e.message||e.code)) || e); })
    .finally(()=>{ __dlInCorso = false; });
}""")
open(os.path.join(HERE, 'Listini_C75S_web.html'), 'w', encoding='utf-8').write(w)
print('html:', len(html), 'bytes; web:', len(w), 'bytes; fonte:', g.FONTE)
