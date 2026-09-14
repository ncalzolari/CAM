# Listini a griglia — altre serie (AluK D67/D77 porte, S140)

`python3 build_listini_serie.py` legge le distinte delle tipologie dal programma commesse
(`../commesse-lmt65/src/dati_app.json`, `dati_porte.json`, `dati_cor80.json`), i prezzi AluK da
`../listini-db/listini.sqlite` (profili: serie 312 D67 / 315 D77 cat. B con addebito, sconto 38%;
accessori sconto 20%), il kit Maico in vista dalle regole WinPlus (`../listini-c75s/genera_listini.py`) e la
ferramenta porte dai blocchi FP D67 (`fp_blk_D67.json`, voci non opzionali, soglia automatica per fascia di
larghezza anta; per D77 è riusato il kit D67). Porte: gruppi "Porta 1/2 ante — apertura interna/esterna" con menù soglia; standard = soglia automatica
senza zoccolo (nodo U51320 interna, U51340 esterna con 732040÷732046 + K1486 + 809944), le altre in variante.
Le esterne con soglia automatica non hanno distinta a catalogo: `deriva_est_automatica()` le ricava dalle 8.18/8.19
(soglia K1769/K2069) applicando le differenze delle 8.07/8.08 (anta H−55, fermavetro H−247, K1486, 809944,
soglia automatica per larghezza); kit ferramenta dal blocco FP 360-02 (1 anta) e 350-21 (2 ante, riusato).
Produce `dati_listini_serie.json`, `Listini_Serie.html`
(autonomo) e `Listini_Serie_web.html` (Artifact).

Stesso modello di costo dei listini C75S: profili a peso × €/kg scontato + accessori e guarnizioni scontati,
sfrido, ferramenta per misura, manodopera; listino = costo × (1 + ricarico). Sezione riservata con marginalità.

## Dati da completare (file modificabili, oppure celle rosse nella pagina)
- `pesi_profili.json`: kg/m dei profili porte (U51200, U51320, U20630, N48823, K1488… e D77). Nessuna fonte
  a disposizione: catalogo AluK o archivio FP Pro (densità kg/ml).
- `prezzi_cortizo.json`: €/kg profili Cortizo, sconti e prezzi unitari di accessori/guarnizioni S140 (ex COR80, spostata in un altro programma)
  (listino Cortizo non caricato).
- Porte: cerniere AluK (codice e prezzo) e serrature da confermare (voci del kit FP marcate).
- S140 (ex COR80, spostata in un altro programma) a scomparsa: cerniere Multi Power da inserire.
I valori inseriti nella pagina restano nel browser; per renderli definitivi metterli nei file e rigenerare.

## Regole porte D67/D77 (aggiornamento)
- **Verniciatura**: all'apertura del programma la verniciatura torna sempre all'aggregazione **20 — CARTELLA CON ADDEBITO CAT B** (+1,75 €/kg, base RAL 7016 opaco); la scelta fatta nella sessione non viene ripristinata al riavvio.
- **Cerniere porte**: sempre cerniere a stelo AluK **H51300-B1** (nero R.9005, 48,66 € listino, sconto accessori applicato). Quantità per anta in funzione dell'altezza anta (regola catalogo AluK tab. 10.51 estesa alle cerniere a stelo): ≤1300 → 2, ≤2400 → 3, oltre → 4. L'altezza anta è presa dal montante battente della tipologia (H−55 con soglia automatica, H−79 con soglia K).
- **Serratura porte**: pacchetto standard al posto della serratura del blocco FP: 1 serratura Performa 3 catenacci + scrocco E35 I85 nera (68,67 €), 1 incontro centrale F29x229 nero (10,03 €), 2 incontri deviatori F29x186 neri (9,96 € cad.), 1 cilindro sagomato 123P 22/10/22 alluminio con pomolo nylon (14,05 €). Kit maniglia passante 201-10510 colore argento (26,50 €). Prezzi netti di acquisto, senza sconto ulteriore; codici interni (SERR-PERFORMA, INC-PERFORMA-229/186, CIL-123P-22-10-22) modificabili nella tabella ferramenta. Stesso pacchetto per 1 e 2 ante.
- **Soglia automatica**: antispifero sottoporta ASACA 25x20 del fornitore CCE (prezzi netti 20,00-44,40 € per lunghezze nominali 330-1530 a passo 100) al posto delle AluK 732040-732046 (netto 49-62 €). Lunghezza nominale = la prima ≥ larghezza anta (L−94 a 1 anta, L/2−37,5 a 2 ante). Compatibilità verificata dal cliente.
- **Porte 2 ante con soglia automatica**: il blocco FP 350-21 non elenca le soglie automatiche; il kit aggiunge 2 soglie ASACA (una per anta) e 2 spazzolini K1488 dal blocco a 1 anta.
- **K1486 e K1777** (portaspazzolino, asta catenacci) nelle distinte a 2 ante sono elencati come accessori senza prezzo: vengono prezzati a peso come profili non isolati (K1486 0,41 kg/m, K1777 0,46 kg/m). Lunghezze: K1486 = larghezza anta − 54 (L−148 a 1 anta, L/2−91,5 a 2 ante); K1777 = metà altezza anta per asta (H/2−27,5, 2 aste) — ipotesi da verificare.
- **Profili K…**: sempre classe non isolata (€/kg serie 108 grezzo, 13,07). Pesi completi per D67/D77; manca solo COR-7088 (S140 (ex COR80, spostata in un altro programma)).
- **Ore manodopera**: valore fisso per tipologia (6 h porta 1 anta, 10 h porta 2 ante, uguali per apertura interna ed esterna), modificabile nella scheda e memorizzato; non è calcolato da lavorazioni o misure.

## Serie S140 (alzante scorrevole / scorrevole in linea) — 14.09.2026
- Catalogo tecnico AluK S140 v5A completo in `listini-db/catalogo_S140/` (sez. 1-5, 5-7, 8 distinte in due parti) + manuale lavorazioni e assemblaggio v3A. Trascrizione in `commesse-lmt65/data/catalogo_S140/catalogo_S140.json`: 39 profili con pesi, 78 accessori, 36 guarnizioni (con lunghezza barra per gli articoli a pezzo), tavola di vetrazione 7.04/7.05.
- Tipologie in `tipologie_s140.json`, generate da `genera_tipologie_s140.py` dalle **18 distinte di taglio ufficiali** (soglia standard): alzante XX (8.02), XX slim U10120 (8.04), 3 ante (8.06), 4 ante (8.08), 4 ante slim (8.10), fisso apribile OX anta esterna/interna (8.12/8.16) e slim (8.14/8.18), 3 ante fissa centrale (8.20), OXO (8.22), 4 ante 2 fisse laterali (8.24) e slim (8.26), 6 ante (8.28); in linea XX (8.52), XX slim (8.54), una fissa (8.56), una fissa slim (8.58). Vetro 28: fermavetro N10823, guarnizione interna 809122, esterna V03000. Voci opzionali escluse; tasselli 712322 e maniglione FKS 1033 con conchiglia esterna 213-00737 F1 argento (31,24 € netto FKS 2025, `listini-db/Listino_2025_FKS_1033_manigliette_defender.xlsx`) aggiunti da noi, 1 per anta mobile.
- Ante uguali: 3 ante L1 = L/3+24, L2 = L/3−48 e 4 ante L1 = L/4+20, L2 = L/4−20 (regole del catalogo); per le altre tipologie a più specchiature divisione in parti uguali (L/3, L/4, L/6).
- Ore manodopera: 4,5 h per specchiatura (2 ante 9 h, 3 ante 13,5 h, 4 ante 18 h, 6 ante 27 h). Soglia ribassata: variante di ogni tipologia (36 tipologie in tutto) generata dalla seconda colonna delle distinte con le regole di `ribassata()` in genera_tipologie_s140.py (soglia U10400/U10401/U10402+U10403, montanti telaio 90-45, pezzi verticali più lunghi, cover V31209/V31211, tappi V55098/V58038/V58041/V53077, kit V59141/V59142).
- Prezzi: profili TT serie 335 (15,92 €/kg grezzo), non isolati serie 114 (13,07), verniciatura agg. 20; accessori e guarnizioni dal listino AluK con sconto accessori; codici a listino solo con suffisso -B risolti automaticamente; V50051 a 0,2132 €/pz (listino per confezione da 100). Kit ferramenta per anta mobile: L&S kit H10600 + meccanismo H10402÷H10405 per altezza anta + asta H10902/H10904 per larghezza anta; S140R carrelli H10203 ×2, serratura 3 punti H10420, anti falsa manovra H10913.
- La COR80 è stata tolta da questo programma (andrà in un programma dedicato); i dati restano in `commesse-lmt65/src/dati_cor80.json`.
