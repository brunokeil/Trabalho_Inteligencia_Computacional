#pragma once
#include <cstdint>
#include <string>
#include <vector>

#include "instancia.hpp"
using Slots = std::vector<unsigned>;
inline bool hospeda(const Slots& s, int j, int t) {
    return (s[j] & (1u << t)) != 0;
}
inline int numeroTipos(unsigned mask) {
    int n = 0;
    while (mask) {
        mask &= mask - 1;
        ++n;
    }
    return n;
}
struct Parametros {
    int K = 1, p = 5, maxIter = 300, semMelhora = 80, tmin = 5, tmax = 12, periodoN3 = 20, adaptar = 5,
        amostrasN3 = 6;
    double alpha = 0, tempoLimite = 0;
    bool first = false, trace = false;
    std::string metodo = "vnd", viz = "123";
    long double lambda = 0, mu = 0;
    void ajustar(const Instancia& in) {
        lambda = mu = (long double)in.n * in.distMax + ESCALA;
    }
};
struct Solucao {
    std::vector<int> esc, carga;
    std::vector<std::vector<int>> porTipo;
    Slots typeSlots;
    Custo dist = 0;
    int excesso = 0, naoAlocados = 0, incompativeis = 0;
    int violacoes() const {
        return excesso + naoAlocados + incompativeis;
    }
    bool viavel() const {
        return violacoes() == 0;
    }
    long double custo(const Parametros& p) const {
        return dist + p.lambda * excesso + p.mu * (naoAlocados + incompativeis);
    }
};
struct Delta {
    Custo dist = 0;
    int excesso = 0, naoAlocados = 0;
    long double custo(const Parametros& p) const {
        return dist + p.lambda * excesso + p.mu * naoAlocados;
    }
};
Solucao montarSolucao(const Instancia&, const Slots&, const std::vector<int>&);
Delta deltaMover(const Instancia&, const Solucao&, int i, int b);
void mover(const Instancia&, Solucao&, int i, int b);
Custo deltaTroca(const Instancia&, const Solucao&, int i, int h);
void trocar(const Instancia&, Solucao&, int i, int h);
bool melhorSolucao(const Solucao&, const Solucao&);
void validar(const Instancia&, const Solucao&, int K);  // recomputação independente das atualizações
void imprimirRelatorio(const Instancia&, const Solucao&);
