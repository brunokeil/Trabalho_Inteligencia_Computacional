# DCC136 — Localização de locais de prova — 2026.3

Implementação C++17 de construção gulosa randomizada, VND e Busca Tabu. A entrega principal segue **um tipo de prova por escola (K=1)**, conforme o PDF fornecido. K=2 é uma extensão disponível no executável. O prazo escrito no PDF é **14/10/2026 às 12h**; eventuais alterações no Classroom não foram verificadas.

## Arquivos para entregar

- `entrega/Trabalho1-entrega.zip`: pacote com fontes, dados, resultados e documentação.
- `docs/relatorio.pdf`: relatório técnico de 11 páginas no modelo SBC.
- `docs/relatorio.tex`: fonte LaTeX; tabelas e estilo SBC estão em `docs/`.
- `docs/apresentacao.html`: 12 slides offline para aproximadamente dez minutos, com notas, cronômetro, exemplo interativo e seletor de resultados.
- `resultados/final_resumo.csv`: resultados das **1680 execuções** (56 configurações × 30 sementes).
- `resultados/final_vnd/` e `resultados/final_tabu/`: JSON/CSV completos, atribuições, distribuição por escola/tipo, curvas, logs e manifestos.

Abra o HTML diretamente no navegador. Use as setas para navegar, `N` para o roteiro e `F` para tela cheia. O botão **PDF** abre a impressão de todos os slides. O exemplo do slide 8 permite alternar construção e melhoria. Nenhuma conexão de rede é necessária.

## Compilar e verificar

Requisitos: compilador C++17, Make e Python 3.9+ com NumPy/SciPy. Matplotlib é necessário somente para gerar figuras. LaTeX com `pdflatex` compila o relatório. O programa usa ambiente POSIX (macOS, Linux ou WSL).

```sh
python3 -m pip install -r requirements.txt
make -j4
make test
make test-sanitize
./alocacao --help
```

Ambiente da campanha: macOS arm64, Apple Clang 21 com `-O2`, Python 3.9.6, NumPy 1.24.2, SciPy 1.11.3 e Matplotlib 3.7.2. Versões em `requirements-tested.txt`.

```sh
./alocacao --instancia instances/preparadas/Instancia1_G1.txt \
  --tipos-por-escola 1 --metodo tabu --alpha 0.3 --runs 30 \
  --seed 1 --max-iter 150 --sem-melhora 50 \
  --saida resultados/meu_teste.json --relatorio
python3 scripts/validar.py resultados/meu_teste.json
```

`--saida` gera JSON e CSV. O JSON registra soluções inicial/final, IDs originais, cargas, ocupação e convergência de cada semente. `assign` usa índices base zero, na ordem do arquivo; `-1` significa não alocado. `typeSlots` é uma máscara de bits sobre `typeNames`.

O modelo inteiro SciPy/HiGHS certifica o número máximo de atendidos e fornece uma salvaguarda de tipos ao construtivo; não otimiza distância. Instâncias estruturalmente inviáveis são marcadas `infeasible`, com o mínimo comprovado de não alocados. Isso é uma solução parcial, não uma solução viável do problema original. Timeout do solver é inconclusivo. A distância parcial só deve ser comparada entre soluções com o mesmo atendimento.

## Instâncias atuais e campanha final

Os 31 arquivos atuais de `instances/` têm 28 instâncias distintas utilizáveis, duas duplicatas e um arquivo contendo apenas um caminho externo. Duas entradas tinham os cabeçalhos na mesma linha. O preparador separa esses cabeçalhos em cópias, preserva todos os originais e não inventa os dados ausentes. Decisões e hashes estão em `instances/auditoria_atual.csv` e JSON. Os diretórios antigos removidos pelo usuário não foram restaurados.

```sh
python3 scripts/preparar_instancias.py
python3 scripts/executar_todas.py --instancias-dir instances/preparadas \
  -k 1 --metodo vnd --runs 30 -j 4 --out resultados/final_vnd
python3 scripts/executar_todas.py --instancias-dir instances/preparadas \
  -k 1 --metodo tabu --runs 30 -j 4 --out resultados/final_tabu
python3 scripts/gerar_entrega.py
make report
python3 scripts/empacotar.py
```

Os resultados finais foram executados **após a correção da N3**. São 28 instâncias × 2 métodos × 30 sementes = 1680 execuções; **3360 soluções iniciais/finais** foram verificadas independentemente com `Decimal`. Cada linha inclui custo inicial/final, melhoria, tempo de construção/busca, dispersão e número de locais utilizados. Os JSONs guardam toda a distribuição dos candidatos. O relatório contém tabelas completas e um exemplo de distribuição por escola/tipo.

Parâmetros: K=1, alpha=0,3, p=5, até 150 iterações, 50 sem melhoria, N3 a cada 20 iterações na tabu, seis reconstruções por chamada, tenure [5,12], sem limite temporal. Os métodos usam quatro processos cada; tempos são indicativos de máquina compartilhada. A pré-checagem é feita uma vez por lote de 30 sementes e não deve ser somada 30 vezes.

`--skip-existing` retoma uma campanha apenas com manifesto compatível. Se mudar binário, dados ou parâmetros, use outra pasta `--out`. `--resumo-only` apenas resume arquivos existentes. `--filter '*G1.txt'` seleciona entradas pelo nome. `make run-all` executa VND/K=1 com 30 sementes nas cópias preparadas.

A semente reproduz decisões no mesmo ambiente com `--tempo 0`. Plataformas, biblioteca C++ e versão do solver podem mudar trajetórias. Amostragem de N3 e listas restritas não permitem afirmar ótimo local completo ou ótimo global.

## Exemplo e correções

```sh
./alocacao --instancia entrega/exemplo8_K1.txt --tipos-por-escola 1 \
  --alpha 0 --n3-amostras 1000 --trace --relatorio --exato \
  --saida resultados/exemplo8_K1.json
```

O construtivo obtém **56 km**; N3 habilita M1 na escola E3 e reduz a distância para **42 km**, melhoria de **25%**, com todos atendidos. O orçamento maior de N3 é apenas didático. Veja `docs/exemplo8_K1.md` e o trace literal.

Foram corrigidos o aproveitamento de escolas recém-habilitadas em N3, a descoberta de instâncias no lote, retomadas incompatíveis e a proteção da entrada contra ambos os arquivos de exportação. Validação normal e com sanitizadores passou; registros em `docs/testes_atual.log.txt` e `docs/sanitizadores_atual.log.txt`. Auditoria em `docs/auditoria.md`.

Os resultados anteriores na árvore de trabalho são históricos e não fundamentam o relatório atual. O pacote final inclui apenas a campanha `final_*` e o exemplo atual. Scripts históricos de ablações continuam disponíveis, mas seus resultados precisam ser refeitos em outra pasta após mudanças do binário.

A submissão ao Classroom é feita pelo grupo. O pacote local é independente da publicação do repositório.

A verificação opcional de navegador está em `scripts/verificar_apresentacao.py` e requer Selenium, Firefox e geckodriver (dependências separadas das necessárias para os algoritmos). O registro está em `docs/verificacao_apresentacao.json`.
