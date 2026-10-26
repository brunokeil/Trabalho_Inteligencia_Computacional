# Auditoria da entrega atual

O PDF foi lido integralmente. Os requisitos são: construtivo viável quando possível, vizinhança, busca local, avaliação justificada, múltiplas execuções quando aleatório, custos inicial/final, melhoria, tempo, locais utilizados, distribuição dos candidatos, exemplo pequeno, caso de falha, relatório LaTeX/SBC e apresentação oral de 8–12 minutos.

## Correções aplicadas

- **N3 / escola vazia:** habilitar um tipo não reconsiderava os candidatos de outras escolas. A proposta era neutra e o VND a rejeitava. Agora os candidatos dos tipos recém-habilitados são liberados para reconstrução. Teste em `tests/core.cpp` e exemplo 56→42 km.
- **Exportação:** a proteção verificava somente o nome pedido, embora o programa escreva `.json` e `.csv`. Agora compara ambos os destinos, incluindo equivalência de arquivos. Teste de regressão na CLI.
- **Lote:** o glob `instancia_*.txt` ignorava a maioria das entradas atuais; passou a `*.txt`. Manifesto impede retomada com binário/dados/parâmetros diferentes. Falhas retornam código não zero. Resumo inclui desvio padrão, máximo, locais e tempo de construção.
- **Portabilidade:** o validador localiza instâncias preparadas depois de mover a entrega.
- **Dados:** cópias com cabeçalhos separados, sem alteração de valores, deduplicação documentada e exclusão do arquivo que só contém um caminho externo. Originais intactos.
- **Documentação:** K=1 é o modelo principal; K=2 é extensão. O prazo informado é o do PDF. Removidas afirmações antigas sobre 41 instâncias e ausência de repositório Git. Relatório, apresentação e pacote usam apenas resultados finais corrigidos.

## Evidência

- `docs/testes_atual.log.txt`: testes C++ de parser/núcleo e seis testes Python de integração aprovados.
- `docs/sanitizadores_atual.log.txt`: núcleo e integração aprovados com AddressSanitizer/UndefinedBehaviorSanitizer.
- `resultados/final_validacao.json`: 1680 execuções e 3360 soluções iniciais/finais validadas independentemente; hashes da campanha.
- `docs/campanha_final_vnd.log.txt` e `docs/campanha_final_tabu.log.txt`: 28/28 lotes concluídos por método, sem falhas.
- `instances/auditoria_atual.csv`: 31 entradas, 28 prontas, duas duplicatas e uma sem dados.

## Limites que permanecem explícitos

O certificado inteiro é uma dependência, não uma prova de distância ótima. Casos estruturalmente inviáveis têm atendimento parcial, identificado. N3 é amostrada e N1/N2 usam restrições de candidatos. Tempos usam máquina compartilhada e paralelismo. O pacote não é submetido automaticamente ao Classroom. Dados históricos removidos não foram restaurados.
