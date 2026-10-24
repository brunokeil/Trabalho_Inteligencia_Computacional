#!/usr/bin/env python3
"""Validador independente: lê texto/JSON, recompõe todas as medidas com Decimal."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import json,sys

ROOT=Path(__file__).resolve().parents[1]
def read_instance(path):
    lines=[s.strip() for s in Path(path).read_text().splitlines() if s.strip() and not s.lstrip().startswith('#')]
    n=int(lines[0].split(':')[1]);m=int(lines[1].split(':')[1]);assert len(lines)==2+2*n+m
    candidates=[[v.strip() for v in s.split(',')] for s in lines[2:2+n]]
    schools=[[v.strip() for v in s.split(',')] for s in lines[2+n:2+n+m]]
    distances=[[Decimal(v.strip()) for v in s.split(',')] for s in lines[2+n+m:]]
    assert all(len(c)==5 for c in candidates) and all(len(s)==6 for s in schools)
    assert all(len(row)==m and all(x>=0 and x.is_finite() for x in row) for row in distances)
    assert len(set(c[0] for c in candidates))==n and len(set(s[0] for s in schools))==m
    caps=[]
    for s in schools:
        rooms=list(map(int,s[5].split(';')));assert len(rooms)==int(s[4]) and all(x>0 for x in rooms);caps.append(sum(rooms))
    return candidates,schools,caps,distances

def validate(path):
    data=json.loads(Path(path).read_text(),parse_float=Decimal)
    source=Path(data['instance'])
    if not source.exists():source=ROOT/'entrega'/data['name']
    cs,ss,caps,ds=read_instance(source);n,m=len(cs),len(ss);names=list(dict.fromkeys(c[2] for c in cs));T=len(names);K=data['K'];assert K in (1,2)
    assert data['candidateIds']==[c[0] for c in cs] and data['schoolIds']==[s[0] for s in ss] and data['typeNames']==names and data['capacities']==caps
    quota=data['certificate_quotas'];assert len(quota)==m and all(len(row)==T for row in quota)
    assert all(all(type(x) is int and x>=0 for x in row) and sum(x>0 for x in row)<=K and sum(row)<=caps[j] for j,row in enumerate(quota))
    demand=Counter(c[2] for c in cs)
    assert all(sum(row[t] for row in quota)<=demand[names[t]] for t in range(T))
    assert sum(map(sum,quota))==data['maximum_assigned']
    assert data['feasibility']==('feasible' if data['maximum_assigned']==n else 'infeasible')
    for run in data['runs']:
        for which in ('initial','final'):
            s=run[which];a=s['assign'];slots=s['typeSlots'];assert len(a)==n and len(slots)==m
            assert all(type(mask) is int and 0<=mask<(1<<T) and bin(mask).count('1')<=K for mask in slots)
            load=[0]*m;bytype=[[0]*T for _ in range(m)];distance=Decimal(0);missing=bad=0
            for i,j in enumerate(a):
                assert type(j) is int and -1<=j<m
                if j<0:missing+=1;continue
                t=names.index(cs[i][2]);load[j]+=1;bytype[j][t]+=1;distance+=ds[i][j];bad+=not bool(slots[j]&(1<<t))
            overflow=sum(max(0,load[j]-caps[j]) for j in range(m))
            assert load==s['load'] and bytype==s['loadByType'] and distance==s['distance'],(path,run['seed'],which,'cost/load mismatch')
            assert missing==s['unassigned'] and bad==s['incompatible'] and overflow==s['overflow']
            assert s['feasible']==(missing+bad+overflow==0)
            objective=distance+data['lambda_initial']*overflow+data['mu']*(missing+bad)
            assert abs(objective-s['objective'])<Decimal('.000001')
            assert all(abs(Decimal(load[j])/caps[j]-s['occupancy'][j])<Decimal('1e-12') for j in range(m))
            assert overflow==bad==0 and missing==n-data['maximum_assigned']
        assert run['final']['distance']<=run['initial']['distance']
        curve=run['convergence'];assert all(curve[i][1]<=curve[i-1][1] for i in range(1,len(curve)))
        if curve:assert curve[-1][1]==run['final']['distance']
    best=data['runs'][data['best_run']]['final'];assert best['distance']==min(r['final']['distance'] for r in data['runs'])
    return len(data['runs'])*2

if __name__=='__main__':
    total=0
    for name in sys.argv[1:]:
        count=validate(name);total+=count;print(f'OK {name}: {count} solucoes')
    if not sys.argv[1:]:raise SystemExit('Uso: python3 scripts/validar.py resultados/*.json')
    print(f'Total: {total} solucoes verificadas independentemente')
