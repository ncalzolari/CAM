const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1400,height:1000}});
  const errs=[]; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://'+require('path').resolve(__dirname,'../dist/Commesse_LMT65.html'));
  await p.evaluate(()=>{
    const set=(id,v)=>{const e=document.querySelector(id);e.value=v;e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input'));};
    set('#r-serie','D67'); set('#r-tip','D67_DUE_ANTE_SOGLIA_K1490_INT_Z'); set('#r-l',1800); set('#r-h',2300);
    document.querySelector('#btn-aggiungi').click();
    set('#r-tip','D67_UN_ANTA_SOGLIA_AUTOMATICA_INT_Z'); set('#r-l',1000); set('#r-h',2200);
    document.querySelector('#btn-aggiungi').click();
    document.querySelector('#btn-calcola').click();
  });
  await p.waitForTimeout(500);
  const sec = await p.$('section.no-stampa'); await sec.screenshot({path:__dirname+'/shot1.png'});
  await p.screenshot({path:__dirname+'/shot2.png', fullPage:true});
  console.log('errs',errs);
  await b.close();
})();
