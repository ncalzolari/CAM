#!/usr/bin/env python3
"""Patch 8 (13/09/2026): ferramenta Maico delle celle apribili nel costruttore a griglia C75S/C82S (sospeso n.2).
Regole delle tipologie singole (validate) trasposte sulla cella tramite un "pezzo virtuale" (anta+43, ante a 21,5 dagli
estremi) e spostate sul pezzo reale (stipite passante o profilo T). Sui profili T: scontro d'angolo a 55,5 dal nodo e
valori Y/faccia decodificati dai job 220_26 come eccezioni di libreria (B23609C/B23608C: sc_angolo Y12, cerniere Y66,2 F4).
Tutto marcato "[DA VERIFICARE composta]" finché non validato col diff sul job 220_26. FX sui perimetri come nelle tipologie."""
import pathlib
P = pathlib.Path(__file__).resolve().parents[1] / 'src' / 'app_logic.js'
s = P.read_text(encoding='utf-8')
def sost(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:80], s.count(old))
    s = s.replace(old, new)

# 1) eccezioni di libreria per i profili T (C75S). Connessioni alle teste (Y62,2 F4): geometria non decodificata, non emesse.
sost("  mart_scasso:  {w:'#1', v1:'12',   v2:'62', y:64,   z:-12,   f:'1', ut:'3',  descr:'Martellina scasso 12x62 (G001)'},\n}};",
     "  mart_scasso:  {w:'#1', v1:'12',   v2:'62', y:64,   z:-12,   f:'1', ut:'3',  descr:'Martellina scasso 12x62 (G001)'},\n"
     "  // profili T del costruttore (job 220_26): scontro d'angolo Y12; cerniere/supporti sul lato opposto F4 Y66,2 (Z come stipite, da verificare)\n"
     "  '@B23609C': {sc_angolo:{y:12}, cern_d7:{y:66.2, f:'4'}, cern_d3:{y:66.2, f:'4'}},\n"
     "  '@B23608C': {sc_angolo:{y:12}, cern_d7:{y:66.2, f:'4'}, cern_d3:{y:66.2, f:'4'}},\n}};")

# 2) motore: funzione ferramentaCelleComposta + uso nel costruttore
sost("function componiMatriceBase(r, t, agg){\n  if(t.composta_cor80) return componiMatriceCOR80(r, t, agg);",
     r"""// ---------- ferramenta Maico delle celle apribili nel costruttore (patch 8) ----------
// Ogni cella apribile è trattata come la tipologia singola equivalente ("pezzo virtuale": anta+43, ante a 21,5 dagli
// estremi) e le lavorazioni vengono spostate sul pezzo reale (stipite passante o profilo T). Sui profili T lo scontro
// d'angolo sta a 55,5 dal nodo (job 220_26); Y/faccia dei T dalle eccezioni di libreria (@B23609C/@B23608C).
const NODO_T = 55.5;
function ferramentaCelleComposta(r, t, D, ws, hs, celle, telaio, anta, trav, mont){
  const F = {tell:[[],[]], telh:[[],[]], trvV:ws.map(()=>[]), trvO:hs.map(()=>ws.map(()=>[])), ant:{}};
  const yb = rr=>hs.slice(rr+1).reduce((a,b)=>a+b,0), xl = c=>ws.slice(0,c).reduce((a,b)=>a+b,0);
  const sposta = (arr, dx)=>arr.map(l=>Object.assign(l, {x:Math.round((l.x+dx)*10)/10}));
  const H = hs.reduce((a,b)=>a+b,0);
  for(let rr=0;rr<hs.length;rr++) for(let c=0;c<ws.length;c++){
    const v=celle[rr][c]; if(v==='F' || v==='VAS') continue;              // vasistas: sospeso 3 (solo FX+drenaggi)
    const id=`C${rr+1}${c+1}`;
    const bordi={sx:c===0, dx:c===ws.length-1, su:rr===0, giu:rr===hs.length-1};
    const d=tel=>tel?0:1;
    const spanW=ws[c], spanH=hs[rr], cellaPF=isPF(v), bordoSoglia=cellaPF&&bordi.giu;
    const aw=spanW-D.anta[d(bordi.sx)]-D.anta[d(bordi.dx)];
    const ah=spanH-D.anta[d(bordi.su)]-(bordoSoglia?8.5:D.anta[d(bordi.giu)]);
    const due = v==='2A'||v==='PF2';
    const manoDx = due ? (r.mano||'dx')==='dx' : /DX/.test(v);
    const hm = (!due && r.hm && hmAmmesse(ah).includes(+r.hm)) ? +r.hm : hmStandard(ah);
    const LvV = ah+43, LvO = aw+43;
    const yo = yb(rr)+(bordoSoglia?8.5:D.anta[d(bordi.giu)])-21.5;    // origine del pezzo virtuale verticale (dal basso)
    const xo = xl(c)+D.anta[d(bordi.sx)]-21.5;                         // origine del pezzo virtuale orizzontale (da sinistra)
    const dS = c===0? D.trvO[0]:D.trvO[1], dD = c===ws.length-1? D.trvO[0]:D.trvO[1];
    const lunT = spanW-dS-dD;
    // pezzi reali che delimitano la cella
    const pV = sx => sx ? (bordi.sx ? {arr:F.telh[0], art:telaio, start:0} : {arr:F.trvV[c-1], art:mont, start:D.trvV_tel, T:true})
                        : (bordi.dx ? {arr:F.telh[1], art:telaio, start:0} : {arr:F.trvV[c],   art:mont, start:D.trvV_tel, T:true});
    const pO = giu => giu ? (bordi.giu ? {arr:F.tell[0], art:telaio, start:0} : {arr:F.trvO[rr][c],   art:trav, start:xl(c)+dS, T:true, len:lunT})
                          : (bordi.su  ? {arr:F.tell[1], art:telaio, start:0} : {arr:F.trvO[rr-1][c], art:trav, start:xl(c)+dS, T:true, len:lunT});
    const nodoSu = yb(rr)+spanH;                                        // asse del traverso sopra la cella (quota dal basso)
    const metti = (p, lav)=>{ p.arr.push(...lav); };
    if(!due){
      // montante lato cerniere
      let p = pV(!manoDx); LAV_CTX.art = p.art;
      let lav = sposta(lavCerniere(LvV, !manoDx), yo-p.start);
      if(p.T) lav.push(SC_SINGLE(Math.round((nodoSu-p.start-NODO_T)*10)/10));   // scontro d'angolo a 55,5 dal nodo
      else lav.push(SC_SINGLE(Math.round((LvV-CORNER_SC+yo-p.start)*10)/10));
      if(ah-20 > 800) lav.push(SC_SINGLE(Math.round((LvV/2-0.5+yo-p.start)*10)/10));     // chiusura centrale lato cerniere
      metti(p, lav);
      // montante lato maniglia
      p = pV(manoDx); LAV_CTX.art = p.art;
      metti(p, sposta(lavScontriMontanteManiglia(LvV, ah, hm), yo-p.start));
      // traverso inferiore: scontro d'angolo lato maniglia (+ chiusura centrale)
      p = pO(true); LAV_CTX.art = p.art;
      lav = lavScontriTraverso(LvO, true, manoDx, aw);
      if(p.T){ const xc = manoDx ? NODO_T : Math.round((p.len-NODO_T)*10)/10; lav = SC_PAIR54(xc).concat(sposta(lav.slice(2), xo-p.start)); }
      else lav = sposta(lav, xo-p.start);
      metti(p, lav);
      // traverso superiore: scontro d'angolo lato cerniere + scontro forbice
      p = pO(false); LAV_CTX.art = p.art;
      lav = lavScontriTraverso(LvO, false, manoDx, aw);
      if(p.T){ const xc = !manoDx ? NODO_T : Math.round((p.len-NODO_T)*10)/10; lav = SC_PAIR54(xc).concat(sposta(lav.slice(2), xo-p.start)); }
      else lav = sposta(lav, xo-p.start);
      lav.push(...sposta(lavScontroForbice(LvO, aw, manoDx), xo-p.start));
      metti(p, lav);
      // martellina sul montante anta lato maniglia
      LAV_CTX.art = anta; F.ant[id] = {k: manoDx?1:0, lav: lavMartellina(ah, hm)};
    } else {                                                             // due ante stulp (doc 750135 pp.27-34)
      const s = manoDx ? 1 : -1;
      [true,false].forEach(sx=>{
        const p = pV(sx); LAV_CTX.art = p.art;
        const lav = sposta(lavCerniere(LvV, sx), yo-p.start);
        const attivo = manoDx ? !sx : sx;
        if(attivo){
          lav.push(SC_SINGLE(p.T ? Math.round((nodoSu-p.start-NODO_T)*10)/10 : Math.round((LvV-CORNER_SC+yo-p.start)*10)/10));
          const hbb = ah-20;
          const Bs = hbb<=1280 ? [565] : hbb<=1700 ? [800] : hbb<=2200 ? [800,1506] : [800,1506,1977];
          if(hbb>800) Bs.forEach((b,i)=> lav.push(SC_SINGLE(Math.round((LvV-(b+(i===0?25.5:24.5))+yo-p.start)*10)/10)));
        } else {
          [LvV/2-19, LvV/2+19].forEach(x=> lav.push(Object.assign({x:Math.round((x+yo-p.start)*10)/10}, lavDef('cern_centrale'))));
        }
        metti(p, lav);
      });
      const pzS = spanW/2-D.anta[d(bordi.sx)]+12, ffb = pzS-20;
      [true,false].forEach(giu=>{
        const p = pO(giu); LAV_CTX.art = p.art;
        const ax = xl(c)+spanW/2-p.start;                                // asse stulp in coordinate pezzo
        const lav = giu ? SC_PAIR54(Math.round((ax-123*s)*10)/10).concat([SC_SINGLE(Math.round((ax+74.8*s)*10)/10)])
                        : SC_PAIR54(Math.round((ax+124.5*s)*10)/10).concat([SC_SINGLE(Math.round((ax-46.8*s)*10)/10)]);
        if(!giu && ffb>800){ const q = FORBICE_QUOTA[forbicePer(ffb+20)];
          if(q!=null) lav.push(SC_SINGLE(Math.round(((s>0 ? q+28.5 : LvO-q-28.5)+xo-p.start)*10)/10)); }
        metti(p, lav);
      });
      LAV_CTX.art = anta; F.ant[id] = {k: manoDx?1:0, lav: lavMartellina(ah, hm)};
    }
  }
  const marca = arr=>arr.forEach(l=>{ if(!/DA VERIFICARE composta/.test(l.descr)) l.descr = (l.descr||'')+' [DA VERIFICARE composta]'; });
  F.tell.forEach(marca); F.telh.forEach(marca); F.trvV.forEach(marca); F.trvO.forEach(rw=>rw.forEach(marca)); Object.values(F.ant).forEach(a=>marca(a.lav));
  return F;
}
function componiMatriceBase(r, t, agg){
  if(t.composta_cor80) return componiMatriceCOR80(r, t, agg);""")

sost("  const L = ws.reduce((a,b)=>a+b,0), H = hs.reduce((a,b)=>a+b,0);\n  const spingi=(art,desc,sc,mm,tag,lav)=>{",
     "  const L = ws.reduce((a,b)=>a+b,0), H = hs.reduce((a,b)=>a+b,0);\n"
     "  const FER = agg.conAnte ? ferramentaCelleComposta(r, t, D, ws, hs, celle, telaio, anta, trav, D.mont||trav)\n"
     "                          : {tell:[[],[]], telh:[[],[]], trvV:ws.map(()=>[]), trvO:hs.map(()=>ws.map(()=>[])), ant:{}};\n"
     "  const spingi=(art,desc,sc,mm,tag,lav)=>{")
# perimetro: FX + ferramenta sugli stipiti
sost("    let lav=[];\n    if(conDren&&k===1){ const pos=posizioniDrenaggio(L);\n      LAV_CTX.art = telaio; lav=pos.map(x=>lavDrenaggio(t.serie,'telaio',x)); capDrenaggio(t.serie,accessori,pos.length); }\n    spingi(telaio,'Traverso stipite',`TELL0${k}`,L,'45-45',lav); });\n  [1,2].forEach(k=>spingi(telaio,'Montante stipite',`TELH0${k}`,H, tuttaPF?(k===1?'45-90':'90-45'):'45-45'));",
     "    let lav=[]; LAV_CTX.art = telaio;\n    if(conDren){ lav.push(...lavFX(L)); }                                   // fissaggi su tutti i lati telaio (come le tipologie)\n"
     "    if(conDren&&k===1){ const pos=posizioniDrenaggio(L);\n      lav.push(...pos.map(x=>lavDrenaggio(t.serie,'telaio',x))); capDrenaggio(t.serie,accessori,pos.length); }\n"
     "    lav.push(...FER.tell[k-1]);\n    spingi(telaio,'Traverso stipite',`TELL0${k}`,L,'45-45',lav); });\n"
     "  [1,2].forEach(k=>{ LAV_CTX.art = telaio; const lav = conDren ? lavFX(H) : []; lav.push(...FER.telh[k-1]);\n"
     "    spingi(telaio,'Montante stipite',`TELH0${k}`,H, tuttaPF?(k===1?'45-90':'90-45'):'45-45',lav); });")
# montanti T e traversi T
sost("  for(let c=0;c<ws.length-1;c++) spingi(D.mont||trav,'Montante T interno',`TRVV0${c+1}`,H-2*D.trvV_tel,'90-90');",
     "  for(let c=0;c<ws.length-1;c++) spingi(D.mont||trav,'Montante T interno',`TRVV0${c+1}`,H-2*D.trvV_tel,'90-90',FER.trvV[c]);")
sost("    spingi(trav,'Traverso T interno',`TRVO${rr+1}${c+1}`,lunT,'90-90',lavT); }",
     "    spingi(trav,'Traverso T interno',`TRVO${rr+1}${c+1}`,lunT,'90-90',lavT.concat(FER.trvO[rr][c])); }")
# martellina sui montanti anta
sost("        for(let k=0;k<3;k++) spingi(anta,'Montante battente',`${id}-ANTH`,ah,'45-45',\n          agg.conAnte? [lavDrenaggio(t.serie,'antaMont',Math.round((ah-350)*10)/10)] : []);",
     "        for(let k=0;k<3;k++) spingi(anta,'Montante battente',`${id}-ANTH`,ah,'45-45',\n          (agg.conAnte? [lavDrenaggio(t.serie,'antaMont',Math.round((ah-350)*10)/10)] : []).concat(FER.ant[id]&&FER.ant[id].k===k ? FER.ant[id].lav : []));")
sost("        [1,2].forEach(()=>spingi(anta,'Montante battente',`${id}-ANTH`,ah,'45-45',\n          agg.conAnte? [lavDrenaggio(t.serie,'antaMont',Math.round((ah-350)*10)/10)] : []));",
     "        [0,1].forEach(k=>spingi(anta,'Montante battente',`${id}-ANTH`,ah,'45-45',\n          (agg.conAnte? [lavDrenaggio(t.serie,'antaMont',Math.round((ah-350)*10)/10)] : []).concat(FER.ant[id]&&FER.ant[id].k===k ? FER.ant[id].lav : [])));")
P.write_text(s, encoding='utf-8'); print('patch 8 OK')
