#!/usr/bin/env python3
"""Matriz experimental reproduzível: 4 instâncias x 2 K x 11 configurações x 30 seeds."""
import argparse,csv,hashlib,json,platform,statistics,subprocess,sys,time,os
from pathlib import Path
from validar import validate
ROOT=Path(__file__).resolve().parents[1]
CONFIGS=[
 ('vnd_a0',{'metodo':'vnd','alpha':0}),
 ('vnd_a03',{'metodo':'vnd','alpha':.3}),
 ('vnd_a07',{'metodo':'vnd','alpha':.7}),
 ('vnd_first',{'metodo':'vnd','alpha':.3,'ls':'first'}),
 ('n1',{'metodo':'vnd','alpha':.3,'viz':'1'}),
 ('n2',{'metodo':'vnd','alpha':.3,'viz':'2'}),
 ('n3',{'metodo':'vnd','alpha':.3,'viz':'3'}),
 ('tabu_a03',{'metodo':'tabu','alpha':.3}),
 ('tabu_t3',{'metodo':'tabu','alpha':.3,'tmin':3,'tmax':3}),
 ('tabu_t10',{'metodo':'tabu','alpha':.3,'tmin':10,'tmax':10}),
 ('tabu_t10_20',{'metodo':'tabu','alpha':.3,'tmin':10,'tmax':20}),
]

def summarize(out):
    summary=[];best={};allrows=[]
    for path in sorted(out.glob('*__*.json')):
        d=json.loads(path.read_text());config=path.stem.split('__')[-1];rows=list(csv.DictReader(path.with_suffix('.csv').open()))
        finals=[r['final']['distance'] for r in d['runs']];initial=[r['initial']['distance'] for r in d['runs']];timing=[r['search_seconds'] for r in d['runs']];total=[r['construction_seconds']+r['search_seconds'] for r in d['runs']]
        row={'instance':d['name'],'K':d['K'],'status':d['feasibility'],'config':config,'runs':len(finals),'initial_mean':statistics.mean(initial),'min':min(finals),'mean':statistics.mean(finals),'std':statistics.stdev(finals) if len(finals)>1 else 0,'max':max(finals),'improvement_mean':statistics.mean(a-b for a,b in zip(initial,finals)),'improvement_pct_mean':statistics.mean(100*(a-b)/a if a else 0 for a,b in zip(initial,finals)),'search_seconds_mean':statistics.mean(timing),'total_seconds_mean':statistics.mean(total),'precheck_seconds':d['precheck_seconds'],'iterations_mean':statistics.mean(r['iterations'] for r in d['runs']),'unassigned':d['runs'][0]['final']['unassigned'],'fallback_runs':sum(r['fallback'] for r in d['runs']),'best_seed':d['runs'][d['best_run']]['seed']}
        summary.append(row)
        for r in rows:r['config']=config;allrows.append(r)
        key=(d['name'],d['K']);candidate=d['runs'][d['best_run']]
        if key not in best or candidate['final']['distance']<best[key][1]['final']['distance']:best[key]=(d,candidate)
    for name,rows in [('resumo.csv',summary),('execucoes.csv',allrows)]:
        with (out/name).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'melhores').mkdir(exist_ok=True)
    for (name,K),(d,run) in best.items():
        d=dict(d);d['runs']=[run];d['best_run']=0;p=out/'melhores'/f'{Path(name).stem}_K{K}.json';p.write_text(json.dumps(d,indent=2));validate(p)
    text=['# Resultados experimentais','',f'{len(summary)} configurações; {len(allrows)} execuções. Desvio padrão amostral. Tempos em segundos; distâncias em km. Casos inviáveis mantêm o número mínimo comprovado de não alocados.','', '| Instância | K | Configuração | Estado | Inicial média | Final média ± dp | Mínimo | Busca média (s) | Não alocados |','|---|---:|---|---|---:|---:|---:|---:|---:|']
    for r in summary:text.append(f"| {r['instance']} | {r['K']} | {r['config']} | {r['status']} | {r['initial_mean']:.4f} | {r['mean']:.4f} ± {r['std']:.4f} | {r['min']:.4f} | {r['search_seconds_mean']:.4f} | {r['unassigned']} |")
    (out/'resumo.md').write_text('\n'.join(text)+'\n')
    return summary

def plots(out):
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(11,7))
    for ax,name in zip(axes.flat,['Modelo_de_Instancia','instancia2','instancia_A','instancia_B']):
        groups={c:json.loads((out/f'{name}__K2__{c}.json').read_text()) for c in ('vnd_a03','tabu_a03')}
        end=max(r['iterations'] for d in groups.values() for r in d['runs'])
        for config,label in [('vnd_a03','VND'),('tabu_a03','Tabu')]:
            runs=groups[config]['runs'];curves=[]
            for r in runs:
                by={int(v[0]):v[1] for v in r['convergence']};last=r['initial']['distance'];curve=[]
                for it in range(end+1):last=by.get(it,last);curve.append(last)
                curves.append(curve)
            ax.plot(range(end+1),[statistics.mean(c[i] for c in curves) for i in range(end+1)],label=label)
        ax.set_title(name+' / K=2');ax.set_xlabel('Iterações');ax.set_ylabel('Melhor distância (km)');ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'convergencia.pdf');fig.savefig(out/'convergencia.png',dpi=180);plt.close(fig)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runs',type=int,default=30);ap.add_argument('--out',type=Path,default=ROOT/'resultados');ap.add_argument('--max-iter',type=int,default=150);ap.add_argument('--sem-melhora',type=int,default=50);ap.add_argument('--resumo-only',action='store_true');args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    if args.resumo_only:summarize(out);plots(out);return
    fingerprint=hashlib.sha256((ROOT/'alocacao').read_bytes()).hexdigest()
    manifest={'platform':platform.platform(),'processor':platform.processor(),'python':sys.version,'binary_sha256':fingerprint,'runs':args.runs,'max_iter':args.max_iter,'stagnation':args.sem_melhora,'seeds':list(range(1,args.runs+1)),'configs':CONFIGS,'instances':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'entrega').glob('*.txt')) if p.stem in ('Modelo_de_Instancia','instancia2','instancia_A','instancia_B')}}
    old=out/'manifest.json'
    if old.exists() and json.loads(old.read_text())!=json.loads(json.dumps(manifest)):raise SystemExit('Manifesto mudou: escolha outra pasta para não misturar experimentos.')
    old.write_text(json.dumps(manifest,indent=2));start=time.perf_counter();completed=0
    for name in ('Modelo_de_Instancia','instancia2','instancia_A','instancia_B'):
        for K in (1,2):
            for config,options in CONFIGS:
                path=out/f'{name}__K{K}__{config}.json';cmd=[str(ROOT/'alocacao'),'--instancia',str(ROOT/'entrega'/f'{name}.txt'),'--tipos-por-escola',str(K),'--runs',str(args.runs),'--seed','1','--max-iter',str(args.max_iter),'--sem-melhora',str(args.sem_melhora),'--n3-periodo','15','--n3-amostras','4','--saida',str(path)]
                for k,v in options.items():cmd+=['--'+k,str(v)]
                if not path.exists():
                    with path.with_suffix('.console.txt').open('w') as log:
                        log.write('COMMAND '+json.dumps(cmd)+'\n');log.flush();subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
                validate(path);completed+=1;print(f'{completed}/88 validado {name} K={K} {config}; elapsed={time.perf_counter()-start:.1f}s',flush=True)
    summarize(out);plots(out);print('Concluído: tabelas, melhores soluções e curvas geradas.',flush=True)
if __name__=='__main__':main()
