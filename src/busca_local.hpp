#pragma once
#include <random>
#include <vector>

#include "construtivo.hpp"
struct Ponto {
    int iter = 0;
    Custo melhorDist = 0, atualDist = 0;
    int naoAlocados = 0, excessoAtual = 0;
    long double lambda = 0;
};
struct EstatBL {
    long long avaliacoes[3] = {0, 0, 0}, movimentos[3] = {0, 0, 0};
    int iteracoes = 0, aspiracoes = 0, tabusRejeitados = 0, ajustesLambda = 0, iteracoesInviaveis = 0;
    std::vector<Ponto> curva;
};
class BuscaLocal {
   public:
    BuscaLocal(const Instancia& in, const Parametros& p, std::mt19937& rng) : in(in), p(p), rng(rng) {}
    EstatBL executar(Solucao&);

   private:
    const Instancia& in;
    Parametros p;
    std::mt19937& rng;
};
