// Collaudo headless costruttore a griglia C75S/C82S con ferramenta Maico delle celle (patch 8): distinta + lavorazioni per pezzo
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage(); const errs=[]; p.on('pageerror', e => errs.push(String(e)));
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://'+require('path').resolve(__dirname,'../dist/Commesse_LMT65.html'));
  const casi = JSON.parse(process.argv.slice(2).find(a=>!a.startsWith('--')) || 'null') || [
    {serie:'C75S', tid:'C75S_COMPOSTA', L:2400, H:2100, ws:[1000,1400], hs:[600,1500], celle:[['F','F'],['ADX','2A']]},   // anta dx + 2 ante stulp sotto sopraluce
    {serie:'C82S-CS', tid:'C82S_COMPOSTA', L:2000, H:1500, ws:[1000,1000], hs:[1500], celle:[['ASX','F']]},                 // anta sx e fisso affiancati
    {serie:'C75S', tid:'C75S_COMPOSTA', L:1200, H:1650, ws:[1200], hs:[1650], celle:[['ADX']]},                             // cella singola = tipologia 1 anta (nessuna marcatura)
  ];
  const out = await p.evaluate((casi)=>{
    const set=(id,v)=>{const e=document.querySelector(id);e.value=v;e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input'));};
    const res = {righe:[]}; righe.length = 0;
    for(const c of casi){
      set('#r-serie', c.serie); set('#r-tip', c.tid); set('#r-l', c.L); set('#r-h', c.H); set('#r-mano', c.mano||'dx');
      set('#m-cols', c.celle[0].length); set('#m-rows', c.celle.length);
      document.querySelector('#m-ws').value = c.ws.join(' ; '); document.querySelector('#m-hs').value = c.hs.join(' ; '); rigeneraMatrice(true);
      matC.celle = c.celle.map(x=>x.slice()); disegnaGriglia();
      const r = leggiRigaCorrente(false); res.righe.push({tid:c.tid, ok:!!r, esito:document.querySelector('#esito').textContent}); if(r) righe.push(r);
    }
    const m = mostra();
    const pezzi = m.calc.pezzi.map(x=>({cod:x.cod, unita:x.unita, art:x.art, desc:x.desc, mm:x.mm, lav:x.lav.map(l=>`${l.descr}|x${l.x}|y${l.y}|z${l.z}|f${l.f}|ut${l.ut}`)}));
    return Object.assign(res, {n:pezzi.length, err:m.calc.erroriFormule, pezzi,
      nLav: pezzi.reduce((a,x)=>a+x.lav.length,0), nFer: pezzi.reduce((a,x)=>a+x.lav.filter(l=>/DA VERIFICARE composta/.test(l)).length,0)});
  }, casi);
  if(process.argv.includes('--full')){ console.log(JSON.stringify({errs, ...out}, null, 1)); }
  else {
    console.log('errs', errs, '| righe', out.righe.map(r=>`${r.tid}:${r.ok?'OK':'ERR'}`).join(' '), '| pezzi', out.n, '| lavorazioni', out.nLav, 'di cui ferramenta celle', out.nFer, '| errori formule', out.err);
    out.pezzi.filter(x=>x.lav.length).forEach(x=>{ console.log(' ', x.cod.padEnd(14), x.art.padEnd(8), String(x.mm).padStart(7), x.desc.padEnd(34), 'lav', x.lav.length);
      x.lav.filter(l=>!/Drenaggio|^FX/.test(l)).forEach(l=>console.log('      ', l)); });
  }
  // controlli minimi
  const pz = Object.fromEntries(out.pezzi.map(x=>[x.cod, x]));
  const has = (cod, re)=> (pz[cod]||{lav:[]}).lav.some(l=>re.test(l));
  const checks = [
    ['TELH01 stipite sx: scontri lato maniglia (ADX)', has('CMP75-TELH01', /alza-anta/)],
    ['TRVV01 montante T: cerniere su F4 Y66.2 [lib.B23609C]', has('CMP75-TRVV01', /Cerniera angolare D7.*lib\.B23609C.*\|y66\.2\|.*\|f4\|/)],
    ['TRVV01 montante T: cerniera centrale semifisso 2A', has('CMP75-TRVV01', /Cerniera centrale/)],
    ['TRVV01 montante T: scontro angolo Y12 [lib.B23609C]', has('CMP75-TRVV01', /Scontro nottolino.*composta|Scontro angolo.*lib\.B23609C/)],
    ['TELH02 stipite dx: cerniere F2 + scontro angolo (2A attiva)', has('CMP75-TELH02', /Cerniera angolare D7.*\|f2\|/) && has('CMP75-TELH02', /Scontro nottolino/)],
    ['TRVO11 traverso T: scontro angolo Y12 lato cerniere + forbice', has('CMP75-TRVO11', /Scontro angolo.*lib\.B23608C.*\|y12\|/)],
    ['TELL01 stipite inf: FX + scontro angolo + catenaccio stulp', has('CMP75-TELL01', /^FX D7\.5/) && has('CMP75-TELL01', /Scontro angolo/) && has('CMP75-TELL01', /Scontro nottolino/)],
    ['anta: martellina sul montante lato maniglia', out.pezzi.some(x=>/ANTH/.test(x.cod) && x.lav.some(l=>/Martellina scasso/.test(l)))],
    ['C82S: stipite sx con cerniere (ASX)', has('CMP82-TELH01', /Cerniera angolare D7/)],
    ['celle con profili T: ferramenta marcata', out.pezzi.filter(x=>!/^R3\./.test(x.unita)).every(x=>x.lav.every(l=>/Drenaggio|^FX|DA VERIFICARE composta/.test(l)))],
    ['cella singola 1x1: nessuna marcatura, cerniere+martellina presenti', out.pezzi.filter(x=>/^R3\./.test(x.unita)).every(x=>!x.lav.some(l=>/DA VERIFICARE/.test(l))) && out.pezzi.some(x=>/^R3\./.test(x.unita) && x.lav.some(l=>/Cerniera angolare D7/.test(l))) && out.pezzi.some(x=>/^R3\./.test(x.unita) && x.lav.some(l=>/Martellina scasso/.test(l)))],
    ['drenaggi anta a 168 e montante a 218 (schema aziendale)', out.pezzi.some(x=>/ANTL/.test(x.cod) && x.lav.some(l=>/Drenaggio anta.*\|x168\|/.test(l))) && out.pezzi.some(x=>/ANTH/.test(x.cod) && x.lav.some(l=>/Drenaggio montante.*\|x218\|/.test(l)))],
  ];
  let ko = 0; checks.forEach(([n,v])=>{ if(!v) ko++; console.log(v?'  ok ':'  KO ', n); });
  if(errs.length || out.err.length || ko) process.exitCode = 1;
  await b.close();
})();
