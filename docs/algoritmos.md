# Especificação reproduzível

## Estado

`Instancia` armazena dados imutáveis em ordem de arquivo, capacidade Q, tipos e distâncias inteiras. `Solucao` contém `esc[i]`, `typeSlots[j]` (bitset de até K tipos), `carga[j]`, `porTipo[j][t]`, distância, excesso, não alocados e incompatíveis. Escola usada significa carga positiva; um slot habilitado pode ter carga zero. Atualizações N1/N2 mantêm esses acumuladores; `validar` recompõe tudo separadamente.

## Certificado

Seja d_t a demanda. Variáveis z_jt binárias e x_jt inteiras não negativas. Maximizar soma x, sujeito a soma_j x_jt ≤ d_t, soma_t x_jt ≤ Q_j, x_jt ≤ Q_j z_jt e soma_t z_jt ≤ K. O ótimo C* determina o mínimo n−C* de não alocados. Como não há restrições individuais além do tipo e a matriz é completa, essas contagens são suficientes para provar a viabilidade. A saída arredondada do solver é conferida em inteiros antes de ser usada. Resultado não ótimo/timeout é inconclusivo.

Para slots fixos, a verificação vira fluxo máximo: fonte→tipo (d_t), tipo→escola habilitada (n), escola→sorvedouro (Q_j). Isso evita contar duas vezes a mesma capacidade em K=2. Esse fluxo pequeno é implementado em C++, sem solver externo durante a busca.

## Construção: escolha de tipos

1. Para cada par (j,t), ordenar distâncias dos candidatos t até j. Seja q=min(Q_j,d_t); proximidade a_jt = média das q menores distâncias / max(1,d_max), usando as unidades inteiras internas.
2. Começar sem slots. Para cada adição admissível (escola com menos de K tipos), calcular o aumento g no fluxo máximo. Descartar g≤0.
3. Maximizar score(j,t) = g/d_t + g/Q_j − a_jt. A primeira parcela favorece cobertura relativa da demanda, a segunda aproveitamento de capacidade e a terceira proximidade.
4. RCL = pares com score ≥ score_max − alpha(score_max−score_min). Com alpha=0 selecionar o primeiro máximo em ordem escola/tipo de arquivo; com alpha>0 sortear uniformemente na RCL.
5. Repetir até alcançar C* ou não haver adição útil. Como a adição gulosa não desfaz escolhas iniciais em instâncias apertadas (especialmente em K=1), um impasse aciona `ajustarTipos`: uma busca local sobre `typeSlots` (adicionar tipo se `< K`, substituir tipo em uma escola ou permutar tipos entre duas escolas), priorizando tipos com déficit de atendimento no fluxo e desempatando pela menor soma de proximidades `a_jt`, com perturbação aleatória em platôs. Caso ainda não atinja C*, reinicia-se até quatro tentativas (uma em alpha=0) e, apenas como salvaguarda final, usam-se os slots do certificado. O CSV registra reinícios e fallback.

## Construção: candidatos e reparação

Calcular para cada candidato as duas escolas habilitadas com vaga mais próximas. Regret = segunda distância − primeira; apenas uma opção recebe prioridade infinita; nenhuma opção aguarda reparação. Selecionar maior regret (desempate pelo índice de arquivo em alpha=0), ou RCL da mesma forma com alpha>0. Regrets infinitos formam uma RCL própria. Alocar na escola de menor distância; empates usam ordem de arquivo. Recalcular opções afetadas quando uma escola lota.

Se houver não alocados, fazer busca em largura no grafo residual: candidato pendente→escola compatível; escola lotada→escola compatível com algum candidato que pode ser ejetado. Ao alcançar uma vaga, aplicar a cadeia de trás para frente. Uma escola é visitada uma vez por busca. É permitido ejetar um candidato de outro tipo em K=2. Cada cadeia aumenta atendimento em um. Quando não há caminho aumentante, atingiu-se o máximo para os slots; como a seleção assegurou C*, a construção alcança exatamente C*.

O exemplo de oito candidatos demonstra por que a reparação é necessária mesmo quando os slots têm capacidade suficiente.

## Avaliação

f(s)=D(s)+λ·excesso(s)+μ·(não_alocados(s)+incompatíveis(s)). Excesso é soma max(0,carga_j−Q_j). Não há custo de escola/sala aberta.

B=n·d_max é um limite superior para distância de qualquer alocação, inclusive parcial, pois todas as distâncias são não negativas. Inicialmente λ=μ=B+1 km. Uma unidade de violação então custa mais que qualquer alteração de distância. São parâmetros de escala, não estimativas empíricas de custo logístico. Avaliação penalizada usa `long double`; distâncias e deltas de distância permanecem inteiros.

K e compatibilidade são invariantes dos movimentos. Tabu admite excesso de capacidade e realocação para −1. A cada k=5 estados viáveis consecutivos, λ é dividido por dois, limitado inferiormente a max(1 unidade interna,d_max/10). A cada k estados inviáveis consecutivos, λ dobra, limitado a 16λ_inicial. μ permanece fixo. Violações consecutivas significam qualquer violação, incluindo candidatos não alocados nas instâncias impossíveis. A adaptação evita overflow numérico e estagnação no valor máximo/mínimo; o contador registra eventos de adaptação mesmo no limite.

O arquivo final é separado do estado corrente: só recebe soluções sem excesso e sem incompatibilidade, primeiro minimizando não alocados e depois distância. O certificado garante que o primeiro critério já é ótimo. Em instâncias viáveis isso é o melhor viável; em inviáveis é a melhor distância observada com a menor violação possível e capacidade respeitada. O custo exportado usa λ inicial, para manter comparabilidade, e as curvas registram λ corrente.

## Vizinhanças

- N1: realocar i às p escolas habilitadas mais próximas diferentes da atual. No tabu há também destino −1. Delta de distância é d_ib−d_ia; overflow muda apenas nas escolas origem/destino. Custo por avaliação O(1).
- N2: trocar duas escolas de candidatos do mesmo tipo, incluindo troca entre alocado e não alocado. Cargas e contagens de violações finais não mudam. Delta é d_ib+d_ha−d_ia−d_hb. Para cada arco origem→destino e tipo, guardar maior ganho (VND) ou quatro melhores (tabu, para alternativas não proibidas). Enumerar pares desses candidatos. Isso reaproveita a ideia eficiente do projeto original; não enumera todos os pares de candidatos. No tabu, a lista limitada pode omitir uma troca admissível de menor ganho.
- N3: adicionar/substituir tipo em uma escola ou trocar um tipo entre duas escolas. Gerar alternativas, embaralhar com o RNG e rejeitar via fluxo aquelas incapazes de manter C*. Avaliar até o orçamento de reconstruções. Liberar candidatos das escolas alteradas e dos tipos recém-habilitados em qualquer escola; preservar os demais e executar regret determinístico e reparação. A cadeia pode atingir escolas inicialmente preservadas. O contador N3 inclui tentativas de topologia, inclusive as rejeitadas pelo fluxo; não é diretamente equivalente ao contador de deltas N1/N2.

VND visita a ordem em `--viz`, aplica uma melhoria e reinicia em N1. `--ls first` aceita a primeira melhoria na enumeração; `best` seleciona a melhor no conjunto examinado. Para N2, a enumeração já é comprimida pelos ganhos; para N3, é amostrada. O critério first/best não altera o tabu, que precisa escolher a melhor opção admissível mesmo sem melhorar o estado corrente.

## Busca Tabu

Em toda iteração examinar N1 e N2 habilitadas. Examinar N3 a cada X iterações ou a cada X iterações de estagnação. Escolher menor delta penalizado admissível, inclusive positivo. Empates preservam a primeira alternativa examinada.

Após N1, proibir retorno de (candidato, escola deixada). Após N2, proibir o par não ordenado de candidatos. Após N3, proibir reintrodução de (escola, tipo removido). Tenure é uniforme inteiro em [tmin,tmax], inclusive; tmin=tmax dá tenure fixo. Movimento efetuado na iteração i fica proibido nas próximas tenure iterações. Aspiração ignora tabu somente se a solução resultante for viável e superar a melhor viável (ou produzir a primeira viável). O teste usa distância total e violações após o movimento composto.

Parar ao atingir máximo de iterações, limite de estagnação, tempo opcional ou ausência de movimentos admissíveis. Contadores de estagnação são atualizados pela melhora do arquivo final, não por melhora transitória da função penalizada. A curva inclui iteração zero e registra [iteração, melhor distância, distância corrente, não alocados do melhor, excesso corrente, λ corrente].

## Limitações conhecidas

Não é um algoritmo exato para distância e não fornece gap global. N3 é amostrada e p restringe N1; alpha=0 torna a construção determinística, mas a busca pode usar aleatoriedade. A garantia de capacidade depende do certificado exato e da reparação, por isso a construção completa é uma heurística com apoio de um pequeno modelo inteiro, explicitamente contabilizado. O tempo de pré-checagem aparece separado. O transporte opcional `--exato` só é exato para os slots finais fixados e requer solução completa.


## Revisão da entrega atual

A N3 libera também todos os candidatos dos tipos recém-habilitados, mesmo que estejam em escolas cujo conjunto de tipos não mudou. Isso permite ocupar uma escola antes vazia. O exemplo principal K=1 está em `docs/exemplo8_K1.md`; resultados atuais em `resultados/final_vnd` e `resultados/final_tabu`. K=1 e K=2 são casos exigidos, escolhidos na execução. As campanhas de K=2 estão em `resultados/final_k2_vnd` e `resultados/final_k2_tabu`.
