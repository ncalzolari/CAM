import math,glob,os,json,sys
def parse(fn):
    L=open(fn,encoding='latin1').read().splitlines()
    ents=[];i=0
    while i<len(L):
        if L[i].strip()=='0' and i+1<len(L) and L[i+1].strip() in('LINE','ARC','CIRCLE','LWPOLYLINE','POLYLINE'):
            typ=L[i+1].strip();d={};i+=2;pts=[]
            while i<len(L) and L[i].strip()!='0':
                c=L[i].strip();v=L[i+1].strip();i+=2
                if typ=='LWPOLYLINE' and c in('10','20'):
                    if c=='10': pts.append([float(v),None])
                    else: pts[-1][1]=float(v)
                else: d[c]=v
            ents.append((typ,d,pts))
        else: i+=1
    return ents
def bbox_path(ents):
    xs=[];ys=[];path=[]
    def P(x,y): xs.append(x);ys.append(y)
    for typ,d,pts in ents:
        if typ=='LINE':
            x1,y1,x2,y2=[float(d[k]) for k in('10','20','11','21')]
            P(x1,y1);P(x2,y2);path.append(('L',x1,y1,x2,y2))
        elif typ=='ARC':
            cx,cy,r=float(d['10']),float(d['20']),float(d['40']);a1,a2=float(d['50']),float(d['51'])
            if a2<a1: a2+=360
            x1,y1=cx+r*math.cos(math.radians(a1)),cy+r*math.sin(math.radians(a1))
            x2,y2=cx+r*math.cos(math.radians(a2)),cy+r*math.sin(math.radians(a2))
            P(x1,y1);P(x2,y2)
            # sample bbox
            a=a1
            while a<a2:
                P(cx+r*math.cos(math.radians(a)),cy+r*math.sin(math.radians(a)));a+=5
            path.append(('A',x1,y1,x2,y2,r,1 if (a2-a1)>180 else 0))
        elif typ=='CIRCLE':
            cx,cy,r=float(d['10']),float(d['20']),float(d['40']);P(cx-r,cy-r);P(cx+r,cy+r)
            path.append(('C',cx,cy,r))
        elif typ=='LWPOLYLINE':
            for a,b in zip(pts,pts[1:]): P(*a);P(*b);path.append(('L',a[0],a[1],b[0],b[1]))
    return min(xs),min(ys),max(xs),max(ys),path
def svg(fn):
    ents=parse(fn);x0,y0,x1,y1,path=bbox_path(ents)
    # flip y (DXF y up -> svg y down), translate to origin
    f=lambda x,y:(round(x-x0,2),round(y1-y,2))
    out=[]
    for p in path:
        if p[0]=='L':
            a=f(p[1],p[2]);b=f(p[3],p[4]);out.append(f"M{a[0]} {a[1]}L{b[0]} {b[1]}")
        elif p[0]=='A':
            a=f(p[1],p[2]);b=f(p[3],p[4]);out.append(f"M{a[0]} {a[1]}A{p[5]} {p[5]} 0 {p[6]} 0 {b[0]} {b[1]}")
        elif p[0]=='C':
            c=f(p[1],p[2]);r=p[3];out.append(f"M{c[0]-r} {c[1]}a{r} {r} 0 1 0 {2*r} 0a{r} {r} 0 1 0 {-2*r} 0")
    return dict(d=''.join(out),w=round(x1-x0,1),h=round(y1-y0,1),x=0,y=0,n=len(path))
if __name__=='__main__':
    res={}
    ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for fn in sorted(glob.glob(os.path.join(ROOT,'data','dxf','D67','*.DXF'))+glob.glob(os.path.join(ROOT,'data','dxf','D77','*.DXF'))):
        k=os.path.basename(fn)[:-4]; s=svg(fn); res[k]=s; print(k,s['w'],s['h'],s['n'],len(s['d']))
    json.dump(res,open(os.path.join(ROOT,'data','dxf_sez_porte.json'),'w'))
