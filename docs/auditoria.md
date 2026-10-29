# Auditoria da entrega atual

O PDF foi lido integralmente. Os requisitos são: construtivo viável quando possível, vizinhança, busca local, avaliação justificada, múltiplas execuções quando aleatório, custos inicial/final, melhoria, tempo, locais utilizados, distribuição dos candidatos, exemplo pequeno, caso de falha, relatório LaTeX/SBC e apresentação oral de 8–12 minutos.

## Correções aplicadas

- **N3 / escola vazia:** habilitar um tipo não reconsiderava os candidatos de outras escolas. A proposta era neutra e o VND a rejeitava. Agora os candidatos dos tipos recém-habilitados são liberados para reconstrução. Teste em `tests/core.cpp` e exemplo 56→42 km.
- **Exportação:** a proteção verificava somente o nome pedido, embora o programa escreva `.json` e `.csv`. Agora compara ambos os destinos, incluindo equivalência de arquivos. Teste de regressão na CLI.
- **Lote:** o glob `instancia_*.txt` ignorava a maioria das entradas atuais; passou a `*.txt`. Manifesto impede retomada com binário/dados/parâmetros diferentes. Falhas retornam código não zero. Resumo inclui desvio padrão, máximo, locais e tempo de construção.
- **Portabilidade:** o validador localiza instâncias preparadas depois de mover a entrega.
- **Dados:** cópias com cabeçalhos separados, sem alteração de valores, deduplicação documentada e exclusão do arquivo que só contém um caminho externo. Originais intactos.
- **Documentação:** K=1 e K=2 são parâmetros exigidos na execução, com tipos escolhidos pelo algoritmo. O prazo atualizado é 26/10/2026 às 10h; o relatório e o slide 12 incluem o GitHub. Removidas afirmações antigas sobre 41 instâncias e ausência de repositório Git. Relatório, apresentação e pacote usam apenas resultados finais corrigidos.

## Evidência

- `docs/testes_atual.log.txt`: testes C++ de parser/núcleo e seis testes Python de integração aprovados.
- `docs/sanitizadores_atual.log.txt`: núcleo e integração aprovados com AddressSanitizer/UndefinedBehaviorSanitizer.
- `resultados/final_validacao.json`: 3360 execuções e 6720 soluções iniciais/finais validadas independentemente; hashes da campanha.
- `docs/campanha_final_vnd.log.txt` e `docs/campanha_final_tabu.log.txt`: 28/28 lotes concluídos por método, sem falhas.
- `instances/auditoria_atual.csv`: 31 entradas, 28 prontas, duas duplicatas e uma sem dados.

## Limites que permanecem explícitos

O certificado inteiro é uma dependência, não uma prova de distância ótima. Casos estruturalmente inviáveis têm atendimento parcial, identificado. N3 é amostrada e N1/N2 usam restrições de candidatos. Tempos usam máquina compartilhada e paralelismo. A aceitação de HTML no Classroom não foi confirmada; a entrega inclui os slides em PDF.

## Revisão dos requisitos corrigidos

Campanha K=1 e K=2 nos mesmos 28 arquivos e sementes 1–30, com VND executando até o ótimo local (uma iteração = uma exploração de Nk; teto de segurança 10^6 nunca atingido) e tabu com até 1000 iterações / 200 sem melhora, validada independentemente. Os resultados preliminares com teto de 150 iterações estão preservados em `resultados/historico_iter150/`. As quatro instâncias inviáveis em K=1 têm atendimento completo em K=2; I2 G2 passa de 96 para 109 candidatos. Dispersão inicial e final, pré-checagem integral por lote e total amortizado constam das tabelas. Nomes de exibição seguem I1 G<n>/I2 G<n>. Os slides incluem motivação, dificuldades e o caso real de piores ótimos locais do VND (I2 G8). O relatório e o CSV são incorporados ao HTML; o PDF dos slides é exportado e validado pelo verificador de navegador.
