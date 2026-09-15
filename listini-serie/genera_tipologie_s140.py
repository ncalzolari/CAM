#!/usr/bin/env python3
"""Tipologie S140 dalle distinte di taglio ufficiali AluK S140 v5A sez. 8 (02.01.2026), colonna soglia standard.
Genera tipologie_s140.json. Vetro 28 mm: fermavetro N10823, guarnizione interna 809122, esterna V03000 (tav. 7.04/7.05).
Voci opzionali del catalogo escluse; tasselli vetro 712322 (4 per specchiatura) e maniglione FKS 1033 213-00737 (netto FKS 2025) aggiunti da noi.
Ore: 4,5 h per specchiatura (14/09/2026). Tipologie a più ante con ante uguali: L1/L2 dalle regole del catalogo dove indicate
(3 ante L1=L/3+24, L2=L/3-48; 4 ante L1=L/4+20, L2=L/4-20), altrimenti divisione in parti uguali."""
import json, os
FONTE = 'Distinta di taglio ufficiale AluK S140 v5A sez. 8, soglia standard. Vetro 28: fermavetro N10823 + 809122 + V03000.'
ORE_SPECCHIATURA = 4.5
def P(art, desc, pz, mis, ang='90-90'): return {'art': art, 'desc': desc, 'pz': pz, 'mis': mis, 'ang': ang}
def A(art, desc, pz): return {'art': art, 'desc': desc, 'pz': pz}
def G(art, desc, mis): return {'art': art, 'desc': desc, 'mis': mis}
def V(pz, l, h): return {'pz': pz, 'l': l, 'h': h}
MANIGLIA = ('213-00737', 'Maniglione alzante scorrevole FKS 1033 con conchiglia esterna, F1 argento, quadro e viti incl. (s.p. 75-80)', 31.24)   # listino netto FKS 2025 (14/09/2026)
def kit(rows):
    out = []
    for c, d, q, fl, fh in rows:
        if not q: continue
        r = {'cod': c, 'desc': d, 'q': q, 'fascia': fl, 'fascia_h': fh}
        if c == 'MANIGLIA-S140': r.update(cod=MANIGLIA[0], desc=MANIGLIA[1], pr=MANIGLIA[2], fonte='netto fornitore FKS 2025')
        out.append(r)
    return out
MECC = [('H10402', 'Meccanismo alzante scorrevole anta H 1370-1970', None, [1370, 1970]), ('H10403', 'Meccanismo alzante scorrevole anta H 1971-2270', None, [1971, 2270]),
        ('H10404', 'Meccanismo alzante scorrevole anta H 2271-2570', None, [2271, 2570]), ('H10405', 'Meccanismo alzante scorrevole anta H 2571-2870', None, [2571, 2870])]
ASTE = [('H10902', 'Asta di collegamento LB anta 730-2000', [730, 2000], None), ('H10904', 'Asta di collegamento LB anta 2001-3240', [2001, 3240], None)]
def KIT_LS(n, n_centr=0):
    return kit([('H10600', 'Kit per alzante scorrevole (max 270 kg)', n - n_centr, None, None), ('H10601', 'Kit per alzante scorrevole anta centrale (max 270 kg)', n_centr, None, None)]
               + [(c, d, n, fl, fh) for c, d, fl, fh in MECC] + [(c, d, n, fl, fh) for c, d, fl, fh in ASTE]
               + [('MANIGLIA-S140', 'Maniglia per alzante scorrevole (catalogo maniglie AluK) — DA INSERIRE', n, None, None)])
def KIT_R(n):
    return kit([('H10203', 'Carrelli per scorrevole (max 240 kg), 2 pz per anta', 2 * n, None, None), ('H10420', 'Serratura per scorrevole 3 punti', n, None, None),
                ('H10913', 'Dispositivo anti falsa manovra', n, None, None), ('MANIGLIA-S140', 'Maniglia per scorrevole (catalogo maniglie AluK) — DA INSERIRE', n, None, None)])
def telaio(art):
    return [P(art, 'Traverso telaio', 2, 'L', '45-45'), P(art, 'Montante telaio', 2, 'H', '45-45')]
def telaio3(): return [P('U10060', 'Traverso telaio esterno', 2, 'L', '45-45'), P('U10061', 'Traverso telaio interno', 2, 'L', '45-45'), P('U10060', 'Montante telaio esterno', 2, 'H', '45-45'), P('U10061', 'Montante telaio interno', 2, 'H', '45-45')]
def fv(n_or, mis_or, n_ve, mis_ve, cosa='anta'): return [P('N10823', f'Fermavetro orizzontale {cosa} (vetro 28)', n_or, mis_or), P('N10823', f'Fermavetro verticale {cosa} (vetro 28)', n_ve, mis_ve)]
def squadr(tel_int, all_, anta, tel_cianf, viti=16, spine=16):
    out = []
    if tel_int: out.append(A('V43000', 'Squadretta interna telaio', tel_int))
    out += [A('V46028', 'Squadretta anta allineamento', all_), A('710036', 'Squadretta anta', anta), A('710400', 'Viti squadrette', viti), A('710401', 'Spine squadrette', spine), A('710407', 'Squadretta telaio', tel_cianf)]
    return out
def tass(n): return A('712322', 'Tassello vetro 26x4 (in base alla misura)', n)
T = []
def tip(id_, cod, nome, rif, forma, mobili, spec, anta_l, anta_h, profili, acc, gua, vetro, kitr, note=''):
    T.append({'id': id_, 'serie': 'S140', 'cod': cod, 'nome': nome, 'rif': rif, 'forma': forma, 'ante_mobili': mobili, 'specchiature': spec, 'ore': ORE_SPECCHIATURA * spec,
              'anta_l': anta_l, 'anta_h': anta_h, 'avviso': FONTE + (' ' + note if note else ''), 'profili': profili, 'accessori': acc, 'guarnizioni': gua, 'vetro': vetro, 'kit': kitr})

# ---------- ALZANTE SCORREVOLE (L&S) ----------
# 8.02-8.03 due ante mobili XX
G_XX = [G('800936', 'Spazzolino L6,9 H9', 'L+2H'), G('809122', 'Guarnizione interna vetro 6.5-8 (vetro 28)', '2L+4H'), G('V02015', 'Guarnizione labirinto', '2H'), G('V03000', 'Guarnizione esterna vetro', '2L+4H'), G('V03018', 'Guarnizione finitura labirinto', '2H'),
        G('V03030', 'Guarnizione anta', '4L+4H'), G('V05031', 'Finitura telaio senza pinne', 'L+2H'), G('V05032', 'Finitura telaio con pinne', 'L'), G('V09050', 'Isolante sotto vetro anta', '2L+4H'), G('V20008', 'Listello LDPE traverso superiore anta', 'L'),
        G('V23000', 'Listello isolante sagomato adesivo telaio', '2H'), G('V23001', 'Listello isolante 35x9', '2H'), G('V23002', 'Listello isolante 50x39', '2H')]
PVC_XX = [G('800167', 'Cover finitura labirinto (2 x H-106.5)', '2H-213'), G('V31013', 'Labirinto (2 x H-96.5)', '2H-193'), G('V31208', 'Cover telaio PVC (2 x L/2-81.5, 2 x H-45, L-45)', '2L+2H-298'), G('V31210', 'Cover anta PVC (2 x L/2-77, 2 x H-141.5)', 'L+2H-437')]
ACC_XX = squadr(0, 16, 16, 8) + [A('V50051', 'Compensazione cover-labirinto', 6), A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 1), A('V53054', 'Kit tappi labirinto V31013', 1), A('V55168', 'Tappi chiusura tubolare U10022', 3),
          A('V58031', 'Kit base 2 ante per alzante scorrevole', 1), A('V58037', 'Tappo tenuta centrale inferiore telaio', 1), A('V58045', 'Kit spessore blocco tappo anta', 2), A('V59140', 'Kit centraggio carrelli', 8), A('V59161', 'Kit spessore per tappo V58037', 2), A('V78004', 'Kit rinforzo anta', 2), A('V90088', 'Tappo paracolpo', 1), tass(8)]
PROF_XX = telaio('U10022') + [P('U10140', 'Traverso anta', 4, 'L/2-7', '45-45'), P('U10140', 'Montante anta', 4, 'H-86.5', '45-45'), P('N10909', 'Profilo scatto labirinto', 2, 'H-90.5'), P('N10901', 'Profilo di finitura laterale', 2, 'H-58'), P('N10902', 'Gocciolatoio', 1, 'L-55'), P('N10630', 'Binario', 2, 'L-104')] + fv(4, 'L/2-135', 4, 'H-250.5')
tip('S140_LS_XX', 'SXX140', 'Alzante scorrevole 2 ante mobili (XX)', 'S140 8.02-8.03', 'S2', 2, 2, 'L/2-7', 'H-86.5', PROF_XX, ACC_XX, G_XX + PVC_XX, [V(2, 'L/2-143', 'H-222.5')], KIT_LS(2))
# 8.04-8.05 due ante mobili XX con montante slim U10120
G_XXS = [g for g in G_XX if g['art'] not in ('V03018', 'V23001', 'V23002')] + [G('V05029', 'Guarnizione finitura labirinto slim', '2H'), G('V20009', 'Listello LDPE 54x4', '2H'), G('V23003', 'Listello isolante 24x9', '2H')]
PVC_XXS = [G('V31015', 'Labirinto slim (2 x H-96.5)', '2H-193'), G('V31208', 'Cover telaio PVC (2 x L/2-81.5, 2 x H-45, L-45)', '2L+2H-298'), G('V31210', 'Cover anta PVC (2 x L/2-99, 2 x H-141.5)', 'L+2H-481')]
ACC_XXS = squadr(0, 8, 8, 8) + [A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 1), A('V53055', 'Kit tappi labirinto slim V31015', 1), A('V55168', 'Tappi chiusura tubolare U10022', 3), A('V58031', 'Kit base 2 ante per alzante scorrevole', 1), A('V58037', 'Tappo tenuta centrale inferiore telaio', 1),
           A('V59140', 'Kit centraggio carrelli', 8), A('V59162', 'Kit spessore 36 mm per tappo V58037 (U10120)', 2), A('V78004', 'Kit rinforzo anta', 2), A('V90088', 'Tappo paracolpo', 1), tass(8)]
PROF_XXS = telaio('U10022') + [P('U10120', 'Montante centrale anta slim', 2, 'H-205.5'), P('U10140', 'Traverso anta', 4, 'L/2-29.5', '45-90'), P('U10140', 'Montante anta', 4, 'H-86.5', '45-45'), P('N10909', 'Profilo scatto labirinto', 2, 'H-90.5'), P('N10901', 'Profilo di finitura laterale', 2, 'H-58'), P('N10902', 'Gocciolatoio', 1, 'L-55'), P('N10630', 'Binario', 2, 'L-104')] + fv(4, 'L/2-112.5', 4, 'H-250.5')
tip('S140_LS_XX_SLIM', 'SXS140', 'Alzante scorrevole 2 ante mobili (XX) con montante slim U10120', 'S140 8.04-8.05', 'S2', 2, 2, 'L/2-29.5', 'H-86.5', PROF_XXS, ACC_XXS, G_XXS + PVC_XXS, [V(2, 'L/2-120.5', 'H-222.5')], KIT_LS(2))
# 8.06-8.07 tre ante mobili (telaio 3 vie): L1 = L/3+24, L2 = L/3-48
PROF_3A = telaio3() + [P('U10140', 'Traverso anta laterale (L1+1)', 4, 'L/3+25', '45-45'), P('U10140', 'Traverso anta centrale (L2+75)', 2, 'L/3+27', '45-45'), P('U10140', 'Montante anta', 6, 'H-71', '45-45'), P('N10909', 'Profilo scatto labirinto', 4, 'H-75'), P('N10901', 'Profilo di finitura laterale', 2, 'H-43'), P('N10902', 'Gocciolatoio', 1, 'L-40'), P('N10903', 'Profilo di finitura laterale tre ante', 2, 'H-43'), P('N10630', 'Binario', 3, 'L-89'),
                       P('N10823', 'Fermavetro orizzontale anta laterale (vetro 28)', 4, 'L/3-103'), P('N10823', 'Fermavetro orizzontale anta centrale (vetro 28)', 2, 'L/3-101'), P('N10823', 'Fermavetro verticale (vetro 28)', 6, 'H-235')]
PVC_3A = [G('800167', 'Cover finitura labirinto (4 x H-91)', '4H-364'), G('V31013', 'Labirinto (4 x H-81)', '4H-324'), G('V31208', 'Cover telaio PVC (inferiori, montanti, superiori)', '4L+4H-476'), G('V31210', 'Cover anta PVC (inferiori e montanti)', 'L+3H-587')]
ACC_3A = squadr(0, 24, 24, 8) + [A('V50051', 'Compensazione cover-labirinto', 12), A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 1), A('V53054', 'Kit tappi labirinto V31013', 2), A('V55097', 'Tappi chiusura tubolare U10060/U10061', 3), A('V58036', 'Kit base 3 ante per alzante scorrevole', 1),
          A('V58037', 'Tappo tenuta centrale inferiore telaio', 2), A('V58045', 'Kit spessore blocco tappo anta', 3), A('V59140', 'Kit centraggio carrelli', 12), A('V59161', 'Kit spessore per tappo V58037', 6), A('V78004', 'Kit rinforzo anta', 2), A('V78005', 'Kit rinforzo terza anta', 2), A('V90088', 'Tappo paracolpo', 2), tass(12)]
G_3A = [G('800936', 'Spazzolino L6,9 H9', 'L+2H'), G('809122', 'Guarnizione interna vetro 6.5-8 (vetro 28)', '2L+6H'), G('V02015', 'Guarnizione labirinto', '4H'), G('V03000', 'Guarnizione esterna vetro', '2L+6H'), G('V03018', 'Guarnizione finitura labirinto', '4H'), G('V03030', 'Guarnizione anta', '4L+4H'), G('V05031', 'Finitura telaio senza pinne', '3L+2H'), G('V05032', 'Finitura telaio con pinne', 'L'),
        G('V09050', 'Isolante sotto vetro anta', '2L+6H'), G('V20008', 'Listello LDPE traverso superiore anta', 'L'), G('V23000', 'Listello isolante sagomato adesivo telaio', '4H'), G('V23001', 'Listello isolante 35x9', '3H'), G('V23002', 'Listello isolante 50x39', '3H')]
tip('S140_LS_3A', 'S3A140', 'Alzante scorrevole 3 ante mobili (telaio 3 binari U10060/U10061)', 'S140 8.06-8.07', 'S3', 3, 3, 'L/3+25', 'H-71', PROF_3A, ACC_3A, G_3A + PVC_3A, [V(2, 'L/3-111', 'H-207'), V(1, 'L/3-109', 'H-207')], KIT_LS(3, 1), 'Ante uguali: L1 = L/3+24, L2 = L/3-48 (catalogo).')
# 8.08-8.09 quattro ante mobili: L1 = L/4+20, L2 = L/4-20
PROF_4A = telaio('U10022') + [P('U10140', 'Traverso anta laterale (L1-7)', 4, 'L/4+13', '45-45'), P('U10140', 'Traverso anta centrale (L2+34.5)', 4, 'L/4+14.5', '45-45'), P('U10140', 'Montante anta', 8, 'H-86.5', '45-45'), P('U10601', 'Riporto ante in linea', 1, 'H-134.5'), P('N10909', 'Profilo scatto labirinto', 4, 'H-90.5'), P('N10901', 'Profilo di finitura laterale', 2, 'H-58'), P('N10902', 'Gocciolatoio', 1, 'L-55'), P('N10630', 'Binario', 2, 'L-104'),
                              P('N10823', 'Fermavetro orizzontale anta laterale (vetro 28)', 4, 'L/4-115'), P('N10823', 'Fermavetro orizzontale anta centrale (vetro 28)', 4, 'L/4-113.5'), P('N10823', 'Fermavetro verticale (vetro 28)', 8, 'H-250.5')]
PVC_4A = [G('800167', 'Cover finitura labirinto (4 x H-106.5)', '4H-426'), G('V31013', 'Labirinto (4 x H-96.5)', '4H-386'), G('V31208', 'Cover telaio PVC (inferiori, montanti, superiore)', '2L+2H-416'), G('V31210', 'Cover anta PVC (inferiori e montanti)', 'L+4H-792')]
ACC_4A = squadr(0, 32, 32, 8) + [A('V50051', 'Compensazione cover-labirinto', 12), A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 1), A('V53054', 'Kit tappi labirinto V31013', 2), A('V55168', 'Tappi chiusura tubolare U10022', 4), A('V58031', 'Kit base 2 ante per alzante scorrevole', 2), A('V58037', 'Tappo tenuta centrale inferiore telaio', 2),
          A('V58042', 'Kit tappi ante in linea', 1), A('V58045', 'Kit spessore blocco tappo anta', 4), A('V59140', 'Kit centraggio carrelli', 16), A('V72121', 'Kit di fissaggio profilo U10601', 2), A('V59161', 'Kit spessore per tappo V58037', 4), A('V78004', 'Kit rinforzo anta', 4), A('V90088', 'Tappo paracolpo', 2), tass(16)]
G_4A = [G('800936', 'Spazzolino L6,9 H9', 'L+2H'), G('809122', 'Guarnizione interna vetro 6.5-8 (vetro 28)', '2L+8H'), G('V02015', 'Guarnizione labirinto', '4H'), G('V03000', 'Guarnizione esterna vetro', '2L+8H'), G('V03018', 'Guarnizione finitura labirinto', '4H'), G('V03030', 'Guarnizione anta', '4L+6H'), G('V05031', 'Finitura telaio senza pinne', 'L+2H'), G('V05032', 'Finitura telaio con pinne', 'L'),
        G('V09050', 'Isolante sotto vetro anta', '2L+8H'), G('V20008', 'Listello LDPE traverso superiore anta', 'L'), G('V23000', 'Listello isolante sagomato adesivo telaio', '2H'), G('V23001', 'Listello isolante 35x9', '4H'), G('V23002', 'Listello isolante 50x39', '4H')]
tip('S140_LS_4A', 'S4A140', 'Alzante scorrevole 4 ante mobili', 'S140 8.08-8.09', 'S4', 4, 4, 'L/4+13', 'H-86.5', PROF_4A, ACC_4A, G_4A + PVC_4A, [V(2, 'L/4-123', 'H-222.5'), V(2, 'L/4-121.5', 'H-222.5')], KIT_LS(4, 1), 'Ante uguali: L1 = L/4+20, L2 = L/4-20 (catalogo).')
# 8.10-8.11 quattro ante mobili con montante slim U10120
PROF_4AS = telaio('U10022') + [P('U10120', 'Montante centrale anta slim', 4, 'H-205.5'), P('U10140', 'Traverso anta laterale (L1-29.5)', 4, 'L/4-9.5', '45-90'), P('U10140', 'Traverso anta centrale (L2+12)', 4, 'L/4-8', '90-45'), P('U10140', 'Montante anta', 4, 'H-86.5', '45-45'), P('U10601', 'Riporto ante in linea', 1, 'H-134.5'), P('N10909', 'Profilo scatto labirinto', 4, 'H-90.5'), P('N10901', 'Profilo di finitura laterale', 2, 'H-58'), P('N10902', 'Gocciolatoio', 1, 'L-55'), P('N10630', 'Binario', 2, 'L-104'),
                               P('N10823', 'Fermavetro orizzontale anta laterale (vetro 28)', 4, 'L/4-92.5'), P('N10823', 'Fermavetro orizzontale anta centrale (vetro 28)', 4, 'L/4-91'), P('N10823', 'Fermavetro verticale (vetro 28)', 8, 'H-250.5')]
PVC_4AS = [G('V31015', 'Labirinto slim (4 x H-96.5)', '4H-386'), G('V31208', 'Cover telaio PVC (inferiori, montanti, superiore)', '2L+2H-416'), G('V31210', 'Cover anta PVC (inferiori e montanti)', 'L+4H-880')]
ACC_4AS = squadr(0, 16, 16, 8) + [A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 1), A('V53055', 'Kit tappi labirinto slim V31015', 2), A('V55168', 'Tappi chiusura tubolare U10022', 4), A('V58031', 'Kit base 2 ante per alzante scorrevole', 2), A('V58037', 'Tappo tenuta centrale inferiore telaio', 2), A('V58042', 'Kit tappi ante in linea', 1),
           A('V59140', 'Kit centraggio carrelli', 16), A('V59162', 'Kit spessore 36 mm per tappo V58037 (U10120)', 4), A('V72121', 'Kit di fissaggio profilo U10601', 2), A('V78004', 'Kit rinforzo anta', 4), A('V90088', 'Tappo paracolpo', 2), tass(16)]
G_4AS = [g for g in G_4A if g['art'] not in ('V03018', 'V23001', 'V23002')] + [G('V05029', 'Guarnizione finitura labirinto slim', '4H'), G('V20009', 'Listello LDPE 54x4', '4H'), G('V23003', 'Listello isolante 24x9', '4H')]
tip('S140_LS_4A_SLIM', 'S4S140', 'Alzante scorrevole 4 ante mobili con montante slim U10120', 'S140 8.10-8.11', 'S4', 4, 4, 'L/4-9.5', 'H-86.5', PROF_4AS, ACC_4AS, G_4AS + PVC_4AS, [V(2, 'L/4-100.5', 'H-222.5'), V(2, 'L/4-99', 'H-222.5')], KIT_LS(4, 1), 'Ante uguali: L1 = L/4+20, L2 = L/4-20.')
# 8.12-8.13 fisso apribile OX (anta esterna) — 8.16-8.17 anta interna: stessa distinta
PROF_OX = telaio('U10000') + [P('U10140', 'Traverso anta', 2, 'L/2+1', '45-45'), P('U10140', 'Montante anta', 2, 'H-71', '45-45'), P('U10600', 'Montante stipite centrale', 1, 'H-31'), P('N10909', 'Profilo scatto labirinto', 1, 'H-75'), P('N10901', 'Profilo di finitura laterale', 1, 'H-43'), P('N10902', 'Gocciolatoio', 1, 'L-40'), P('N10904', 'Cover telaio OX standard traverso', 2, 'L/2-95'), P('N10904', 'Cover telaio OX standard montante', 1, 'H-55'), P('N10906', 'Cover montante centrale OX', 1, 'H-55'), P('N10630', 'Binario', 1, 'L-89')] + fv(2, 'L/2-127', 2, 'H-235') + fv(2, 'L/2-54', 2, 'H-91', 'fisso')
PVC_OX = [G('800167', 'Cover finitura labirinto (2 x H-91)', '2H-182'), G('V31013', 'Labirinto (2 x H-81)', '2H-162'), G('V31210', 'Cover anta PVC (L/2-69 + H-126)', 'L/2+H-195'), G('V31212', 'Cover telaio OX PVC (2 x L/2-74, 2 x H-30, L-30)', '2L+2H-238')]
ACC_OX = squadr(4, 8, 8, 4) + [A('V50051', 'Compensazione cover-labirinto', 3), A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 1), A('V53054', 'Kit tappi labirinto V31013', 1), A('V55097', 'Tappi chiusura tubolare U10000', 3), A('V58039', 'Kit base OX per alzante scorrevole', 1), A('V58040', 'Tappo tenuta centrale inferiore telaio U10000', 1),
          A('V58045', 'Kit spessore blocco tappo anta', 1), A('V59140', 'Kit centraggio carrelli', 4), A('V59163', 'Kit spessore per tappo V58040', 2), A('V78004', 'Kit rinforzo anta', 1), A('V90088', 'Tappo paracolpo', 1), tass(8)]
G_OX = [G('800172', 'Guarnizione appoggio aggiuntivi', 'L+H'), G('800936', 'Spazzolino L6,9 H9', '2L+2H'), G('809122', 'Guarnizione interna vetro 6.5-8 (vetro 28)', '2L+4H'), G('V02015', 'Guarnizione labirinto', '2H'), G('V03000', 'Guarnizione esterna vetro', '2L+4H'), G('V03018', 'Guarnizione finitura labirinto', '2H'), G('V03030', 'Guarnizione anta', '2L+2H'), G('V05031', 'Finitura telaio senza pinne', 'L/2+H'), G('V05032', 'Finitura telaio con pinne', 'L/2'),
        G('V09050', 'Isolante sotto vetro anta', 'L+3H'), G('V20008', 'Listello LDPE traverso superiore anta', 'L/2'), G('V20010', 'Listello LDPE 40x16 (fisso)', 'L+H'), G('V23000', 'Listello isolante sagomato adesivo telaio', '2H'), G('V23001', 'Listello isolante 35x9', 'H'), G('V23002', 'Listello isolante 50x39', 'H'), G('V29002', 'Listello isolante montante centrale', 'H')]
VET_OX = [V(1, 'L/2-135', 'H-207'), V(1, 'L/2-63', 'H-65')]
tip('S140_LS_OX', 'SOX140', 'Alzante scorrevole fisso apribile (OX), anta esterna', 'S140 8.12-8.13', 'S1', 1, 2, 'L/2+1', 'H-71', PROF_OX, ACC_OX, G_OX + PVC_OX, VET_OX, KIT_LS(1))
tip('S140_LS_OX_INT', 'SOI140', 'Alzante scorrevole fisso apribile (OX), anta interna', 'S140 8.16-8.17', 'S1', 1, 2, 'L/2+1', 'H-71', PROF_OX, ACC_OX, G_OX + PVC_OX, VET_OX, KIT_LS(1), 'Stessa distinta della 8.12 (anta esterna).')
# 8.14-8.15 fisso apribile OX con montante slim U10120 (anta esterna) — 8.18-8.19 anta interna
PROF_OXS = telaio('U10000') + [P('U10120', 'Montante centrale fisso slim', 1, 'H-31'), P('U10120', 'Montante centrale anta slim', 1, 'H-190'), P('U10140', 'Traverso anta', 2, 'L/2-21.5', '45-90'), P('U10140', 'Montante anta', 1, 'H-71', '45-45'), P('N10909', 'Profilo scatto labirinto anta', 1, 'H-75'), P('N10909', 'Profilo scatto labirinto fisso', 1, 'H-55'), P('N10901', 'Profilo di finitura laterale', 1, 'H-43'), P('N10902', 'Gocciolatoio', 1, 'L-40'),
                               P('N10904', 'Cover telaio OX standard traverso', 2, 'L/2-72.5'), P('N10904', 'Cover telaio OX standard montante', 1, 'H-55'), P('N10630', 'Binario', 1, 'L-89')] + fv(2, 'L/2-104.5', 2, 'H-235') + fv(2, 'L/2-31.5', 2, 'H-91', 'fisso')
PVC_OXS = [G('V31015', 'Labirinto slim (2 x H-81)', '2H-162'), G('V31210', 'Cover anta PVC (L/2-91 + H-126)', 'L/2+H-217'), G('V31212', 'Cover telaio OX PVC (2 x L/2-74, 2 x H-30, L-30)', '2L+2H-238')]
ACC_OXS = squadr(4, 4, 4, 4) + [A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 1), A('V53055', 'Kit tappi labirinto slim V31015', 1), A('V55097', 'Tappi chiusura tubolare U10000', 3), A('V58039', 'Kit base OX per alzante scorrevole', 1), A('V58040', 'Tappo tenuta centrale inferiore telaio U10000', 1),
           A('V59140', 'Kit centraggio carrelli', 4), A('V59164', 'Kit spessore 36 mm per tappo V58040 (U10120)', 2), A('V78004', 'Kit rinforzo anta', 1), A('V90088', 'Tappo paracolpo', 1), tass(8)]
G_OXS = [g for g in G_OX if g['art'] not in ('V03018', 'V23001', 'V23002', 'V29002')] + [G('V05029', 'Guarnizione finitura labirinto slim', '2H'), G('V20009', 'Listello LDPE 54x4', '2H'), G('V23003', 'Listello isolante 24x9', '2H')]
VET_OXS = [V(1, 'L/2-112.5', 'H-207'), V(1, 'L/2-40.5', 'H-65')]
tip('S140_LS_OX_SLIM', 'SOS140', 'Alzante scorrevole fisso apribile (OX) con montante slim U10120, anta esterna', 'S140 8.14-8.15', 'S1', 1, 2, 'L/2-21.5', 'H-71', PROF_OXS, ACC_OXS, G_OXS + PVC_OXS, VET_OXS, KIT_LS(1))
tip('S140_LS_OX_SLIM_INT', 'SOT140', 'Alzante scorrevole fisso apribile (OX) con montante slim U10120, anta interna', 'S140 8.18-8.19', 'S1', 1, 2, 'L/2-21.5', 'H-71', PROF_OXS, ACC_OXS, G_OXS + PVC_OXS, VET_OXS, KIT_LS(1), 'Stessa distinta della 8.14 (anta esterna).')
# 8.20-8.21 tre ante, fissa interna centrale (XFX): L1 = L2 = L/3
PROF_3FC = telaio('U10000') + [P('U10140', 'Traverso anta (L1+1)', 4, 'L/3+1', '45-45'), P('U10140', 'Montante anta', 4, 'H-71', '45-45'), P('U10600', 'Montante stipite centrale', 2, 'H-31'), P('N10909', 'Profilo scatto labirinto', 2, 'H-75'), P('N10902', 'Gocciolatoio', 1, 'L-40'), P('N10904', 'Cover telaio OX standard traverso (L1-95)', 4, 'L/3-95'), P('N10904', 'Cover telaio OX standard montante', 2, 'H-55'), P('N10906', 'Cover montante centrale OX', 2, 'H-55'), P('N10630', 'Binario', 1, 'L-89'),
                               P('N10823', 'Fermavetro orizzontale anta (vetro 28)', 4, 'L/3-127'), P('N10823', 'Fermavetro verticale anta (vetro 28)', 4, 'H-235'), P('N10823', 'Fermavetro orizzontale fisso (vetro 28)', 2, 'L/3-53'), P('N10823', 'Fermavetro verticale fisso (vetro 28)', 2, 'H-91')]
PVC_3FC = [G('800167', 'Cover finitura labirinto (4 x H-91)', '4H-364'), G('V31013', 'Labirinto (4 x H-81)', '4H-324'), G('V31210', 'Cover anta PVC (2 x L1-69, 2 x H-126)', '2L/3+2H-390'), G('V31212', 'Cover telaio OX PVC (inferiori, montanti, superiore)', '2L+2H-356')]
ACC_3FC = squadr(4, 16, 16, 4) + [A('V50051', 'Compensazione cover-labirinto', 6), A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 1), A('V53054', 'Kit tappi labirinto V31013', 2), A('V58039', 'Kit base OX per alzante scorrevole', 2), A('V58040', 'Tappo tenuta centrale inferiore telaio U10000', 2), A('V58045', 'Kit spessore blocco tappo anta', 2),
           A('V59140', 'Kit centraggio carrelli', 8), A('V59163', 'Kit spessore per tappo V58040', 4), A('V78004', 'Kit rinforzo anta', 2), A('V90088', 'Tappo paracolpo', 2), tass(12)]
G_3FC = [G('800172', 'Guarnizione appoggio aggiuntivi', '4L/3+2H'), G('800936', 'Spazzolino L6,9 H9', '7L/3+2H'), G('809122', 'Guarnizione interna vetro 6.5-8 (vetro 28)', '2L+6H'), G('V02015', 'Guarnizione labirinto', '4H'), G('V03000', 'Guarnizione esterna vetro', '2L+6H'), G('V03018', 'Guarnizione finitura labirinto', '4H'), G('V03030', 'Guarnizione anta', '4L/3+4H'), G('V05031', 'Finitura telaio senza pinne', '2L/3+2H'), G('V05032', 'Finitura telaio con pinne', '2L/3'),
         G('V09050', 'Isolante sotto vetro anta', '4L/3+6H'), G('V20008', 'Listello LDPE traverso superiore anta', '2L/3'), G('V23000', 'Listello isolante sagomato adesivo telaio', '2H'), G('V20010', 'Listello LDPE 40x16 (fisso)', '2L/3'), G('V23001', 'Listello isolante 35x9', '2H'), G('V23002', 'Listello isolante 50x39', '2H'), G('V29002', 'Listello isolante montante centrale', '2H')]
tip('S140_LS_3A_FC', 'S3F140', 'Alzante scorrevole 3 ante, fissa interna centrale (XFX)', 'S140 8.20-8.21', 'S3', 2, 3, 'L/3+1', 'H-71', PROF_3FC, ACC_3FC, G_3FC + PVC_3FC, [V(2, 'L/3-135', 'H-207'), V(1, 'L/3-61', 'H-65')], KIT_LS(2), 'Ante uguali: L1 = L2 = L/3 (nessuna regola a catalogo).')
# 8.22-8.23 OXO anta interna centrale: L1 = L2 = L/3
PROF_OXO = telaio('U10000') + [P('U10140', 'Traverso anta (L2+74)', 2, 'L/3+74', '45-45'), P('U10140', 'Montante anta', 2, 'H-71', '45-45'), P('U10600', 'Montante stipite centrale', 2, 'H-31'), P('N10909', 'Profilo scatto labirinto', 1, 'H-75'), P('N10901', 'Profilo di finitura laterale', 2, 'H-43'), P('N10901', 'Profilo di finitura lato OXO (L1-90)', 1, 'L/3-90'), P('N10904', 'Cover telaio OX standard (L2-89)', 2, 'L/3-89'), P('N10906', 'Cover montante centrale OX', 2, 'H-55'),
                               P('N10630', 'Binario (L1+L2-15.5)', 1, '2L/3-15.5'), P('N10602', 'Montante telaio OXO', 1, 'H-30'), P('N10911', 'Cover OXO', 1, 'H-47'), P('N10823', 'Fermavetro orizzontale anta (vetro 28)', 2, 'L/3-54'), P('N10823', 'Fermavetro verticale anta (vetro 28)', 2, 'H-235'), P('N10823', 'Fermavetro orizzontale fisso (vetro 28)', 4, 'L/3-54'), P('N10823', 'Fermavetro verticale fisso (vetro 28)', 4, 'H-91')]
PVC_OXO = [G('800167', 'Cover finitura labirinto (2 x H-91)', '2H-182'), G('V31013', 'Labirinto standard (2 x H-81) + OXO (H-46)', '3H-208'), G('V31210', 'Cover anta PVC (L2+4 + H-126)', 'L/3+H-122'), G('V31212', 'Cover telaio OX PVC (montanti, superiore, lato OXO, inferiori)', '2L+2H-244')]
ACC_OXO = squadr(4, 8, 8, 4) + [A('V50051', 'Compensazione cover-labirinto', 3), A('V51052', 'Valvolina di drenaggio', 1), A('V53054', 'Kit tappi labirinto V31013', 1), A('V58039', 'Kit base OX per alzante scorrevole', 1), A('V58040', 'Tappo tenuta centrale inferiore telaio U10000', 1), A('V58045', 'Kit spessore blocco tappo anta', 1),
           A('V59140', 'Kit centraggio carrelli', 4), A('V59163', 'Kit spessore per tappo V58040', 2), A('V78004', 'Kit rinforzo anta', 1), A('V90088', 'Tappo paracolpo', 1), tass(12)]
G_OXO = [G('800172', 'Guarnizione appoggio aggiuntivi', '2L/3'), G('800936', 'Spazzolino L6,9 H9', '2L/3+2H'), G('809122', 'Guarnizione interna vetro 6.5-8 (vetro 28)', '2L+6H'), G('V02015', 'Guarnizione labirinto', '2H'), G('V03000', 'Guarnizione esterna vetro', '2L+6H'), G('V03018', 'Guarnizione ad infilare finitura labirinto', '3H'), G('V03030', 'Guarnizione anta', '4L/3+2H'), G('V05029', 'Guarnizione finitura labirinto slim', 'H'), G('V05031', 'Finitura telaio senza pinne', '2L/3'), G('V05032', 'Finitura telaio con pinne', 'L/3'),
         G('V09050', 'Isolante sotto vetro anta', '2L/3+4H'), G('V20008', 'Listello LDPE traverso superiore anta', 'L/3'), G('V20010', 'Listello LDPE 40x16 (fissi)', '4L/3+2H'), G('V23000', 'Listello isolante sagomato adesivo telaio', '2H'), G('V23001', 'Listello isolante 35x9', 'H'), G('V23002', 'Listello isolante 50x39', 'H'), G('V29002', 'Listello isolante montante centrale', '2H')]
tip('S140_LS_OXO', 'SOO140', 'Alzante scorrevole OXO, anta interna centrale', 'S140 8.22-8.23', 'S3', 1, 3, 'L/3+74', 'H-71', PROF_OXO, ACC_OXO, G_OXO + PVC_OXO, [V(1, 'L/3-62', 'H-207'), V(2, 'L/3-63', 'H-65')], KIT_LS(1), 'Specchiature uguali: L1 = L2 = L/3 (nessuna regola a catalogo).')
# 8.24-8.25 quattro ante, due fisse laterali (FXXF): L1 = L2 = L/4
PROF_4F = telaio('U10000') + [P('U10140', 'Traverso anta (L2+34)', 4, 'L/4+34', '45-45'), P('U10140', 'Montante anta', 4, 'H-71', '45-45'), P('U10600', 'Montante stipite centrale', 2, 'H-31'), P('U10601', 'Riporto ante in linea', 1, 'H-120'), P('N10909', 'Profilo scatto labirinto', 2, 'H-75'), P('N10901', 'Profilo di finitura laterale', 2, 'H-43'), P('N10902', 'Gocciolatoio', 1, 'L-40'), P('N10904', 'Cover telaio OX standard traverso (2L2-89)', 2, 'L/2-89'), P('N10906', 'Cover montante centrale OX', 2, 'H-55'), P('N10630', 'Binario', 1, 'L-89'),
                              P('N10823', 'Fermavetro orizzontale anta (vetro 28)', 4, 'L/4-94'), P('N10823', 'Fermavetro verticale anta (vetro 28)', 4, 'H-235'), P('N10823', 'Fermavetro orizzontale fisso (vetro 28)', 4, 'L/4-54'), P('N10823', 'Fermavetro verticale fisso (vetro 28)', 4, 'H-91')]
PVC_4F = [G('800167', 'Cover finitura labirinto (4 x H-91)', '4H-364'), G('V31013', 'Labirinto (4 x H-81)', '4H-324'), G('V31210', 'Cover anta PVC (2 x L2-36, 2 x H-126)', 'L/2+2H-324'), G('V31212', 'Cover telaio OX PVC (inferiori, montanti, superiore)', '2L+2H-356')]
ACC_4F = squadr(4, 16, 16, 4) + [A('V50051', 'Compensazione cover-labirinto', 6), A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 2), A('V53054', 'Kit tappi labirinto V31013', 2), A('V55097', 'Tappi chiusura tubolare U10000', 4), A('V58039', 'Kit base OX per alzante scorrevole', 2), A('V58040', 'Tappo tenuta centrale inferiore telaio U10000', 2), A('V58042', 'Kit tappi ante in linea', 1),
          A('V58045', 'Kit spessore blocco tappo anta', 2), A('V59140', 'Kit centraggio carrelli', 8), A('V59163', 'Kit spessore per tappo V58040', 4), A('V72121', 'Kit di fissaggio profilo U10601', 2), A('V78004', 'Kit rinforzo anta', 2), A('V90088', 'Tappo paracolpo', 2), tass(16)]
G_4F = [G('800172', 'Guarnizione appoggio aggiuntivi', 'L'), G('800936', 'Spazzolino L6,9 H9', '2L+2H'), G('809122', 'Guarnizione interna vetro 6.5-8 (vetro 28)', '2L+8H'), G('V02015', 'Guarnizione labirinto', '4H'), G('V03000', 'Guarnizione esterna vetro', '2L+8H'), G('V03018', 'Guarnizione finitura labirinto', '4H'), G('V03030', 'Guarnizione anta', '2L+2H'), G('V05031', 'Finitura telaio senza pinne', 'L/2'), G('V05032', 'Finitura telaio con pinne', 'L/2'),
        G('V09050', 'Isolante sotto vetro anta', 'L+6H'), G('V20008', 'Listello LDPE traverso superiore anta', 'L/2'), G('V20010', 'Listello LDPE 40x16 (fissi)', 'L+2H'), G('V23000', 'Listello isolante sagomato adesivo telaio', '2H'), G('V23001', 'Listello isolante 35x9', '2H'), G('V23002', 'Listello isolante 50x39', '2H'), G('V29002', 'Listello isolante montante centrale', '2H')]
tip('S140_LS_4A_2F', 'S4F140', 'Alzante scorrevole 4 ante, due fisse laterali (FXXF)', 'S140 8.24-8.25', 'S4', 2, 4, 'L/4+34', 'H-71', PROF_4F, ACC_4F, G_4F + PVC_4F, [V(2, 'L/4-102', 'H-207'), V(2, 'L/4-63', 'H-65')], KIT_LS(2, 1), 'Specchiature uguali: L1 = L2 = L/4 (nessuna regola a catalogo).')
# 8.26-8.27 quattro ante, due fisse laterali con montante slim (FXXF slim)
PROF_4FS = telaio('U10000') + [P('U10120', 'Montante centrale fisso slim', 2, 'H-31'), P('U10120', 'Montante centrale anta slim', 2, 'H-190'), P('U10140', 'Traverso anta (L2+12)', 4, 'L/4+12', '45-90'), P('U10140', 'Montante anta', 2, 'H-71', '45-45'), P('U10601', 'Riporto ante in linea', 1, 'H-120'), P('N10909', 'Profilo scatto labirinto anta', 2, 'H-75'), P('N10909', 'Profilo scatto labirinto fisso', 2, 'H-55'), P('N10901', 'Profilo di finitura laterale', 2, 'H-43'), P('N10902', 'Gocciolatoio', 1, 'L-40'), P('N10904', 'Cover telaio OX standard traverso (2L2-44)', 2, 'L/2-44'), P('N10630', 'Binario', 1, 'L-89'),
                               P('N10823', 'Fermavetro orizzontale anta (vetro 28)', 4, 'L/4-71'), P('N10823', 'Fermavetro verticale anta (vetro 28)', 4, 'H-235'), P('N10823', 'Fermavetro orizzontale fisso (vetro 28)', 4, 'L/4-31.5'), P('N10823', 'Fermavetro verticale fisso (vetro 28)', 4, 'H-91')]
PVC_4FS = [G('V31015', 'Labirinto slim (4 x H-81)', '4H-324'), G('V31210', 'Cover anta PVC (2 x L2-58, 2 x H-126)', 'L/2+2H-368'), G('V31212', 'Cover telaio OX PVC (inferiori, montanti, superiore)', '2L+2H-356')]
ACC_4FS = squadr(4, 8, 8, 4) + [A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 2), A('V53055', 'Kit tappi labirinto slim V31015', 2), A('V55097', 'Tappi chiusura tubolare U10000', 4), A('V58039', 'Kit base OX per alzante scorrevole', 2), A('V58040', 'Tappo tenuta centrale inferiore telaio U10000', 2), A('V58042', 'Kit tappi ante in linea', 1),
           A('V59140', 'Kit centraggio carrelli', 8), A('V59164', 'Kit spessore 36 mm per tappo V58040 (U10120)', 4), A('V72121', 'Kit di fissaggio profilo U10601', 2), A('V78004', 'Kit rinforzo anta', 2), A('V90088', 'Tappo paracolpo', 2), tass(16)]
G_4FS = [g for g in G_4F if g['art'] not in ('V03018', 'V23001', 'V23002', 'V29002')] + [G('V05029', 'Guarnizione finitura labirinto slim', '4H'), G('V20009', 'Listello LDPE 54x4', '4H'), G('V23003', 'Listello isolante 24x9', '4H')]
tip('S140_LS_4A_2F_SLIM', 'S4T140', 'Alzante scorrevole 4 ante, due fisse laterali, montante slim U10120', 'S140 8.26-8.27', 'S4', 2, 4, 'L/4+12', 'H-71', PROF_4FS, ACC_4FS, G_4FS + PVC_4FS, [V(2, 'L/4-79', 'H-207'), V(2, 'L/4-41', 'H-65')], KIT_LS(2, 1), 'Specchiature uguali: L1 = L2 = L/4.')
# 8.28-8.30 sei ante mobili (telaio 3 vie): L1 = L2 = L3 = L/6
PROF_6A = telaio3() + [P('U10140', 'Traverso anta laterale L1 (+1)', 4, 'L/6+1', '45-45'), P('U10140', 'Traverso anta laterale L2 (+75)', 4, 'L/6+75', '45-45'), P('U10140', 'Traverso anta centrale L3 (+34.5)', 4, 'L/6+34.5', '45-45'), P('U10140', 'Montante anta', 12, 'H-71', '45-45'), P('U10601', 'Riporto ante in linea', 1, 'H-120'), P('N10909', 'Profilo scatto labirinto', 8, 'H-75'), P('N10901', 'Profilo di finitura laterale', 2, 'H-43'), P('N10902', 'Gocciolatoio', 1, 'L-40'), P('N10903', 'Profilo di finitura laterale tre ante', 2, 'H-43'), P('N10630', 'Binario', 3, 'L-89'),
                       P('N10823', 'Fermavetro orizzontale anta L1 (vetro 28)', 4, 'L/6-127'), P('N10823', 'Fermavetro orizzontale anta L2 (vetro 28)', 4, 'L/6-53'), P('N10823', 'Fermavetro orizzontale anta L3 (vetro 28)', 4, 'L/6-93.5'), P('N10823', 'Fermavetro verticale (vetro 28)', 12, 'H-235')]
PVC_6A = [G('800167', 'Cover finitura labirinto (8 x H-91)', '8H-728'), G('V31013', 'Labirinto (8 x H-81)', '8H-648'), G('V31208', 'Cover telaio PVC (inferiori, montanti, superiori)', '4L+4H-712'), G('V31210', 'Cover anta PVC (inferiori e montanti)', 'L+6H-1062')]
ACC_6A = squadr(0, 48, 48, 8) + [A('V50051', 'Compensazione cover-labirinto', 24), A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 2), A('V53054', 'Kit tappi labirinto V31013', 4), A('V55097', 'Tappi chiusura tubolare U10060/U10061', 4), A('V58036', 'Kit base 3 ante per alzante scorrevole', 2), A('V58037', 'Tappo tenuta centrale inferiore telaio', 4), A('V58042', 'Kit tappi ante in linea', 1),
          A('V58045', 'Kit spessore blocco tappo anta', 6), A('V59140', 'Kit centraggio carrelli', 24), A('V59161', 'Kit spessore per tappo V58037', 8), A('V72121', 'Kit di fissaggio profilo U10601', 2), A('V78004', 'Kit rinforzo anta', 4), A('V78005', 'Kit rinforzo terza anta', 4), A('V90088', 'Tappo paracolpo', 4), tass(24)]
G_6A = [G('800936', 'Spazzolino L6,9 H9', 'L+2H'), G('809122', 'Guarnizione interna vetro 6.5-8 (vetro 28)', '2L+12H'), G('V02015', 'Guarnizione labirinto', '8H'), G('V03000', 'Guarnizione esterna vetro', '2L+12H'), G('V03018', 'Guarnizione finitura labirinto', '8H'), G('V03030', 'Guarnizione anta', '4L+4H'), G('V05031', 'Finitura telaio senza pinne', '3L+2H'), G('V05032', 'Finitura telaio con pinne', 'L'),
        G('V09050', 'Isolante sotto vetro anta', '2L+12H'), G('V20008', 'Listello LDPE traverso superiore anta', 'L'), G('V23000', 'Listello isolante sagomato adesivo telaio', '4H'), G('V23001', 'Listello isolante 35x9', '6H'), G('V23002', 'Listello isolante 50x39', '6H')]
tip('S140_LS_6A', 'S6A140', 'Alzante scorrevole 6 ante mobili (telaio 3 binari)', 'S140 8.28-8.30', 'S6', 6, 6, 'L/6+1', 'H-71', PROF_6A, ACC_6A, G_6A + PVC_6A, [V(2, 'L/6-135', 'H-207'), V(2, 'L/6-61', 'H-207'), V(2, 'L/6-102', 'H-207')], KIT_LS(6, 3), 'Ante uguali: L1 = L2 = L3 = L/6 (nessuna regola a catalogo).')

# ---------- SCORREVOLE IN LINEA (S140R) ----------
G_R = [G('800936', 'Spazzolino L6,9 H9', 'L+2H'), G('809122', 'Guarnizione interna vetro 6.5-8 (vetro 28)', '2L+4H'), G('V02015', 'Guarnizione labirinto', '2H'), G('V03000', 'Guarnizione esterna vetro', '2L+4H'), G('V03018', 'Guarnizione finitura labirinto', '2H'), G('V05031', 'Finitura telaio senza pinne', 'L+2H'), G('V05032', 'Finitura telaio con pinne', 'L'),
       G('V09050', 'Isolante sotto vetro anta', '2L+4H'), G('V10022', 'Spazzolino L6,9 H10 Quadrifin', '4L+4H'), G('V20008', 'Listello LDPE traverso superiore anta', 'L'), G('V23000', 'Listello isolante sagomato adesivo telaio', '2H'), G('V23001', 'Listello isolante 35x9', '2H'), G('V23002', 'Listello isolante 50x39', '2H')]
PVC_RXX = [G('800167', 'Cover finitura labirinto (2 x H-106.5)', '2H-213'), G('V31013', 'Labirinto (2 x H-96.5)', '2H-193'), G('V31208', 'Cover telaio PVC (2 x L/2-81.5, 2 x H-45, L-45)', '2L+2H-298'), G('V31210', 'Cover anta PVC (2 spezzoni 75, 2 x H-141.5)', '2H-133')]
ACC_R = squadr(0, 16, 16, 8) + [A('V50051', 'Compensazione cover-labirinto', 6), A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 1), A('V53054', 'Kit tappi labirinto V31013', 1), A('V53059', 'Tappo tenuta centrale inferiore telaio', 1), A('V55168', 'Tappi chiusura tubolare U10022', 3), A('V58055', 'Kit base 2 ante scorrevole', 1), A('V78004', 'Kit rinforzo anta', 2), A('V90088', 'Tappo paracolpo', 1), tass(8)]
tip('S140_R_XX', 'SRX140', 'Scorrevole in linea 2 ante mobili (XX)', 'S140 8.52-8.53', 'S2', 2, 2, 'L/2-7', 'H-86.5', PROF_XX, ACC_R, G_R + PVC_RXX, [V(2, 'L/2-143', 'H-222.5')], KIT_R(2))
PVC_ROX = [G('800167', 'Cover finitura labirinto (2 x H-106.5)', '2H-213'), G('V31013', 'Labirinto (2 x H-96.5)', '2H-193'), G('V31208', 'Cover telaio PVC (2 x L/2-81.5, 2 x H-45, L-45)', '2L+2H-298'), G('V31210', 'Cover anta PVC (L/2-77 anta fissa, spezzone 75, 2 x H-141.5)', 'L/2+2H-285')]
G_ROX = [g if g['art'] != 'V05031' else G('V05031', 'Finitura telaio senza pinne', 'L+H') for g in G_R]
tip('S140_R_OX', 'SRF140', 'Scorrevole in linea 2 ante, una fissa', 'S140 8.56-8.57', 'S1', 1, 2, 'L/2-7', 'H-86.5', PROF_XX, ACC_R + [A('V58049', 'Kit di fissaggio anta (anta fissa)', 1)], G_ROX + PVC_ROX, [V(2, 'L/2-143', 'H-222.5')], KIT_R(1))
# 8.54-8.55 in linea XX con montante slim; 8.58-8.59 una fissa con montante slim
G_RS = [g for g in G_R if g['art'] not in ('V03018', 'V23001', 'V23002')] + [G('V05029', 'Guarnizione finitura labirinto slim', '2H'), G('V20009', 'Listello LDPE 54x4', '2H'), G('V23003', 'Listello isolante 24x9', '2H')]
PVC_RXS = [G('V31015', 'Labirinto slim (2 x H-96.5)', '2H-193'), G('V31208', 'Cover telaio PVC (2 x L/2-81.5, 2 x H-45, L-45)', '2L+2H-298'), G('V31210', 'Cover anta PVC (2 spezzoni 75, 2 x H-141.5)', '2H-133')]
ACC_RS = squadr(0, 8, 8, 8) + [A('V51046', 'Coppia tappi laterali gocciolatoio', 1), A('V51052', 'Valvolina di drenaggio', 1), A('V53055', 'Kit tappi labirinto slim V31015', 1), A('V53059', 'Tappo tenuta centrale inferiore telaio', 1), A('V55168', 'Tappi chiusura tubolare U10022', 3), A('V58055', 'Kit base 2 ante scorrevole', 1), A('V78004', 'Kit rinforzo anta', 2), A('V90088', 'Tappo paracolpo', 1), tass(8)]
tip('S140_R_XX_SLIM', 'SRS140', 'Scorrevole in linea 2 ante mobili (XX) con montante slim U10120', 'S140 8.54-8.55', 'S2', 2, 2, 'L/2-29.5', 'H-86.5', PROF_XXS, ACC_RS, G_RS + PVC_RXS, [V(2, 'L/2-120.5', 'H-222.5')], KIT_R(2))
PVC_ROS = [G('V31015', 'Labirinto slim (2 x H-96.5)', '2H-193'), G('V31208', 'Cover telaio PVC (2 x L/2-81.5, 2 x H-45, L-45)', '2L+2H-298'), G('V31210', 'Cover anta PVC (L/2-99 anta fissa, spezzone 75, 2 x H-141.5)', 'L/2+2H-307')]
G_ROS = [g if g['art'] != 'V05031' else G('V05031', 'Finitura telaio senza pinne', 'L+H') for g in G_RS]
tip('S140_R_OX_SLIM', 'SRT140', 'Scorrevole in linea 2 ante, una fissa, montante slim U10120', 'S140 8.58-8.59', 'S1', 1, 2, 'L/2-29.5', 'H-86.5', PROF_XXS, ACC_RS + [A('V58049', 'Kit di fissaggio anta (anta fissa)', 1)], G_ROS + PVC_ROS, [V(2, 'L/2-120.5', 'H-222.5')], KIT_R(1), 'Accessori come 8.57 con tappi labirinto slim.')

# ---------- VARIANTE SOGLIA RIBASSATA (seconda colonna delle distinte) ----------
import re, copy
def shift(mis, art_delta):
    """sposta la costante di una formula 'aH-b' o 'aL-b' di delta per ogni termine H (o L) presente"""
    m = re.fullmatch(r'\s*(\d*)H\s*([+-]\s*[\d.]+)?\s*', mis)
    if m:
        k = int(m.group(1) or 1); c = float((m.group(2) or '0').replace(' ', '')); c += k * art_delta          # soglia ribassata: pezzi verticali più lunghi
        return f"{m.group(1)}H{c:+g}".replace('+0', '') if c else f"{m.group(1)}H"
    m = re.fullmatch(r'\s*(.*?H)\s*([+-]\s*[\d.]+)\s*', mis)   # es. 'L+2H-437', '2L/3+2H-390'
    if m:
        k = int(re.search(r'(\d*)H', m.group(1)).group(1) or 1); c = float(m.group(2).replace(' ', '')) + k * art_delta
        return f"{m.group(1)}{c:+g}"
    return mis
def ribassata(t):
    r = copy.deepcopy(t); tel = r['profili'][0]['art']
    fam = 'XX' if tel == 'U10022' else 'OX' if tel == 'U10000' else '3V'
    r['id'] += '_SR'; r['cod'] += 'R'; r['soglia'] = 'ribassata'; r['nome'] += ' — soglia ribassata'
    r['avviso'] = FONTE.replace('soglia standard', 'soglia ribassata (seconda colonna della distinta)')
    D = {'XX': {'U10140m': 26, 'N10909': 25.5, 'N10909f': 25.5, 'N10901': 15, 'N10903': 15, 'U10120': 26, 'U10120f': 12, 'U10601': 26, 'FVa': 26, 'FVf': 19.5, 'PVC': 26, 'U10600': 12, 'N10904m': 19.5, 'N10906': 19.5, 'vetro_a': 26, 'vetro_f': 19.5, 'N10602': 7, 'N10911': 7},
         'OX': {'U10140m': 18.5, 'N10909': 18, 'N10909f': 19.5, 'N10901': 7.5, 'N10903': 7.5, 'U10120': 18, 'U10120f': 12, 'U10601': 19, 'FVa': 18, 'FVf': 19.5, 'PVC': 18, 'U10600': 12, 'N10904m': 19.5, 'N10906': 19.5, 'vetro_a': 18, 'vetro_f': 19.5, 'N10602': 7, 'N10911': 7},
         '3V': {'U10140m': 18.5, 'N10909': 18, 'N10909f': 19.5, 'N10901': 7.5, 'N10903': 7.5, 'U10120': 18, 'U10120f': 12, 'U10601': 19, 'FVa': 18, 'FVf': 19.5, 'PVC': 18, 'U10600': 12, 'N10904m': 19.5, 'N10906': 19.5, 'vetro_a': 18, 'vetro_f': 19.5, 'N10602': 7, 'N10911': 7}}[fam]
    prof = []
    for p in r['profili']:
        a, d = p['art'], p['desc']
        if a in ('U10022', 'U10000', 'U10060', 'U10061') and d.startswith('Traverso'): p = dict(p, pz=1); prof.append(p); continue
        if a in ('U10022', 'U10000', 'U10060', 'U10061') and d.startswith('Montante'): p = dict(p, ang='90-45'); prof.append(p); continue
        if a == 'U10140' and d.startswith('Montante'): p = dict(p, mis=shift(p['mis'], D['U10140m']))
        elif a == 'N10909': p = dict(p, mis=shift(p['mis'], D['N10909f'] if 'fisso' in d else D['N10909']))
        elif a in ('N10901', 'N10903') and 'H' in p['mis']: p = dict(p, mis=shift(p['mis'], D[a]))
        elif a == 'U10120': p = dict(p, mis=shift(p['mis'], D['U10120f'] if 'fisso' in d else D['U10120']))
        elif a == 'U10601': p = dict(p, mis=shift(p['mis'], D['U10601']))
        elif a == 'U10600': p = dict(p, mis=shift(p['mis'], D['U10600']))
        elif a == 'N10904' and 'montante' in d: p = dict(p, mis=shift(p['mis'], D['N10904m']))
        elif a == 'N10904' and 'traverso' in d and p['pz'] >= 2:
            prof.append(dict(p, pz=p['pz'] // 2)); p = dict(p, art='N10905', desc=d.replace('OX standard', 'OX ribassata'), pz=p['pz'] // 2)
        elif a == 'N10906': p = dict(p, mis=shift(p['mis'], D['N10906']))
        elif a in ('N10602', 'N10911'): p = dict(p, mis=shift(p['mis'], D[a]))
        elif a == 'N10630': p = dict(p, mis=re.sub(r'-(\d+(?:\.\d+)?)$', lambda m: f"-{float(m.group(1))+2:g}", p['mis']))
        elif a == 'N10823' and 'verticale' in d: p = dict(p, mis=shift(p['mis'], D['FVf'] if 'fisso' in d else D['FVa']))
        prof.append(p)
    # soglia ribassata al posto del traverso inferiore
    if fam == 'XX': prof.insert(2, P('U10400', 'Soglia ribassata XX', 1, 'L-106'))
    elif fam == 'OX': prof.insert(2, P('U10401', 'Soglia ribassata OX', 1, 'L-31'))
    else: prof.insert(4, P('U10402', 'Soglia ribassata interno XXX', 1, 'L-91')); prof.insert(5, P('U10403', 'Soglia ribassata esterno XXX', 1, 'L-91'))
    r['profili'] = prof
    gua = []
    for g in r['guarnizioni']:
        a = g['art']
        if a in ('800167', 'V31013', 'V31015'): g = dict(g, mis=shift(g['mis'], D['PVC']), desc=g['desc'] + ' ribassata')
        elif a == 'V31210':
            k = int(re.search(r'(\d*)H', g['mis']).group(1) or 1); g = dict(g, mis=shift(g['mis'], D['PVC'] if fam != 'XX' else 26))   # montanti più corti
        elif a == 'V31208':
            g = dict(g, mis=('L+2H-140' if fam == 'XX' else '2L+4H-220'), desc='Cover telaio PVC (montanti H-47.5/H-40, superiore)')   # senza inferiori
            gua.append(g); gua.append(G('V31209', 'Cover telaio ribassata inferiore', r.get('_v31209', 'L-224'))); continue
        elif a == 'V31212':
            sup = {'S140_LS_OXO': '4L/3+2H-172'}.get(t['id'], 'L+2H-110')
            g = dict(g, mis=sup, desc='Cover telaio OX PVC (montanti H-40, superiore, lato OXO)'); gua.append(g); gua.append(G('V31211', 'Cover telaio ribassata OX inferiore', r.get('_v31211', 'L-209'))); continue
        gua.append(g)
    r['guarnizioni'] = gua
    acc = []
    for a in r['accessori']:
        c = a['art']
        if c == 'V55168': a = dict(a, art='V55098', desc='Tappi chiusura tubolare U10400', pz=max(1, a['pz'] // 3))
        elif c == 'V55097': a = dict(a, art='V55098', desc='Tappi chiusura tubolare U10401', pz=max(1, a['pz'] // 3 if a['pz'] == 3 else a['pz'] // 2))
        elif c == 'V58037': a = dict(a, art='V58038', desc='Tappo tenuta centrale inferiore telaio U10400')
        elif c == 'V58040': a = dict(a, art='V58041', desc='Tappo tenuta centrale inferiore telaio U10401')
        elif c == 'V53059': a = dict(a, art='V53077', desc='Tappo tenuta centrale inferiore telaio U10400')
        elif c in ('710400', '710401', '710407', 'V43000'): a = dict(a, pz=a['pz'] // 2)
        acc.append(a)
    n_sog = 2 if t['forma'] in ('S3', 'S6') and fam != 'OX' else 1
    acc.append(A('V59141', 'Kit tappi montante-soglia U10400', n_sog) if fam != 'OX' else A('V59142', 'Kit tappi montante-soglia U10401', 1))
    r['accessori'] = acc
    r['vetro'] = [dict(v, h=shift(v['h'], D['vetro_f'] if v['h'].endswith('-65') else D['vetro_a'])) for v in r['vetro']]
    r['anta_h'] = shift(t['anta_h'], D['U10140m'])
    return r
V31209 = {'S140_LS_XX': 'L-224', 'S140_LS_XX_SLIM': 'L-224', 'S140_LS_4A': 'L-342', 'S140_LS_4A_SLIM': 'L-342', 'S140_LS_3A': '2L-418', 'S140_LS_6A': '2L-654', 'S140_R_XX': 'L-224', 'S140_R_OX': 'L-224', 'S140_R_XX_SLIM': 'L-224', 'S140_R_OX_SLIM': 'L-224'}
V31211 = {'S140_LS_OX': 'L-209', 'S140_LS_OX_INT': 'L-209', 'S140_LS_OX_SLIM': 'L-209', 'S140_LS_OX_SLIM_INT': 'L-209', 'S140_LS_3A_FC': 'L-327', 'S140_LS_OXO': 'L-212.5', 'S140_LS_4A_2F': 'L-327', 'S140_LS_4A_2F_SLIM': 'L-327'}
for t in list(T):
    t['soglia'] = 'standard'; t['_v31209'] = V31209.get(t['id']); t['_v31211'] = V31211.get(t['id'])
    T.append(ribassata(t))
for t in T:
    t.pop('_v31209', None); t.pop('_v31211', None)

# ---------- raggruppamento per sigla: montante slim, soglia ribassata e lato anta come varianti ----------
META = {'S140_LS_XX': ('XX', 'Alzante scorrevole 2 ante mobili', 'standard', None), 'S140_LS_XX_SLIM': ('XX', 'Alzante scorrevole 2 ante mobili', 'slim', None),
        'S140_LS_3A': ('XXX', 'Alzante scorrevole 3 ante mobili (3 binari)', 'standard', None),
        'S140_LS_4A': ('XXXX', 'Alzante scorrevole 4 ante mobili', 'standard', None), 'S140_LS_4A_SLIM': ('XXXX', 'Alzante scorrevole 4 ante mobili', 'slim', None),
        'S140_LS_OX': ('OX', 'Alzante scorrevole fisso apribile', 'standard', 'esterna'), 'S140_LS_OX_INT': ('OX', 'Alzante scorrevole fisso apribile', 'standard', 'interna'),
        'S140_LS_OX_SLIM': ('OX', 'Alzante scorrevole fisso apribile', 'slim', 'esterna'), 'S140_LS_OX_SLIM_INT': ('OX', 'Alzante scorrevole fisso apribile', 'slim', 'interna'),
        'S140_LS_3A_FC': ('XFX', 'Alzante scorrevole 3 ante, fissa centrale', 'standard', None), 'S140_LS_OXO': ('OXO', 'Alzante scorrevole OXO, anta interna centrale', 'standard', None),
        'S140_LS_4A_2F': ('FXXF', 'Alzante scorrevole 4 ante, 2 fisse laterali', 'standard', None), 'S140_LS_4A_2F_SLIM': ('FXXF', 'Alzante scorrevole 4 ante, 2 fisse laterali', 'slim', None),
        'S140_LS_6A': ('XXXXXX', 'Alzante scorrevole 6 ante mobili (3 binari)', 'standard', None),
        'S140_R_XX': ('S140R XX', 'Scorrevole in linea 2 ante mobili', 'standard', None), 'S140_R_XX_SLIM': ('S140R XX', 'Scorrevole in linea 2 ante mobili', 'slim', None),
        'S140_R_OX': ('S140R OX', 'Scorrevole in linea 2 ante, una fissa', 'standard', None), 'S140_R_OX_SLIM': ('S140R OX', 'Scorrevole in linea 2 ante, una fissa', 'slim', None)}
ORD = ['XX', 'OX', 'XXX', 'XFX', 'OXO', 'XXXX', 'FXXF', 'XXXXXX', 'S140R XX', 'S140R OX']
for t in T:
    base = t['id'][:-3] if t['id'].endswith('_SR') else t['id']; sigla, descr, mont, lato = META[base]
    t['sigla'] = sigla; t['montante'] = mont; t['lato'] = lato; t['gruppo'] = f"{sigla} — {descr}"
    parti = [('montante slim U10120' if mont == 'slim' else 'montante standard'), ('soglia ribassata' if t['soglia'] == 'ribassata' else 'soglia standard')] + ([f'anta {lato}'] if lato else [])
    std = mont == 'standard' and t['soglia'] == 'standard' and lato in (None, 'esterna')
    t['variante'] = ', '.join(parti) + (' — STANDARD' if std else '') + f" [distinta {t['rif'].replace('S140 ', '')}]"
T.sort(key=lambda t: (ORD.index(t['sigla']), t['soglia'] != 'standard', t['montante'] != 'standard', (t['lato'] or '') == 'interna'))

out = {'_nota': FONTE + ' Voci opzionali escluse; tasselli vetro e maniglione FKS 213-00737 aggiunti da noi. Ore = 4,5 h per specchiatura.', 'tipologie': T}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tipologie_s140.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('tipologie S140:', len(T), [t['cod'] for t in T])
