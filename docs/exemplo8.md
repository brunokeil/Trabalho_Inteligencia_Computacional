# Exemplo manual: 8 candidatos, 3 escolas, K=2

Reproduzir:

```sh
./alocacao --instancia entrega/exemplo8.txt --tipos-por-escola 2 \
  --alpha 0 --seed 1 --metodo vnd --ls best --n3-amostras 20 \
  --trace --saida resultados/exemplo8.json
```

E1 e E2 têm três vagas cada; E3 tem duas. Quatro candidatos fazem M1 e quatro fazem M2. Todas as distâncias estão em km.

| Candidato | Tipo | E1 | E2 | E3 |
|---|---|---:|---:|---:|
| C1 | M1 | 8 | 10 | 6 |
| C2 | M1 | 5 | 3 | 3 |
| C3 | M1 | 14 | 11 | 1 |
| C4 | M1 | 6 | 9 | 8 |
| C5 | M2 | 10 | 2 | 6 |
| C6 | M2 | 9 | 10 | 12 |
| C7 | M2 | 1 | 12 | 7 |
| C8 | M2 | 3 | 12 | 8 |

O certificado confirma atendimento de 8/8. A fase de tipos adiciona, nesta ordem:

| Passo | Par escolhido | Score | Atendimento possível por fluxo |
|---:|---|---:|---:|
| 1 | E1 recebe M2 | 1,440476 | 3 |
| 2 | E3 recebe M1 | 1,357143 | 5 |
| 3 | E2 recebe M1 | 0,642857 | 7 |
| 4 | E3 recebe M2 | 0,285714 | 8 |

Por exemplo, para E1/M2, g=3, demanda=4, capacidade=3. As três menores distâncias são 1, 3 e 9. Como d_max=14, score=3/4+3/3−[(1+3+9)/3]/14=1,440476.

Na alocação por regret:

| Passo | Decisão | Justificativa | Vagas restantes no destino |
|---:|---|---|---:|
| 1 | C3 → E3 | regret 11−1=10 | 1 |
| 2 | C7 → E1 | regret 7−1=6 | 2 |
| 3 | C8 → E1 | regret 8−3=5 | 1 |
| 4 | C1 → E3 | regret 10−6=4; desempate por ordem com C5 | 0 |
| 5 | C2 → E2 | única escola habilitada com vaga | 2 |
| 6 | C4 → E2 | única opção | 1 |
| 7 | C5 → E1 | única opção | 0 |

C6 fica sem vaga compatível: E1 e E3 estão cheias. Entretanto, E2 ainda possui uma vaga. A reparação encontra a cadeia **C6 → E3, C1 → E2** e a aplica de trás para frente. Agora todos estão alocados.

Solução inicial:

- E1/M2: C5, C7, C8 → 10+1+3 = 14 km.
- E2/M1: C1, C2, C4 → 10+3+9 = 22 km.
- E3/M1,M2: C3, C6 → 1+12 = 13 km.

**Total: 49 km.** Todas as escolas estão cheias. N1 não melhora sem exceder capacidade. N2 troca C5 (E1) com C6 (E3), ambos M2:

Δ = d(C5,E3)+d(C6,E1)−d(C5,E1)−d(C6,E3) = 6+9−10−12 = **−7 km**.

Depois da troca, E1 contém C6,C7,C8 (13 km); E2 permanece com 22 km; E3 contém C3,C5 (7 km). **Total final: 42 km**, melhoria de 14,2857%. Cargas e compatibilidade permanecem válidas.

A enumeração de todas as alocações desse exemplo confirma que 42 km é ótimo **para esses tipos fixos**. Isso não é uma afirmação de ótimo global sobre todas as atribuições de tipos.

O trace literal está em `docs/exemplo8-trace.txt`; o teste automatizado confere a reparação, 49 km inicialmente e a referência exata de 42 km.
