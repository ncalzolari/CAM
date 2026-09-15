// Collaudo headless serie AluK S140 (alzante scorrevole): tipologie allineate al listino -> distinta, accessori kit, vetri, job XML
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage(); const errs=[]; p.on('pageerror', e => errs.push(String(e)));
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://'+require('path').resolve(__dirname,'../dist/Commesse_LMT65.html'));
  const casi = JSON.parse(process.argv.slice(2).find(a=>!a.startsWith('--')) || 'null') || [
    {tid:'S140_LS_XX', L:2900, H:2400},
    {tid:'S140_LS_XX_SLIM_SR', L:2900, H:2400},
    {tid:'S140_LS_OX_SR', L:2600, H:2400},
    {tid:'S140_LS_3A', L:4350, H:2400},
    {tid:'S140_LS_4A_2F', L:5000, H:2500},
    {tid:'S140_LS_6A_SR', L:6000, H:2600},
    {tid:'S140_R_XX', L:2300, H:2400},
    {tid:'S140_R_OX_SLIM', L:2000, H:2200},
  ];
  const out = await p.evaluate((casi)=>{
    const set=(id,v)=>{const e=document.querySelector(id);e.value=v;e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input'));};
    const res = {serie:[...document.querySelectorAll('#r-serie option')].map(o=>o.value), righe:[]};
    set('#r-serie','S140');
    res.tipologie = [...document.querySelectorAll('#r-tip option')].map(o=>o.value);
    for(const c of casi){
      set('#r-tip', c.tid); set('#r-l', c.L); set('#r-h', c.H);
      if(c.vetro) set('#r-vetro', c.vetro);
      const r = leggiRigaCorrente(false);
      res.righe.push({tid:c.tid, ok:!!r, esito:document.querySelector('#esito').textContent, vetro:document.querySelector('#r-vetro').value,
        vetri:[...document.querySelectorAll('#r-vetro option')].map(o=>o.value).join(','),
        svg: (document.querySelector('#prospetto') ? document.querySelector('#prospetto').innerHTML.length : -1)});
      if(r) righe.push(r);
    }
    const r = mostra();
    const seriePer = {}; r.calc.pezzi.forEach(p => seriePer[p.art] = p.serie);
    const job = r.barre.map((bb, i) => xmlBarra(bb, i + 1, seriePer[bb.art], 'T')).join('\n');
    const pezzi = r.calc.pezzi.map(x=>({cod:x.cod, art:x.art, desc:x.desc, mm:x.mm, al:x.al, ar:x.ar, nlav:x.lav.length}));
    return Object.assign(res, {n:r.calc.pezzi.length, barre:r.barre.length, macch:(job.match(/<MACHINING /g)||[]).length,
      syst:[...new Set(job.match(/<SYST>[^<]*/g))], err:r.calc.erroriFormule, pezzi, acc:r.calc.accessori, gu:r.calc.guarnizioni, ve:r.calc.vetri, ore: r.calc.ore});
  }, casi);
  const full = process.argv.includes('--full');
  if(full) console.log(JSON.stringify({errs, ...out}, null, 1));
  else {
    console.log('errs', errs, '| serie', out.serie, '| tipologie S140', out.tipologie.length);
    out.righe.forEach(r=>console.log(' ', r.ok?'OK ':'ERR', r.tid.padEnd(22), '| vetro', r.vetro, '[', r.vetri, '] | svg', r.svg, '|', r.esito));
    console.log('pezzi', out.n, 'barre', out.barre, 'machining', out.macch, 'syst', out.syst, 'errori formule:', out.err, 'ore', out.ore);
    console.log('vetri', JSON.stringify(out.ve));
    const accL = Array.isArray(out.acc) ? out.acc : Object.entries(out.acc||{}).map(([k,v])=>Object.assign({art:k}, typeof v==='object'?v:{q:v}));
    const kit = accL.filter(a=>/^(H10|213-)/.test(a.art||''));
    console.log('accessori', accL.length, 'kit ferramenta:'); kit.forEach(a=>console.log('   ', JSON.stringify(a)));
    console.log('guarnizioni', Array.isArray(out.gu)? out.gu.length : Object.keys(out.gu||{}).length);
    out.pezzi.forEach(p=>console.log('  ', p.cod.padEnd(22), p.art.padEnd(9), String(p.mm).padStart(7), `${p.al}/${p.ar}`, p.desc.padEnd(44), 'lav', p.nlav));
  }
  await b.close();
})();
