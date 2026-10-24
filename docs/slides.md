# Roteiro de apresentação — aproximadamente 10 minutos

1. **Problema e motivação — 0:00–0:50.** Alocar candidatos em escolas próximas, com capacidade e tipos compatíveis. As decisões incluem os tipos das escolas. Mostrar K=1 e K=2; objetivo é distância da matriz.
2. **Representação e dados — 0:50–1:40.** Mostrar `typeSlots`, `assign`, carga e carga por tipo. IDs fora de ordem e CEP com hífen. Explicar capacidade agregada por escola e precisão exata das distâncias.
3. **Viabilidade e avaliação — 1:40–2:30.** ILP pequeno certifica máximo atendimento, sem otimizar distância. Mostrar 18/20 não alocados nos dois casos K=1 inviáveis. Mostrar f=D+λ excesso+μ não alocados, λ adaptativo.
4. **Construção e justificativas — 2:30–3:40.** Score de cobertura/capacidade/proximidade; RCL alpha; regret; cadeia de reparação e fallback certificado. Não afirmar que o guloso garante viabilidade sozinho.
5. **Exemplo manual — 3:40–5:20.** Usar tabela de oito candidatos de `exemplo8.md`. Mostrar slots escolhidos, impasse de C6, cadeia C1→E2 e C6→E3. Mostrar soma 49 km.
6. **N1, N2, N3 e VND — 5:20–6:20.** Troca C5↔C6: delta −7, final 42 km. Explicar deltas O(1), ganho por pares e alteração de tipos. N3 usa amostragem.
7. **Busca Tabu — 6:20–7:20.** Atributos, tenure [5,12], aspiração, movimentos não melhorantes, λ adaptativo. Melhor viável fica separado do estado corrente.
8. **Resultados — 7:20–8:40.** Usar tabelas reais de `resultados/resumo.csv` e curva `convergencia.pdf`. Informar 30 sementes, 88 configurações, 2640 execuções, limite comum de 150 iterações. Mostrar VND/tabu, alpha e tenure; não apresentar somente a melhor semente.
9. **Falha e limites — 8:40–9:25.** Modelo K=1 impossível apesar da capacidade total; A apertada e N3 limitada. Distinguir ótimo dos tipos fixos e ótimo global. Todos os resultados validados independentemente.
10. **Conclusões e próximos passos — 9:25–10:00.** Síntese dos resultados medidos; melhorar escolha de tipos, listas adaptativas e exploração N3. Exibir repositório real quando a publicação for concluída.

Material de apoio: terminal com comando do exemplo, trace salvo, planilha CSV e PDF do relatório. Manter a matriz manual legível em um slide próprio. Reservar detalhes de ILP, penalidades e contadores para perguntas.
