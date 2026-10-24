#pragma once
#include "solucao.hpp"
struct Certificado {
    int atendidos = 0;
    Slots slots;
    std::vector<std::vector<int>> quotas;
};
Certificado preChecar(const Instancia&, int K, const std::string& script);
// Fluxo máximo agregado com tipos fixos; capacidade compartilhada para K=2.
Certificado fluxoTipos(const Instancia&, const Slots&);
// Referência exata de distância para tipos fixos (não é ótimo global dos tipos).
std::vector<int> resolverTransporteExato(const Instancia&, const Slots&);
