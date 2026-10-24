#!/usr/bin/env python3
"""Gera tabelas LaTeX a partir dos resultados efetivamente executados."""
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'resultados/resumo.csv').open()))
names={'Modelo_de_Instancia.txt':'Modelo','instancia2.txt':'Inst. 2','instancia_A.txt':'A','instancia_B.txt':'B'}
def num(x):return f'{float(x):.2f}'.replace('.',',')
principal=[r for r in rows if r['config'] in ('vnd_a03','tabu_a03')]
text=[r'\begin{table}[ht]',r'\centering\scriptsize',r'\caption{Resultados com $\alpha=0{,}3$: 30 sementes por linha. Distâncias em km. Asterisco indica instância inviável; a distância é parcial.}',r'\begin{tabular}{lclrrrrr}',r'\hline Inst. & K & Método & Inicial média & Final média $\pm$ dp & Mín. & Máx. & Busca (s) \\ \hline']
for r in principal:
 label=names[r['instance']]+('*' if r['status']=='infeasible' else '')
 text.append(f"{label} & {r['K']} & {'VND' if r['config']=='vnd_a03' else 'Tabu'} & {num(r['initial_mean'])} & {num(r['mean'])} $\\pm$ {num(r['std'])} & {num(r['min'])} & {num(r['max'])} & {float(r['search_seconds_mean']):.4f} \\\\")
text += [r'\hline\end{tabular}',r'\label{tab:principal}',r'\end{table}']
(ROOT/'docs/tab_principal.tex').write_text('\n'.join(text)+'\n')
text=[r'\begin{table}[ht]',r'\centering\small',r'\caption{Ablações em A, K=2. As outras instâncias constam no CSV completo.}',r'\begin{tabular}{lrrrrr}',r'\hline Configuração & Média & dp & Mínimo & Máximo & Busca (s) \\ \hline']
for r in rows:
 if r['instance']=='instancia_A.txt' and r['K']=='2':
  label=r['config'].replace('_',r'\_')
  text.append(f"{label} & {num(r['mean'])} & {num(r['std'])} & {num(r['min'])} & {num(r['max'])} & {float(r['search_seconds_mean']):.4f} \\\\")
text += [r'\hline\end{tabular}',r'\label{tab:ablacoes}',r'\end{table}']
(ROOT/'docs/tab_ablacoes.tex').write_text('\n'.join(text)+'\n')

# Texto quantitativo também é regenerado, evitando discussão com dados obsoletos.
index={(r['instance'],r['K'],r['config']):r for r in rows}
a=index['instancia_A.txt','1','vnd_a03'];b=index['instancia_A.txt','1','tabu_a03']
best=min((r for r in rows if r['instance']=='instancia_A.txt' and r['K']=='2'),key=lambda r:float(r['mean']))
label=best['config'].replace('_','\\_')
wins=sum(float(index[name,K,'tabu_a03']['mean'])<float(index[name,K,'vnd_a03']['mean']) for name in names for K in ('1','2'))
fb_msg = (
    f"Em A, K=1, o reparo local de tipos na construção atingiu o atendimento máximo sem recorrer aos tipos do certificado ({a['fallback_runs']} fallbacks nas 30 sementes com $\\alpha=0{{,}}3$)."
    if int(a['fallback_runs']) == 0
    else f"Em A, K=1, a construção recorreu aos tipos do certificado em {a['fallback_runs']} das 30 sementes com $\\alpha=0{{,}}3$. Isso evidencia uma limitação da fase gulosa na instância apertada."
)
text=f'''No orçamento utilizado, a tabu com $\\alpha=0{{,}}3$ apresentou menor distância média que o VND correspondente em {wins} dos oito pares instância/K, incluindo casos de atendimento parcial. Em A, K=1, a média passou de {num(a['mean'])} km no VND para {num(b['mean'])} km na tabu, com tempos médios de busca de {float(a['search_seconds_mean']):.3f} s e {float(b['search_seconds_mean']):.3f} s. Essa comparação não estabelece significância estatística e usa o mesmo limite de iterações, não o mesmo tempo.

{fb_msg} Para A, K=2, a configuração de menor média entre as testadas foi \\texttt{{{label}}}, com {num(best['mean'])} km. Não há uma tenure universalmente recomendada a partir desses dados.

Muitas execuções atingiram 150 iterações; portanto, parte das diferenças reflete também a velocidade de melhoria antes do limite. A flexibilização para K=2 amplia o conjunto viável, mas uma heurística com orçamento finito pode encontrar resultado pior que em K=1, como observado em algumas médias de B. Essa é uma limitação de exploração, não uma inversão da relação entre ótimos dos modelos.
'''
perf=ROOT/'resultados/performance_A.json'
if perf.exists():
    import json
    d=json.loads(perf.read_text());r=d['runs'][0]
    text+=f'''\nEm uma execução adicional de A, K=1, com semente {r['seed']}, $\\alpha=0{{,}}3$ e limite de 5000 iterações, o VND encerrou após {r['iterations']} iterações, em {r['search_seconds']:.3f} s de busca, passando de {num(r['initial']['distance'])} para {num(r['final']['distance'])} km. Essa medição individual ilustra o alvo de desempenho, não substitui as 30 repetições da campanha e continua sujeita à amostragem de N3.\n'''
(ROOT/'docs/discussao_resultados.tex').write_text(text)
