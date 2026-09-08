// Collaudo headless dell'app: aggiunge porte D67/D77 e calcola distinta + job
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://'+require('path').resolve(__dirname,'../dist/Commesse_LMT65.html'));
  const casi = JSON.parse(process.argv[2] || '[]');
  const out = await p.evaluate(async (casi) => {
    const set = (id, v) => { const e = document.querySelector(id); e.value = v; e.dispatchEvent(new Event(e.tagName === 'SELECT' ? 'change' : 'input')); };
    const res = { serie: [...document.querySelectorAll('#r-serie option')].map(o => o.value + '|' + o.textContent), righe: [] };
    for (const c of casi) {
      set('#r-serie', c.serie); set('#r-tip', c.tid);
      set('#r-l', c.L); set('#r-h', c.H);
      if (c.h2) set('#r-h2', c.h2);
      if (c.telaio) set('#r-telaio', c.telaio);
      if (c.vetro) set('#r-vetro', c.vetro);
      if (c.mano) set('#r-mano', c.mano);
      if (c.hm) set('#r-hm', c.hm);
      if (c.cern) set('#r-cern', c.cern);
      if (c.ncern != null) set('#r-ncern', c.ncern);
      if (c.serr) set('#r-serr', c.serr);
      const r = leggiRigaCorrente(false);
      res.righe.push({ ok: !!r, esito: document.querySelector('#esito').textContent, opts: { telaio: [...document.querySelectorAll('#r-telaio option')].map(o => o.value + '=' + o.textContent), vetro: [...document.querySelectorAll('#r-vetro option')].map(o => o.value), hm: document.querySelector('#r-hm').value, boxes: ['#box-hm', '#box-h2', '#box-ferr-porta', '#box-mano', '#box-blocal', '#box-traverso'].map(x => x + ':' + document.querySelector(x).style.display) } });
      if (r) righe.push(r);
    }
    const calc = calcolaCommessa();
    const pezzi = calc.pezzi.map(x => ({ art: x.art, desc: x.desc, mm: x.mm, al: x.al, ar: x.ar, cod: x.cod, unita: x.unita, serie: x.serie, lav: x.lav.map(l => `${l.descr}|x${l.x}|y${l.y}|z${l.z}|f${l.f}|ut${l.ut}|v${l.v1}/${l.v2}`) }));
    // job xml (senza download)
    let job = null;
    try {
      const rr = mostra();
      const seriePer = {}; rr.calc.pezzi.forEach(p => seriePer[p.art] = p.serie);
      job = rr.barre.map((bb, i) => xmlBarra(bb, i + 1, (seriePer[bb.art] || 'C75S').replace('C82S-CS', 'C82S_CS'), 'TEST')).join('\n');
    } catch (e) { job = 'ERR ' + e; }
    return Object.assign(res, { pezzi, accessori: calc.accessori, guarnizioni: calc.guarnizioni, vetri: calc.vetri, errori: calc.erroriFormule, job, esito: document.querySelector('#esito').textContent });
  }, casi);
  console.log(JSON.stringify({ errs, ...out }, null, 1));
  await b.close();
})();
