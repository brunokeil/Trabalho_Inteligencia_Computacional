#!/usr/bin/env python3
"""Gera tabelas, figuras e apresentação offline exclusivamente da campanha final."""
import csv, hashlib, json, os, platform, statistics, sys
from pathlib import Path
from validar import validate
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'resultados'
DOC=ROOT/'docs'

def tex(s):
    return str(s).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
def num(x,d=2):return f'{x:.{d}f}'.replace('.',',')
def label(name):return Path(name).stem.replace('Instancia','I').replace('instancia','I').replace('_',' ')

def collect():
    rows=[];data={};solutions=0
    binary_hash=hashlib.sha256((ROOT/'alocacao').read_bytes()).hexdigest()
    for method in ('vnd','tabu'):
        folder=OUT/f'final_{method}'
        manifest=json.loads((folder/'manifest.json').read_text())
        assert manifest['binary_sha256']==binary_hash, 'Campanha não corresponde ao executável atual'
        files=sorted(folder.glob('*__K1__*.json'))
        assert len(files)==28
        assert {p.name.split('__')[0]+'.txt' for p in files}==set(manifest['instances'])
        for p in files:
            d=json.loads(p.read_text());solutions+=validate(p)
            assert d['K']==1 and len(d['runs'])==30 and d['method']==method
            assert [r['seed'] for r in d['runs']]==list(range(1,31))
            source=ROOT/'instances/preparadas'/d['name']
            assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['instances'][d['name']]
            runs=d['runs'];fin=[r['final']['distance'] for r in runs];ini=[r['initial']['distance'] for r in runs]
            best=runs[d['best_run']]
            r={'instance':d['name'],'method':method,'n':len(d['candidateIds']),'m':len(d['schoolIds']),
               'capacity':sum(d['capacities']),'unassigned':runs[0]['final']['unassigned'],
               'initial':statistics.mean(ini),'final':statistics.mean(fin),'std':statistics.stdev(fin),
               'min':min(fin),'max':max(fin),
               'improvement_pct':statistics.mean(100*(a-b)/a if a else 0 for a,b in zip(ini,fin)),
               'construction_s':statistics.mean(r['construction_seconds'] for r in runs),
               'search_s':statistics.mean(r['search_seconds'] for r in runs),
               'schools':statistics.mean(sum(v>0 for v in r['final']['load']) for r in runs),
               'precheck_s':d['precheck_seconds'],'fallback':sum(r['fallback'] for r in runs),
               'best_seed':best['seed'],'best_load':best['final']['load'],
               'best_types':best['final']['loadByType'],'type_names':d['typeNames'],
               'capacities':d['capacities'],'school_ids':d['schoolIds'],
               'max_iter_runs':sum(r['iterations']==150 for r in runs)}
            rows.append(r);data[(d['name'],method)]=d
    with (OUT/'final_resumo.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    metadata={'platform':platform.platform(),'python':sys.version,'binary_sha256':binary_hash,
              'campaigns':['final_vnd','final_tabu'],'instances':28,'runs':1680,'validated_solutions':solutions,
              'scope':'K=1, um tipo por escola','input_audit':'instances/auditoria_atual.csv'}
    (OUT/'final_validacao.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False))
    return rows,data,metadata

def tables(rows,data,meta):
    idx={(r['instance'],r['method']):r for r in rows}
    names=sorted({r['instance'] for r in rows})
    feasible=[n for n in names if idx[n,'vnd']['unassigned']==0]
    wins=sum(idx[n,'tabu']['final']<idx[n,'vnd']['final']-1e-8 for n in names)
    ties=sum(abs(idx[n,'tabu']['final']-idx[n,'vnd']['final'])<=1e-8 for n in names)
    a=idx['Instancia1_G1.txt','vnd'];b=idx['Instancia1_G1.txt','tabu']
    text=f'''Das 28 instâncias, {len(feasible)} admitem atendimento completo e {28-len(feasible)} são estruturalmente inviáveis no modelo de um tipo por escola. Todas as 3360 soluções iniciais/finais respeitaram a capacidade e compatibilidade e atingiram o atendimento certificado. A tabu apresentou menor distância média em {wins} instâncias; houve {ties} empates e o VND obteve menor média nas {28-wins-ties} restantes. A contagem inclui distâncias parciais, sempre comparadas dentro da mesma instância e do mesmo atendimento. Não estabelece significância estatística.

Em G1/1, a distância média final foi {num(a['final'])} km no VND e {num(b['final'])} km na tabu, com melhorias médias de {num(a['improvement_pct'])}\\% e {num(b['improvement_pct'])}\\%, respectivamente. Os tempos médios de busca foram {num(a['search_s'],4)} s e {num(b['search_s'],4)} s. O VND utilizou em média {num(a['schools'])} escolas e a tabu {num(b['schools'])}, dentre {a['m']} disponíveis. O número de escolas não é penalizado no objetivo.

O fallback do certificado foi utilizado em {sum(r['fallback'] for r in rows)} das 1680 construções. O limite de 150 iterações foi atingido em {sum(r['max_iter_runs'] for r in rows)} execuções. Consequentemente, os resultados medem qualidade sob orçamento finito. A pré-checagem ocorre uma vez por lote de 30 sementes e seu custo deve ser somado uma única vez ao custo do lote, não a cada execução.

Ambiente da campanha: {tex(meta['platform'])}, Python {platform.python_version()}, C++17 compilado com Apple Clang e otimização \\texttt{{-O2}}, NumPy 1.24.2 e SciPy 1.11.3. Cada método foi executado com quatro processos; os tempos incluem competição por CPU e são indicativos. Os manifestos contêm hashes de binário e entradas, parâmetros e versão do Python. O hash do binário da campanha é \\texttt{{{meta['binary_sha256'][:16]}}} (prefixo).
'''
    (DOC/'resultados_atual_texto.tex').write_text(text)
    selected=['Instancia1_G1.txt','Instancia2_G1.txt','Instancia1_G2.txt','Instancia2_G2.txt','Instancia1_G6.txt','Instancia2_G7.txt']
    lines=[r'\begin{table}[ht]',r'\centering\scriptsize',r'\caption{Seleção de resultados em K=1, 30 sementes por linha; distâncias em km. U é o número mínimo de não alocados. Tempo: apenas busca.}',r'\begin{tabular}{llrrrrr}',r'\toprule Instância & Método & U & Inicial & Final $\pm$ dp & Melhora (\%) & Busca (s)\\\midrule']
    for n in selected:
        for method in ('vnd','tabu'):
            r=idx[n,method]
            lines.append(f"{tex(label(n))} & {method.upper()} & {r['unassigned']} & {num(r['initial'])} & {num(r['final'])} $\\pm$ {num(r['std'])} & {num(r['improvement_pct'])} & {num(r['search_s'],4)} \\")
    # Use explicit two-backslash row terminators.
    lines=[s+'\\' if s.endswith(' \\') else s for s in lines]
    lines.extend([r'\bottomrule\end{tabular}',r'\end{table}'])
    (DOC/'resultados_atual_tabela.tex').write_text('\n'.join(lines))
    full=[r'\small',r'\setlength{\tabcolsep}{3pt}',r'\begin{longtable}{llrrrrr}',r'\caption{Todas as instâncias: média, desvio padrão amostral, mínimo e máximo da distância; U é o déficit certificado.}\\',r'\toprule Instância & Método & U & Média & dp & Mínimo & Máximo\\\midrule\endfirsthead',r'\toprule Instância & Método & U & Média & dp & Mínimo & Máximo\\\midrule\endhead']
    for n in names:
        for method in ('vnd','tabu'):
            r=idx[n,method]
            full.append(' & '.join([tex(label(n)),method.upper(),str(r['unassigned']),num(r['final']),num(r['std']),num(r['min']),num(r['max'])])+r' \\')
    full.extend([r'\bottomrule\end{longtable}',r'\begin{longtable}{llrrrr}',r'\caption{Tempos médios por execução (segundos), locais usados e melhoria percentual média. C: construção; BL: busca. Pré-checagem fica nos CSVs e é compartilhada pelo lote.}\\',r'\toprule Instância & Método & C (s) & BL (s) & Locais & Melhora (\%)\\\midrule\endfirsthead',r'\toprule Instância & Método & C (s) & BL (s) & Locais & Melhora (\%)\\\midrule\endhead'])
    for n in names:
        for method in ('vnd','tabu'):
            r=idx[n,method]
            full.append(' & '.join([tex(label(n)),method.upper(),num(r['construction_s'],4),num(r['search_s'],4),num(r['schools']),num(r['improvement_pct'])])+r' \\')
    full.extend([r'\bottomrule\end{longtable}',r'\normalsize',r'\subsection{Distribuição da melhor solução em G1/1}',r'As cargas abaixo correspondem à melhor execução da tabu, selecionada por distância mínima entre as 30 sementes. O JSON registra a atribuição de cada candidato e as distribuições das demais instâncias.',r'\begin{center}\small\begin{tabular}{lrrl}',r'\toprule Escola & Carga/capacidade & Ocupação (\%) & Tipo: candidatos\\\midrule'])
    r=idx['Instancia1_G1.txt','tabu']
    for j,school in enumerate(r['school_ids']):
        types=', '.join(f'{t}: {v}' for t,v in zip(r['type_names'],r['best_types'][j]) if v)
        full.append(f"{tex(school)} & {r['best_load'][j]}/{r['capacities'][j]} & {num(100*r['best_load'][j]/r['capacities'][j])} & {tex(types) or '--'}"+r' \\')
    full.extend([r'\bottomrule\end{tabular}\end{center}'])
    (DOC/'resultados_atual_completo.tex').write_text('\n'.join(full))
    return {'feasible':len(feasible),'wins':wins,'ties':ties,'vnd_wins':28-wins-ties}

def plots(data):
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(2,2,figsize=(10,6))
    for ax,name in zip(axs.flat,['Instancia1_G1.txt','Instancia2_G1.txt','Instancia2_G2.txt','Instancia2_G7.txt']):
        for method,color in [('vnd','#346538'),('tabu','#9F2F2D')]:
            curves=[]
            for r in data[name,method]['runs']:
                by={int(v[0]):v[1] for v in r['convergence']};last=r['initial']['distance'];curve=[]
                for i in range(151):last=by.get(i,last);curve.append(last)
                curves.append(curve)
            ax.plot(range(151),[statistics.mean(c[i] for c in curves) for i in range(151)],label=method.upper(),color=color)
        partial=data[name,'vnd']['feasibility']=='infeasible'
        ax.set_title(label(name)+(' (parcial)' if partial else ' (completa)'))
        ax.set_xlabel('Iteração');ax.set_ylabel('Distância média (km)');ax.grid(alpha=.15);ax.legend()
    fig.tight_layout();fig.savefig(OUT/'final_convergencia.pdf');fig.savefig(OUT/'final_convergencia.png',dpi=180)
    plt.close(fig)

def main():
    rows,data,meta=collect();stats=tables(rows,data,meta);plots(data)
    from gerar_apresentacao import generate
    generate(rows,data,stats)
    print(f"Entrega gerada: {len(rows)} configurações, {meta['runs']} execuções, {meta['validated_solutions']} soluções verificadas")
if __name__=='__main__':main()
