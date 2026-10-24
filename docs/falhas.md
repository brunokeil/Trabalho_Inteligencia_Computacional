# Onde a abordagem falha ou perde qualidade

## Inviabilidade estrutural: Modelo, K=1

Há seis tipos com demanda positiva e cinco escolas. Como uma escola só pode receber um tipo, alguma prova fica sem escola. Capacidade total 121 > 109 não resolve essa incompatibilidade. O modelo inteiro comprova máximo de 91 candidatos atendidos: pelo menos **18 não alocados**, mesmo com qualquer heurística ou quantidade de tempo. O limite de 18 é mais forte que simplesmente deixar de fora o menor tipo (17), pois as capacidades precisam também acomodar os demais tipos.

A implementação anuncia `INVIAVEL COMPROVADA` antes de construir, mantém as capacidades e exporta os candidatos não alocados com `assign=-1`. Isso é uma solução parcial documentada, não uma solução viável. K=2 elimina essa inviabilidade e atende todos os 109.

## Capacidade por tipo: instancia2, K=1

A capacidade total é 3000 para 2550 candidatos, mas a distribuição das capacidades entre escolas não permite separar todos os tipos sem compartilhar escolas. O ILP comprova máximo de **2530**, isto é, 20 não alocados mínimos. K=2 atende 2550. Esse caso mostra por que testar apenas demanda total contra capacidade total não basta.

## Instância viável difícil: A

A ocupa 4518/4830 = 93,54% da capacidade. Mudanças aparentemente boas podem deixar um tipo sem cobertura ou impedir a alocação do último candidato. Muitas modificações N3 são rejeitadas pelo fluxo; o guloso pode precisar dos slots de segurança do certificado. Esse apoio deve ser declarado como componente do método, não escondido como pré-processamento gratuito.

Listas de p escolas e amostragem de N3 deixam movimentos de fora. O limite experimental de 150 iterações pode interromper antes da convergência. Uma tabu mais longa pode melhorar a qualidade, mas não há garantia de ótimo global. A tabela de ablações e os contadores de fallback, avaliações e iterações permitem avaliar esses compromissos.

## Limite da referência exata

Transporte exato otimiza a alocação **condicionada aos tipos escolhidos**. Um gap zero contra essa referência não certifica que os tipos são bons. A versão auditada congelava tipos sem olhar distâncias; corrigimos essa decisão, mas a nova N3 ainda é limitada/amostrada.

## Cuidados ao interpretar experimentos

Distância parcial não deve ser comparada com distância completa: excluir pessoas pode reduzir a soma artificialmente. Compare somente configurações com a mesma instância, K e atendimento. Min/mean/std/max não substituem um teste de significância; os resultados apresentados são descritivos. Tempos foram medidos em máquina de uso compartilhado, sem isolamento de CPU, e não devem ser tratados como benchmark de hardware.
