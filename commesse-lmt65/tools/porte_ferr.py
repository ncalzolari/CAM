import json
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT,'src')+'/'
P = json.load(open(F+'dati_porte.json'))
P['porte_ferr'] = {
  'nota': 'TUTTO DA TARARE: convenzioni facce/versi per analogia con C75S; quote dal manuale AluK v4.A. Modificare qui (o in dati_serie.js) senza toccare il codice.',
  'AM': 1050,
  'x_da_alto_dx': True, 'dx_specchio': True,
  'nota_dx': 'Pezzi con taglio 45-90 (montanti DX): nel job lo zero X è in testa (x_da_alto_dx) e le facce sono ribaltate F2<->F3 con Y speculare (dx_specchio). Se in FSTLine risultano invertite, mettere a false.',
  'facce': {'telaio': {'battuta': '1', 'muro': '4', 'interno': '2', 'esterno': '3'},
            'anta':   {'battuta': '4', 'interno': '2', 'esterno': '3'}},
  'utensili': {'3': '4', '4': '4', '5': '12', '6': '12', '7': '12', '8': '3', '10': '2', '11': '2', '15': '2', 'fresa': '2', 'default': '12'},
  'fx': {'attivo': True, 'a': 200, 'passo': 700, 'y_est': 21.9, 'd1': 7, 'd2': 15, 'z1': -3, 'z2': -20.5,
         'nota': '10.01: punta a due diametri Ø7 (parete a muro) / Ø15 (parete lato battuta); A=200 dagli angoli, interasse ≤700; asse a 21.9 dalla faccia esterna'},
  'cerniere': {
    'n': [[1300, 2], [2400, 3], [9999, 4]],
    'pos_alto': 256, 'pos_basso': 244, 'pos_basso_zoccolo': 274, 'offset_telaio': 6,
    'nota_pos': 'Posizioni asse cerniera dal filo anta: 256 dall\'alto, 244 dal basso (274 con zoccolo) = tabella cerniere nascoste 10.51, estesa a tutti i tipi (DA TARARE); intermedie equidistanti. offset_telaio: asse sul telaio = asse anta + 6 (aria).',
    'ali': {'d': 11, 'z': -3,
            'y_anta': {'default': 47, 'U20000': 50.5, 'U28002': 50.5, 'U51630': 36, 'U52630': 36},
            'y_telaio': {'default': 17.5, 'U20000': 14, 'U28002': 14, 'U51630': 42, 'U52630': 42},
            'seq2': {'anta': [11, -11], 'telaio': [-31, -53]},
            'seq3': {'anta': [11, -11], 'telaio': [54, 32, -31, -53]},
            'nota': '10.32-10.35: fori Ø11 dima T10095; interassi 22 nelle ali, 21 (sopra) / 20 (sotto) tra ala e ala. Offset rispetto all\'asse dei 2 fori anta (positivo = verso l\'alto). Y anta dal bordo interno (aria); Y telaio dal bordo interno del telaio.'},
    'stelo': {'z': -3,
              'telaio': [[-100, 12, 4], [-100, 30, 4], [100, 12, 4], [100, 30, 4], [-60, 12, 6], [60, 12, 6]],
              'anta':   [[-100, 12, 4], [-100, 30, 4], [100, 12, 4], [100, 30, 4], [-60, 22, 4], [60, 22, 4]],
              'nota': '10.41-10.42: dima T10020 (L 206, asse a ±200 dall\'estremità). Il manuale NON quota le posizioni dei fori (date dalla dima): [offset X, Y, Ø] qui sono SEGNAPOSTO da rilevare dalla dima.'},
    'nascoste': {'d': 11, 'z': -3,
                 'tel_sede': [124, 36, 41], 'tel_y_sede': 11.5, 'tel_int': 146, 'tel_y_fori': [16, 35.5],
                 'anta_sede': [170, 28, 43], 'anta_y_sede': 16, 'anta_int': 189, 'anta_y_fori': [22, 38],
                 'nota': '10.52 (ap. interna U51200/U51320): sede telaio 124x36 R7 prof.41 a 11.5 dal bordo battuta; fori Ø11 interasse 146 a 16 e 35.5; sede anta 170x28 R7 prof.43 a 16 dal bordo; fori Ø11 interasse 189 a 22 e 38. Fresata labbro 92x8 e 37x5 NON emesse. Ap. esterna (10.53-57) da verificare.'},
  },
  'serrature': {
    '732251': {'nome': 'Serratura AluK 732251', 'y_est': 22.5, 'y_centrale': 22.5, 'z': -3, 'z_facce': -3, 'entrata': 35, 'd_maniglia': 20, 'cilindro': [10.5, 33.5], 'int_cilindro': 92, 'd_fori': 4,
               'anta': [{'tipo': 'asola', 'nome': 'corpo', 'da': -145, 'a': 110, 'lung': 255, 'larg': 16},
                        {'tipo': 'asola', 'nome': 'deviatore sup.', 'da': 630, 'a': 820, 'lung': 190, 'larg': 16},
                        {'tipo': 'asola', 'nome': 'deviatore inf.', 'da': -855, 'a': -665, 'lung': 190, 'larg': 16}],
               'incontri': [{'nome': 'scrocco 732261/2', 'da': -12, 'a': 68, 'lung': 80, 'larg': 22},
                            {'nome': 'catenaccio', 'da': -85, 'a': -31, 'lung': 54, 'larg': 16},
                            {'nome': 'gancio sup. 732253', 'da': 678, 'a': 778, 'lung': 100, 'larg': 16},
                            {'nome': 'gancio inf. 732253', 'da': -815, 'a': -715, 'lung': 100, 'larg': 16}],
               'nota': '10.72: quote da AM (positivo verso l\'alto). Foro maniglia Ø non quotato (20 = segnaposto). Interpretazione asole stipite 80/19/31/54 da verificare.'},
    'H51400': {'nome': 'Serratura AluK H51400', 'y_est': 22.5, 'y_centrale': 22.5, 'z': -3, 'z_facce': -3, 'entrata': 35, 'd_maniglia': 20, 'cilindro': [10.5, 33.5], 'int_cilindro': 92, 'd_fori': 4,
               'anta': [{'tipo': 'asola', 'nome': 'corpo', 'da': -145, 'a': 110, 'lung': 255, 'larg': 16},
                        {'tipo': 'asola', 'nome': 'deviatore sup.', 'da': 630, 'a': 820, 'lung': 190, 'larg': 16},
                        {'tipo': 'asola', 'nome': 'deviatore inf.', 'da': -855, 'a': -665, 'lung': 190, 'larg': 16}],
               'incontri': [{'nome': 'scrocco centrale', 'da': -12, 'a': 68, 'lung': 80, 'larg': 22},
                            {'nome': 'catenaccio', 'da': -85, 'a': -31, 'lung': 54, 'larg': 16},
                            {'nome': 'scrocco sup. 732253', 'da': 678, 'a': 778, 'lung': 100, 'larg': 16},
                            {'nome': 'scrocco inf. 732253', 'da': -815, 'a': -715, 'lung': 100, 'larg': 16}],
               'nota': '10.74: come 732251; con blocco H51700 l\'asola centrale sale di 65 (AM+175) — non gestito.'},
    '732259': {'nome': 'Serratura AluK 732259', 'y_est': 22.5, 'y_centrale': 22.5, 'z': -3, 'z_facce': -3, 'entrata': 35, 'd_maniglia': 20, 'cilindro': [10.5, 33.5], 'int_cilindro': 92, 'd_fori': 4,
               'anta': [{'tipo': 'asola', 'nome': 'corpo', 'da': -145, 'a': 110, 'lung': 255, 'larg': 16}],
               'incontri': [{'nome': 'scrocco 732261/2', 'da': -12, 'a': 68, 'lung': 80, 'larg': 22},
                            {'nome': 'catenaccio', 'da': -85, 'a': -31, 'lung': 54, 'larg': 16}],
               'nota': '10.77: serratura a un punto.'},
    'cisa': {'nome': 'Serratura CISA/ISEO', 'y_est': 23, 'y_centrale': 21.5, 'z': -3, 'z_facce': -3, 'entrata': 35, 'd_maniglia': 20, 'cilindro': [10.5, 33.5], 'int_cilindro': 85, 'd_fori': 4,
             'anta': [],
             'incontri': [{'nome': 'scrocco 732176', 'da': 54, 'a': 109, 'lung': 55, 'larg': 11.5, 'fori': [40, 123]},
                          {'nome': 'catenaccio 732176', 'da': -67, 'a': 26, 'lung': 93, 'larg': 11.5}],
             'nota': '10.79: asole frontale anta e incontri deviatori 732177 dipendono dalla serratura (interasse maniglia-cilindro variabile, 85 = segnaposto): NON emesse. Fori Ø4 incontro: posizione segnaposto.'},
  },
  'catenacci': {'attivo': True, 'x_sup_da_alto': 643, 'asola': [130, 20], 'y': 44.5, 'x_inf_da_basso': None,
                'nota': '10.21: asola 130x20 R3 sulla battuta del montante centrale semifisso, inizio a X = AB − AM − 643 dal filo superiore; parte inferiore (10.22) non quotata qui (x_inf_da_basso=null → non emessa). Foro Ø10.5 in testa non emesso.'},
}
# libreria (secondo foglio)
lib = []
def L(id, el, serie, prof, geo, dim, quota, pos, ut, rif, nome, stato='da_tarare', tipo='cnc'):
    lib.append({'id': id, 'el': el, 'serie': serie, 'prof': prof, 'tipo': tipo, 'geo': geo, 'dim': dim, 'quota': quota, 'pos': pos, 'ut': ut, 'rif': rif, 'stato': stato, 'nome': nome})
for s, tel, anta, telE, antaE in (('D67', 'U51200', 'U51320', 'U51201', 'U51340'), ('D77', 'U52200', 'U52320', 'U52201', 'U52340')):
    L(f'P{s}01', 'telaio', s, [tel, telE], 'fori', 'Ø7 + Ø15', 'Y 21.9 dalla faccia esterna · F4 (muro) / F1 (battuta)', '200 dagli angoli, interasse ≤700, tutti i lati', 'ut.12 (d5) / ut.2 (d10)', '10.01', 'Fissaggio telaio a muro V50006 (punta a due diametri)')
    L(f'P{s}02', 'telaio', s, [tel, telE], 'fori', 'Ø11 ×2 (2 ali) / ×4 (3 ali)', 'Y 17.5 dal bordo interno · F1', 'asse cerniera = asse anta + 6; interassi 22/21/20', 'ut.2 (d10)', '10.32-10.35', 'Cerniere 2/3 ali lato stipite (dima T10095)')
    L(f'P{s}03', 'anta', s, [anta, antaE], 'fori', 'Ø11 ×2', 'Y 47 dal bordo interno · F4', 'asse cerniera: 256 dall\'alto, 244/274 dal basso, intermedie equidistanti', 'ut.2 (d10)', '10.32-10.35', 'Cerniere 2/3 ali lato anta (dima T10095)')
    L(f'P{s}04', 'telaio', s, [tel, telE], 'fori', 'Ø4 ×4 + Ø6 ×2 per cerniera', 'segnaposto (dima T10020)', 'asse ±200', 'ut.4 (d3)', '10.41-10.42', 'Cerniere a stelo H51300 lato stipite', 'indicativo')
    L(f'P{s}05', 'anta', s, [anta, antaE], 'fori', 'Ø4 ×6 per cerniera', 'segnaposto (dima T10020)', 'asse ±200', 'ut.4 (d3)', '10.41-10.42', 'Cerniere a stelo H51300 lato anta', 'indicativo')
    L(f'P{s}06', 'telaio', s, [tel], 'fresata+fori', '124×36 R7 prof.41 + Ø11 ×4', 'sede a 11.5 dal bordo; fori Y 16 / 35.5, interasse 146 · F1', 'asse cerniera 250 dal telaio', 'ut.2 (d10)', '10.51-10.52', 'Cerniere nascoste H59313 lato stipite')
    L(f'P{s}07', 'anta', s, [anta], 'fresata+fori', '170×28 R7 prof.43 + Ø11 ×4', 'sede a 16 dal bordo; fori Y 22 / 38, interasse 189 · F4', 'asse cerniera 256 dall\'alto / 244 dal basso', 'ut.2 (d10)', '10.51-10.52', 'Cerniere nascoste H59313 lato anta')
    L(f'P{s}08', 'anta', s, [anta, antaE], 'asole', '255×16 + 2× 190×16', 'asse 22.5 dalla faccia esterna · F4', 'AM−145…AM+110; deviatori AM+630…820 e AM−855…−665', 'ut.2 (d10)', '10.72-10.78', 'Serratura AluK 732251 / H51400 / 732259: asole frontale')
    L(f'P{s}09', 'anta', s, [anta, antaE], 'foro+asola', 'maniglia Ø? + cilindro 10.5×33.5', 'E 35 dal bordo battuta · F2/F3', 'AM e AM−92', 'ut.2 (d10)', '10.72', 'Serratura AluK: maniglia e cilindro (facce anta)')
    L(f'P{s}10', 'telaio', s, [tel, telE], 'asole', '80×22 + 54×16 (+2× 100×16)', 'asse 22.5 dalla faccia esterna · F1', 'AM−12…+68; AM−85…−31; ganci AM+678…778 e AM−815…−715', 'ut.2 (d10)', '10.72-10.78', 'Incontri serratura AluK 732261/732262 + 732253')
    L(f'P{s}11', 'telaio', s, [tel, telE], 'asole', '55×11.5 + 93×11.5', 'asse 23 dalla faccia esterna · F1', 'AM+54…109; AM−67…+26', 'ut.3 (d8)', '10.79-10.84', 'Incontri CISA/ISEO 732176 (732177 deviatori: posizione secondo serratura)')
    L(f'P{s}12', 'anta', s, [antaE if s=='D67' else antaE], 'asola', '130×20 R3', 'Y 44.5 · F4', 'X = AB − AM − 643 dal filo superiore', 'ut.2 (d10)', '10.21-10.23', 'Catenacci 732089 anta semifissa (parte superiore)')
    L(f'P{s}13', 'telaio', s, [tel, telE], 'fori', 'Ø14 + Ø5', '49.2/17.1 e 30/8', 'angoli (tranciante 909310 / punzonatrice T00001)', 'banco', '10.02-10.03', 'Squadrette stipiti V42002/710410 e battenti V42003/730036', 'banco', 'banco')
P['libreria'] = lib
json.dump(P, open(F+'dati_porte.json', 'w'), ensure_ascii=False, indent=1)
print('porte_ferr ok, libreria', len(lib))
