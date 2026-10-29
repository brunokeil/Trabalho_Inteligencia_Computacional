#!/bin/sh
# Campanha final: VND até o ótimo local (sem teto efetivo de movimentos) e
# busca tabu com 1000 iterações / 200 sem melhora. 30 sementes, K=1 e K=2.
set -e
cd "$(dirname "$0")/.."
VND_ITER=1000000
TABU_ITER=1000
TABU_STAG=200
(
  python3 scripts/executar_todas.py --instancias-dir instances/preparadas -k 1 --metodo vnd --runs 30 \
    --max-iter $VND_ITER --sem-melhora $VND_ITER -j 4 --out resultados/final_vnd
  python3 scripts/executar_todas.py --instancias-dir instances/preparadas -k 2 --metodo vnd --runs 30 \
    --max-iter $VND_ITER --sem-melhora $VND_ITER -j 4 --out resultados/final_k2_vnd
) > docs/campanha_final_vnd.log.txt 2>&1 &
(
  python3 scripts/executar_todas.py --instancias-dir instances/preparadas -k 1 --metodo tabu --runs 30 \
    --max-iter $TABU_ITER --sem-melhora $TABU_STAG -j 4 --out resultados/final_tabu
  python3 scripts/executar_todas.py --instancias-dir instances/preparadas -k 2 --metodo tabu --runs 30 \
    --max-iter $TABU_ITER --sem-melhora $TABU_STAG -j 4 --out resultados/final_k2_tabu
) > docs/campanha_final_tabu.log.txt 2>&1 &
wait
echo "campanha concluida"
