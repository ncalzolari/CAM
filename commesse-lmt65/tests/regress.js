const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const run = async (file) => {
    const p = await b.newPage(); const errs=[]; p.on('pageerror', e => errs.push(String(e)));
    await p.goto('file://'+file);
    const out = await p.evaluate(()=>{
      const set=(id,v)=>{const e=document.querySelector(id);e.value=v;e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input'));};
      set('#r-serie','C75S'); set('#r-tip','C75S_FIN_1ANTA'); set('#r-l',1200); set('#r-h',1650); set('#r-mano','dx'); righe.push(leggiRigaCorrente(false));
      set('#r-tip','C75S_FIN_2ANTE'); set('#r-l',1600); set('#r-h',1800); righe.push(leggiRigaCorrente(false));
      set('#r-tip','C75S_PB_1ANTA'); set('#r-l',900); set('#r-h',2200); righe.push(leggiRigaCorrente(false));
      set('#r-serie','C82S-CS'); set('#r-tip','C82S_FIN_1ANTA_LATFISSO'); set('#r-l',1500); set('#r-h',1400); righe.push(leggiRigaCorrente(false));
      const c = calcolaCommessa();
      return {pezzi:c.pezzi.map(x=>[x.art,x.desc,x.mm,x.al,x.ar,x.lav.map(l=>`${l.descr}|${l.x}|${l.y}|${l.z}|${l.f}|${l.ut}|${l.v1}|${l.v2}`)]), acc:c.accessori, gu:c.guarnizioni, ve:c.vetri, err:c.erroriFormule};
    });
    await p.close(); return {errs,out};
  };
  const a = await run(require('path').resolve(__dirname,'reference/Commesse_LMT65_base_2026-09-07.html'));
  const c = await run(require('path').resolve(__dirname,'../dist/Commesse_LMT65.html'));
  const sa=JSON.stringify(a.out), sc=JSON.stringify(c.out);
  console.log('errs', a.errs, c.errs, 'pezzi', a.out.pezzi.length, c.out.pezzi.length, 'IDENTICI:', sa===sc);
  if(sa!==sc){ for(let i=0;i<a.out.pezzi.length;i++){ const x=JSON.stringify(a.out.pezzi[i]), y=JSON.stringify(c.out.pezzi[i]); if(x!==y){ console.log('DIFF',i,x,'\n   ',y); break; } } }
  await b.close();
})();
