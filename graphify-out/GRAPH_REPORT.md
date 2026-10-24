# Graph Report - Trabalho1  (2026-10-22)

## Corpus Check
- Large corpus: 493 files · ~7,654,958 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 610 nodes · 977 edges · 23 communities (18 shown, 5 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 198 edges (avg confidence: 0.92)
- Token cost: 39,700 input · 7,550 output

## Community Hubs (Navigation)
- CLI & Benchmark Execution Logs
- Experiment Scripts & Ablation Campaign
- Standardized Benchmark Instances
- Raw Instance Datasets & Normalization
- Unit Tests & Sanitizer Verification
- Technical Report & Local Search
- Instance Model & Room Capacities
- Exact Feasibility Certificate & Flow
- VND, Tabu & Neighborhoods N1-N3
- Experiment Manifest & Configurations
- Type Selection & Local Repair (ajustarTipos)
- Solution State & Cost Evaluation
- Delivery Package Canonical Instances
- Convergence Curves & Comparisons
- End-to-End Integration Tests
- Room & School Data Structures
- Constructive Heuristic Statistics
- Local Search Statistics
- Convergence Trajectory Points
- Neighborhood Move Representation
- MILP Feasibility Certification (SciPy/HiGHS)

## God Nodes (most connected - your core abstractions)
1. `main()` - 190 edges
2. `main()` - 58 edges
3. `Instancia` - 49 edges
4. `Solucao` - 32 edges
5. `Parametros` - 28 edges
6. `construir()` - 18 edges
7. `README Principal: Localização de Locais de Prova (DCC136)` - 17 edges
8. `main()` - 15 edges
9. `alocarRegret()` - 14 edges
10. `EstatBL` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Função de Avaliação com Penalização Adaptativa de Excesso e Incompatibilidade` --rationale_for--> `Solucao`  [INFERRED]
  docs/relatorio.pdf → src/solucao.hpp
- `plots()` --shares_data_with--> `Gráfico de Convergência: VND vs Busca Tabu em 4 Instâncias K=2 (convergencia.png)`  [INFERRED]
  scripts/experimentos.py → resultados/convergencia.png
- `main()` --references--> `instancia_2 (1).txt (N=6798, M=20)`  [EXTRACTED]
  scripts/padronizar_instancias.py → instances/originais/instancia_2 (1).txt
- `main()` --references--> `instancia_base(1).txt (N=4744, M=15)`  [EXTRACTED]
  scripts/padronizar_instancias.py → instances/originais/instancia_base(1).txt
- `main()` --references--> `instancias1.txt (N=3696, M=14)`  [EXTRACTED]
  scripts/padronizar_instancias.py → instances/originais/instancias1.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Atendimento aos Requisitos do Enunciado do Trabalho 1 no Relatório e Resultados** — trabalho_1_2026_3_implementacao_1_requisitos_heuristica, docs_relatorio_relatorio_tecnico, docs_relatorio_exemplo8_e_casos_falha, docs_relatorio_campanha_experimental_ablacoes, resultados_convergencia_curvas_convergencia_k2 [EXTRACTED 1.00]
- **Suíte de Verificação, Sanitizadores e Validação Independente** — docs_testes_log_execucao, docs_sanitizadores_log_execucao, tests_core, tests_parser, tests_test_integration, scripts_validar [EXTRACTED 1.00]
- **Arquitetura de Busca Local (VND, Busca Tabu e Vizinhanças N1/N2/N3)** — docs_relatorio_vizinhancas_n1_n2_n3, docs_relatorio_vnd_busca_tabu, docs_relatorio_funcao_avaliacao_penalidade_adaptativa, src_busca_local_buscalocal_executar, src_solucao_deltamover, src_solucao_deltatroca [INFERRED 0.95]
- **Arquitetura de Busca Local (VND, Busca Tabu, Vizinhanças N1/N2/N3 e Penalização Adaptativa)** — docs_algoritmos_vizinhancas_n1_n2_n3, docs_algoritmos_funcao_penalizada, src_busca_local_buscalocal, src_busca_local_buscalocal_executar, src_solucao_deltamover, src_solucao_deltatroca [INFERRED 0.95]
- **Pipeline Construtivo com Certificado ILP, Escolha de Tipos, Regret e Reparação BFS** — docs_algoritmos_certificado_ilp, docs_algoritmos_escolha_tipos_rcl, docs_algoritmos_regret_reparacao, src_exato_prechecar, src_exato_fluxotipos, src_construtivo_construir, src_construtivo_alocarregret, src_construtivo_reparar [INFERRED 0.95]
- **Pipeline Construtivo Guloso Randomizado com Regret e Reparo por Fluxo** — docs_relatorio_construcao_gulosa_regret_reparo, docs_relatorio_certificacao_ilp_fluxo, src_construtivo_construir, src_construtivo_alocarregret, src_construtivo_reparar, src_exato_fluxotipos [INFERRED 0.95]

## Communities (23 total, 5 thin omitted)

### Community 0 - "CLI & Benchmark Execution Logs"
Cohesion: 0.01
Nodes (171): instancia2__K1__n1.console.txt (INVIAVEL), instancia2__K1__n2.console.txt (INVIAVEL), instancia2__K1__n3.console.txt (INVIAVEL), instancia2__K1__tabu_a03.console.txt (INVIAVEL), instancia2__K1__tabu_t10_20.console.txt (INVIAVEL), instancia2__K1__tabu_t10.console.txt (INVIAVEL), instancia2__K1__tabu_t3.console.txt (INVIAVEL), instancia2__K1__vnd_a03.console.txt (INVIAVEL) (+163 more)

### Community 1 - "Experiment Scripts & Ablation Campaign"
Cohesion: 0.05
Nodes (56): Reparo Local de Tipos por Escola (ajustarTipos) sem Fallback ao Certificado, Construção Gulosa Randomizada de Tipos (Score e RCL), Especificação Reproduzível dos Algoritmos, Alocação por Regret e Reparação por Cadeia Aumentante em BFS, Vizinhanças N1 (Realocação), N2 (Troca), N3 (Tipos) em VND e Busca Tabu, Registro de Performance VND Longa na Instância A (K=1, 2740 iterações), Construção Gulosa Randomizada em Duas Fases com Regret e Reparo por Caminhos Aumentantes, Estruturas de Vizinhança N1 (Realocação), N2 (Troca com Cache de Pares) e N3 (Alteração de Tipos) (+48 more)

### Community 2 - "Standardized Benchmark Instances"
Cohesion: 0.07
Nodes (28): Exemplo Manual Passo a Passo (8 Candidatos, 3 Escolas, K=2), Trace Literal do Exemplo de 8 Candidatos (49 km -> 42 km), Campanha Experimental (2640 Execuções, Ablações e Validação Independente), Roteiro de Apresentação (10 minutos), Instruções do Pacote de Entrega Local (LEIA-ME.txt), Catálogo de 41 Instâncias Padronizadas da Turma DCC136, Dissertação de Oliveira (PUC-Rio, 2021), README Principal: Localização de Locais de Prova (DCC136) (+20 more)

### Community 3 - "Raw Instance Datasets & Normalization"
Cohesion: 0.06
Nodes (21): Certificado ILP de Atendimento Máximo e Fluxo Máximo, Log de Testes com AddressSanitizer e UndefinedBehaviorSanitizer, Log de Execução da Suíte de Testes Unitários e Integração, pairKey(), preChecar(), quote(), Temp, path (+13 more)

### Community 4 - "Unit Tests & Sanitizer Verification"
Cohesion: 0.04
Nodes (40): instancia1 2.txt (N=100, M=5), instancia1.txt (N=2550, M=10), instancia2 2.txt (N=109, M=5), instancia2.txt (N=2550, M=10), instancia_1 (1)(1).txt (N=370, M=12), instancia_1 (1).txt (N=5557, M=18), instancia_1(2).txt (N=4213, M=15), instancia_1(3).txt (N=316, M=12) (+32 more)

### Community 5 - "Technical Report & Local Search"
Cohesion: 0.04
Nodes (44): instancia_01_prof_A.txt (N=4518, M=15), instancia_02_prof_B.txt (N=4442, M=15), instancia_03_pequena_100.txt (N=100, M=5), instancia_04_pequena_109.txt (N=109, M=5), instancia_05_turma_2550_1.txt (N=2550, M=10), instancia_06_turma_2550_2.txt (N=2550, M=10), instancia_07_malvacini_1.txt (N=5557, M=18), instancia_08_malvacini_2.txt (N=6798, M=20) (+36 more)

### Community 6 - "Instance Model & Room Capacities"
Cohesion: 0.07
Nodes (26): Relatório Técnico: Construção gulosa randomizada e busca tabu para a localização de locais de prova, Estratégias de Busca Local: VND e Busca Tabu com Critério de Aspiração, Gráfico de Convergência: Média da Melhor Distância por Iteração em K=2 (VND vs Tabu), BuscaLocal, p, Parametros, adaptar, alpha (+18 more)

### Community 7 - "Exact Feasibility Certificate & Flow"
Cohesion: 0.13
Nodes (14): binary_sha256, configs, instances, instancia2.txt, instancia_A.txt, instancia_B.txt, Modelo_de_Instancia.txt, max_iter (+6 more)

### Community 8 - "VND, Tabu & Neighborhoods N1-N3"
Cohesion: 0.20
Nodes (7): exemplo8.txt (N=8, M=3), Instancia1_G1.txt (N=4518, M=15), instancia2.txt (N=2550, M=10), Instancia2_G1.txt (N=4442, M=15), instancia_A.txt (N=4518, M=15), instancia_B.txt (N=4442, M=15), Modelo_de_Instancia.txt (N=109, M=5)

### Community 9 - "Experiment Manifest & Configurations"
Cohesion: 0.25
Nodes (9): Gráfico de Convergência: VND vs Busca Tabu em 4 Instâncias K=2 (convergencia.png), Convergência instancia2 / K=2 (VND ~10700 km vs Tabu ~10010 km), Convergência instancia_A / K=2 (VND ~29340 km vs Tabu ~28720 km), Convergência instancia_B / K=2 (VND ~17840 km vs Tabu ~17290 km), Métrica de Convergência: Melhor Distância (km) vs Iterações (0 a 150), Convergência Modelo_de_Instancia / K=2 (VND ~371 km vs Tabu ~323 km), Curva de Convergência Busca Tabu (Escape de Ótimos Locais com Quedas a cada ~15 Iterações), Curva de Convergência VND (Descida Monotônica / Estagnação em Ótimo Local) (+1 more)

### Community 11 - "Solution State & Cost Evaluation"
Cohesion: 0.32
Nodes (3): Sala, cap, id

### Community 12 - "Delivery Package Canonical Instances"
Cohesion: 0.25
Nodes (8): EstatBL, ajustesLambda, aspiracoes, avaliacoes, iteracoes, iteracoesInviaveis, movimentos, tabusRejeitados

### Community 13 - "Convergence Curves & Comparisons"
Cohesion: 0.25
Nodes (7): Ponto, atualDist, excessoAtual, iter, lambda, melhorDist, naoAlocados

### Community 14 - "End-to-End Integration Tests"
Cohesion: 0.25
Nodes (8): Move, aspiration, b, delta, h, i, kind, next

### Community 15 - "Room & School Data Structures"
Cohesion: 0.25
Nodes (8): Run, construction, final, initial, search, seed, tc, tls

### Community 17 - "Local Search Statistics"
Cohesion: 0.33
Nodes (4): Certificado, atendidos, quotas, slots

### Community 18 - "Convergence Trajectory Points"
Cohesion: 0.33
Nodes (4): Delta, dist, excesso, naoAlocados

### Community 19 - "Neighborhood Move Representation"
Cohesion: 0.40
Nodes (5): EstatConstr, ajustesTipos, fallback, reinicios, reparos

## Knowledge Gaps
- **306 isolated node(s):** `kind`, `i`, `b`, `h`, `delta` (+301 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 372 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `CLI & Benchmark Execution Logs` to `Experiment Scripts & Ablation Campaign`, `Raw Instance Datasets & Normalization`, `Technical Report & Local Search`, `Instance Model & Room Capacities`?**
  _High betweenness centrality (0.513) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `main()` (e.g. with `construir()` and `preChecar()`) actually correct?**
  _`main()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `kind`, `i`, `b` to the rest of the system?**
  _306 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CLI & Benchmark Execution Logs` be split into smaller, more focused modules?**
  _Cohesion score 0.011695906432748537 - nodes in this community are weakly interconnected._
- **Why does `Instancia` connect `Experiment Scripts & Ablation Campaign` to `Solution State & Cost Evaluation`, `Raw Instance Datasets & Normalization`, `Technical Report & Local Search`, `Instance Model & Room Capacities`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Should `Experiment Scripts & Ablation Campaign` be split into smaller, more focused modules?**
  _Cohesion score 0.05126452494873548 - nodes in this community are weakly interconnected._
- **Why does `README Principal: Localização de Locais de Prova (DCC136)` connect `Standardized Benchmark Instances` to `Experiment Scripts & Ablation Campaign`, `Raw Instance Datasets & Normalization`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._