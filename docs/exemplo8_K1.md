# Exemplo didático — um tipo por escola

Entrada: `entrega/exemplo8_K1.txt`. Capacidades E1=4, E2=4 e E3=2; quatro candidatos M1 e quatro M2. A matriz completa consta no relatório. Execução: alpha=0, semente 1, VND/best, N3 com até 1000 reconstruções para examinar todas as propostas pequenas.

1. Habilitar E1/M2: score 1,589286; atendimento possível 4.
2. Habilitar E2/M1: score 1,410714; atendimento possível 8. Encerrar escolha de tipos com E3 vazia.
3. Alocar C1–C4 em E2: distâncias 10+3+11+9=33 km. Alocar C5–C8 em E1: 10+9+1+3=23 km. Inicial: **56 km**.
4. N1 não tem destino alternativo compatível; N2 não muda o destino entre candidatos do mesmo tipo.
5. N3 habilita M1 em E3 e reconsidera candidatos M1. Regrets: C3=10, C1=4, C4=1, C2=0. C3 e C1 ocupam E3; C2 e C4 ficam em E2.
6. Final: E1/M2 contém C5,C6,C7,C8 (23 km); E2/M1 contém C2,C4 (12 km); E3/M1 contém C1,C3 (7 km). **42 km**, redução de 14 km ou **25%**.

Cargas finais: 4/4, 2/4, 2/2. Todos são atendidos e cada escola hospeda um único tipo. O transporte exato confirma 42 km **para os tipos finais fixos**, sem certificar a escolha global dos tipos.

A regressão corrigida: antes, a N3 preservava todos os candidatos de escolas inalteradas. Adicionar M1 à escola E3 vazia não movia ninguém, produzia custo neutro e era rejeitado pelo VND. Agora liberamos também os candidatos dos tipos recém-habilitados. O núcleo possui um teste para essa situação.

O trace literal está em `docs/exemplo8_K1-trace.txt`. O exemplo antigo `exemplo8.txt`, de capacidades 3,3,2, continua disponível para demonstrar reparação na extensão K=2; não é o exemplo principal do relatório atual.
