#!/usr/bin/env python3
"""Script para executar todas as instâncias em lote com ./alocacao.
Suporta paralelismo multi-processo, validação automática, geração de resumo CSV e Markdown.

Exemplos de uso:
  # Executa todas as instâncias com K=1 e K=2:
  python3 scripts/executar_todas.py -k 1,2

  # Executa apenas K=1 com método VND em 4 processos paralelos:
  python3 scripts/executar_todas.py -k 1 --metodo vnd -j 4

  # Executa apenas instâncias pequenas ou específicas:
  python3 scripts/executar_todas.py --filter "*pequena*"

  # Executa com 10 sementes por instância:
  python3 scripts/executar_todas.py --runs 10

  # Retoma execução pulando instâncias já concluídas:
  python3 scripts/executar_todas.py --skip-existing

  # Apenas regera as tabelas de resumo a partir dos JSONs existentes:
  python3 scripts/executar_todas.py --resumo-only
"""

import argparse, csv, fnmatch, glob, hashlib, json, multiprocessing, os, statistics, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
try:
    from validar import validate, read_instance
except ImportError:
    validate = None
    read_instance = None

def get_instance_info(inst_path):
    try:
        with open(inst_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
        n = int(lines[0].split(':')[1].strip())
        m = int(lines[1].split(':')[1].strip())
        schools = lines[2+n:2+n+m]
        caps = [sum(map(int, s.split(',')[5].split(';'))) for s in schools]
        return n, m, sum(caps)
    except Exception:
        return None, None, None

def run_single_job(job):
    (inst_path, K, bin_path, out_dir, metodo, alpha, runs, seed, max_iter, sem_melhora, tempo, skip_existing, do_validate) = job
    
    stem = inst_path.stem
    json_path = out_dir / f"{stem}__K{K}__{metodo}.json"
    console_path = out_dir / f"{stem}__K{K}__{metodo}.console.txt"
    
    if skip_existing and json_path.exists():
        try:
            d = json.loads(json_path.read_text(encoding='utf-8'))
            if do_validate and validate:
                validate(json_path)
            return {'status': 'SKIPPED', 'path': json_path, 'stem': stem, 'K': K, 'error': None}
        except Exception:
            pass # Re-run if invalid

    cmd = [
        str(bin_path),
        '--instancia', str(inst_path),
        '--tipos-por-escola', str(K),
        '--metodo', metodo,
        '--alpha', str(alpha),
        '--runs', str(runs),
        '--seed', str(seed),
        '--max-iter', str(max_iter),
        '--sem-melhora', str(sem_melhora),
        '--tempo', str(tempo),
        '--saida', str(json_path)
    ]
    
    t0 = time.perf_counter()
    with open(console_path, 'w', encoding='utf-8') as log:
        log.write('COMMAND: ' + ' '.join(cmd) + '\n')
        log.flush()
        res = subprocess.run(cmd, cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT)
    elapsed = time.perf_counter() - t0
    
    if res.returncode != 0:
        err_msg = console_path.read_text(encoding='utf-8')[-300:]
        return {'status': 'ERROR', 'path': json_path, 'stem': stem, 'K': K, 'error': err_msg, 'elapsed': elapsed}
    
    # Validation
    val_err = None
    if do_validate and validate:
        try:
            validate(json_path)
        except Exception as e:
            val_err = str(e)
            return {'status': 'VALIDATION_FAILED', 'path': json_path, 'stem': stem, 'K': K, 'error': val_err, 'elapsed': elapsed}
            
    return {'status': 'OK', 'path': json_path, 'stem': stem, 'K': K, 'error': None, 'elapsed': elapsed}

def generate_summary(out_dir, instances_dir):
    json_files = sorted(out_dir.glob("*__K*__*.json"))
    if not json_files:
        print("Nenhum arquivo JSON de resultado encontrado para resumir.")
        return []

    rows = []
    for p in json_files:
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
            runs = d.get('runs', [])
            if not runs:
                continue
            finals = [r['final']['distance'] for r in runs]
            initials = [r['initial']['distance'] for r in runs]
            search_secs = [r.get('search_seconds', 0.0) for r in runs]
            constr_secs = [r.get('construction_seconds', 0.0) for r in runs]
            unassigned = runs[0]['final'].get('unassigned', 0)
            
            # Instance stats
            inst_p = instances_dir / d['name']
            n, m, cap = get_instance_info(inst_p) if inst_p.exists() else (len(d.get('candidateIds', [])), len(d.get('schoolIds', [])), sum(d.get('capacities', [])))
            
            min_f = min(finals)
            mean_f = sum(finals) / len(finals)
            mean_init = sum(initials) / len(initials)
            melhora_pct = statistics.mean(100 * (a-b) / a if a else 0 for a, b in zip(initials, finals))
            
            rows.append({
                'instancia': d['name'],
                'K': d['K'],
                'metodo': d.get('method', 'vnd'),
                'status': d.get('feasibility', 'unknown'),
                'nao_alocados': unassigned,
                'n_candidatos': n,
                'm_escolas': m,
                'capacidade_total': cap,
                'runs': len(runs),
                'dist_inicial_media': f"{mean_init:.4f}",
                'dist_inicial_desvio_amostral': f"{statistics.stdev(initials) if len(initials)>1 else 0:.4f}",
                'dist_inicial_min': f"{min(initials):.4f}",
                'dist_inicial_max': f"{max(initials):.4f}",
                'dist_min': f"{min_f:.4f}",
                'dist_media': f"{mean_f:.4f}",
                'dist_desvio_amostral': f"{statistics.stdev(finals) if len(finals)>1 else 0:.4f}",
                'dist_max': f"{max(finals):.4f}",
                'locais_usados_media': f"{statistics.mean(sum(x>0 for x in r['final']['load']) for r in runs):.2f}",
                'construcao_seg_media': f"{statistics.mean(constr_secs):.6f}",
                'melhora_pct': f"{melhora_pct:.2f}%",
                'precheck_seg': f"{d.get('precheck_seconds', 0.0):.4f}",
                'busca_seg_media': f"{sum(search_secs)/len(search_secs):.4f}",
                'total_seg_medio': f"{(d.get('read_seconds', 0.0) + d.get('precheck_seconds', 0.0) + sum(constr_secs) + sum(search_secs))/len(runs):.4f}"
            })
        except Exception as e:
            print(f"Aviso ao ler {p.name}: {e}")

    # Write summary CSV
    csv_path = out_dir / 'resumo.csv'
    if rows:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
            
    # Write summary Markdown
    md_path = out_dir / 'resumo.md'
    md_lines = [
        '# Resumo da Execução de Todas as Instâncias',
        '',
        f'Total de configurações/instâncias executadas: {len(rows)}.',
        'Tempos totais incluem leitura e pré-checagem amortizadas pelo número de sementes; pré-check é o custo integral do lote.',
        '',
        '| Instância | K | Método | Estado | Não Aloc. | Inicial (média ± dp) | Mínima (km) | Média final (km) | Melhora | Pré-check lote (s) | Busca (s) | Total médio (s) |',
        '|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|'
    ]
    for r in rows:
        md_lines.append(f"| `{r['instancia']}` | {r['K']} | {r['metodo']} | {r['status']} | {r['nao_alocados']} | {r['dist_inicial_media']} ± {r['dist_inicial_desvio_amostral']} | {r['dist_min']} | {r['dist_media']} | {r['melhora_pct']} | {r['precheck_seg']} | {r['busca_seg_media']} | {r['total_seg_medio']} |")
    
    md_lines.append('')
    md_path.write_text('\n'.join(md_lines), encoding='utf-8')
    
    print(f"\nResumos consolidados salvos com sucesso:")
    print(f"  -> {csv_path}")
    print(f"  -> {md_path}")
    return rows

def main():
    ap = argparse.ArgumentParser(description="Executa todas as instâncias em lote com o resolvedor C++.")
    ap.add_argument('--instancias-dir', type=Path, default=ROOT / 'instances', help="Diretório contendo as instâncias (padrão: instances/)")
    ap.add_argument('--alocacao-bin', type=Path, default=ROOT / 'alocacao', help="Executável C++ (padrão: ./alocacao)")
    ap.add_argument('-k', '--tipos-por-escola', default='1', help="Limites de tipos por escola: 1, 2 ou 1,2; os tipos são escolhidos pelo algoritmo")
    ap.add_argument('--metodo', choices=['vnd', 'tabu'], default='vnd', help="Método de busca local: vnd ou tabu (padrão: vnd)")
    ap.add_argument('--alpha', type=float, default=0.3, help="Parâmetro alpha da construção gulosa randomizada (padrão: 0.3)")
    ap.add_argument('--runs', type=int, default=1, help="Número de execuções com sementes diferentes (padrão: 1)")
    ap.add_argument('--seed', type=int, default=1, help="Semente inicial (padrão: 1)")
    ap.add_argument('--max-iter', type=int, default=150, help="Iterações máximas (padrão: 150)")
    ap.add_argument('--sem-melhora', type=int, default=50, help="Critério de estagnação sem melhora (padrão: 50)")
    ap.add_argument('--tempo', type=int, default=0, help="Limite temporal em segundos por execução (0: sem limite; padrão: 0)")
    ap.add_argument('-j', '--workers', type=int, default=min(4, multiprocessing.cpu_count()), help="Processos em paralelo (padrão: min(4, CPU count))")
    ap.add_argument('--out', type=Path, default=ROOT / 'resultados' / 'todas_instancias', help="Diretório de saída (padrão: resultados/todas_instancias/)")
    ap.add_argument('--filter', default='*', help="Padrão glob/filtro para selecionar instâncias (ex: '*prof*', '*01*'; padrão: '*')")
    ap.add_argument('--skip-existing', action='store_true', help="Pula instâncias cujos arquivos de saída já existam")
    ap.add_argument('--no-validate', action='store_true', help="Desativa a validação independente pós-execução")
    ap.add_argument('--resumo-only', action='store_true', help="Apenas gera os resumos a partir de resultados existentes")
    args = ap.parse_args()

    inst_dir = args.instancias_dir.resolve()
    out_dir = args.out.resolve()
    bin_path = args.alocacao_bin.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.resumo_only:
        generate_summary(out_dir, inst_dir)
        return

    # Certifica que o executável existe ou compila via make
    if not bin_path.exists():
        print(f"Executável {bin_path} não encontrado. Executando 'make'...")
        subprocess.run(['make', '-C', str(ROOT)], check=True)
        if not bin_path.exists():
            sys.exit(f"Erro: não foi possível compilar {bin_path}")

    # Lista instâncias
    all_files = sorted([p for p in inst_dir.glob("*.txt") if p.is_file()])
    if args.filter != '*':
        all_files = [p for p in all_files if fnmatch.fnmatch(p.name, args.filter)]

    if not all_files:
        sys.exit(f"Nenhuma instância encontrada em {inst_dir} correspondente ao filtro '{args.filter}'")

    try:
        k_values = [int(x.strip()) for x in args.tipos_por_escola.split(',') if x.strip()]
    except ValueError:
        sys.exit(f"Valores inválidos para -k: {args.tipos_por_escola}")
    if not k_values or any(k not in (1,2) for k in k_values):
        sys.exit('K deve ser 1 ou 2')
    if args.runs < 1 or args.workers < 1 or not 0 <= args.alpha <= 1:
        sys.exit('runs/workers devem ser positivos; alpha deve estar em [0,1]')

    # Never resume results from a different binary, input or configuration.
    manifest = {'binary_sha256': hashlib.sha256(bin_path.read_bytes()).hexdigest(),
                'instances': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in all_files},
                'K': k_values, 'method': args.metodo, 'alpha': args.alpha,
                'runs': args.runs, 'seed': args.seed, 'max_iter': args.max_iter,
                'stagnation': args.sem_melhora, 'time_limit': args.tempo,
                'python': sys.version, 'platform': sys.platform}
    manifest_path = out_dir / 'manifest.json'
    if any(out_dir.glob('*__K*__*.json')) and (not manifest_path.exists() or json.loads(manifest_path.read_text()) != manifest):
        sys.exit('Manifesto ausente ou diferente: escolha outra pasta --out para não misturar resultados.')
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    jobs = []
    for inst_p in all_files:
        for K in k_values:
            jobs.append((
                inst_p, K, bin_path, out_dir,
                args.metodo, args.alpha, args.runs, args.seed,
                args.max_iter, args.sem_melhora, args.tempo,
                args.skip_existing, not args.no_validate
            ))

    total = len(jobs)
    print("=" * 80)
    print(f"DCC136 — Execução em Lote de Instâncias")
    print(f"Instâncias selecionadas: {len(all_files)}")
    print(f"Valores de K: {k_values}")
    print(f"Total de execuções planejadas: {total}")
    print(f"Método: {args.metodo} (alpha={args.alpha}, runs={args.runs}, max_iter={args.max_iter})")
    print(f"Paralelismo: {args.workers} worker(s)")
    print(f"Diretório de saída: {out_dir}")
    print("=" * 80)
    start_time = time.perf_counter()
    completed = 0
    errors = 0

    if args.workers <= 1:
        for job in jobs:
            res = run_single_job(job)
            completed += 1
            status = res['status']
            stem = res['stem']
            K = res['K']
            if status == 'OK':
                print(f"[{completed:3d}/{total:3d}] OK: {stem} (K={K}) [{res.get('elapsed', 0):.2f}s]")
            elif status == 'SKIPPED':
                print(f"[{completed:3d}/{total:3d}] PULADO (já existe): {stem} (K={K})")
            else:
                errors += 1
                print(f"[{completed:3d}/{total:3d}] FALHA ({status}): {stem} (K={K}) -> {res.get('error')}")
    else:
        with multiprocessing.Pool(processes=args.workers) as pool:
            for res in pool.imap_unordered(run_single_job, jobs):
                completed += 1
                status = res['status']
                stem = res['stem']
                K = res['K']
                if status == 'OK':
                    print(f"[{completed:3d}/{total:3d}] OK: {stem} (K={K}) [{res.get('elapsed', 0):.2f}s]")
                elif status == 'SKIPPED':
                    print(f"[{completed:3d}/{total:3d}] PULADO (já existe): {stem} (K={K})")
                else:
                    errors += 1
                    print(f"[{completed:3d}/{total:3d}] FALHA ({status}): {stem} (K={K}) -> {res.get('error')}")

    total_time = time.perf_counter() - start_time
    print("=" * 80)
    print(f"Concluído em {total_time:.1f}s. Sucessos: {completed - errors}/{total}. Falhas: {errors}.")
    print("Gerando resumos consolidados...")
    generate_summary(out_dir, inst_dir)
    print("=" * 80)
    if errors:
        sys.exit(1)

if __name__ == '__main__':
    main()
