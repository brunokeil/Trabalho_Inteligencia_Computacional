# DCC136 — Localização de locais de prova

Projeto em C++17 para DCC136 / UFJF / 2026.3: construção gulosa randomizada, VND e Busca Tabu. O algoritmo escolhe os tipos hospedados pelas escolas e a alocação dos candidatos. Prazo informado: **26/10/2026, 10h00**.

## Compilar e executar

Requisitos: compilador C++17, Make, Python 3.9+ com NumPy/SciPy. Matplotlib é usado somente nos gráficos. Testado com Apple Clang 21, Python 3.9, NumPy 1.24.2, SciPy 1.11.3 e Matplotlib 3.7.2 em macOS arm64. A integração da pré-checagem usa `mkstemp`/shell POSIX: macOS, Linux ou WSL.

```sh
python3 -m pip install -r requirements.txt
make -j4
./alocacao --instancia entrega/instancia_A.txt --tipos-por-escola 2 \
  --seed 1 --runs 30 --alpha 0.3 --metodo tabu --ls best \
  --saida resultados/meu_experimento.json --relatorio
```

`--saida x.json` ou `x.csv` gera **ambos**: CSV tabular e JSON com todas as soluções iniciais/finais, IDs originais, ocupações, certificado e curvas. Os índices de `assign` no JSON são base zero, na ordem do arquivo; `-1` significa não alocado. `candidateIds` e `schoolIds` permitem recuperar os identificadores originais. `typeSlots` é uma máscara de bits sobre `typeNames` (uma representação compacta do conjunto).

```sh
./alocacao --help
./alocacao --instancia entrega/Modelo_de_Instancia.txt --tipos-por-escola 1 --saida resultados/inviavel.json
python3 scripts/validar.py resultados/inviavel.json
make test
```

Parâmetros adicionais: `--p 5`, `--max-iter 300`, `--sem-melhora 80`, `--tmin 5 --tmax 12`, `--n3-periodo 20`, `--n3-amostras 6`, `--adaptar 5`, `--tempo 0`, `--viz 123`, `--sem-busca`, `--trace`, `--exato`. O parâmetro `--tipos-por-escola {1|2}` é obrigatório em toda execução. O exemplo com caminho posicional da instância continua aceito. Os antigos custos de sala/escola foram retirados do objetivo.

A mesma semente e os mesmos parâmetros reproduzem decisões no mesmo ambiente, usando limite de iterações e `--tempo 0`. Tempos medidos naturalmente variam. Limite temporal pode interromper em iterações diferentes, e distribuições/shuffle da biblioteca C++ ou certificados de outra versão do solver podem mudar a trajetória; o manifesto registra o ambiente. Em `--runs`, a execução r usa `seed+r`, começando em r=0.

## Modelo e precisão

- Capacidade de escola = soma das salas. Salas são dados de entrada, não decisões. **Não implementa a variante de um tipo por sala.**
- K é 1 ou 2. Não há custos de abertura nem coordenadas na distância; latitude/longitude são apenas lidas/validadas.
- Distâncias não negativas em formato decimal de até seis casas são armazenadas exatamente em inteiros de milionésimos de km (1 mm). Mais casas causam erro, nunca arredondamento silencioso.
- CEP é string. IDs são preservados; a matriz usa exclusivamente a ordem do arquivo.
- Arquivos vazios, campos ausentes, dimensões incorretas, IDs repetidos e capacidades inválidas são rejeitados com mensagem e código 1.

A pré-checagem resolve **maximização do número atendido** em um ILP agregado com no máximo 90 binárias e 90 contagens inteiras nas instâncias fornecidas. O solver SciPy/HiGHS é uma dependência explícita e é usado somente para certificar capacidade e fornecer uma atribuição de tipos de segurança; não otimiza a distância. Um timeout de 120 s é reportado como **inconclusivo**, nunca como inviável.

| Instância | n | m | Capacidade | Utilização | Não alocados mínimos K=1 | K=2 |
|---|---:|---:|---:|---:|---:|---:|
| Modelo | 109 | 5 | 121 | 90,08% | 18 | 0 |
| instancia2 | 2550 | 10 | 3000 | 85,00% | 20 | 0 |
| A | 4518 | 15 | 4830 | 93,54% | 0 | 0 |
| B | 4442 | 15 | 5260 | 84,45% | 0 | 0 |

Casos inviáveis são anunciados **antes da construção**. O programa retorna código 0, relatório marcado `infeasible`, capacidade respeitada e o número mínimo comprovado de não alocados. Entre soluções com esse atendimento, devolve a menor distância encontrada; não afirma otimalidade global da distância. Distâncias de soluções que deixam pessoas de fora não devem ser comparadas diretamente às de soluções completas.

## Algoritmos e reaproveitamento

O código mantém os módulos do projeto auditado. Foram reaproveitados representação por vetor, regret/RCL, deltas de realocação, ganhos por pares de escolas para troca, controle VND e o transporte por caminhos aumentantes. A antiga escolha de tipos escondida no parser tornou-se uma fase explícita da construção; salas abertas deixaram de participar do custo. As cadeias agora reparam capacidade compartilhada, inclusive deslocando candidatos de tipos diferentes.

Veja [descrição reproduzível](docs/algoritmos.md), [exemplo manual](docs/exemplo8.md), [casos de falha](docs/falhas.md) e [roteiro de apresentação](docs/slides.md).

## Experimentos

```sh
python3 scripts/experimentos.py
# Retoma arquivos já existentes somente com o mesmo manifesto/binário.
python3 scripts/experimentos.py --resumo-only
```

São 4 instâncias × 2 valores de K × 11 configurações × 30 sementes = **2640 execuções**. As configurações cobrem alpha=0/0,3/0,7, first/best no VND, N1/N2/N3 isoladas, VND/tabu e três alternativas de tenure além de [5,12]. Todos usam 150 iterações máximas, 50 sem melhoria, p=5, N3 a cada 15 iterações e orçamento de quatro reconstruções por chamada. O limite comum é de iterações, não de avaliações ou tempo; as três medidas são registradas. VND pode terminar antes; com N3 amostrada não se afirma ótimo local da vizinhança completa.

Saídas em `resultados/`: `execucoes.csv`, `resumo.csv`, `resumo.md`, `manifest.json`, JSON/CSV de cada configuração, `melhores/`, `convergencia.pdf` e PNG. O validador Python relê a instância e usa `Decimal`, sem reutilizar os deltas do C++. Ele é executado automaticamente para **cada solução inicial e final**. O CSV contém tempos de construção/busca separados; pré-checagem é custo único compartilhado pelas 30 execuções, não deve ser somada 30 vezes.

## Execução em lote de todas as instâncias (`instances/`)

As 41 instâncias únicas compartilhadas pela turma foram limpas, validadas e padronizadas em `instances/` (com os 52 downloads originais preservados em `instances/originais/` e mapeamento em `instances/manifesto.csv` e `instances/README.md`).

Para executar todas as instâncias em lote:

```sh
# Via Makefile (usa 4 processos em paralelo):
make run-all

# Via script Python com opções avançadas:
python3 scripts/executar_todas.py -k 1,2 -j 4 --metodo vnd --runs 1

# Exemplos com filtros ou retomada:
python3 scripts/executar_todas.py --filter "*malvacini*"
python3 scripts/executar_todas.py --skip-existing
python3 scripts/executar_todas.py --resumo-only
```

Os resultados consolidados são gravados em `resultados/todas_instancias/resumo.csv` e `resultados/todas_instancias/resumo.md`.

`docs/relatorio.tex` contém a estrutura SBC em português, decisões implementadas e tabelas geradas. Para atualizar/compilar:

```sh
python3 scripts/tabelas_relatorio.py
cd docs
pdflatex -interaction=nonstopmode -halt-on-error relatorio.tex
pdflatex -interaction=nonstopmode -halt-on-error relatorio.tex
```

O estilo SBC foi obtido do [espelho do SBGames](https://www.sbgames.org/arquivos/Template_SBC/template-latex/sbc-template.sty), consultado em 09/10/2026. A referência acadêmica é a [dissertação de Oliveira, PUC-Rio, 2021](https://www.maxwell.vrac.puc-rio.br/52465/52465.PDF), orientada por Rafael Martinelli Pinto e coorientada por Bruno Milanez.

## Histórico e publicação

A criação de `.git` nesta pasta foi bloqueada pelo ambiente de execução. Os commits foram feitos em uma cópia temporária e exportados para `entrega/historico.bundle`. Para recuperar o histórico em uma pasta normal:

```sh
git clone entrega/historico.bundle ../Trabalho1-git
```

O bundle contém fontes, testes, documentação e resumo dos experimentos; os resultados brutos permanecem nesta entrega e podem ser reproduzidos pelo script. **GitHub pendente:** a autenticação `gh` disponível estava inválida, e falta definir/confirmar a URL de destino. Não há URL fictícia no relatório. Após autenticar e configurar o remoto, enviar os commits e preencher `docs/repositorio.tex`.

As versões efetivamente usadas estão fixadas em `requirements-tested.txt`. `make test-sanitize` repete os testes do núcleo e da CLI com AddressSanitizer/UndefinedBehaviorSanitizer. Os registros estão em `docs/testes.log.txt` e `docs/sanitizadores.log.txt`.

Além da campanha limitada a 150 iterações, `resultados/performance_A.json` registra uma busca VND em A/K=1 com limite de 5000: encerramento em 2740 iterações, aproximadamente 1,012 s de busca, 27323,5365 km. N3 continua amostrada; esse encerramento não prova ótimo local da vizinhança completa.
