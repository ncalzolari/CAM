# DOSSIER DI CONTINUITÀ — Generatore Commesse FOM LMT65 (Nord Infissi)
*Da caricare all'inizio della nuova chat insieme a `Commesse_LMT65.html` (e, se si lavora sui dati, `dati_serie.js`). Versione 15/09/2026: serie Cortizo COR80 spinoff indipendente in `../commesse-cor80/` (sez. 11 qui è solo il pointer); serie AluK S140 con lavorazioni dal manuale v3A (sez. 12); 07/09/2026: serie porte D67/D77 (sez. 10).*

## 1. CONTESTO
Produttore serramenti alluminio. Flusso attuale: FP Pro/WinPlus → job XML → **FSTLine** su centro **FOM LMT 65**.
Obiettivo: app HTML **standalone offline** che genera commesse complete (tagli+lavorazioni+distinta) senza FP Pro.
Serie: **AluK C75S** (anta-ribalta in vista, ferramenta **Maico Multi-Matic**) e **C82S-CS** (scomparsa); dal 07/09/2026 anche **porte AluK D67 = IWG 67ID** e **D77 = IWG 77ID** (sez. 10).

## 2. CONSEGNE ATTUALI
- **Commesse_LMT65.html** (~700 KB): app completa. Struttura interna: template + `const DATI = {...}` + logica.
  Sorgenti di lavoro (nella sessione precedente): `app_template.html` + `dati_app.json` + `app_logic.js`,
  assemblati con `tpl.replace('/*__DATI__*/',dati).replace('/*__SCRIPT__*/',js)`.
  ⚠️ In una nuova chat i sorgenti NON esistono più: **estrarli dall'HTML** (split su `<script src="dati_serie.js"></script>\n<script>` … `</script>`; DATI = primo `const DATI = …;`).
- **dati_serie.js**: archivio dati esterno (fusione all'avvio se accanto all'HTML; pulsante "Esporta archivio dati" nel programma).

## 3. STATO VALIDAZIONE (contro job FP Pro reali)
- **Pilota esteso** (provaxml__4_.xml, 6 serramenti C75S): **420/421 lavorazioni**, 0 spurie
  + **5 extra VOLUTI** (sfiato semifissa, schema aziendale che FP non faceva).
  F1AR 1200×1650 (1 anta): 54/54 · F2AR 1600×1800 e altre 4 due-ante stulp (1200×1800, 1550×1850, 1800×2000, 1650×1650).
  Unico mancante: foro X404,5 su 1800×2000 = **forbice supplementare ante >800 larghe E alte** (regola non fissata, non emesso).
- **Composta F09** (scuola, 3955×2088, 6 ribalte + 5 montanti T): **33/33 tagli** identici.
- **Prova del nove**: cella 1×1 PFDX ≡ tipologia portabalcone (entrambe le serie).
- **Importatore XML**: 6/6 serramenti del pilota riconosciuti (tipologia+misure esatte).
- **NON ancora fatto: collaudo a video in FSTLine dall'utente** (istruzioni già date: pilota nostro vs provaxml; unica differenza attesa = sfiato X576 su trav. sup. semifissa F2AR).

## 4. FORMATO JOB MACCHINA (validato)
XML **UTF-16LE con BOM**; JOB>BODY>BAR(SYST,CODE)>CUT(ANGL/ANGR: 135=45°, 90=squadro; IL; 4×LBL =
[descr. commessa, codice commessa, **ruolo** TEL/BAT/TRV/MNT, **etichetta serramento** es. "F18(25-26).H"])
>MACHINING(WCODE #0 foro/#1 asola; OFFSET=X; OFFSETY; OFFSETZ; FACE; VAR1=raggio; VAR2=lung. asola; CODUTENSILE).
Utensili: ut.2=d10 pos12 · ut.3=d8 p13 · ut.4=d3 p14 · ut.7=d3 F2 · ut.8=d8 p31 · ut.11=d8 p41 · ut.12=d5 p42 · ut.17=d6 p23 · ut.18=d6 p33.

## 5. REGOLE DI PRODUZIONE CALIBRATE (il tesoro — NON ricavare dal catalogo, vince la produzione)
**Tagli**: convenzione **−43** (anta = misura−43; catalogo dice −42). Fermavetri dal vetro (29↔N45861 anta / battente; 35↔N45860…: tabella nei DATI).
**Celle costruttore (da F09)**: detrazioni anta **21,5 (telaio) / 14,5 (montante T)**; PF bordo soglia 8,5; montante T C75S = **B23609C**, traverso T = B23608C (C82S: B23610C entrambi); montante T = H−46 (90/90).
**FX fissaggi** (in vista, tutte le tipologie): 150 dagli estremi + intermedi passo ≤900; Ø7,5 F4 Y62,999 Z−3 ut12 + lamatura Ø13,5 F1 Y11 Z−20,5 ut2.
**Drenaggi** (schema aziendale confermato): telaio C75S asola 6×33,6 Y22,7 Z3 F3 ut18 alle posizioni FX ±2; C82S 10×28 Y66,4 (B23610C: Y13,6). Anta: trav. inf. 2×Ø8 a 168; montanti 1×Ø8 a **218 dall'alto**; 2 ante stulp: **sfiato trav. SUP semifissa a 200 dal nodo** (novità vs FP) + scarico telaio extra a L/2 sotto il nodo. Il "③" dello schema = taglio guarnizione (banco, ignorato).
**Maico A-R** (doc 750135; quote **+26,5 singoli / +27,5 coppia** dal filo, **HBB = anta−20**):
- cremonese `cremoneseMaico(hbb)`; **HM_AMMESSE** per GR (1590→500/600, 1700→500/700…); campo maniglia per riga (precompilato, validato); martellina X = HM+18.
- montante maniglia: coppia alza-anta (int.16 Y10 Z−20,5) + singoli A1/A2 (Y8 Z−21,5) **dall'alto**; tabella SCONTRI_A per GR/HM.
- montante cerniere: angolo L−142; chiusure B dall'alto (hbb≤1280: 565 · ≤1700: 800 · ≤2200: 800+1506 · oltre +1977, offset 25,5/24,5); cerniere: Ø7 Y9,5 Z2 **F2** ut17 a [23,5/93,5] (specchiate [25,5/95,5]) + 4×Ø3 ut7 a 37,5–79,5.
- traversi 1 anta: coppia54 (Y9 Z−20,5) a 143,5 lato maniglia (basso) / L−142 (alto); chiusura orizz. C+27 se LBB>800 (C: 565/800); **scontro forbice** X = 506+28,5 (=534,5) — fasce aziendali forbice: 801–1050→"1050", 1051–1650→"1300", **quota 506 per entrambe** (provata su ffb 856 e 1137); ≤800 → null (non emesso).
- **2 ante stulp**: montante attivo = angolo+B/B1; montante semifisso = **cerniera centrale** coppia Ø3 int.38 a L/2 SEMPRE (Y9 Z−21,5); traversi al nodo: giù coppia54 a asse−123·s + catenaccio a asse+74,8·s; su coppia54 asse+124,5·s + catenaccio asse−46,8·s + forbice semifisso 506+28,5 dal cardine se ffb>800 (s=+1 mano DX).
- guard: ferramenta A-R solo forme ['1','2','P1','P2']; riconoscimento stulp: battuta==='stulp' OR /stulp/ nel nome tipologia.
**Facce** (conferme operatore): **1=superiore (zero a DESTRA, spigolo CAMERA)** · 2=destra (zero alto, DEDOTTO da verificare) · **3=sinistra (zero basso)** · **4=inferiore (zero SINISTRA)**. FP lavora sulla **camera rettangolare** (alette escluse) → `dxf_sez[].cam` ricavata dai DXF. **FACCIA_FISICA**: profili anta ruotati 180° in macchina → B23122C e B23100 rimappa {1↔4, 2↔3} SOLO in visualizzazione (job invariato; prova: martellina job F3→reale F2, scasso F1→F4). Audit 4100+ lav × 18 combinazioni: zero quote fuori estensione.

## 6. FUNZIONI DELL'APP (tutte collaudate)
COSTRUTTORE grafico prima voce menu: telaio L×H → griglia (interassi editabili, +/− montante/traverso) → **clic sulla cella nel disegno** cicla FISSO→ADX→ASX→VAS→2A (+PFDX/PFSX/PF2 solo riga inferiore, soglia ribassata std L−46 90-90, montanti 45-90/90-45; mista→segmenti "DA VERIFICARE") → **clic su montante/traverso** = profilo T ⇄ **telai accoppiati** (affiancati -U# / sovrapposti -O#); vincolo C82S per-giunto; sezioni DXF dei profili T mostrate al posto del vecchio selettore. Righe: **✎ modifica** (ricarica tutto nell'editor, "Salva modifiche riga N"), **quantità inline**. Distinta: righe verdi + badge, clic→schema pezzo **per faccia** (sezione DXF reale + camera + utensile verde stile FSTLine + zero). Anteprima: bande verdi sui lati lavorati, tocco→popup lavorazioni (calcolo al volo con leggiRigaCorrente). Libreria su secondo foglio. **Ferramenta celle nel costruttore** (13/09/2026): stipiti, montanti/traversi T e ante delle celle apribili (ADX/ASX/PF/2A stulp) ricevono FX, cerniere, scontri Maico, forbice, cerniera centrale e martellina con le stesse funzioni delle tipologie singole, trasposte per cella; sui T scontro d'angolo a 55,5 dal nodo e Y/faccia da libreria (`@B23609C`, `@B23608C`); marcatura `[DA VERIFICARE composta]` solo per le celle con almeno un profilo T (patch 8b, 14/09): la cella 1×1 (telai accoppiati con giunto R = unità distinte) coincide con la tipologia singola, drenaggi allineati allo schema aziendale (telaio FX ±2, anta 168, montante 218). Differenza residua nota: fermavetro orizzontale battente 1059 nel costruttore contro 1065 nella tipologia (anta 1157: detrazione 49+49 vs 46+46), da decidere con la produzione. **Tarature lavorazioni** (secondo foglio): regole ΔX/ΔY/ΔZ e cambio faccia per serie/profilo/faccia/lavorazione, salvate nel browser ed esportate con l'archivio dati (vedi sez. 11). **Importa job XML** (BOM utf-16/8, ricostruisce righe; composte segnalate). BLOCAL opzione (solo distinta, macro 201SAV00 da tarare). Esporta/importa commessa JSON; Esporta archivio dati.

## 6b. VERIFICA 15/09/2026 CONTRO I JOB REALI (220_26_1.xml, 220_26_2.xml, provaxml.xml)
Ricevuti finalmente i file XML nativi (non solo i .ncw) dei job citati in questo dossier: `220_26_1.xml` (50 barre, progetto "Scuola Corridoni", unità PT_F01.1.2 = composta con sopraluce), `220_26_2.xml` (152 barre), `provaxml.xml` (10 barre, il pilota). Struttura reale: `JOB > BODY > BAR > CUT > MACHININGS > MACHINING` con gli **stessi attributi** che il nostro `xmlBarra()` emette (`WCODE, OFFSET, OFFSETY, OFFSETZ, FACE, CODUTENSILE, DESCRIPTION`…) — conferma che il nostro formato job è compatibile con l'originale FST/FP Pro. La `DESCRIPTION` reale non è un nome semantico ma un'etichetta posizionale generica del CAM ("3-Circle pocket", "1-Rect"…): il confronto va quindi fatto per **impronta geometrica** (profilo + faccia + utensile + Y + Z + W/v1/v2), non per testo.
Estratte tutte le 4237 lavorazioni dei tre file (`C75S` 2716, `C82S_CS` 1443, `COMMON_C75_C82` 78) e confrontate contro `LAV_DEF_BASE.C75S` + `DATI.drain` (la libreria che il programma usa davvero): **8 lavorazioni su 11 verificate trovano un riscontro ESATTO** (stesso W/v1/v2/Y/Z/faccia/utensile) nei job reali — `fx_foro` (B23008C, F4 UT12 Y62.999 Z-3), `fx_lamatura` (F1 UT2 Y11 Z-20.5), `dren_telaio` (F3 UT18 Y22.7 Z3, W#1 6×33.6), `dren_antaMont`/`dren_antaTrav` (B23122C, F4 UT11 Y60.6 Z-19), `mart_d10` (F3 UT8 Y30 Z3), `mart_scasso` (F1 UT3 Y64 Z-12, W#1 12×62), `sc_angolo` (F1 UT4 Y9 Z-20.5), `cern_centrale` (F1 UT4 Y9 Z-21.5). Nessuna delle 8 impronte controllate si discosta di un solo millimetro dai job reali: **la libreria base C75S/C82S non risulta alterata** da nessuna delle modifiche di questa sessione (coerente con `regress.js` rimasto IDENTICO a ogni build). Una voce (`cern_d7`, F2 UT17 Y9.5 Z2) non trova riscontro in questi tre file: non è necessariamente un errore, i job non usano per forza ogni tipo di cerniera — resta da confermare su un job che la usi. **Non verificata** in questa sessione: la ferramenta celle composta (sospeso #2, unità PT_F01.1.2) — richiede ricostruire la matrice esatta della composta nel costruttore, non solo l'impronta delle lavorazioni base.

## 7. SOSPESI (in ordine di valore)
1. **Collaudo FSTLine dell'utente** (pilota) — poi primo pezzo fisico con ferramenta a secco.
2. **Ferramenta celle composta** — IMPLEMENTATA il 13/09/2026 (patch 8, `ferramentaCelleComposta()`, test `tests/composta_test.js`), DA VALIDARE col diff sul job 220_26 (marcatura `[DA VERIFICARE composta]`; connessioni alle teste dei T Y62,2 F4 non emesse: geometria non decodificata). Regole sui profili T già DECODIFICATE dai job 220_26 (scontri Y8, alza-anta Y10, **angolo a 55,5 dal nodo** Y12; lato opposto F4: connessioni Y62,2 alle teste, cerniere/supporti Y66,2) → implementare emissione nel costruttore e validare col diff su un serramento composto 220_26 (F09 ricostruito; PT_F01.1.2 = 16 unità [2A+sopraluce]; F13 = 2 unità vasistas; F10 = trav. passante → modellare come sovrapposti).
3. **Vasistas**: solo FX+drenaggi oggi. Approfondito il 17-18/09/2026 (richiesta utente "finestra 1 anta ribalta C75", già la tipologia `C75S_VASISTAS`/VAS75 esistente): nel job reale 220_26_2.xml, le celle vasistas trovate (`F23/1.(17)` e `F23/2`, anta 645-864mm/776-863mm — celle dentro una composta più ampia, coerente col riferimento "F13 = 2 unità vasistas" del punto 2) hanno **`<MACHININGS/>` vuoto sia sull'anta (BAT) sia sul montante (MNT)** — nessun foro CNC. Coerente con una ferramenta ribalta a montaggio superficiale (compasso/cerniera avvitati a secco, senza forature di fabbrica): **il "solo FX+drenaggi" attuale potrebbe già essere completo per l'anta**, non un segnaposto mancante. I fori extra (profondi, Z fino a -59) trovati sul telaio (`TEL F13.*`) sono le connessioni T già note e non decodificate del punto 2 (celle composta), non qualcosa di specifico del vasistas — da non confondere. **Non verificato**: il riferimento "F35" citato in una nota precedente non è presente nei file XML disponibili in questa sessione (solo `220_26_1.xml`/`220_26_2.xml`); se recuperabile, andrebbe controllato allo stesso modo prima di chiudere definitivamente questo sospeso.
4. **Scomparsa C82S**: rif. F12 (lot con 72 fitting: E167/S167 Multi Power; job 220_26_2).
5. Forbice supplementare (X404,5) · verso zero **faccia 2** · rimappa **B23100** · PB reale (convenzione −43 estesa senza riscontro) · profilo di giunzione telai accoppiati (articolo?) · BLOCAL macro.
6. **Archivio utensili** (vedi sez. 8): scheda catalogo "fresa d.8 + **d.4**" (T05/T06, telaio C75S/C82S) non trova un utensile da 4 mm nell'archivio FSTLine ricevuto — verificare in produzione se è un refuso (d.3/d.5/d.10?); utensili **14 e 15** mancanti dall'export, probabile lama/troncatrice usata per i placeholder "lama"/"lama/fresa" (A06/A07) — servirebbe l'export completo o conferma diretta. Nessun impatto sul job oggi: sono solo le schede descrittive del catalogo, non i codici realmente emessi.

## 8. FILE DI RIFERIMENTO (ricaricare quando serve il tema)
- Pilota: `provaxml__4_.xml` + `provaxml__2_.ncw` (6 serramenti; ncw: CLabel4=serramento, CLabel3=ruolo).
- Produzione: `220_26_1/2.ncw` (+ job xml macchina se disponibili), `220_26_*.jlt`, correzioni `*_Tipo_F35/F23-2.jlt`.
- `FERRAMENTA_MAICO_TUTTO.xml` (personalizzazione WinPlus, 6754 regole), catalogo `C75S_C82S-CS_CAT_v3_C_unlocked.pdf` (lavorazioni sez.9 p.93-113), doc Maco **750135** (tabelle p.26-34, su maco.eu).
- I **DXF dei profili sono dentro le macro .LDT** dell'archivio macchina (zip: Machine.ini + .SERIE + DXF + binario FomCam).

- `docs/riferimenti/FP_PRO_10_User_Manual_ENG.txt` — estratto testo del **manuale utente FP PRO 10** (Emmegisoft, 1996-2009; ricevuto il 13/09/2026 come "il software che usiamo oggi"). Copre progettazione tipologie (macro, multi-giunti, sezioni), profili/DXF archivio, **kit e accessori** (variabili standard L H P W A, `E[n]` lati, `O[n]` aperture, `AE` aletta esterna, `LBOX`/`HBOX` ingombro, `S[n]`/`HS[n]` scorrevoli; sistemi "range" e "distanza" per la quantità = attributi `RefDim`/`CalcDim`/`ParametricSystem` dei `FP_FITTING` nei `.BLK`), calcolo commessa, ottimizzazione barre, preventivi, FPOffer. **Non contiene nulla sulle lavorazioni macchina** (facce 1-4, zero, orientamento barre, camera): quella parte è in FP_CAM / FST, di cui non abbiamo il manuale.

- `docs/riferimenti/CAMplus_2.0_manuale_ITA.txt` — estratto testo del **manuale CAMplus 2.0** (Emmegisoft 2005; ricevuto il 13/09/2026): il programma che crea i gruppi di lavorazione **LDT** della libreria macchina (`docs/inventario_LDT_macchina.txt`). **Convenzioni che contano per noi**: (1) sistema di riferimento pezzo fisso W (larghezza), H (altezza), X (lunghezza); origine W/H in basso a sinistra del contorno del profilo, X riferita alla **coda** del pezzo (estremo sinistro) con quote assolute o parametriche (`MIN`, `MID`, `MAX±offset`, `w1/1`, `HMID`…); Y e Z sono nel sistema **utensile** (Y perpendicolare all'utensile con verso positivo in alto, Z parallela con verso positivo uscente dal pezzo); (2) il piano di lavoro è la faccia resa perpendicolare al mandrino, le "quattro facce notevoli" sono selezionabili direttamente; la faccia inferiore, se la macchina non porta il mandrino sotto, si ottiene **ribaltando il pezzo di 180° in CAMplus come in macchina** (icona Appoggio 180°); (3) "riferimento a camera" (aletta/camera interna/esterna × lato caldo/freddo) e `iW`/`iH` per rendere lo stesso LDT applicabile a profili diversi, a patto che **tutti i profili siano orientati allo stesso modo** (`Strumenti – Definisci appoggio profilo`); (4) **DXF per Frame Project Pro: vetro in alto e lato freddo a sinistra**, scala 1:1, senza blocchi, solo la sezione; tabella Fronte/Retro in funzione di appoggio (freddo/caldo) e taglio (vetro interno/esterno); orientamento del pezzo in macchina come direzione X: vista Fronte → perimetrali in senso orario, separatori verticali verso il basso e orizzontali verso sinistra (Retro: il contrario); (5) Appendice A = tabella dei **codici LDT** (001-008 squadrette, 010-015 fori fissaggio, 040/041 regolo, 050 scarico acqua, 060/061 cremonese, 560-565 maniglia, 070-088 cerniere, 090-107 serrature/incontri, 120-146 scassi) con suffissi (S) simmetrica, (AA) asimmetrica per ala, (AR) asimmetrica Sx/Dx (si crea solo la Sx); nome LDT = codice + marca accessorio + progressivo, esattamente lo schema dell'inventario macchina (`010NOR01` fissaggio telaio, `040GS003` regolo Giesse, `050MED02` scarico acqua Medal, `090CIS02` serratura Cisa, `105FAP19` incontro Fapim…; 141 LDT su 313 con prefisso in tabella, i codici 018/055/200-215 sono estensioni aziendali). **Conseguenze**: la richiesta "COR80 ruotata di 180°" coincide con la convenzione FP Pro: i DXF Cortizo "SinCotas" sono disegnati con vetro in basso e freddo a destra, la rotazione li porta a vetro in alto / freddo a sinistra (`ruota180`, patch 7e); le facce F1-F4 e le Y per faccia del job FST restano la nostra convenzione di uscita (sez. 5), diversa dal sistema W/H/X di CAMplus ma coerente con esso (F1 = faccia superiore in appoggio normale, F4 = faccia lavorata con appoggio 180°).

- `docs/riferimenti/utensili_macchina.json` — **archivio utensili FSTLine** (export 23/12/2025, ricevuto il 15/09/2026): 19 frese numerate 1-19 (ID = `CODUTENSILE` nel job, "pos." = posizione mandrino, non il codice), diametro/lunghezza di taglio e velocità di ingresso/finitura/lavoro/uscita per ciascuna. Confrontato con i codici già usati in `DATI.lav_def[serie][...].ut` (quelli che generano davvero il job XML): **ut.11** (fresa d.8 pos.41), **ut.12** (fresa d.5 pos.42), **ut.17/18** (fresa d.6 pos.23/33), **ut.2/3/4/7/8** (COR80) risultano tutti coerenti con l'archivio — nessuna correzione necessaria ai codici di produzione. Le voci descrittive del catalogo (`DATI.libreria`, le schede a video, **non** usate nel job) restano invariate: "fresa d.3"/"fresa d.5" generiche hanno più utensili equivalenti in archivio (es. d.3 = ut.4/7/10/13, tutte stesse specifiche) e non serve sciogliere l'ambiguità; "fresa d.8 + **d.4**" (T05/T06 catalogo C75S/C82S) **non trova riscontro**: l'archivio non contiene nessuna fresa da 4 mm (diametri presenti: 3-5-6-8-10) — probabile refuso per d.3/d.5/d.10, da chiedere in produzione. Mancano gli ID **14 e 15** (numerazione che salta da 13 a 16): verosimilmente la lama/troncatrice usata per i placeholder "lama" (A07) e "lama/fresa" (A06) del catalogo ante C75S/C82S, non risolvibili senza l'export completo.

## 9. METODO (che ha prodotto il 100%)
1) Riferimento FP reale → 2) genera → 3) **diff multiset** chiave `prof|geo|Y|Z|F|ut|X(±0,5)` → 4) ogni scarto = una regola da capire (mai copiare quote: ancorarle a tabelle/assi) → 5) flag onesto su ciò che è calibrato su un solo esemplare. Collaudi in node: mock DOM minimale (el() con value/innerHTML/dispatchEvent), `eval(js)` con const→var per DATI/righe/matC. ⚠️ **Sostituzioni testo sempre con assert** (una replace silenziosa ha nascosto una toolbar per giorni). Prudenza: meglio un foro mancante e dichiarato che uno inventato.


## 10. SERIE PORTE D67 / D77 (IWG 67ID / IWG 77ID) — aggiunte il 07/09/2026
**Fonti**: Catalogo tecnico AluK D67-D77 v4C (23.06.2025; distinte di taglio sez. 8 del 14.10.2024, sinottico 2.01-2.06, indice 2.07-2.15, vetrazione 7.04/7.05, accessori 3.01-3.21) e Manuale lavorazioni e assemblaggio v4.A (10.01-10.84). Trascrizioni complete in `dati_catalogo_D67_D77/*.json` (distinte, indice profili, accessori, lavorazioni manuale). **Nessun job FP Pro di riferimento: serie mai prodotta** → tutto ciò che non è una formula di catalogo è marcato DA TARARE.
**Serie nel programma**: id `D67` / `D77` (= SYST nel job e cartella libreria macchina `W:\LMT_65\CAM\D67|D77`). `DATI.serie_info` (nome, porta:true), `DATI.varianti_porte` (telaio standard ↔ con ala 32: U51200→U51220, U51201→U51240, U52200→U52220, U52201→U52240), `DATI.porte_ferr` (tutti i parametri lavorazioni), tavole vetro `vetrazione.tavD67/tavD77` (spessore → fermavetro squadrato N488xx, tubolare, clips; guarnizione interna), `altezze`/`profili_ana`/`dxf_sez` per 31 profili (16 sezioni reali dai DXF di macchina; `cam` = ingombro totale, DA TARARE).
**Tipologie** (35 = tutte le pagine 8.01-8.20 D67 e 8.21-8.39 D77): id `D67_<titolo>_INT|EST|VENT[_Z]`, cod `P{1|2}{I|E|V}{A auto|K K1490|S K1769/K2069|P pannello|L sopraluce}[E esodo][Z zoccolo]{67|77}`, es. **P1IAZ67** = 1 anta ap. interna soglia automatica con zoccolo. forma P1/P2; campi `porta`, `apertura`, `sopraluce` (formule H1/H2: **H2 = altezza sopraluce inserita, H1 = H−H2**, `valuta(formula,L,H,r)`), `anta_rif`, `telaio_rif`. Profili con `fv:true` = fermavetro dalla tavola (art `FVxx`). Pezzi SX/DX con sc `TELS/TELD/ANTS/ANTD`, centrale `ANTC`. K1777 asta catenacci e tutti gli accessori a testo ("in base alle dimensioni", "vedi lavorazioni") vanno in distinta con quantità nulla.
**Distinta (sicura, = catalogo)**: anta L−94 / H−55 (H−79 con soglia K1769/K2069, H−57 senza zoccolo ap. esterna), 2 ante L/2−37,5, zoccolo L−230 (L/2−173,5), soglia K1490 L−95, K1769/K2069 L−123, sopraluce con U20001/U28003 + N51260/N52260 + tagliavetro U20601/U28602 L−83. Vetro L−258 × H−283 ecc. per pagina.
**Lavorazioni porte** (`lavPorta` in `porte_logic.js`, parametri in `DATI.porte_ferr`, TUTTE marcate "[DA TARARE]" nel job):
- Convenzione facce/versi (per analogia con C75S, MAI verificata): telaio F1 = battuta verso anta, F4 = muro, F2 interno, F3 esterno; anta ruotata 180° → battuta F4. Pezzi con taglio **45-90 (montanti DX)**: zero X in testa (`x_da_alto_dx`) e facce ribaltate F2↔F3 con Y speculare (`dx_specchio`); i pezzi 90-45 hanno lo zero al piede. Se in FSTLine risulta invertito: mettere a false i due flag.
- Fissaggi telaio (10.01): Ø7 lato muro F4 + Ø15 lato battuta F1, asse 21,9 dalla faccia esterna, A=200, interasse ≤700, su montanti e traverso (checkbox "Drenaggi telaio").
- Cerniere (select per riga): 2/3 ali Ø11 (Y anta 47 / telaio 17,5 dal bordo interno; seq. fori 22/21/20; dima T10095), stelo H51300 (**fori segnaposto**: il manuale rimanda alla dima T10020), nascoste H59313 (sede 124×36 prof.41 / 170×28 prof.43 + 4 Ø11). N. cerniere: ≤1300→2, ≤2400→3, oltre 4 (o forzato); asse a 256 dall'alto, 244 dal basso (274 con zoccolo) dal filo anta, +6 sul telaio — regola presa dalla tabella cerniere nascoste 10.51 ed estesa a tutte.
- Serrature (select): AluK 732251 / H51400 / 732259 (asole frontale 255×16, deviatori 190×16 a AM+630…820 / AM−855…−665; incontri stipite 80×22 AM−12…+68, 54×16 AM−85…−31, ganci 100×16; asse asole 22,5 dalla faccia esterna), CISA/ISEO (solo incontri 732176: 55×11,5 e 93×11,5, asse 23; frontale e deviatori dipendono dalla serratura → non emessi). Maniglia Ø20 (**non quotata**) e cilindro 10,5×33,5 a AM−92 su F2/F3 a E=35 dal bordo. **AM = 1050** dal filo inferiore anta (campo "altezza maniglia").
- 2 ante: anta attiva = destra (montante "(DX)" k=1 = centrale attiva), incontri sul montante centrale U51340/U52340 della semifissa; catenaccio 732089 asola 130×20 a X = AB−AM−643 dal filo superiore (parte inferiore 10.22 non emessa).
- NON emessi: squadrette (tranciante/punzonatrice, banco), fresate labbro cerniere nascoste, fori Ø6 posizionamento dima, catenacci inferiori, tappi/soglie (spuntature), Dorma ventola, drenaggi (non previsti a manuale).
**Collaudo fatto**: headless (Playwright) su 1 anta int., 2 ante K1490, sopraluce D77 (H2), ap. esterna 45-45, tutte le cerniere/serrature: nessun errore, job XML con SYST D67/D77, schemi pezzo ok. **Regressione C75S/C82S: output identico** al programma precedente (4 tipologie, 66 pezzi).
**Sospesi porte** (in ordine): 1) collaudo a video FSTLine di P1IAZ67 1000×2200 → tarare facce/versi/Y in `porte_ferr`; 2) **libreria macchina D77 incompleta** (solo U52200, U52201, U52320, U52340, U52630: mancano U52220/U52240/U28003/U28602/U28630/U52501/U52500/U52300/N52260/K2069 → job rifiutato per quei codici finché non si caricano i DXF AluK); D67 mancano U20001/U20601/K1486/K1483/K1488/K1577; 3) quote dima T10020 (stelo) da rilevare; 4) Ø foro maniglia; 5) altezze `altezze[]` porte = nominali di catalogo (U51320 82, U51340/U52320/U52340 96) → verificare OL; 6) costruttore a griglia per porte (celle porta in composta) non fatto; 7) importatore job XML non riconosce D67/D77.
**Sorgenti di lavoro (cartella `sorgenti_porte/`)**: `build_porte.py` (distinte JSON → tipologie/profili/vetrazione), `porte_ferr.py` (parametri lavorazioni + libreria), `porte_logic.js` (modulo lavorazioni, sostituisce il segnaposto in `app_logic.js`), `patch1.py` (modifiche al programma base con assert), `assemble.py` (template + DATI + logica → HTML), `test_porte.js` / `regress.js` / `job_test.js` (collaudi Playwright). Job 220_26_2.xml (scuola, C75S/C82S, portefinestre PT/P1) ricevuto: utile per il sospeso 5 di sez. 7, non contiene porte D67/D77.

**Libreria macchina FP_CAM D67/D77 (archivio `Documents.zip`, 11/09/2026)**: cartelle `D67` e `D77` con i DXF di macchina (importati in `data/dxf/`: D77 passa da 5 a 22 sezioni, tra cui U52240/U52261/U52300/U52500/U52501/N52260/K2069/U28630; D67 U20630B e U51340A aggiornati), file `.ADD`/`.CMPBAK`/`.nod`/`SHAPES.DAT` (binari FP, indici dei profili), e per D67 i 23 blocchi tipologia `.BLK` (XML FP Pro 10.0.14: "Telaio 3L apertura interna", "Anta apertura interna con soglia K1490", "2 ante con stulp per via di esodo"…) con kit e accessori → estratto in `data/catalogo_D67_D77/fp_blk_D67.json`. I blocchi **non** contengono le coordinate delle lavorazioni (sono nei kit di FP_CAM, non presenti nell'archivio): le lavorazioni porte restano DA TARARE. Profili ancora senza DXF: K1483, K1486, K1488, K1577, U20001, U20601, U28003, U28602, U52360.


## 11. SERIE CORTIZO COR80: SPINOFF INDIPENDENTE (15/09/2026)
La sezione 11 originale (serie Cortizo COR 80 Evolution) è stata tolta da qui: la serie è diventata un progetto
autonomo, `../commesse-cor80/` (stesso motore di calcolo copiato, solo i dati COR80; dossier proprio in
`../commesse-cor80/docs/DOSSIER_COR80.md`, contenuto identico a questa sezione prima dello spinoff, consultabile
nella cronologia git di questo file per chi la cerca qui). Questo programma (`commesse-lmt65`) copre da qui in
avanti solo le serie AluK: C75S, C82S-CS, D67, D77, S140.

## 12. SERIE ALUK S140 — LAVORAZIONI MACCHINA DAL MANUALE V3A (15/09/2026)
**Fonte**: `Manuale di lavorazioni e assemblaggio S140 v3A` (07.04.2025; 82 pagine, sez. 9 "Lavorazioni" 9.01-9.49,
sez. 10 "Assemblaggio" 10.01-10.36), caricato dall'utente il 15/09/2026. **Nessun job di produzione S140 esiste**
(la serie non è mai stata fabbricata su questo centro di lavoro): a differenza di C75S/C82S-CS (calibrate su job
FP Pro reali) e alla pari di D67/D77, qui non c'è nulla contro cui validare — tutto resta `[DA TARARE]` per
definizione, non per prudenza temporanea.

**Cosa fa il motore (`src/s140_lav_logic.js`, funzione `lavS140`, chiamata da `calcolaCommessa()` per ogni pezzo
con `t.serie==='S140'`, come `lavPorta` per le porte)**:
- **Fissaggio telaio a muro** (pag. 9.01): Ø5, 200 mm dagli estremi + intermedi a passo ≤800 mm (stesso algoritmo
  di `posFX`/`posizioniDrenaggio`, `bordo=200, passo=800`), su ogni traverso/montante di U10020/U10400/U10060/
  U10061/U10402/U10403/U10000/U10401 (checkbox "Drenaggi telaio").
- **Squadretta telaio** (pag. 9.02): 2× Ø8 per angolo (49.8 e 99.6 mm dal filo di squadro), sui tagli a 45° di
  U10020/U10060/U10061/U10000. I profili soglia ribassata (U10400/U10401/U10402/U10403) **non** sono in questa
  tabella del manuale (si assemblano diversamente, pag. 9.03, non implementata — vedi sotto).
- **Squadretta anta** (pag. 9.41, sezione superiore): Ø5 a 7.7 mm dal filo di squadro, su ogni taglio a 45° di
  ogni pezzo U10140 (traverso/montante anta), qualunque tipologia.
- **Drenaggio soglia** (pag. 9.04/9.06/9.08/9.10/9.12/9.14): asola 5×30 (fresa 909333), passo ~400 mm ("zona
  esposta" del manuale), bordo dagli estremi variabile per profilo (160 mm per U10020/U10060/U10061/U10000, 100
  mm per U10400/U10401/U10402/U10403 — soglie ribassate, più corte). Applicato al pezzo dedicato soglia ribassata
  (riconosciuto da `/soglia/i` nella descrizione) oppure, quando la soglia è standard, al primo traverso telaio
  tagliato per quella tipologia (`k===0`, per analogia con la convenzione C75S "il primo pezzo è il traverso
  inferiore" — **mai verificata per S140**, potrebbe risultare invertita).
- **Ventilazione/drenaggio anta apribile** (pag. 9.48): asola 5×15 su ogni traverso anta non centrale delle
  tipologie scorrevoli (`forma` che comincia per `S:`), entrambe L&S e R.

**Quote per cui il manuale NON dà un numero** (X lungo la barra chiaro dal disegno, Y nella sezione stimata —
al centro profilo via `DATI.profili_ana[art].w/2` per i profili a sezione rettangolare/scatolare (telaio), a un
valore ricorrente nel disegno (drenaggio soglia), o verificata con un controllo geometrico automatico sul
tracciato DXF reale per i profili a "L" dove il centro della bounding box cade fuori dal materiale (squadretta/
ventilazione anta U10140 — vedi addendum 15/09/2026 sotto); faccia macchina **F1 per convenzione mai validata**,
codici utensile segnaposto — tutte le lavorazioni portano `[DA TARARE]` in coda alla descrizione): sono da tarare
dal pannello "Tarature lavorazioni" alla prima produzione reale, esattamente come le lavorazioni porte D67/D77
(sez. 10).

**Cosa NON è coperto** (pagine lette e trascritte — vedi note di sessione — ma non implementabili o fuori scopo):
- **Montaggio montante centrale OX/OXO** (pag. 9.24-9.28, 9.34-9.36): la foratura è definita dalla dima fisica
  T10082 (posizioni 1-4), **nessuna quota mm a disegno** — il manuale stesso dice di allineare la dima a L/2 o
  L1 e forare, non dà coordinate. Non implementabile senza il disegno della dima.
- **Foratura montante ↔ soglia ribassata** (pag. 9.03): assemblaggio specifico U10020+U10400/U10402/U10403/U10401
  (quote presenti: Ø5/Ø10, 31.3/77.4/31.3 ecc.) — non ancora implementato, da aggiungere in un secondo tempo.
- **Ferramenta maniglia/meccanismo alzante e serratura scorrevole** (pag. 9.42 L&S, 9.45 R): quote presenti
  (Ø10/Ø12/Ø20, offset 48.8, 40+40 ecc.) ma manca la **taratura dell'altezza maniglia (AM)** per S140 — a
  differenza di Maico C75S (tabella `cremoneseMaico`) o porte (AM=1050 da manuale), qui non c'è un riferimento
  con cui calcolare la posizione lungo l'anta.
- **Paracolpo + colonnina K1459** (pag. 9.49): K1459 non è un pezzo tagliato da nessuna delle 36 tipologie del
  programma (nessuna voce in `DATI.profili_ana` lo referenzia da `t.profili`) — irrilevante finché non si
  aggiunge una tipologia che lo usa.
- **Punzonature cover** (N10900/N10901/N10903/N10904/N10906/N10909, pag. 9.23/9.29-9.31/9.38-9.39/9.43-9.44/
  9.46-9.47, tranciante T00061): i profili cover sono registrati come **accessori** a quantità fissa
  (`data/catalogo_S140/catalogo_S140.json` → `accessori`, es. V31208/V31209/V31211/V31212, barra 6.8 m), non
  come pezzi tagliati in `t.profili` — il motore genera CUT/MACHINING solo per i pezzi di `t.profili`, quindi
  queste lavorazioni sono fuori dalla pipeline attuale finché i cover non diventano pezzi tagliati a sé.
- **Tutta la sez. 10 "Assemblaggio"** (10.01-10.36: viti, sigillante, spugne, colla, ordine di montaggio) sono
  istruzioni di montaggio a banco, non lavorazioni macchina: non generano `MACHINING` nel job per definizione,
  non solo per scelta di scopo.

**Estrazione del manuale**: fatta pagina per pagina con lo strumento di lettura immagini (il PDF è protetto,
`pdftoppm`/poppler-utils per il rendering), in parte in parallelo su 3 agenti per le pagine 31-82 (le pagine
1-30 lette direttamente in sessione). Dettaglio pagina-per-pagina (quote, tabelle viti/tappi, note di
incertezza) conservato nella cronologia della sessione; le quote effettivamente confluite nel codice sono solo
quelle sopra elencate, tutte con riferimento alla pagina del manuale nella descrizione della lavorazione.

**Collaudo fatto**: `tests/s140_test.js` (8 righe, tutte le sigle) genera 656 `MACHINING` senza errori;
`tests/regress.js` (C75S/C82S) resta IDENTICO; `tests/job_test.js` e `tests/composta_test.js` invariati.
Nessun collaudo "a video" FSTLine (nessun job reale contro cui confrontare, per definizione — vedi sopra).

**Metodo FP Pro / FPCAM per le quote di una lavorazione** (dedotto da due video caricati dall'utente il
15/09/2026, "Creazione nuovo profilo da modello FPPRO" e "FP CAM - Creazione di una lavorazione per EasyMac",
analizzati fotogramma per fotogramma con `ffmpeg` — nessuna trascrizione audio disponibile): **le quote di una
lavorazione in FP Pro non sono mai numeri assoluti da un angolo del profilo**. Il flusso è: (1) sul profilo
importato da DXF si crea prima una o più **"Guide"** (assi di riferimento con nome, es. `#1:GuidaX`,
posizionate cliccando sulla sezione o lasciate "non posizionate" con un nome libero tipo `asse_centrale`); (2)
ogni lavorazione si quota **relativamente** a quella guida e a elementi nominati del profilo stesso (nel video,
l'esempio quota l'asola a **H = -15.6 mm dall'"Aletta Esterna Lato Caldo"**, un'alettatura specifica del
profilo, non un bordo generico); (3) tool, verso di percorrenza (le stesse frecce rosso/blu di "scegli verso"),
W/H/X e poi Z (profondità, "Vuoto"/"Fine"/"Affondamento") si inseriscono in passaggi separati; (4) la
lavorazione finita si salva come **file `.LDT` per articolo profilo** nella libreria macchina
(`CAM\LDT\n65\<codice_articolo><variante>.ldt`, es. `56000A00.ldt`), riusabile da lì in poi. Da notare: nell'albero
lavorazioni FPCAM etichetta la voce come `#1: 90°-F6` — quell'**"F6" è il codice UTENSILE**, non la faccia
macchina (la nostra `FACE` nel job XML è una convenzione a livello di schema del file macchina, validata sui
job reali C75S — dominio diverso, nessun conflitto, ma da non confondere).
**Implicazione per S140**: questo conferma che le quote Y/faccia lasciate `[DA TARARE]` in `s140_lav_logic.js`
non sono ricavabili con certezza dal solo manuale AluK — la serie non è mai stata programmata in FPCAM (nessuna
Guida è mai stata creata sui profili S140), quindi manca esattamente il passaggio (1)-(2) sopra. Servirà o un
job di produzione reale (come per C75S) oppure che un tecnico CAM prepari le Guide sui profili S140 in FPCAM e
fornisca l'export risultante.

**Sospesi S140** (in ordine di valore): 1) tarare Y/faccia/utensile appena si dispone di un primo job di
produzione reale, o delle Guide FPCAM sui profili S140 (vedi nota di metodo sopra); 2) foratura montante↔soglia
ribassata (9.03); 3) taratura altezza maniglia (AM) per implementare 9.42/9.45; 4) valutare se rendere i cover
(V31208 ecc.) pezzi tagliati per coprire le loro punzonature; 5) montaggio montante OX/OXO: richiede il disegno
fisico della dima T10082 (non nel PDF ricevuto).

### Addendum 15/09/2026 — bug "lavorazione nel vuoto" (squadretta/ventilazione anta U10140) e audit geometrico

**Segnalazione utente**: nello schema-pezzo di un traverso anta U10140 (S140_LS_XX), il marker della squadretta
anta Ø5 (9.41, Y=31) appariva visibilmente fuori dal tracciato del profilo ("questa lavorazione è nel vuoto").

**Causa**: `Y = Math.round(w/2*10)/10` con `w = DATI.profili_ana['U10140'].w` (62, la larghezza della bounding
box) era un segnaposto puramente inventato (nessuna base nel manuale né nella geometria) — il manuale (pag. 9.41)
non quota affatto una Y per questa lavorazione: l'operazione si posiziona inserendo la dima T10067/il punzone
T00061 nel profilo "fino alla piastra d'arresto", cioè è definita dall'attrezzo fisico, non da un disegno
quotato. Per un profilo a sezione rettangolare il centro-bbox è comunque una stima plausibile; per U10140, a
sezione a **"L"** (`forma:'L'`), il centro della bounding box (31, 82) non è materiale — da cui il "vuoto".

**Verifica sistematica**: dato che lo stesso pattern `w/2` (e, per D67/D77, `dep - offset`) è usato altrove nel
programma, e l'utente ha giustamente chiesto se il problema fosse più esteso, è stato scritto un controllo
geometrico automatico (`tools/audit_geom_lav.py` + `tests/audit_lav_extract.js`): estrae **tutte** le
combinazioni uniche (profilo, faccia, Y) generate dal programma su ogni tipologia S140/D67/D77 del listino, e
per ciascuna verifica se il punto che lo schema-pezzo disegna (`sezioneFacciaSvg` in `app_logic.js`, stesse
formule replicate in Python) cade entro 2 mm dal tracciato DXF reale del profilo (`data/dxf_sez_s140.json` /
`dxf_sez_porte.json`, parsing SVG path con archi approssimati e distanza punto-segmento).

**Esito (85 combinazioni uniche testate)**: prima della correzione, 2 casi S140 "nel vuoto" — squadretta/
ventilazione anta U10140 (Y=31, ~27 mm dal tracciato più vicino: il bug segnalato) e drenaggio soglia U10403
(Y=8, condiviso per errore con gli altri profili soglia ma non valido per questo specifico profilo, ~4 mm fuori)
— **corretti** rispettivamente a Y=59 e Y=23 (punto medio del tratto di parete reale più vicino al vecchio
valore). Tutte le altre combinazioni S140 (fissaggio telaio, squadretta telaio, restante drenaggio soglia,
ventilazione) erano già su materiale reale (il centro-bbox funziona per i profili telaio, a sezione più
scatolare) — nessun'altra modifica necessaria lato S140.

**D67/D77: stesso audit ha trovato circa 40 combinazioni su 85 "nel vuoto"** (fissaggio telaio muro/battuta,
cerniere 2 ali telaio/anta, serratura corpo/incontri, catenaccio — su U51200/U51201/U51320/U51340/U51300,
U52200/U52201/U52320/U52340/U52300). **Non corrette in questa sessione**: a differenza di S140, per D67/D77
questo programma non ha mai avuto il vero "manuale di lavorazioni e assemblaggio" AluK (solo il `Catalogo
Tecnico D67-D77 v4C`, un catalogo prodotti/pesi senza sezione lavorazioni — verificato via `pdftotext`, nessuna
occorrenza di "10.01"/"Fissaggio telaio"/ecc.); le quote Y in `porte_logic.js`/`tools/porte_ferr.py` sono
"CONVENZIONI ricavate per analogia con C75S ... mai validate" fin dall'origine (vedi nota in testa a
`porte_ferr.py`). Inoltre l'audit mostra che per questi profili la faccia F4 tocca materiale reale solo in una
stretta fascia (~6 mm) vicino a un angolo: uno snap geometrico "al punto valido più vicino", come fatto per
S140, avrebbe fatto collassare lì fissaggio/cerniera/serratura — operazioni diverse, quote diverse nel manuale —
sullo stesso punto, dando un falso senso di correttezza peggiore del difetto attuale. **Serve il manuale
lavorazioni D67/D77 vero e proprio** (equivalente al PDF S140 v3A) per rifare questo modulo con lo stesso
rigore; nel frattempo lo stato resta quello dichiarato (`DA TARARE`), ora con un audit riproducibile per
misurare l'entità del problema invece di scoprirlo per segnalazioni sparse a video.

**Collaudo**: `tools/audit_geom_lav.py` dopo la correzione riporta 0 casi S140 "nel vuoto" (43/85 OK totali,
40 D67/D77 ancora da rivedere, 2 `NO_DXF` per K1577 — profilo senza sezione disegnata); `tests/regress.js`,
`tests/s140_test.js`, `tests/job_test.js`, `tests/composta_test.js` tutti invariati/passano.
