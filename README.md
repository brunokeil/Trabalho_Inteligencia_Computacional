# DCC136 — Localização de locais de prova — 2026.3

Implementação C++17 de construção gulosa randomizada, VND e Busca Tabu. O programa recebe **K=1 ou K=2 em tempo de execução** e escolhe os tipos de prova de cada escola, conforme as correções da professora. Ambos os casos são avaliados. Prazo atualizado: **26/10/2026 às 10h**. Repositório: [brunokeil/Trabalho_Inteligencia_Computacional](https://github.com/brunokeil/Trabalho_Inteligencia_Computacional).

## Arquivos para entregar

- `entrega/Trabalho1-entrega.zip`: pacote com fontes, dados, resultados e documentação.
- `docs/relatorio.pdf`: relatório técnico no modelo SBC.
- `docs/relatorio.tex`: fonte LaTeX; tabelas e estilo SBC estão em `docs/`.
- `docs/apresentacao.pdf`: versão de 12 páginas para apresentação em PDF.
- `docs/apresentacao.html`: 12 slides offline para aproximadamente dez minutos, com notas, cronômetro, exemplo interativo e seletor de resultados.
- `resultados/final_resumo.csv`: 112 linhas de resumo das **3360 execuções** (28 instâncias × 2 valores de K × 2 métodos × 30 sementes), com dispersão inicial/final e pré-checagem.
- `resultados/final_vnd/`, `resultados/final_tabu/`, `resultados/final_k2_vnd/` e `resultados/final_k2_tabu/`: JSON/CSV completos, atribuições, distribuição por escola/tipo, curvas, logs e manifestos.

Abra o HTML diretamente no navegador. Use as setas para navegar, `N` para o roteiro e `F` para tela cheia. O botão **PDF** abre a impressão de todos os slides. O exemplo do slide 8 permite alternar construção e melhoria. O CSV e o relatório estão incorporados ao HTML: os downloads funcionam mesmo movendo somente esse arquivo para outra pasta. A conexão de rede é necessária apenas para abrir o GitHub. O PDF preserva um resultado fixo do seletor (I2 G2, ambos os valores de K) e o exemplo de 56 → 42 km; o HTML permite explorar as demais instâncias.

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
  --seed 1 --max-iter 1000 --sem-melhora 200 \
  --saida resultados/meu_teste.json --relatorio
python3 scripts/validar.py resultados/meu_teste.json
```

`--saida` gera JSON e CSV. O JSON registra soluções inicial/final, IDs originais, cargas, ocupação e convergência de cada semente. `assign` usa índices base zero, na ordem do arquivo; `-1` significa não alocado. `typeSlots` é uma máscara de bits sobre `typeNames`.

O modelo inteiro SciPy/HiGHS certifica o número máximo de atendidos e fornece uma salvaguarda de tipos ao construtivo; não otimiza distância. Instâncias estruturalmente inviáveis são marcadas `infeasible`, com o mínimo comprovado de não alocados. Isso é uma solução parcial, não uma solução viável do problema original. Timeout do solver é inconclusivo. A distância parcial só deve ser comparada entre soluções com o mesmo atendimento.

## Instâncias atuais e campanha final

Os 31 arquivos atuais de `instances/` têm 28 instâncias distintas utilizáveis, duas duplicatas e um arquivo contendo apenas um caminho externo. Duas entradas tinham os cabeçalhos na mesma linha. O preparador separa esses cabeçalhos em cópias, preserva todos os originais e não inventa os dados ausentes. Decisões e hashes estão em `instances/auditoria_atual.csv` e JSON.

```sh
python3 scripts/preparar_instancias.py
sh scripts/campanha_final.sh   # VND até o ótimo local; tabu 1000 it./200 sem melhora; K=1 e K=2
python3 scripts/gerar_entrega.py
make report
python3 scripts/verificar_apresentacao.py --driver /caminho/geckodriver --export-pdf
python3 scripts/empacotar.py
```

Os resultados finais foram executados **após a correção da N3**. São 28 instâncias × 2 valores de K × 2 métodos × 30 sementes = 3360 execuções; **6720 soluções iniciais/finais** foram verificadas independentemente com `Decimal`. Cada linha inclui custo inicial/final, melhoria, tempo de pré-checagem/construção/busca, dispersão inicial e final e número de locais utilizados. Os JSONs guardam toda a distribuição dos candidatos. O relatório contém tabelas completas e distribuições por escola/tipo de I1 G1 (K=1) e I2 G2 (K=2).

Parâmetros: K=1 e K=2, alpha=0,3, p=5, VND com melhor melhoria até o ótimo local (uma iteração = uma exploração da vizinhança corrente; teto de segurança 10^6), tabu com até 1000 iterações e 200 sem melhoria e N3 a cada 20 iterações, seis reconstruções por chamada, tenure [5,12], sem limite temporal. VND e tabu rodam simultaneamente com quatro processos cada; tempos são indicativos de máquina compartilhada. A pré-checagem é feita uma vez por lote de 30 sementes, para cada método e K. O resumo informa seu custo integral e o total amortizado: construção média + busca média + (leitura + pré-checagem)/30. Isso inclui o solver sem multiplicar seu custo por 30. Os tempos não são de CPU isolada nem permitem comparar desempenho absoluto entre campanhas executadas em momentos diferentes.

Em K=1, 24 das 28 instâncias admitem atendimento completo; em K=2, todas as 28. I2 G2 tem 109 candidatos, seis tipos e cinco escolas: o atendimento certificado passa de 96 para 109. Não se comparam diretamente distâncias parciais e completas. O fallback de tipos foi usado em 0 de 1680 construções de K=1 e em 0 de 1680 de K=2; a certificação por MILP continua obrigatória.

`--skip-existing` retoma uma campanha apenas com manifesto compatível. Se mudar binário, dados ou parâmetros, use outra pasta `--out`. `--resumo-only` apenas resume arquivos existentes. `--filter '*G1.txt'` seleciona entradas pelo nome. `make run-all` executa as quatro campanhas finais nas cópias preparadas. A campanha anterior com teto de 150 iterações, que interrompia o VND antes do ótimo local, está em `resultados/historico_iter150/` apenas como registro.

A semente reproduz decisões no mesmo ambiente com `--tempo 0`. Plataformas, biblioteca C++ e versão do solver podem mudar trajetórias. Amostragem de N3 e listas restritas não permitem afirmar ótimo local completo ou ótimo global.

## Exemplo e correções

```sh
./alocacao --instancia entrega/exemplo8_K1.txt --tipos-por-escola 1 \
  --alpha 0 --n3-amostras 1000 --trace --relatorio --exato \
  --saida resultados/exemplo8_K1.json
```

O construtivo obtém **56 km**; N3 habilita M1 na escola E3 e reduz a distância para **42 km**, melhoria de **25%**, com todos atendidos. O orçamento maior de N3 é apenas didático. Veja `docs/exemplo8_K1.md` e o trace literal.

A correção de N3 libera candidatos dos tipos recém-habilitados, inclusive em escolas inalteradas, para aproveitar escolas antes vazias. As correções de infraestrutura incluem descoberta de todos os nomes `.txt` (em vez de apenas `instancia_*.txt`), manifesto com hashes de entradas e binário para impedir retomadas incompatíveis, retorno de erro quando há falhas, localização das instâncias pelo validador após mover a entrega e proteção contra sobrescrita da entrada pelos dois arquivos de exportação, incluindo aliases de arquivos. Validação normal e com sanitizadores passou; registros em `docs/testes_atual.log.txt` e `docs/sanitizadores_atual.log.txt`. Auditoria em `docs/auditoria.md`.

Os resultados anteriores na árvore de trabalho são históricos e não fundamentam o relatório atual. O pacote final inclui apenas a campanha `final_*` e o exemplo atual. Scripts históricos de ablações continuam disponíveis, mas seus resultados precisam ser refeitos em outra pasta após mudanças do binário.

A verificação opcional de navegador está em `scripts/verificar_apresentacao.py` e requer Selenium, Node.js, Firefox, geckodriver e PyMuPDF para conferir o PDF (dependências separadas das necessárias para os algoritmos). O registro está em `docs/verificacao_apresentacao.json`. `--export-pdf` gera `docs/apresentacao.pdf` por impressão do Firefox headless. `make report` também atualiza o PDF do relatório incorporado ao HTML. O enunciado local não define formato dos slides; a aceitação de HTML no Classroom não foi confirmada, por isso a entrega inclui o PDF.
