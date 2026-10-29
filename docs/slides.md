# Apresentação

`docs/apresentacao.html` e `docs/apresentacao.pdf`: 12 slides, roteiro de 10:00. Setas para navegar; N para notas; F para tela cheia. O exemplo mostra 56 → 42 km em K=1. O seletor compara K=1 e K=2 em cada uma das 28 instâncias; o PDF mostra I2 G2. I2 G8 (K=2) é exibido no slide 9 como caso real de qualidade variável no ótimo local do VND. Motivação (slide 2) e principais dificuldades (slide 12) estão visíveis.

O slide 12 inclui o GitHub e downloads do relatório/CSV incorporados ao HTML; mover o HTML sozinho não quebra esses downloads. Os arquivos incorporados correspondem à última geração; `make report` atualiza o relatório embutido.

Regenerar: `python3 scripts/gerar_entrega.py`, `make report` e `python3 scripts/verificar_apresentacao.py --driver /caminho/geckodriver --export-pdf`. Fontes: `scripts/gerar_apresentacao.py` e `docs/apresentacao_template.html`. O roteiro cobre os oito tópicos exigidos. O PDF está incluído porque o enunciado local não confirma aceitação de HTML.
