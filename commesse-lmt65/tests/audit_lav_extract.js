// Estrae TUTTE le lavorazioni (art, f, y, descr) generate per S140 e D67/D77, su tutte le tipologie
// del listino con un paio di misure rappresentative ciascuna. Uso:
//   node tests/audit_lav_extract.js > /tmp/audit_lav.json
//   python3 tools/audit_geom_lav.py /tmp/audit_lav.json
// Il secondo passo verifica, per ogni combinazione (profilo, faccia, Y) unica generata dal programma,
// se il marker della lavorazione nello schema-pezzo cade abbastanza vicino al tracciato DXF reale del
// profilo (altrimenti e' "nel vuoto", vedi bug 2026-09-15 su S140 U10140).
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://'+require('path').resolve(__dirname,'../dist/Commesse_LMT65.html'));
  const out = await p.evaluate(() => {
    const set = (id, v) => { const e = document.querySelector(id); e.value = v; e.dispatchEvent(new Event(e.tagName === 'SELECT' ? 'change' : 'input')); };
    const serie = ['S140','D67','D77'];
    const errAdd = [];
    for(const s of serie){
      set('#r-serie', s);
      const tips = [...document.querySelectorAll('#r-tip option')].map(o=>o.value);
      for(const tid of tips){
        set('#r-tip', tid);
        // due misure rappresentative: piccola e grande, per intercettare eventuali rami mis-dipendenti
        for(const [L,H] of [[1200,2200],[3500,2400]]){
          set('#r-l', L); set('#r-h', H);
          try{
            const r = leggiRigaCorrente(false);
            if(r) righe.push(Object.assign({}, r, {q:1}));
          }catch(e){ errAdd.push({tid, L, H, err:String(e)}); }
        }
      }
    }
    let calc; try{ calc = calcolaCommessa(); }catch(e){ return {errs2:String(e)}; }
    const lav = [];
    calc.pezzi.forEach(pz=>{
      (pz.lav||[]).forEach(l=>{
        lav.push({art:pz.art, serie:pz.serie, desc:pz.desc, f:String(l.f), y:l.y, x:l.x, z:l.z, v1:l.v1, v2:l.v2, descr:l.descr});
      });
    });
    return {nPezzi:calc.pezzi.length, nLav:lav.length, lav, err:calc.erroriFormule, errAdd};
  });
  console.log(JSON.stringify({errs, ...out}));
  await b.close();
})();
