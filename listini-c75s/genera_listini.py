# Generatore listini a griglia C75S senza vetro — RAL 7016
# Struttura: foglio Prezzo (griglia LISTINO + griglia COSTO), Parametri, Coefficienti
import csv, os, re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# Parametri di default (celle gialle del foglio Parametri): usati anche dal self-check finale
PARAM = {"eur_kg":14.82, "sc_prof":0.43, "sc_acc":0.20, "sfrido":0.09, "eur_h":65.0, "ricarico":2.13}

def carica_netto(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "ferramenta.csv")):
    """ferramenta.csv (Codice;Prezzo;Unità) -> {codice: prezzo €/pezzo}. Unità = pezzi per confezione."""
    netto = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            unita = float(r.get("Unità") or r.get("Unita'") or 1) or 1.0
            netto[r["Codice"].strip()] = float(r["Prezzo"].replace(",", ".")) / unita
    return netto

NETTO = carica_netto()   # netto Maico 2025

PESI = {"B23008C":1.38,"B23122C":1.61,"B23100C":1.41,"N23637C":0.39,
        "B23401":1.00,"K50":0.21,"N45860":0.37,"FV2":0.62}  # FV2 = coppia N45856 int+est

PRZ = {"712010":0.696,"V40014":2.659,"V40022":0.607,"V43017":1.768,"V46005":0.334,
       "V46028":1.206,"V51015":1.181,"V52014":1.517,"V52055":0.469,"V62008":1.225}
G_VETRO = 0.559+1.335   # 809119+809122 €/ml
G = {"V03011":0.445,"V03026":1.491,"V03027":0.704,"V09049":0.559}

def lin(expr):
    """'L-42' -> (cL,cH,cost) in mm; supporta L/2, H/2."""
    e = expr.replace(" ","")
    cL=cH=c=0.0
    for m in re.finditer(r'([+-]?)(L|H)(/2)?|([+-]?\d+(?:\.\d+)?)', e):
        s = -1 if m.group(1)=='-' else 1
        if m.group(2):
            v = 0.5 if m.group(3) else 1.0
            if m.group(2)=='L': cL += s*v
            else: cH += s*v
        elif m.group(4):
            c += float(m.group(4))
    return cL,cH,c

def kg_coef(profili):
    kL=kH=kC=0.0
    for art,pz,mis in profili:
        cL,cH,c = lin(mis); p = PESI[art]/1000.0
        kL+=pz*p*cL; kH+=pz*p*cH; kC+=pz*p*c
    return kC,kL,kH

def g_coef(guarn):
    gL=gH=gC=0.0
    for prezzo,mis in guarn:
        cL,cH,c = lin(mis); p = prezzo/1000.0
        gL+=p*cL; gH+=p*cH; gC+=p*c
    return gC,gL,gH

TIP = {
 "FISSO":{"nome":"TELAIO FISSO (TF75)","ore":1+1/3.,
   "profili":[("B23008C",2,"L"),("B23008C",2,"H"),("FV2",2,"L-54"),("FV2",2,"H-82")],
   "acc":[("V40022",4),("V43017",4),("V46028",4)],
   "guarn":[(G_VETRO,"2L+2H")],
   "L":(500,3000),"H":(600,2700)},
 "F1":{"nome":"FINESTRA 1 ANTA (1A75)","ore":8/3.,
   "profili":[("B23008C",2,"L"),("B23008C",2,"H"),("B23122C",2,"L-42"),("B23122C",2,"H-42"),
              ("N45860",2,"L-140"),("N45860",2,"H-168")],
   "acc":[("V40014",4),("V40022",8),("V43017",4),("V46005",4),("V46028",4),("V62008",4)],
   "guarn":[(G_VETRO,"2L+2H"),(G["V09049"],"2L+2H")],
   "L":(500,1200),"H":(500,2000)},
 "F2":{"nome":"FINESTRA 2 ANTE (2A75)","ore":13/3.,
   "profili":[("B23008C",2,"L"),("B23008C",2,"H"),("B23100C",1,"H-74"),("B23122C",4,"L/2-9"),
              ("B23122C",3,"H-42"),("N23637C",1,"H-105"),("N45860",4,"L/2-107"),("N45860",4,"H-168")],
   "acc":[("V40014",8),("V40022",12),("V43017",4),("V46005",8),("V46028",4),
          ("V52014",1),("V52055",1),("V62008",8)],
   "guarn":[(G_VETRO,"2L+4H"),(G["V03027"],"H"),(G["V09049"],"2L+5H")],
   "L":(800,2000),"H":(500,2000)},
 "PF1":{"nome":"PORTAFINESTRA 1 ANTA (PB175)","ore":8/3.,
   "profili":[("B23008C",1,"L"),("B23008C",2,"H"),("B23122C",2,"L-42"),("B23122C",2,"H-29.5"),
              ("B23401",1,"L-46"),("K50",1,"L-111"),("N45860",2,"L-140"),("N45860",2,"H-156")],
   "acc":[("712010",1),("V40014",4),("V40022",6),("V43017",2),("V46005",4),("V46028",2),
          ("V51015",2),("V62008",4)],
   "guarn":[(G_VETRO,"2L+2H"),(G["V03026"],"L"),(G["V09049"],"2L+2H")],
   "L":(500,1200),"H":(1900,2700)},
 "PF2":{"nome":"PORTAFINESTRA 2 ANTE (PB275)","ore":13/3.,
   "profili":[("B23008C",1,"L"),("B23008C",2,"H"),("B23100C",1,"H-61.5"),("B23122C",4,"L/2-9"),
              ("B23122C",3,"H-29.5"),("B23401",1,"L-46"),("K50",1,"L/2-78"),("K50",1,"L/2-46.5"),
              ("N23637C",1,"H-92.5"),("N45860",4,"L/2-107"),("N45860",4,"H-155.5")],
   "acc":[("712010",2),("V40014",8),("V40022",10),("V43017",2),("V46005",8),("V46028",2),
          ("V51015",2),("V52014",1),("V52055",1),("V62008",8)],
   "guarn":[(G_VETRO,"2L+4H"),(G["V03026"],"L"),(G["V03027"],"H"),(G["V09049"],"2L+5H")],
   "L":(800,1800),"H":(1900,2700)},
}


# Ferramenta: (descrizione, codice Maico, q.tà, prezzo manuale).
# Il prezzo viene da ferramenta.csv tramite il codice; il prezzo manuale vale solo
# se il codice non è nel netto (es. martellina 1033). Codice None = voce da inserire.
FERR_ANTA = [
    ("Martellina DK",                       "1033",   1, 5.50),   # non nel netto 2025
    ("Cremonese Multi Matic GR1590",        "201745", 1, None),
    ("Chiusura centrale MM",                "201752", 1, None),
    ("Movimento angolare MM",               "222201", 1, None),
    ("Movimento angolare prolungabile",     "222209", 1, None),
    ("Scontro fungo scost.9",               "356361", 2, None),
    ("Scontro nottolino",                   "355866", 4, None),   # non nel netto 2025
    ("Cerniere a vista (set anta)",         None,     1, None),
    ("Forbice a vista + braccio",           None,     1, None),
]
FERR_SEMIFISSA = [
    ("Asta a leva MM anta semifissa",       "221911", 1, None),
    ("Movimento angolare prolungabile",     "222205", 1, None),
    ("Scontri anta semifissa",              None,     1, None),
]
FERR = {"FISSO": [], "F1": FERR_ANTA, "PF1": FERR_ANTA,
        "F2": FERR_ANTA + FERR_SEMIFISSA, "PF2": FERR_ANTA + FERR_SEMIFISSA}

def righe_ferr(key):
    """-> [(descrizione, q.tà, prezzo €/pz, fonte)] con i prezzi risolti da ferramenta.csv."""
    out = []
    for desc, cod, q, manuale in FERR[key]:
        if cod is None:
            out.append((f"{desc} — DA INSERIRE", q, 0.0, "da inserire"))
        elif cod in NETTO:
            out.append((f"{desc} ({cod})", q, round(NETTO[cod], 4), "netto 2025"))
        elif manuale is not None:
            out.append((f"{desc} ({cod}) — non nel netto 2025", q, manuale, "manuale"))
        else:
            out.append((f"{desc} ({cod}) — NON a listino", q, 0.0, "da inserire"))
    return out

ARIAL = Font(name="Arial", size=10)
BOLD  = Font(name="Arial", size=10, bold=True)
TITLE = Font(name="Arial", size=12, bold=True)
YELL  = PatternFill("solid", fgColor="FFFF00")
GREY  = PatternFill("solid", fgColor="DDDDDD")
BLUE  = Font(name="Arial", size=10, color="0000FF")

def scrivi(nome_file, key):
    t = TIP[key]
    wb = Workbook()

    # ---- Parametri ----
    wp = wb.create_sheet("Parametri")
    par = [("Prezzo profili €/kg (10820 CAT.B +ADD — RAL 7016)", PARAM["eur_kg"], "0.00"),
           ("Sconto profili su listino AluK", PARAM["sc_prof"], "0%"),
           ("Sconto accessori/guarnizioni su listino AluK", PARAM["sc_acc"], "0%"),
           ("Sfrido", PARAM["sfrido"], "0%"),
           ("Tariffa oraria manodopera €/h", PARAM["eur_h"], "0.00"),
           ("Ricarico su costo totale", PARAM["ricarico"], "0%")]
    for i,(lab,val,fmt) in enumerate(par, start=1):
        a = wp.cell(row=i, column=1, value=lab); a.font = ARIAL
        b = wp.cell(row=i, column=2, value=val); b.font = BLUE
        b.number_format = fmt; b.fill = YELL
    wp.cell(row=8, column=1, value="Celle gialle = valori modificabili: tutte le griglie si ricalcolano.").font = ARIAL
    wp.cell(row=9, column=1, value="Listino AluK decorrenza 15-06-2026. Ferramenta: prezzi nel foglio dedicato.").font = ARIAL
    wp.column_dimensions['A'].width = 52; wp.column_dimensions['B'].width = 12

    # ---- Coefficienti ----
    kC,kL,kH = kg_coef(t["profili"])
    gC,gL,gH = g_coef(t["guarn"])
    accTot = sum(PRZ[a]*q for a,q in t["acc"])
    wc = wb.create_sheet("Coefficienti")
    rows = [("Peso alluminio costante (kg)", kC), ("Peso per mm di L (kg/mm)", kL),
            ("Peso per mm di H (kg/mm)", kH), ("Guarnizioni costante (€ listino)", gC),
            ("Guarnizioni per mm di L (€/mm)", gL), ("Guarnizioni per mm di H (€/mm)", gH),
            ("Accessori totale (€ listino)", accTot), ("Ore manodopera", t["ore"])]
    for i,(lab,val) in enumerate(rows, start=1):
        wc.cell(row=i, column=1, value=lab).font = ARIAL
        c = wc.cell(row=i, column=2, value=round(val,8)); c.font = ARIAL
    note = ["Derivati dalle distinte catalogo AluK C75S sez. 8 e pesi kg/m catalogo v3.",
            "Assunzioni: supporti vetro V62008 = 4 per vetro; mascherine V51015 = 2 pz;",
            "fermavetro battenti N45860 (0,37 kg/m), fisso coppia N45856 (0,62 kg/m);",
            "squadrette V40022/V40037 prezzate come V40022 (0,607 €).",
            "Manodopera: 1h telaio + 1h/anta + 20' ferramenta/anta + 20'/vetro.",
            "Prezzi unitari accessori e guarnizioni dal listino AluK 15-06-2026 (pre-sconto)."]
    for i,n in enumerate(note, start=10):
        wc.cell(row=i, column=1, value=n).font = ARIAL
    wc.column_dimensions['A'].width = 46


    # ---- Ferramenta ----
    wf = wb.create_sheet("Ferramenta")
    for col,lab in enumerate(["Componente","Q.tà","Prezzo €/pz","Subtotale €","Fonte"], start=1):
        c = wf.cell(row=1, column=col, value=lab); c.font = BOLD; c.fill = GREY
    fr = righe_ferr(key)
    for i,(desc,q,pr,fonte) in enumerate(fr, start=2):
        wf.cell(row=i, column=1, value=desc).font = ARIAL
        wf.cell(row=i, column=5, value=fonte).font = ARIAL
        qc = wf.cell(row=i, column=2, value=q); qc.font = BLUE; qc.fill = YELL
        pc = wf.cell(row=i, column=3, value=pr); pc.font = BLUE; pc.fill = YELL
        pc.number_format = "0.00"
        sc = wf.cell(row=i, column=4, value=f"=B{i}*C{i}"); sc.font = ARIAL
        sc.number_format = "0.00"
    tot_row = 2+len(fr)
    wf.cell(row=tot_row, column=1, value="TOTALE FERRAMENTA").font = BOLD
    if fr:
        tc = wf.cell(row=tot_row, column=4, value=f"=SUM(D2:D{tot_row-1})")
    else:
        wf.cell(row=2, column=1, value="Nessuna ferramenta (telaio fisso)").font = ARIAL
        tc = wf.cell(row=tot_row, column=4, value=0)
    tc.font = BOLD; tc.number_format = "0.00"
    wf.cell(row=tot_row+2, column=1,
            value="Celle gialle modificabili. Prezzi a 0 = da inserire: il listino li ignora finché vuoti.").font = ARIAL
    wf.column_dimensions['A'].width = 44; wf.column_dimensions['E'].width = 12
    FT = f"Ferramenta!$D${tot_row}"
    ferr_tot = sum(q*pr for _,q,pr,_ in fr)

    # ---- Prezzo (griglie) ----
    ws = wb.active; ws.title = "Prezzo"
    L0,L1 = t["L"]; H0,H1 = t["H"]
    Ls = list(range(L0, L1+1, 100)); Hs = list(range(H0, H1+1, 100))
    P = "Parametri!$B$"; C = "Coefficienti!$B$"

    def griglia(r0, titolo, formula):
        ws.cell(row=r0, column=1, value=titolo).font = TITLE
        hd = ws.cell(row=r0+1, column=1, value="H/L"); hd.font = BOLD; hd.fill = GREY
        for j,Lv in enumerate(Ls):
            c = ws.cell(row=r0+1, column=2+j, value=Lv); c.font = BOLD; c.fill = GREY
            c.alignment = Alignment(horizontal="center")
        for i,Hv in enumerate(Hs):
            c = ws.cell(row=r0+2+i, column=1, value=Hv); c.font = BOLD; c.fill = GREY
        for i in range(len(Hs)):
            for j in range(len(Ls)):
                cell = ws.cell(row=r0+2+i, column=2+j)
                Lref = f"{get_column_letter(2+j)}${r0+1}"
                Href = f"$A{r0+2+i}"
                cell.value = formula(Lref, Href)
                cell.font = ARIAL; cell.number_format = "0.00"
        return r0+2+len(Hs)

    def f_costo(Lr, Hr):
        kg   = f"({C}1+{C}2*{Lr}+{C}3*{Hr})"
        gua  = f"({C}4+{C}5*{Lr}+{C}6*{Hr})"
        return (f"=ROUND(({kg}*{P}1*(1-{P}2)+({gua}+{C}7)*(1-{P}3))*(1+{P}4)"
                f"+{FT}+{C}8*{P}5,2)")

    r = griglia(1, f"LISTINO — {t['nome']} — C75S SENZA VETRO — RAL 7016 (costo +213%)",
                lambda Lr,Hr: f"={f_costo(Lr,Hr)[1:]}*(1+{P}6)")
    # arrotondo il listino a 2 decimali avvolgendo
    # (riscrivo le celle con ROUND esterno)
    r1_first = 3
    for i in range(len(Hs)):
        for j in range(len(Ls)):
            cell = ws.cell(row=r1_first+i, column=2+j)
            cell.value = f"=ROUND({cell.value[1:]},2)"

    griglia(r+2, "COSTO SERRAMENTO (materiale scontato + sfrido + manodopera)", f_costo)

    ws.column_dimensions['A'].width = 8
    for j in range(len(Ls)):
        ws.column_dimensions[get_column_letter(2+j)].width = 9

    wb.save(nome_file)
    return kC,kL,kH,gC,gL,gH,accTot,t["ore"],ferr_tot,Ls,Hs

check = {}
for key in ["FISSO","F1","F2","PF1","PF2"]:
    out = f"{key}_SENZA_VETRO.xlsx"
    res = scrivi(out, key)
    check[key] = res[:9]
    print(key, "->", out)

# verifica: F1 1000x1500 con i parametri di default, stessa formula delle griglie
# (materiale scontato + sfrido, + ferramenta, + manodopera; listino = costo arrotondato x ricarico)
kC,kL,kH,gC,gL,gH,acc,ore,ferr = check["F1"]
P = PARAM
L,H = 1000,1500
kg  = kC+kL*L+kH*H
gua = gC+gL*L+gH*H
costo = round((kg*P["eur_kg"]*(1-P["sc_prof"]) + (gua+acc)*(1-P["sc_acc"]))*(1+P["sfrido"])
              + ferr + ore*P["eur_h"], 2)
listino = round(costo*(1+P["ricarico"]), 2)
print(f"\nF1 1000x1500: kg={kg:.3f} guarn€={gua:.2f} acc€={acc:.2f} ferr€={ferr:.2f} ore={ore:.2f}")
print(f"costo atteso={costo:.2f}  listino atteso={listino:.2f}")
