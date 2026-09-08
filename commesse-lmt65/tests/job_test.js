const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage(); const errs=[]; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://'+require('path').resolve(__dirname,'../dist/Commesse_LMT65.html'));
  const out = await p.evaluate(()=>{
    const set=(id,v)=>{const e=document.querySelector(id);e.value=v;e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input'));};
    set('#r-serie','D67'); set('#r-tip','D67_UN_ANTA_SOGLIA_AUTOMATICA_INT_Z'); set('#r-l',1000); set('#r-h',2200); righe.push(leggiRigaCorrente(false));
    set('#r-serie','D77'); set('#r-tip','D77_DUE_ANTE_SOPRALUCE_EST_Z'); set('#r-l',1700); set('#r-h',2700); set('#r-h2',450); righe.push(leggiRigaCorrente(false));
    const r = mostra();
    const seriePer = {}; r.calc.pezzi.forEach(p => seriePer[p.art] = p.serie);
    const job = r.barre.map((bb, i) => xmlBarra(bb, i + 1, seriePer[bb.art], 'T')).join('\n');
    // schema pezzo per ogni pezzo con lavorazioni
    let nSchemi=0; r.calc.pezzi.forEach(pz=>{ if(pz.lav.length){ svgPezzoLav(pz); nSchemi++; } });
    return {n:r.calc.pezzi.length, barre:r.barre.length, jobLen:job.length, nSchemi, macch:(job.match(/<MACHINING /g)||[]).length, syst:[...new Set(job.match(/<SYST>[^<]*/g))], err:r.calc.erroriFormule, esito:document.querySelector('#esito').textContent};
  });
  console.log(errs, out); await b.close();
})();
