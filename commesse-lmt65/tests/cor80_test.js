// Collaudo headless serie Cortizo COR80: tipologie principali -> distinta, lavorazioni, job XML, schemi pezzo
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage(); const errs=[]; p.on('pageerror', e => errs.push(String(e)));
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://'+require('path').resolve(__dirname,'../dist/Commesse_LMT65.html'));
  const casi = JSON.parse(process.argv.slice(2).find(a=>!a.startsWith('--')) || 'null') || [
    {tid:'COR80_FISSO_ALA39', L:1000, H:1200},
    {tid:'COR80_1A_SEMIVISTA', L:1000, H:1400, mano:'dx'},
    {tid:'COR80_2A_VISTA', L:1600, H:1500},
    {tid:'COR80_2A_SEMIVISTA_INVRID', L:1400, H:1300},
    {tid:'COR80_1A_FISSOINF_VISTA', L:1000, H:2000, h2:600},
    {tid:'COR80_PF1_VISTA', L:900, H:2200, mano:'sx'},
    {tid:'COR80_1A_SCOMPARSA', L:1000, H:1400},
    {tid:'COR80_2A_FISSOINF_SEMIVISTA_RID_INVRID', L:1800, H:2100, h2:500},
    {tid:'COR80_1A_SEMIVISTA', L:1000, H:1800, hdiv:700},                       // divisore d'anta
    {tid:'COR80_PF1_VISTA', L:900, H:2300, hdiv:900},                           // divisore portafinestra in vista
    {tid:'COR80_2A_VISTA_INVRID', L:1500, H:1400, manc:true, hdiv:500},         // maniglia centrata + divisore su 2 ante
    {tid:'COR80_1A_SCOMPARSA', L:1000, H:1600, hdiv:600},                        // divisore anta a scomparsa
    {tid:'COR80_COMPOSTA_V', L:2400, H:2200, celle:[['ADX','F'],['F','2A']]},      // costruttore a griglia in vista
    {tid:'COR80_COMPOSTA_R', L:1800, H:1500, celle:[['F','ASX','VAS']]},            // costruttore a griglia semivista ridotta
  ];
  const out = await p.evaluate((casi)=>{
    const set=(id,v)=>{const e=document.querySelector(id);e.value=v;e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input'));};
    const res = {serie:[...document.querySelectorAll('#r-serie option')].map(o=>o.value), righe:[]};
    set('#r-serie','COR80');
    res.tipologie = [...document.querySelectorAll('#r-tip option')].map(o=>o.value);
    for(const c of casi){
      set('#r-tip', c.tid); set('#r-l', c.L); set('#r-h', c.H);
      if(c.h2) set('#r-h2', c.h2); if(c.mano) set('#r-mano', c.mano); if(c.telaio) set('#r-telaio', c.telaio); if(c.vetro) set('#r-vetro', c.vetro);
      set('#r-hdiv', c.hdiv||''); document.querySelector('#r-manc').checked = !!c.manc;
      if(c.celle){ set('#m-cols', c.celle[0].length); set('#m-rows', c.celle.length); matC.celle = c.celle.map(x=>x.slice()); disegnaGriglia(); }
      const r = leggiRigaCorrente(false);
      res.righe.push({tid:c.tid, ok:!!r, esito:document.querySelector('#esito').textContent, vetro:document.querySelector('#r-vetro').value,
        telaio:[...document.querySelectorAll('#r-telaio option')].map(o=>o.textContent), hm:document.querySelector('#r-hm').value,
        boxes:['#box-hm','#box-h2','#box-div','#box-manc','#box-mano'].map(x=>x+':'+document.querySelector(x).style.display).join(' ')});
      if(r) righe.push(r);
    }
    const r = mostra();
    const seriePer = {}; r.calc.pezzi.forEach(p => seriePer[p.art] = p.serie);
    const job = r.barre.map((bb, i) => xmlBarra(bb, i + 1, seriePer[bb.art], 'T')).join('\n');
    let nSchemi=0; r.calc.pezzi.forEach(pz=>{ if(pz.lav.length){ svgPezzoLav(pz); nSchemi++; } });
    const pezzi = r.calc.pezzi.map(x=>({cod:x.cod, art:x.art, desc:x.desc, mm:x.mm, al:x.al, ar:x.ar, nlav:x.lav.length, lav:x.lav.map(l=>`${l.descr}|x${l.x}|y${l.y}|z${l.z}|f${l.f}|ut${l.ut}`)}));
    return Object.assign(res, {n:r.calc.pezzi.length, barre:r.barre.length, nSchemi, macch:(job.match(/<MACHINING /g)||[]).length,
      syst:[...new Set(job.match(/<SYST>[^<]*/g))], err:r.calc.erroriFormule, pezzi, acc:r.calc.accessori, gu:r.calc.guarnizioni, ve:r.calc.vetri,
      nonTarate: r.calc.pezzi.flatMap(x=>x.lav).filter(l=>!/DA TARARE/.test(l.descr)).length});
  }, casi);
  const full = process.argv.includes('--full');
  if(full) console.log(JSON.stringify({errs, ...out}, null, 1));
  else {
    console.log('errs', errs, '| serie', out.serie, '| tipologie COR80', out.tipologie.length);
    out.righe.forEach(r=>console.log(' ', r.ok?'OK ':'ERR', r.tid, '| vetro', r.vetro, '| telaio', r.telaio.join(' / '), '| hm', r.hm, '|', r.esito, '|', r.boxes));
    console.log('pezzi', out.n, 'barre', out.barre, 'schemi', out.nSchemi, 'machining', out.macch, 'syst', out.syst, 'lav non marcate DA TARARE:', out.nonTarate, 'errori formule:', out.err);
    console.log('vetri', JSON.stringify(out.ve));
    out.pezzi.forEach(p=>console.log('  ', p.cod.padEnd(14), p.art.padEnd(9), String(p.mm).padStart(7), `${p.al}/${p.ar}`, p.desc.padEnd(44), 'lav', p.nlav));
  }
  await b.close();
})();
