import zipfile,sys,os,re,struct,glob
def info(p):
    z=zipfile.ZipFile(p)
    names=z.namelist()
    inner=[n for n in names if n.lower().endswith('.ldt')]
    d=z.read(inner[0]) if inner else b''
    serie=[n[:-6] for n in names if n.endswith('.SERIE')]
    dxf=[n for n in names if n.upper().endswith('.DXF')]
    desc=d[10:10+40].split(b'\0')[0].decode('latin1') if d else ''
    s=d[50:50+20].split(b'\0')[0].decode('latin1') if d else ''
    prof=d[70:70+20].split(b'\0')[0].decode('latin1') if d else ''
    m=re.search(rb'CREATA IL [0-9\-]+',d); 
    ini=z.read('LDT.ini').decode('latin1') if 'LDT.ini' in names else ''
    tools=re.findall(r'^(T\d+) = 1',ini,re.M)
    steps=re.findall(rb'(F\d\d\.LAV|[A-Z]\d\d\.[A-Z]{3})',d)
    return dict(file=p,desc=desc,serie=s,prof=prof,date=(m.group(0).decode() if m else ''),dxf=dxf,tools=tools,size=len(d),steps=sorted(set(x.decode() for x in steps)))
if __name__=='__main__':
    for p in sorted(glob.glob(sys.argv[1])):
        try: i=info(p); print(f"{os.path.basename(p):22} {i['serie']:8} {i['prof']:10} {i['desc']:40} {i['date']:22} {i['tools']} {i['steps']} {i['size']}")
        except Exception as e: print(p,'ERR',e)
