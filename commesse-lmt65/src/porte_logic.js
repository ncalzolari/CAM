
// ======================================================================================
// PORTE D67 / D77 (IWG 67ID / 77ID) — lavorazioni ferramenta e fissaggi
// Fonte: manuale lavorazioni AluK D67/D77 v4.A (10.01 fissaggi, 10.32-10.35 cerniere 2/3 ali,
// 10.41-10.42 cerniere a stelo H51300, 10.51-10.57 cerniere nascoste H59313, 10.72-10.84 serrature).
// STATO: DA TARARE. Nessun riscontro di produzione: facce, versi Y e verso X sono CONVENZIONI
// (tabella DATI.porte_ferr.facce) ricavate per analogia con C75S (F1 = faccia di battuta del telaio
// verso l'anta, F4 = faccia a muro, F2 = interno, F3 = esterno; anta ruotata di 180° in macchina).
// Le quote lungo il profilo sono ancorate ad AM (asse maniglia) e alle posizioni cerniera; tutto è
// parametrico in DATI.porte_ferr e correggibile senza toccare il codice.
// ======================================================================================
const PF = DATI.porte_ferr;
let _pfCtx = {dx:false, w:67, h:82};   // contesto pezzo corrente: pezzo "destro" (45-90, zero in testa) e ingombri facce
function pfLav(w, descr, x, y, z, f, v1, v2, ut){
  f = String(f);
  if(_pfCtx.dx && PF.dx_specchio){      // pezzo ribaltato testa-piede: F2<->F3 (Y dal lato opposto), F1/F4 con Y speculare
    if(f==='2'){ f='3'; y=_pfCtx.h-y; } else if(f==='3'){ f='2'; y=_pfCtx.h-y; } else { y=_pfCtx.w-y; }
  }
  return {x:Math.round(x*10)/10, w, v1:String(v1), v2:v2==null?'':String(v2), v3:'2', y:Math.round(y*1000)/1000, z, f, ut:String(ut), descr:descr+' [DA TARARE]'};
}
function pfForo(descr, x, y, d, f, z, ut){ return pfLav('#0', descr, x, y, z, f, d/2, '', ut); }
function pfAsola(descr, xc, y, larg, lung, f, z, ut){ return pfLav('#1', descr, xc, y, z, f, larg, lung, ut); }
function pfUt(d){ // utensile per diametro (tabella utensili LMT65 in dossier)
  const t = PF.utensili; return t[String(d)] || t.default;
}
// numero e posizioni cerniere (asse) dal filo INFERIORE dell'anta
function pfPosCerniere(AB, ncern, zoccolo){
  let n = ncern>0 ? ncern : (PF.cerniere.n.find(([lim])=>AB<=lim)||[0,3])[1];
  const alto = AB - PF.cerniere.pos_alto, basso = zoccolo ? PF.cerniere.pos_basso_zoccolo : PF.cerniere.pos_basso;
  if(n<=1) return [Math.round((AB/2)*10)/10];
  const out=[]; for(let i=0;i<n;i++) out.push(Math.round((basso + (alto-basso)*i/(n-1))*10)/10);
  return out;
}
// X macchina: pezzi "SX" (90-45) con lo zero al piede; pezzi "DX" (45-90) con lo zero in testa (opzione PF.x_da_alto_dx)
function pfX(xDalBasso, mm, dx){ return (dx && PF.x_da_alto_dx) ? Math.round((mm - xDalBasso)*10)/10 : Math.round(xDalBasso*10)/10; }

function lavPorta(t, r, p, k, mm, conDren, conForo8, accessori){
  const out=[]; const ferr = r.ferr||{cern:'2ali',ncern:0,serr:'732251'};
  const F = PF.facce, serie = t.serie, prof = p.art;
  const d = p.desc.toLowerCase();
  const montStip = /montante stipite/.test(d), travStip = /traverso stipite/.test(d);
  const montAnta = /montante battente/.test(d) && !/centr/.test(d), montCentr = /montante battente/.test(d) && /centr/.test(d);
  const dueAnte = t.forma==='P2';
  const mano = (r.mano||'dx');
  // ruolo del pezzo: SX / DX (lato esterno, cerniere o serratura) / CENTRO (montante centrale dell'anta attiva, 2 ante)
  const label = /\(sx\)/.test(d) ? 'SX' : /\(dx\)/.test(d) ? 'DX' : null;
  const ruolo = montStip ? (label || (k===0?'SX':'DX')) : label ? (k===0 ? label : 'CENTRO') : (['SX','DX','CENTRO'][k] || 'CENTRO');
  const isSX = ruolo==='SX', isDX = ruolo==='DX';
  const dx = p.ang==='45-90';   // pezzo con taglio 45° a sinistra (testa) e 90° a destra: nel job lo zero X è in testa
  const AB = valuta(t.profili.find(q=>/montante battente/i.test(q.desc)).mis, r.L, r.H, r) || (r.H-55);
  const AM = r.hm || PF.AM;
  const zoccolo = t.profili.some(q=>/zoccolo/i.test(q.desc));
  const prof_tel = t.telaio_rif, prof_anta = t.anta_rif;
  const dep = DATI.altezze[prof_tel] ? (DATI.profili_ana[prof_tel]||{}).w || 67 : 67;   // profondità telaio (67 / 77)
  const depA = (DATI.profili_ana[prof_anta]||{}).w || dep;
  const hA = DATI.altezze[prof_anta] || 82;                                            // altezza anta (faccia)
  _pfCtx = {dx, w: (montStip||travStip) ? dep : depA, h: (montStip||travStip) ? (DATI.altezze[prof_tel]||66) : hA};

  // ---------- 1) FISSAGGI TELAIO A MURO (10.01): Ø7 lato muro + Ø15 lato battuta, A=200, passo ≤700 ----------
  if(conDren && (montStip || travStip) && PF.fx.attivo){
    const A = PF.fx.a, span = mm - 2*A, n = Math.max(1, Math.ceil(span/PF.fx.passo)), passo = span/n;
    for(let i=0;i<=n;i++){
      const x = Math.round((A + i*passo)*10)/10;
      out.push(pfForo(`Fissaggio telaio Ø${PF.fx.d1} lato muro (10.01)`, x, dep - PF.fx.y_est, PF.fx.d1, F.telaio.muro, PF.fx.z1, pfUt(PF.fx.d1)));
      out.push(pfForo(`Fissaggio telaio Ø${PF.fx.d2} lato battuta (10.01)`, x, PF.fx.y_est, PF.fx.d2, F.telaio.battuta, PF.fx.z2, pfUt(PF.fx.d2)));
    }
  }
  if(!conForo8) return out;

  // lato cerniere: 1 anta -> montante secondo la mano; 2 ante -> entrambi i montanti stipite / entrambe le ante esterne
  const latoCern = dueAnte ? (isSX || isDX) : (mano==='dx' ? isDX : isSX);
  const latoSerr = dueAnte ? (ruolo==='CENTRO') : (montStip ? !latoCern : (mano==='dx' ? isSX : isDX));
  const pos = pfPosCerniere(AB, ferr.ncern, zoccolo);

  // ---------- 2) CERNIERE ----------
  const C = PF.cerniere;
  if(ferr.cern==='2ali' || ferr.cern==='3ali'){
    const q = C.ali; const yTel = dep - (q.y_telaio[prof_tel] ?? q.y_telaio.default), yAnta = (q.y_anta[prof_tel] ?? q.y_anta.default);
    const seq = ferr.cern==='2ali' ? q.seq2 : q.seq3;   // offset dei fori rispetto all'asse cerniera (dall'alto: telaio/anta)
    if(montStip && latoCern){
      pos.forEach(xc=>{ seq.telaio.forEach(o=> out.push(pfForo(`Cerniera ${ferr.cern} telaio Ø${q.d} (10.32-35)`, pfX(xc + C.offset_telaio + o, mm, dx), yTel, q.d, F.telaio.battuta, q.z, pfUt(q.d)))); });
    }
    if(montAnta && latoCern){
      pos.forEach(xc=>{ seq.anta.forEach(o=> out.push(pfForo(`Cerniera ${ferr.cern} anta Ø${q.d} (10.32-35)`, pfX(xc + o, mm, dx), yAnta, q.d, F.anta.battuta, q.z, pfUt(q.d)))); });
    }
  } else if(ferr.cern==='stelo'){
    const q = C.stelo;
    if(montStip && latoCern){
      pos.forEach(xc=>{ q.telaio.forEach(([o,y,dd])=> out.push(pfForo(`Cerniera stelo H51300 telaio Ø${dd} (10.41)`, pfX(xc + C.offset_telaio + o, mm, dx), dep - y, dd, F.telaio.battuta, q.z, pfUt(dd)))); });
    }
    if(montAnta && latoCern){
      pos.forEach(xc=>{ q.anta.forEach(([o,y,dd])=> out.push(pfForo(`Cerniera stelo H51300 anta Ø${dd} (10.41)`, pfX(xc + o, mm, dx), y, dd, F.anta.battuta, q.z, pfUt(dd)))); });
    }
  } else if(ferr.cern==='nascoste'){
    const q = C.nascoste;
    if(montStip && latoCern){
      pos.forEach(xc=>{
        const xt = xc + C.offset_telaio;
        out.push(pfAsola(`Cerniera nascosta H59313 telaio sede ${q.tel_sede[0]}x${q.tel_sede[1]} prof.${q.tel_sede[2]} (10.52)`, pfX(xt, mm, dx), dep - q.tel_y_sede - q.tel_sede[1]/2, q.tel_sede[1], q.tel_sede[0], F.telaio.battuta, -q.tel_sede[2], pfUt('fresa')));
        [-q.tel_int/2, q.tel_int/2].forEach(o=> q.tel_y_fori.forEach(y=> out.push(pfForo(`Cerniera nascosta telaio Ø${q.d} (10.52)`, pfX(xt+o, mm, dx), dep - y, q.d, F.telaio.battuta, q.z, pfUt(q.d)))));
      });
    }
    if(montAnta && latoCern){
      pos.forEach(xc=>{
        out.push(pfAsola(`Cerniera nascosta H59313 anta sede ${q.anta_sede[0]}x${q.anta_sede[1]} prof.${q.anta_sede[2]} (10.52)`, pfX(xc, mm, dx), q.anta_y_sede + q.anta_sede[1]/2, q.anta_sede[1], q.anta_sede[0], F.anta.battuta, -q.anta_sede[2], pfUt('fresa')));
        [-q.anta_int/2, q.anta_int/2].forEach(o=> q.anta_y_fori.forEach(y=> out.push(pfForo(`Cerniera nascosta anta Ø${q.d} (10.52)`, pfX(xc+o, mm, dx), y, q.d, F.anta.battuta, q.z, pfUt(q.d)))));
      });
    }
  }

  // ---------- 3) SERRATURA (anta attiva) e INCONTRI (stipite lato serratura / montante centrale semifisso) ----------
  const S = PF.serrature[ferr.serr];
  if(S){
    const yAntaS = depA - S.y_est, yTelS = S.y_est;   // asse asole: 22.5 (AluK) / 23 (Cisa-Iseo) dalla faccia esterna
    // anta: montante lato serratura (1 anta: opposto alle cerniere; 2 ante: montante CENTRO dell'anta attiva —
    // nel catalogo il montante centrale U51340/U52340 "centr" è quello della semifissa, l'attiva chiude sul secondo "(DX)")
    if(montAnta && latoSerr){
      const xr = (o)=> pfX(AM + o, mm, dx);
      S.anta.forEach(a=>{
        if(a.tipo==='asola') out.push(pfAsola(`${S.nome}: ${a.nome} ${a.lung}x${a.larg}`, xr((a.da+a.a)/2), yAntaS, a.larg, a.lung, F.anta.battuta, S.z, pfUt('fresa')));
      });
      // maniglia e cilindro sulle facce dell'anta (interno + esterno)
      const fMan = [F.anta.interno, F.anta.esterno];
      fMan.forEach(f=>{
        const y = (f===F.anta.interno) ? (hA - S.entrata) : S.entrata;     // 35 dal bordo battuta anta (E)
        out.push(pfForo(`${S.nome}: foro maniglia Ø${S.d_maniglia} (AM)`, xr(0), y, S.d_maniglia, f, S.z_facce, pfUt(S.d_maniglia)));
        if(S.cilindro) out.push(pfAsola(`${S.nome}: cilindro ${S.cilindro[1]}x${S.cilindro[0]} (AM-${S.int_cilindro})`, xr(-S.int_cilindro), y, S.cilindro[0], S.cilindro[1], f, S.z_facce, pfUt('fresa')));
      });
    }
    // incontri: stipite (1 anta, lato serratura) oppure montante centrale semifisso (2 ante)
    const suStipite = !dueAnte && montStip && latoSerr;
    const suCentrale = dueAnte && montCentr;
    if(suStipite || suCentrale){
      const y = suStipite ? yTelS : (depA - (S.y_centrale||S.y_est));
      const f = suStipite ? F.telaio.battuta : F.anta.battuta;
      const xr = (o)=> pfX(AM + (suStipite ? C.offset_telaio : 0) + o, mm, dx);
      S.incontri.forEach(a=>{
        out.push(pfAsola(`${S.nome}: incontro ${a.nome} ${a.lung}x${a.larg}`, xr((a.da+a.a)/2), y, a.larg, a.lung, f, S.z, pfUt('fresa')));
        (a.fori||[]).forEach(o=> out.push(pfForo(`${S.nome}: foro fissaggio incontro Ø${S.d_fori||4}`, xr(o), y, S.d_fori||4, f, S.z, pfUt(S.d_fori||4))));
      });
    }
  }

  // ---------- 4) CATENACCI anta semifissa (2 ante, kit 732089 / 732281, 10.21-10.23) ----------
  if(dueAnte && montCentr && PF.catenacci.attivo){
    const q = PF.catenacci;
    const xSup = AB - AM - q.x_sup_da_alto;           // inizio asola dal filo superiore (X = AB - AM - 643)
    const xcSup = AB - (xSup + q.asola[0]/2);         // centro asola dal basso
    out.push(pfAsola(`Catenaccio 732089 semifissa sup. asola ${q.asola[0]}x${q.asola[1]} (10.21)`, pfX(xcSup, mm, dx), depA - q.y, q.asola[1], q.asola[0], F.anta.battuta, S? S.z : -3, pfUt('fresa')));
    if(q.x_inf_da_basso) out.push(pfAsola(`Catenaccio 732089 semifissa inf. asola ${q.asola[0]}x${q.asola[1]} (10.22)`, pfX(q.x_inf_da_basso + q.asola[0]/2, mm, dx), depA - q.y, q.asola[1], q.asola[0], F.anta.battuta, S? S.z : -3, pfUt('fresa')));
  }
  return out;
}
