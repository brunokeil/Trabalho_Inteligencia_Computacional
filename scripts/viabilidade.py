#!/usr/bin/env python3
"""Certificado agregado: maximiza atendimento, sem usar distâncias.
Entrada: m T K, capacidades e demandas. Saída: ótimo e matriz inteira x[j,t].
Somente status ótimo autoriza afirmar inviabilidade; timeout é erro explícito.
"""
import sys
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint

def solve(caps, dem, K):
    m,T=len(caps),len(dem);q=m*T
    rows=[];lb=[];ub=[]
    for t in range(T):
        r=np.zeros(2*q);r[q+t::T]=1;rows.append(r);lb.append(0);ub.append(dem[t])
    for j in range(m):
        r=np.zeros(2*q);r[j*T:(j+1)*T]=1;rows.append(r);lb.append(0);ub.append(K)
        r=np.zeros(2*q);r[q+j*T:q+(j+1)*T]=1;rows.append(r);lb.append(0);ub.append(caps[j])
        for t in range(T):
            r=np.zeros(2*q);r[q+j*T+t]=1;r[j*T+t]=-caps[j];rows.append(r);lb.append(-np.inf);ub.append(0)
    res=milp(np.r_[np.zeros(q),-np.ones(q)],integrality=np.r_[np.ones(q),np.zeros(q)],
        bounds=Bounds(np.zeros(2*q),np.r_[np.ones(q),np.repeat(caps,T)]),
        constraints=LinearConstraint(np.array(rows),lb,ub),options={'time_limit':120,'mip_rel_gap':0})
    if res.status!=0:raise RuntimeError('checagem inconclusiva: '+res.message)
    x=np.rint(res.x[q:]).astype(int).reshape(m,T)
    assert (x>=0).all() and (x.sum(0)<=dem).all() and (x.sum(1)<=caps).all() and ((x>0).sum(1)<=K).all()
    assert abs(x.sum()+res.fun)<1e-5
    return x

if __name__=='__main__':
    a=list(map(int,open(sys.argv[1]).read().split()));m,T,K=a[:3];caps=a[3:3+m];dem=a[3+m:]
    assert K in (1,2) and len(dem)==T
    x=solve(np.array(caps),np.array(dem),K)
    with open(sys.argv[2],'w') as f:
        f.write(f'{int(x.sum())} {m} {T} {K}\n')
        for row in x:f.write(' '.join(map(str,row))+'\n')
