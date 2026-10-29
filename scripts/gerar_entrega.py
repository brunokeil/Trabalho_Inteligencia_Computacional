#!/usr/bin/env python3
"""Gera relatório e slides a partir das campanhas finais em K=1 e K=2."""
import csv, hashlib, json, os, platform, re, statistics, sys
from pathlib import Path
from validar import validate
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'resultados'
DOC = ROOT / 'docs'
CAMPAIGNS = [(1, 'vnd', 'final_vnd'), (1, 'tabu', 'final_tabu'),
             (2, 'vnd', 'final_k2_vnd'), (2, 'tabu', 'final_k2_tabu')]
REPOSITORY = 'https://github.com/brunokeil/Trabalho_Inteligencia_Computacional'


def tex(s):
    return str(s).replace('_', r'\_').replace('%', r'\%').replace('&', r'\&')


def num(x, d=2):
    return f'{x:.{d}f}'.replace('.', ',')


def label(name):
    match = re.fullmatch(r'instancia_?([12])_?G(\d+)(?:\(1\))?\.txt', name, re.I)
    if not match:
        raise ValueError(f'Nome de instância desconhecido: {name}')
    return f'I{match[1]} G{int(match[2])}'


def name_key(name):
    variant, group = label(name).split()
    return int(group[1:]), int(variant[1:])


def collect():
    rows, data, solutions = [], {}, 0
    binary_hash = hashlib.sha256((ROOT / 'alocacao').read_bytes()).hexdigest()
    for K, method, campaign in CAMPAIGNS:
        folder = OUT / campaign
        manifest = json.loads((folder / 'manifest.json').read_text())
        assert manifest['binary_sha256'] == binary_hash, 'Campanha não corresponde ao executável atual'
        files = sorted(folder.glob(f'*__K{K}__{method}.json'))
        assert len(files) == 28
        assert {p.name.split('__')[0] + '.txt' for p in files} == set(manifest['instances'])
        for p in files:
            d = json.loads(p.read_text())
            solutions += validate(p)
            assert d['K'] == K and len(d['runs']) == 30 and d['method'] == method
            assert [r['seed'] for r in d['runs']] == list(range(1, 31))
            source = ROOT / 'instances/preparadas' / d['name']
            assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['instances'][d['name']]
            runs = d['runs']
            fin = [r['final']['distance'] for r in runs]
            ini = [r['initial']['distance'] for r in runs]
            assert all(r['initial']['unassigned'] == r['final']['unassigned'] ==
                       len(d['candidateIds']) - d['maximum_assigned'] for r in runs)
            best = runs[d['best_run']]
            construction = statistics.mean(r['construction_seconds'] for r in runs)
            search = statistics.mean(r['search_seconds'] for r in runs)
            read, precheck = d['read_seconds'], d['precheck_seconds']
            r = {'instance': d['name'], 'label': label(d['name']), 'K': K, 'method': method,
                 'runs': len(runs), 'n': len(d['candidateIds']), 'm': len(d['schoolIds']),
                 'capacity': sum(d['capacities']), 'unassigned': runs[0]['final']['unassigned'],
                 'initial': statistics.mean(ini), 'initial_std': statistics.stdev(ini),
                 'initial_min': min(ini), 'initial_max': max(ini),
                 'final': statistics.mean(fin), 'std': statistics.stdev(fin),
                 'min': min(fin), 'max': max(fin),
                 'improvement_pct': statistics.mean(100 * (a-b) / a if a else 0 for a, b in zip(ini, fin)),
                 'construction_s': construction, 'search_s': search,
                 'schools': statistics.mean(sum(v > 0 for v in r['final']['load']) for r in runs),
                 'read_s': read, 'precheck_s': precheck,
                 'total_s': (read + precheck) / len(runs) + construction + search,
                 'batch_s': read + precheck + len(runs) * (construction + search),
                 'fallback': sum(r['fallback'] for r in runs),
                 'best_seed': best['seed'], 'best_load': best['final']['load'],
                 'best_types': best['final']['loadByType'], 'type_names': d['typeNames'],
                 'capacities': d['capacities'], 'school_ids': d['schoolIds'],
                 'max_iter': d['max_iter'], 'stagnation': d['stagnation'],
                 'iterations_mean': statistics.mean(r['iterations'] for r in runs),
                 'iterations_max': max(r['iterations'] for r in runs),
                 'max_iter_runs': sum(r['iterations'] >= d['max_iter'] for r in runs)}
            rows.append(r)
            data[d['name'], K, method] = d
    with (OUT / 'final_resumo.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    metadata = {'platform': platform.platform(), 'python': sys.version, 'binary_sha256': binary_hash,
                'campaigns': [c for _, _, c in CAMPAIGNS], 'instances': 28,
                'configurations': len(rows), 'runs': sum(r['runs'] for r in rows),
                'validated_solutions': solutions, 'scope': 'K=1 e K=2, tipos escolhidos pelo algoritmo',
                'input_audit': 'instances/auditoria_atual.csv', 'repository': REPOSITORY}
    (OUT / 'final_validacao.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False))
    return rows, data, metadata


def tables(rows, data, meta):
    idx = {(r['instance'], r['K'], r['method']): r for r in rows}
    names = sorted({r['instance'] for r in rows}, key=name_key)
    stats = {}
    system = 'macOS' if platform.system() == 'Darwin' else platform.system()
    paragraphs = []
    for K in (1, 2):
        feasible = sum(idx[n, K, 'vnd']['unassigned'] == 0 for n in names)
        wins = sum(idx[n, K, 'tabu']['final'] < idx[n, K, 'vnd']['final'] - 1e-8 for n in names)
        ties = sum(abs(idx[n, K, 'tabu']['final'] - idx[n, K, 'vnd']['final']) <= 1e-8 for n in names)
        vnd_wins = len(names) - wins - ties
        fallback = sum(r['fallback'] for r in rows if r['K'] == K)
        stats[K] = {'feasible': feasible, 'wins': wins, 'ties': ties, 'vnd_wins': vnd_wins,
                    'fallback': fallback, 'runs': 1680}
        tie_text = f"{ties} empate" + ('' if ties == 1 else 's')
        paragraphs.append(f'Em $K={K}$, {feasible} das 28 instâncias admitem atendimento completo. '
                          f'A comparação de distância média entre métodos resulta em {wins} vitórias da tabu, '
                          f'{vnd_wins} do VND e {tie_text}. O fallback foi usado em {fallback} das 1680 construções desse caso.')
    a, b = idx['Instancia2_G2.txt', 1, 'vnd'], idx['Instancia2_G2.txt', 2, 'vnd']
    # Pior caso do VND: maior distância média relativa à melhor solução conhecida
    # (mínimo entre as 60 execuções de ambos os métodos), apenas com atendimento completo.
    gaps = []
    for n in names:
        for K in (1, 2):
            v, t = idx[n, K, 'vnd'], idx[n, K, 'tabu']
            if v['unassigned']:
                continue
            ref = min(v['min'], t['min'])
            gaps.append((100 * (v['final'] - ref) / ref, 100 * (v['max'] - ref) / ref, n, K, ref))
    gap, gap_max, wn, wK, ref = max(gaps)
    failure = idx[wn, wK, 'vnd']
    stats['worst'] = {'instance': wn, 'label': label(wn), 'K': wK, 'gap': gap, 'gap_max': gap_max,
                      'ref': ref, 'min': failure['min'], 'max': failure['max'], 'final': failure['final'],
                      'std': failure['std'], 'tabu': idx[wn, wK, 'tabu']['final']}
    vnd_rows = [r for r in rows if r['method'] == 'vnd']
    tabu_rows = [r for r in rows if r['method'] == 'tabu']
    bud = {'vnd_max_iter': vnd_rows[0]['max_iter'], 'tabu_max_iter': tabu_rows[0]['max_iter'],
           'tabu_stagnation': tabu_rows[0]['stagnation'],
           'vnd_cap': sum(r['max_iter_runs'] for r in vnd_rows),
           'tabu_cap': sum(r['max_iter_runs'] for r in tabu_rows),
           'vnd_iter_max': max(r['iterations_max'] for r in vnd_rows),
           'vnd_iter_mean': statistics.mean(r['iterations_mean'] for r in vnd_rows),
           'vnd_search_mean': statistics.mean(r['search_s'] for r in vnd_rows),
           'tabu_search_mean': statistics.mean(r['search_s'] for r in tabu_rows),
           'vnd_impr': statistics.mean(r['improvement_pct'] for r in vnd_rows),
           'tabu_impr': statistics.mean(r['improvement_pct'] for r in tabu_rows)}
    stats['budget'] = bud
    paragraphs.extend([
        f'As quatro inviabilidades em $K=1$ são I1 G2, I2 G2, I2 G3 e I2 G5; essa classificação depende de $K$. '
        f'Em I2 G2 (109 candidatos, seis tipos e cinco escolas), o atendimento certificado passa de '
        f"{a['n']-a['unassigned']} em $K=1$ para {b['n']-b['unassigned']} em $K=2$. "
        'A distância parcial de $K=1$ não mede a mesma tarefa da distância completa de $K=2$; '
        'portanto, não calculamos melhoria percentual entre esses dois casos.',
        ("O VND foi executado até o ótimo local em todas as execuções: o teto de segurança de "
         f"{bud['vnd_max_iter']} iterações foi atingido 0 vezes; a trajetória média teve "
         if bud['vnd_cap'] == 0 else
         f"O teto de segurança do VND, de {bud['vnd_max_iter']} iterações, foi atingido {bud['vnd_cap']} vezes; a trajetória média teve ")+
        f"{num(bud['vnd_iter_mean'], 0)} iterações e a mais longa {bud['vnd_iter_max']}. A tabu atingiu o teto de "
        f"{bud['tabu_max_iter']} iterações em {bud['tabu_cap']} das 1680 execuções; nas demais, parou após "
        f"{bud['tabu_stagnation']} iterações sem melhora. A melhoria média sobre a construção foi de "
        f"{num(bud['vnd_impr'])}\\% no VND e {num(bud['tabu_impr'])}\\% na tabu, com tempo médio de busca de "
        f"{num(bud['vnd_search_mean'], 3)} s e {num(bud['tabu_search_mean'], 3)} s por execução, respectivamente.",
        f"O pior desempenho relativo do VND ocorreu em {label(wn)} com $K={wK}$: a distância média final "
        f"({num(failure['final'])} km, desvio padrão {num(failure['std'])}) ficou {num(gap)}\\% acima da melhor "
        f"solução conhecida ({num(ref)} km, mínimo entre as 60 execuções dos dois métodos), e a pior semente ficou "
        f"{num(gap_max)}\\% acima. A tabu obteve média de {num(idx[wn, wK, 'tabu']['final'])} km na mesma instância.",
        f"Todas as {meta['validated_solutions']} soluções iniciais/finais respeitaram capacidade e compatibilidade e atingiram "
        'o atendimento certificado. As contagens de vitórias são descritivas e comparam os métodos somente '
        'dentro da mesma instância, do mesmo K e do mesmo atendimento; não estabelecem significância estatística.',
        'A pré-checagem é executada uma vez por lote de 30 sementes, separadamente para cada método e K. '
        'A tabela de tempos inclui esse custo integral em P e o amortiza em Total: '
        r'$T_{\mathrm{total}}=(T_{\mathrm{leitura}}+P)/30+T_{\text{construção}}+T_{\mathrm{busca}}$. '
        'O custo do lote é 30 vezes esse total médio; não se trata de medição isolada com CPU exclusiva.',
        f"Ambiente: {tex(system)} ({tex(platform.machine())}), Python {platform.python_version()}, C++17 com Apple Clang e "
        r'otimização \texttt{-O2}, NumPy 1.24.2 e SciPy 1.11.3. VND e tabu foram executados simultaneamente, com quatro processos cada (oito processos em oito núcleos); '
        'os tempos incluem competição por CPU. Os manifestos registram entradas, binário e parâmetros. '
        f"O prefixo do hash do binário é \\texttt{{{meta['binary_sha256'][:16]}}}."
    ])
    (DOC / 'resultados_atual_texto.tex').write_text('\n\n'.join(paragraphs) + '\n')
    selected = ['Instancia1_G1.txt', 'Instancia1_G2.txt', 'Instancia2_G2.txt']
    selected += [n for n in (wn, 'Instancia2_G9.txt') if n not in selected][:1]
    lines = [r'\begin{table}[ht]', r'\centering\small', r'\setlength{\tabcolsep}{3pt}',
             r'\caption{Comparação de K=1 e K=2, 30 sementes por linha; distâncias em km. Inicial e Final: média $\pm$ desvio padrão amostral. U é o déficit certificado. Tempos e extremos constam do Apêndice A.}',
             r'\begin{tabular}{lrlrrrr}',
             r'\toprule Instância & K & Método & U & Inicial (média) & Final (média) & Melhora (\%)\\\midrule']
    for n in selected:
        for K in (1, 2):
            for method in ('vnd', 'tabu'):
                r = idx[n, K, method]
                lines.append(' & '.join([tex(label(n)), str(K), method.upper(), str(r['unassigned']),
                             f"{num(r['initial'])} $\\pm$ {num(r['initial_std'])}",
                             f"{num(r['final'])} $\\pm$ {num(r['std'])}", num(r['improvement_pct'])]) + r' \\')
    lines.extend([r'\bottomrule\end{tabular}', r'\end{table}'])
    (DOC / 'resultados_atual_tabela.tex').write_text('\n'.join(lines))
    full = [r'\scriptsize', r'\setlength{\tabcolsep}{3pt}']
    for phase, title, fields in [('initial', 'solução inicial', ['initial', 'initial_std', 'initial_min', 'initial_max']),
                                 ('final', 'solução final', ['final', 'std', 'min', 'max'])]:
        full.extend([r'\begin{longtable}{lrlrrrrr}',
                     rf'\caption{{Todas as instâncias e ambos os valores de K: {title}, em km. dp é o desvio padrão amostral de 30 sementes; U é o déficit certificado.}}\\',
                     r'\toprule Instância & K & Método & U & Média & dp & Mínimo & Máximo\\\midrule\endfirsthead',
                     r'\toprule Instância & K & Método & U & Média & dp & Mínimo & Máximo\\\midrule\endhead'])
        for n in names:
            for K in (1, 2):
                for method in ('vnd', 'tabu'):
                    r = idx[n, K, method]
                    full.append(' & '.join([tex(label(n)), str(K), method.upper(), str(r['unassigned'])] +
                                           [num(r[f]) for f in fields]) + r' \\')
        full.append(r'\bottomrule\end{longtable}')
    full.extend([r'\begin{longtable}{lrlrrrrrr}',
                 r'\caption{Tempos em segundos: P é a pré-checagem integral do lote de 30 sementes; C e BL são construção e busca médias por execução. Total inclui leitura e P amortizados por 30. Locais é o número médio de escolas utilizadas.}\\',
                 r'\toprule Instância & K & Método & P (lote) & C & BL & Total & Locais & Melhora (\%)\\\midrule\endfirsthead',
                 r'\toprule Instância & K & Método & P (lote) & C & BL & Total & Locais & Melhora (\%)\\\midrule\endhead'])
    for n in names:
        for K in (1, 2):
            for method in ('vnd', 'tabu'):
                r = idx[n, K, method]
                full.append(' & '.join([tex(label(n)), str(K), method.upper()] +
                            [num(r[f], 4) for f in ['precheck_s', 'construction_s', 'search_s', 'total_s']] +
                            [num(r['schools']), num(r['improvement_pct'])]) + r' \\')
    full.extend([r'\bottomrule\end{longtable}', r'\normalsize'])
    for name, K in [('Instancia1_G1.txt', 1), ('Instancia2_G2.txt', 2)]:
        r = idx[name, K, 'tabu']
        full.extend([rf'\subsection{{Distribuição em {label(name)}, K={K}}}',
                     f"Melhor execução da tabu entre as 30 sementes (semente {r['best_seed']}); distância "
                     f"{num(r['min'])} km e {r['n']-r['unassigned']} de {r['n']} candidatos atendidos. "
                     'Cada linha mostra uma escola; em K=2, os tipos compartilham sua capacidade.',
                     r'\begin{center}\small\begin{tabular}{lrrl}',
                     r'\toprule Escola & Carga/capacidade & Ocupação (\%) & Tipo: candidatos\\\midrule'])
        for j, school in enumerate(r['school_ids']):
            types = ', '.join(f'{t}: {v}' for t, v in zip(r['type_names'], r['best_types'][j]) if v)
            full.append(' & '.join([tex(school), f"{r['best_load'][j]}/{r['capacities'][j]}",
                        num(100 * r['best_load'][j] / r['capacities'][j]), tex(types) or '--']) + r' \\')
        full.append(r'\bottomrule\end{tabular}\end{center}')
    (DOC / 'resultados_atual_completo.tex').write_text('\n'.join(full))
    return stats


def mean_curve(runs):
    """Melhor distância média por iteração; execuções encerradas mantêm o último valor."""
    length = max(int(r['convergence'][-1][0]) for r in runs) + 1
    curves = []
    for r in runs:
        by = {int(v[0]): v[1] for v in r['convergence']}
        last, curve = r['initial']['distance'], []
        for i in range(length):
            last = by.get(i, last)
            curve.append(last)
        curves.append(curve)
    return [statistics.mean(c[i] for c in curves) for i in range(length)]


def plots(data):
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(10, 6))
    for axes, name in zip(axs, ['Instancia1_G1.txt', 'Instancia2_G2.txt']):
        for ax, K in zip(axes, (1, 2)):
            for method, color in [('vnd', '#346538'), ('tabu', '#9F2F2D')]:
                curve = mean_curve(data[name, K, method]['runs'])
                ax.plot(range(len(curve)), curve, label=method.upper(), color=color)
            partial = data[name, K, 'vnd']['feasibility'] == 'infeasible'
            ax.set_title(label(name) + f' / K={K}' + (' (parcial)' if partial else ' (completa)'))
            ax.set_xlabel('Iteração')
            ax.set_ylabel('Distância média (km)')
            ax.grid(alpha=.15)
            ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / 'final_convergencia.pdf')
    fig.savefig(OUT / 'final_convergencia.png', dpi=180)
    plt.close(fig)


def main():
    rows, data, meta = collect()
    stats = tables(rows, data, meta)
    plots(data)
    from gerar_apresentacao import generate
    generate(rows, data, stats)
    print(f"Entrega gerada: {len(rows)} configurações, {meta['runs']} execuções, {meta['validated_solutions']} soluções verificadas")


if __name__ == '__main__':
    main()
