#pragma once
#include <random>

#include "exato.hpp"
struct EstatConstr {
    int reinicios = 0, reparos = 0;
    int ajustesTipos = 0;  // movimentos aceitos pela busca local de tipos (antes do fallback)
    bool fallback = false;
};
// Regret global com capacidade compartilhada; cadeias aumentantes reparam impasses.
Solucao alocarRegret(const Instancia&, const Slots&, double alpha, std::mt19937&, bool trace = false,
                     const Solucao* anterior = nullptr, int* reparos = nullptr);
Solucao construir(const Instancia&, const Parametros&, const Certificado&, std::mt19937&, EstatConstr&);
