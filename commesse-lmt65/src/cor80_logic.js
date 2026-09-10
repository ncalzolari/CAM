// ---------- motore di composizione COR80 (Cortizo COR 80 Evolution, telaio ala 21 COR-7419 + traverso COR-7561) ----------
// Parametri in t.composta_cor80 (generati da tools/build_cor80.py). Detrazioni per lato: [lato telaio, lato traverso/montante T].
// Tutto ciò che riguarda l'anta (fermavetri, vetro) è relativo alle misure dell'anta, come nelle distinte di catalogo.
function componiMatriceCOR80(r, t, agg){
  const C = t.composta_cor80;
  const includiFV_m = $('#c-fermavetro-si').value !== 'no';
  const {pezzi, accessori, guarnizioni, vetri, erroriFormule, conDren, unita} = agg;
  const ws=r.mat.ws, hs=r.mat.hs, celle=r.mat.celle;
  const telaio = codiceProfilo(t.serie, r, C.telaio, ''), anta = C.anta_art, trav = C.trav;
  const risA = risolviVetro(r.vetro, anta, C.tav), risF = risolviVetro(r.vetro, telaio, C.tavF);
  const fvA = risA? risA.fv : null, fvF = risF? risF.fv : null;
  if(!risA) erroriFormule.push(`${t.cod}: vetro ${r.vetro} mm fuori tavola per ${anta}`);
  if(!risF) erroriFormule.push(`${t.cod}: vetro ${r.vetro} mm fuori tavola per ${telaio} (fissi)`);
  const L = ws.reduce((a,b)=>a+b,0), H = hs.reduce((a,b)=>a+b,0);
  const tara = lav=>{ specchiaY(t.serie, lav||[]); (lav||[]).forEach(l=>{ if(!/DA TARARE/.test(l.descr)) l.descr += ' [DA TARARE]'; }); return lav||[]; };
  const spingi=(art,desc,sc,mm,tag,lav)=>{ if(mm==null||mm<=0){erroriFormule.push(`${t.cod}: ${desc} nullo`);return;}
    const [al,ar]=angoliJob(tag);
    pezzi.push({art,desc,mm:Math.round(mm*10)/10,al,ar,unita,tip:t.nome,tcod:t.cod,
      cod:`${t.cod}-${sc}`,serie:t.serie,lav:tara(lav)}); };
  const acc=(lista,mult)=>lista.forEach(([a,q])=>registraAccessorio(accessori, a, (((DATI.cor80_note||{}).acc_desc||{})[a])||`Accessorio ${a}`, q*(mult||1), null));
  const gua=(art,mm)=>{ const k=art+'|'+((((DATI.cor80_note||{}).acc_desc||{})[art])||'Guarnizione'); guarnizioni[k]=(guarnizioni[k]||0)+mm; };
  const dT = (DRAIN[t.serie]||{});
  const posDren = lun => posizioniDrenaggio(lun, dT.telaio21.bordo||75, dT.telaio21.passo||1000);
  // perimetro telaio
  [1,2].forEach(k=>{
    let lav=[];
    if(conDren&&k===1){ const pos=posDren(L); lav=pos.map(x=>lavDrenaggio(t.serie,'telaio21',x)); capDrenaggio(t.serie,accessori,pos.length); }
    spingi(telaio,'Traverso stipite',`TELL0${k}`,L,'45-45',lav); });
  [1,2].forEach(k=>spingi(telaio,'Montante stipite',`TELH0${k}`,H,'45-45'));
  acc(C.acc_telaio);
  gua('320023', 2*L+2*H);
  // montanti T verticali (passanti) e traversi T orizzontali (interrotti tra i montanti)
  for(let c=0;c<ws.length-1;c++){ spingi(trav,'Montante T interno',`TRVV0${c+1}`,H-2*C.trv_len[0],'90-90'); acc(C.acc_trav); gua('320023', 2*(H-2*C.trv_len[0])); }
  for(let rr=0;rr<hs.length-1;rr++) for(let c=0;c<ws.length;c++){
    const dS = c===0? C.trv_len[0]:C.trv_len[1], dD = c===ws.length-1? C.trv_len[0]:C.trv_len[1];
    const lunT = ws[c]-dS-dD;
    let lavT=[];
    if(conDren){ const pos=posDren(lunT); lavT=pos.map(x=>lavDrenaggio(t.serie,'traversoT',x)); capDrenaggio(t.serie,accessori,pos.length); }
    spingi(trav,'Traverso T interno',`TRVO${rr+1}${c+1}`,lunT,'90-90',lavT); acc(C.acc_trav); gua('320023', 2*lunT); }
  // celle
  const d=(tel)=>tel?0:1;
  for(let rr=0;rr<hs.length;rr++) for(let c=0;c<ws.length;c++){
    const v=celle[rr][c], id=`C${rr+1}${c+1}`;
    const bordi={sx:c===0, dx:c===ws.length-1, su:rr===0, giu:rr===hs.length-1}; // true = telaio
    const spanW=ws[c], spanH=hs[rr];
    if(v==='F' || isPF(v)){
      if(isPF(v)) erroriFormule.push(`${t.cod} ${id}: portefinestre non previste nella composta COR80 (cella trattata come fisso)`);
      const fo=spanW-C.fv_fis[0][d(bordi.sx)]-C.fv_fis[0][d(bordi.dx)];
      const fv=spanH-C.fv_fis[1][d(bordi.su)]-C.fv_fis[1][d(bordi.giu)];
      if(fvF && includiFV_m){ [1,2].forEach(()=>spingi(fvF,'Fermavetro orizz. fisso',`${id}-FVFL`,fo,'90-90'));
                              [1,2].forEach(()=>spingi(fvF,'Fermavetro vert. fisso',`${id}-FVFH`,fv,'90-90')); }
      else if(fvF) registraAccessorio(accessori, fvF, 'Fermavetro fisso (da tagliare a parte)', 4, 2*fo+2*fv);
      const gl=spanW-C.vetro_fis[0][d(bordi.sx)]-C.vetro_fis[0][d(bordi.dx)], gh=spanH-C.vetro_fis[1][d(bordi.su)]-C.vetro_fis[1][d(bordi.giu)];
      vetri.push({q:1,l:Math.round(gl),h:Math.round(gh),sp:r.vetro,tip:`${t.nome} ${id} fisso`,unita});
      if(risF) gua(risF.g, 2*gl+2*gh);
      gua(C.gask_fis_ext, 2*gl+2*gh);
      acc(C.acc_fis);
    } else {
      const aw=spanW-C.anta[d(bordi.sx)]-C.anta[d(bordi.dx)];
      const ah=spanH-C.anta[d(bordi.su)]-C.anta[d(bordi.giu)];
      const dx0 = C.dren_x||100;
      const lavTrav = aw => agg.conAnte? [dx0, Math.round((aw-dx0)*10)/10].map(x=>lavDrenaggio(t.serie,'antaTrav',x)) : [];
      const lavMont = (ah,k) => agg.conAnte? [lavDrenaggio(t.serie,'antaMont', k%2===0? dx0 : Math.round((ah-dx0)*10)/10)] : [];
      const sash=(lab, awS, n)=>{                       // n = indice per i codici pezzo
        spingi(anta,`Traverso battente${lab}`,`${id}-ANTL`,awS,'45-45',lavTrav(awS));
        spingi(anta,`Traverso battente${lab}`,`${id}-ANTL`,awS,'45-45');
        [0,1].forEach(k=>spingi(anta,`Montante battente${lab}`,`${id}-ANTH`,ah,'45-45',lavMont(ah,k)));
        const fo=awS-C.fv_anta[0], fvv=ah-C.fv_anta[1];
        if(fvA && includiFV_m){ [1,2].forEach(()=>spingi(fvA,`Fermavetro orizz. battente${lab}`,`${id}-FVBL`,fo,'90-90'));
                                [1,2].forEach(()=>spingi(fvA,`Fermavetro vert. battente${lab}`,`${id}-FVBH`,fvv,'90-90')); }
        else if(fvA) registraAccessorio(accessori, fvA, 'Fermavetro battente (da tagliare a parte)', 4, 2*fo+2*fvv);
        const gl=awS-C.vetro_anta[0], gh=ah-C.vetro_anta[1];
        vetri.push({q:1,l:Math.round(gl),h:Math.round(gh),sp:r.vetro,tip:`${t.nome} ${id} ${NOMI_CELLA[v]||v}${lab}`,unita});
        if(risA) gua(risA.g, 2*gl+2*gh);
        gua(C.gask_vetro_ext, 2*gl+2*gh);
        C.gask_anta.forEach(([art,scope])=>{
          if(scope==='batt2') gua(art, 2*(2*awS+2*ah)); else if(scope==='batt3') gua(art, 3*(2*awS+2*ah));
          else if(scope==='anta') gua(art, 2*awS+2*ah); });
      };
      if(v==='2A'){
        const awS = spanW/2-C.anta[d(bordi.sx)]-C.due_ante_c, awD = spanW/2-C.anta[d(bordi.dx)]-C.due_ante_c;
        sash(' sx', awS, 1); sash(' dx', awD, 2);
        spingi(C.inv,'Inversore (su anta semifissa)',`${id}-INVH`,ah-C.inv_ded,'90-90');
        acc(C.acc_2a);
      } else { sash('', aw, 1); acc(C.acc_anta); }
      C.gask_anta.forEach(([art,scope])=>{ if(scope==='cella') gua(art, 2*spanW+2*spanH); });
      // complemento telaio COR-5600 sui lati della cella apribile che stanno sul telaio COR-7419
      const co = spanW-C.comp_ded[0][d(bordi.sx)]-C.comp_ded[0][d(bordi.dx)];
      const cv = spanH-C.comp_ded[1][d(bordi.su)]-C.comp_ded[1][d(bordi.giu)];
      let nComp=0;
      [bordi.su, bordi.giu].forEach(tel=>{ if(tel||true){ spingi(C.comp,'Complemento telaio orizz. (cella apribile)',`${id}-COML`,co,'90-90'); nComp++; } });
      [bordi.sx, bordi.dx].forEach(tel=>{ if(tel){ spingi(C.comp,'Complemento telaio vert. (cella apribile)',`${id}-COMH`,cv,'90-90'); nComp++; } });
      acc(C.acc_comp);
    }
  }
}
