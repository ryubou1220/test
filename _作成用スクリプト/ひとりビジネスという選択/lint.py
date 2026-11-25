import sys
LIM={"COVER":[30,10,22,20,40],"BUL":[20,15,[24]],"GRID4":[20,28,11,24,11,24,11,24,11,24],
 "SEC":[8,2,11,16],"ROWS3S":[20,28,2,8,26,2,8,26,2,8,26],"ROWS3":[20,2,8,26,2,8,26,2,8,26],
 "SUM":[20,2,6,14,2,6,14,2,6,14,22],"NEXT":[6,10,[22],40]}
def lint(L):
    bad=0
    for l in L:
        for i,s in enumerate(l["slides"],1):
            for v,lim in zip(s["t"],LIM[s["type"]]):
                vs=v if isinstance(v,list) else [v]; lm=lim[0] if isinstance(lim,list) else lim
                for x in vs:
                    if len(x)>lm: bad+=1; print(f"L{l['no']} s{i} {s['type']} {len(x)}>{lm}: {x}")
    return bad
