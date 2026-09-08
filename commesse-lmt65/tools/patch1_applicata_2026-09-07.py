import json, re
F = '/home/claude/files/'
js = open(F+'app_logic.js', encoding='utf-8').read()
tpl = open(F+'app_template.html', encoding='utf-8').read()

def rep(src, old, new, n=1):
    c = src.count(old)
    assert c == n, f"atteso {n} trovato {c}: {old[:80]!r}"
    return src.replace(old, new)

# 1) valuta con H1/H2 (sopraluce)
js = rep(js, """function valuta(formula, L, H){
  // "L-42", "L/2-9", "H-29.5", "2L+4H", "L+3H" -> mm
  let s = String(formula).replace(/,/g,'.').replace(/\\s/g,'');
  if(!/^[0-9LH+\\-*/().]+$/.test(s)) return null;
  s = s.replace(/L\\/2/g,'(L/2)').replace(/(\\d)([LH])/g,'$1*$2');
  try{ const v = Function('L','H',`return (${s});`)(L,H); return (isFinite(v)&&v>0)?v:null; }
  catch(e){ return null; }
}""", """function valuta(formula, L, H, r){
  // "L-42", "L/2-9", "H-29.5", "2L+4H", "L+3H" -> mm ; porte con sopraluce: H1 = parte porta, H2 = sopraluce (r.h2)
  let s = String(formula).replace(/,/g,'.').replace(/\\s/g,'');
  if(!/^[0-9LH+\\-*/().]+$/.test(s)) return null;
  const H2 = (r && r.h2>0) ? r.h2 : 0, H1 = H - H2;
  if(/H[12]/.test(s) && !(H2>0)) return null;
  s = s.replace(/H1/g,'A').replace(/H2/g,'B').replace(/L\\/2/g,'(L/2)').replace(/(\\d)([LHAB])/g,'$1*$2');
  try{ const v = Function('L','H','A','B',`return (${s});`)(L,H,H1,H2); return (isFinite(v)&&v>0)?v:null; }
  catch(e){ return null; }
}
const SERIE_INFO = DATI.serie_info || {};
function isPorta(serie){ return !!(SERIE_INFO[serie] && SERIE_INFO[serie].porta); }""")

# 2) codiceProfilo: variante telaio con ala per porte
js = rep(js, """function codiceProfilo(serie, r, art, desc){
  const v = DATI.varianti[serie];""", """function codiceProfilo(serie, r, art, desc){
  const vp = (DATI.varianti_porte||{})[serie];
  if(vp){ return (r.telaio==='ala' && vp.ala[art]) ? vp.ala[art] : art; }
  const v = DATI.varianti[serie];""")

# 3) tavola vetro per porte
js = rep(js, """function tavolaVetro(codProfilo){
  if(DATI.vetrazione.tav702.profili.includes(codProfilo)) return DATI.vetrazione.tav702;""",
"""function tavolaVetro(codProfilo){
  for(const k of Object.keys(DATI.vetrazione)) if(/^tavD/.test(k) && DATI.vetrazione[k].profili.includes(codProfilo)) return DATI.vetrazione[k];
  if(DATI.vetrazione.tav702.profili.includes(codProfilo)) return DATI.vetrazione.tav702;""")

# 4) selettore serie con nome esteso
js = rep(js, """  $('#r-serie').innerHTML = serie.map(s=>`<option>${s}</option>`).join('');""",
"""  $('#r-serie').innerHTML = serie.map(s=>`<option value="${s}">${(SERIE_INFO[s]&&SERIE_INFO[s].nome)||s}</option>`).join('');
  $('#r-h2').addEventListener('input', aggiornaAnteprima);""")

# 5) selettori profili per porte
js = rep(js, """function aggiornaSelettoriProfili(){
  const s = $('#r-serie').value, v = DATI.varianti[s];
  $('#r-telaio').innerHTML""", """function aggiornaSelettoriProfili(){
  const s = $('#r-serie').value, v = DATI.varianti[s];
  if(isPorta(s)){
    const t = DATI.tipologie.find(x=>x.id===$('#r-tip').value) || {};
    const vp = DATI.varianti_porte[s];
    const tel = t.telaio_rif || vp.telaio_int, ala = vp.ala[tel];
    $('#r-telaio').innerHTML = `<option value="std">${tel} — standard</option>` + (ala? `<option value="ala">${ala} — con ala 32 mm</option>` : '');
    $('#r-anta').innerHTML = `<option value="${t.anta_rif||''}">${t.anta_rif||'—'} — anta della tipologia</option>`;
    $('#r-traverso').innerHTML = `<option value="">—</option>`;
    const tav = tavolaVetro(t.anta_rif||'');
    const spess = Object.keys(tav.righe).sort((a,b)=>a-b);
    const def = spess.includes('30')? '30' : spess.includes('46')? '46' : spess[0];
    $('#r-vetro').innerHTML = spess.map(m=>`<option value="${m}" ${m===def?'selected':''}>${m} mm</option>`).join('');
    aggiornaSezioni(); return;
  }
  $('#r-telaio').innerHTML""")

# 6) aggiornaSezioni: porte (maniglia AM, niente Maico / blocal / traverso)
js = rep(js, """  const apribile = t && ['1','P1','1F','2','P2'].includes(t.forma);
  $('#box-blocal').style.display = (t && ['1','1F','2','P1','P2','M'].includes(t.forma)) ? 'block' : 'none';
  $('#box-hm').style.display = apribile ? 'block' : 'none';
  if(apribile) aggiornaHM();""", """  const porta = t && t.porta;
  const apribile = t && ['1','P1','1F','2','P2'].includes(t.forma);
  $('#box-blocal').style.display = (t && !porta && ['1','1F','2','P1','P2','M'].includes(t.forma)) ? 'block' : 'none';
  $('#box-hm').style.display = apribile ? 'block' : 'none';
  if(bt && porta) bt.style.display = 'none';
  const bh2 = $('#box-h2'); if(bh2) bh2.style.display = (porta && t.sopraluce) ? 'block' : 'none';
  const bfp = $('#box-ferr-porta'); if(bfp) bfp.style.display = porta ? 'block' : 'none';
  if(apribile) aggiornaHM();""")

js = rep(js, """function aggiornaHM(forza){
  const H = parseFloat($('#r-h').value)||1400; const hAnta = H-43;""", """function aggiornaHM(forza){
  const tP = DATI.tipologie.find(x=>x.id===$('#r-tip').value);
  if(tP && tP.porta){                                            // porte: altezza maniglia AM dal filo inferiore anta (manuale AluK: 1050)
    if(forza || !$('#r-hm').value || parseFloat($('#r-hm').value)<600) $('#r-hm').value = 1050;
    $('#info-hm').innerHTML = `<div style="font-size:.72rem;line-height:1.5">AM = asse maniglia/serratura dal filo inferiore dell'anta.<br>Standard AluK: <b class="num">1050</b> (manuale lavorazioni 10.71-10.84)</div>`;
    return;
  }
  const H = parseFloat($('#r-h').value)||1400; const hAnta = H-43;""")

# 7) leggiRigaCorrente: h2 e ferramenta porta
js = rep(js, """  const blocal = $('#r-blocal').checked || false;
  let mat = null;""", """  const blocal = $('#r-blocal').checked || false;
  const h2 = (t.porta && t.sopraluce) ? (parseFloat(String($('#r-h2').value).replace(',','.'))||null) : null;
  if(t.porta && t.sopraluce && !(h2>50 && h2<H-300)){
    if(!quiet) $('#esito').textContent = 'Porta con sopraluce: inserisci H2 (altezza sopraluce, mm) tra 50 e H-300.';
    return null;
  }
  const ferr = t.porta ? {cern:$('#r-cern').value, ncern:parseInt($('#r-ncern').value,10)||0, serr:$('#r-serr').value} : null;
  let mat = null;""")
js = rep(js, """  return {tid:t.id, codTip, mat, battuta, mano, hm, blocal, telaio:$('#r-telaio').value, anta:$('#r-anta').value,
    traverso:$('#r-traverso').value, vetro:$('#r-vetro').value, base, L, H, q};""",
"""  return {tid:t.id, codTip, mat, battuta, mano, hm, blocal, telaio:$('#r-telaio').value, anta:$('#r-anta').value,
    traverso:$('#r-traverso').value, vetro:$('#r-vetro').value, base, L, H, q, h2, ferr};""")

# 8) modificaRiga: h2 / ferramenta
js = rep(js, """  if(r.hm){ $('#r-hm').value = r.hm; fire('#r-hm'); }
  const bl = $('#r-blocal');""", """  if(r.hm){ $('#r-hm').value = r.hm; fire('#r-hm'); }
  if(r.h2) $('#r-h2').value = r.h2;
  if(r.ferr){ $('#r-cern').value = r.ferr.cern; $('#r-ncern').value = r.ferr.ncern||0; $('#r-serr').value = r.ferr.serr; }
  const bl = $('#r-blocal');""")

# 9) disegnaRighe: mostra H2 e ferramenta
js = rep(js, """${r.mano?' · '+r.mano.toUpperCase():''}${r.hm?' · man. '+r.hm:''}</td>""",
"""${r.mano?' · '+r.mano.toUpperCase():''}${r.hm?' · man. '+r.hm:''}${r.h2?'<br>H2 '+r.h2:''}${r.ferr?'<br>'+r.ferr.cern+(r.ferr.ncern?'×'+r.ferr.ncern:'')+' · '+r.ferr.serr:''}</td>""")

# 10) calcolaCommessa: formule con r, fermavetri porte, guardie drenaggi anta, guarnizioni
js = rep(js, """        let art = codiceProfilo(t.serie, r, p.art, p.desc);
        const isFV = art.startsWith('N458');
        if(isFV){
          // i fermavetri stanno sull'anta, salvo quelli del vetro fisso e del telaio fisso
          const suFisso = /fisso/i.test(p.desc) || t.forma==='F';
          const codRif = suFisso ? (r.telaio||'B23008C') : (r.anta||'B23122C');
          const ris = risolviVetro(r.vetro, codRif);
          if(!ris){ erroriFormule.push(`${t.nome}: vetro ${r.vetro} mm fuori tavola per ${codRif}`); return; }
          if(!includiFV){ registraAccessorio(accessori, ris.fv, p.desc+' (da tagliare a parte)', p.pz, valuta(p.mis,r.L,r.H)); return; }
          art = ris.fv;
        }
        const mm = valuta(p.mis, r.L, r.H);""", """        let art = codiceProfilo(t.serie, r, p.art, p.desc);
        const isFV = art.startsWith('N458') || p.fv===true;
        if(isFV){
          // i fermavetri stanno sull'anta, salvo quelli del vetro fisso e del telaio fisso
          const suFisso = /fisso/i.test(p.desc) || t.forma==='F';
          const codRif = t.porta ? (t.anta_rif||r.anta) : (suFisso ? (r.telaio||'B23008C') : (r.anta||'B23122C'));
          const ris = risolviVetro(r.vetro, codRif);
          if(!ris){ erroriFormule.push(`${t.nome}: vetro ${r.vetro} mm fuori tavola per ${codRif}`); return; }
          if(!ris.fv || ris.fv==='-'){ erroriFormule.push(`${t.nome}: nessun fermavetro a catalogo per vetro ${r.vetro} mm (${codRif})`); return; }
          if(!includiFV){ registraAccessorio(accessori, ris.fv, p.desc+' (da tagliare a parte)', p.pz, valuta(p.mis,r.L,r.H,r)); return; }
          art = ris.fv;
        }
        const mm = valuta(p.mis, r.L, r.H, r);""")
js = rep(js, """          if(conForo8 && traversoAnta && k < p.pz/2){                  // drenaggio anta: 168 dagli estremi""",
"""          if(t.porta){ lav.push(...lavPorta(t, r, p, k, mm, conDren, conForo8, accessori)); }
          if(!t.porta && conForo8 && traversoAnta && k < p.pz/2){       // drenaggio anta: 168 dagli estremi""")
js = rep(js, """          if(conForo8 && montanteAnta)                                 // 218 dal basso""",
"""          if(!t.porta && conForo8 && montanteAnta)                     // 218 dal basso""")
js = rep(js, """      t.guarnizioni.forEach(g=>{
        const mm = valuta(g.mis, r.L, r.H);
        let art = g.art, desc = g.desc;
        if(/^809119/.test(g.art)){  // guarnizione interna vetro -> dalla tavola di vetrazione
          const ris = risolviVetro(r.vetro, r.anta||'B23122C');""", """      t.guarnizioni.forEach(g=>{
        const mm = valuta(g.mis, r.L, r.H, r);
        let art = g.art, desc = g.desc;
        if(/^809119/.test(g.art) || (t.porta && /^interna vetro/i.test(g.desc))){  // guarnizione interna vetro -> dalla tavola di vetrazione
          const ris = risolviVetro(r.vetro, t.porta ? (t.anta_rif||r.anta) : (r.anta||'B23122C'));""")
js = rep(js, """      t.vetro.forEach(v=>{
        const l=valuta(v.l,r.L,r.H), h=valuta(v.h,r.L,r.H);""", """      t.vetro.forEach(v=>{
        const l=valuta(v.l,r.L,r.H,r), h=valuta(v.h,r.L,r.H,r);""")

# 11) template: H2 + ferramenta porta
tpl = rep(tpl, """            <div id="box-hm" style="display:none"><label>Altezza maniglia (mm dal fondo anta)</label>""",
"""            <div id="box-h2" style="display:none"><label>H2 — altezza sopraluce (mm, da filo esterno telaio)</label>
              <input id="r-h2" class="mis" placeholder="es. 400">
              <div style="font-size:.68rem;color:var(--acciaio)">H1 = H − H2 (parte porta). Formule di catalogo AluK 8.05/8.15.</div></div>
            <div id="box-ferr-porta" style="display:none"><label>Ferramenta porta (lavorazioni da tarare)</label>
              <select id="r-cern">
                <option value="2ali">Cerniere a 2 ali (fori Ø11, dima T10095)</option>
                <option value="3ali">Cerniere a 3 ali (fori Ø11, dima T10095)</option>
                <option value="stelo">Cerniere a stelo H51300 (dima T10020)</option>
                <option value="nascoste">Cerniere nascoste H59313 (fresate)</option>
                <option value="nessuna">Nessuna lavorazione cerniere</option>
              </select>
              <label style="margin-top:.3rem">N. cerniere per anta (0 = automatico dall'altezza)</label>
              <input id="r-ncern" class="mis" value="0">
              <label style="margin-top:.3rem">Serratura</label>
              <select id="r-serr">
                <option value="732251">AluK 732251 (ganci + punzoni)</option>
                <option value="H51400">AluK H51400 (scrocchi + punzoni)</option>
                <option value="732259">AluK 732259</option>
                <option value="cisa">CISA / ISEO (incontri 732176/732177)</option>
                <option value="nessuna">Nessuna lavorazione serratura</option>
              </select>
              <div id="info-ferr-porta" style="font-size:.68rem;color:var(--acciaio)"></div></div>
            <div id="box-hm" style="display:none"><label>Altezza maniglia (mm dal fondo anta)</label>""")

js = rep(js, """  $('#r-tip').addEventListener('change', ()=>{mostraAvvisoTip(); aggiornaSezioni();});""",
"""  $('#r-tip').addEventListener('change', ()=>{mostraAvvisoTip(); if(isPorta($('#r-serie').value)) aggiornaSelettoriProfili(); else aggiornaSezioni();});""")
js += "\n// ---------- porte D67/D77: lavorazioni (segnaposto, vedi modulo porte) ----------\nif(typeof lavPorta!=='function'){ window.lavPorta = function(){ return []; }; }\n"
open(F+'app_logic.js', 'w', encoding='utf-8').write(js)
open(F+'app_template.html', 'w', encoding='utf-8').write(tpl)
print('patch1 ok')
