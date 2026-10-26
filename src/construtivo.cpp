#include "construtivo.hpp"

#include <algorithm>
#include <iostream>
#include <limits>
#include <numeric>
#include <queue>

namespace {
// Caminho aumentante: candidato -> escola -> candidato deslocado -> ... -> vaga.
// Permite ejetar outro tipo em K=2; equivale ao residual do matching capacitado.
bool reparar(const Instancia& in, Solucao& s, int root, bool trace) {
    std::vector<int> predecessor(in.m, -2), candidate(in.m, -1);
    std::queue<int> q;
    for (int j = 0; j < in.m; ++j)
        if (hospeda(s.typeSlots, j, in.tipoCand[root])) {
            predecessor[j] = -1;
            candidate[j] = root;
            q.push(j);
        }
    int end = -1;
    while (!q.empty()) {
        int a = q.front();
        q.pop();
        if (s.carga[a] < in.capEsc[a]) {
            end = a;
            break;
        }
        for (int i = 0; i < in.n; ++i)
            if (s.esc[i] == a)
                for (int b = 0; b < in.m; ++b)
                    if (predecessor[b] == -2 && hospeda(s.typeSlots, b, in.tipoCand[i])) {
                        predecessor[b] = a;
                        candidate[b] = i;
                        q.push(b);
                    }
    }
    if (end < 0)
        return false;
    while (end >= 0) {
        int i = candidate[end];
        if (trace)
            std::cout << "reparo " << in.idCand[i] << " -> " << in.idEsc[end] << "\n";
        mover(in, s, i, end);
        end = predecessor[end];
    }
    return true;
}

// Busca local sobre a atribuição de tipos, usada quando a fase gulosa não alcança
// o atendimento certificado. O objetivo é lexicográfico: maior cobertura por fluxo
// e, em empate, menor custo de proximidade (soma de near[j][t] dos pares hospedados).
// Movimentos: (a) adicionar um tipo a uma escola com menos de K tipos; (b) trocar um
// tipo de uma escola por outro; (c) permutar tipos entre duas escolas. Movimentos que
// passam a hospedar um tipo com demanda não atendida são avaliados primeiro (primeira
// melhora). Em platô, aplica-se uma perturbação aleatória; o melhor estado visto é
// devolvido. O orçamento de avaliações limita o tempo.
bool ajustarTipos(const Instancia& in, const Parametros& p, const std::vector<std::vector<double>>& near,
                  int alvo, Slots& slots, std::mt19937& rng, int& aceitos) {
    auto proximidade = [&](const Slots& z) {
        double s = 0;
        for (int j = 0; j < in.m; ++j)
            for (int t = 0; t < in.k; ++t)
                if (hospeda(z, j, t))
                    s += near[j][t];
        return s;
    };
    auto atual = slots;
    int cobertura = fluxoTipos(in, atual).atendidos;
    double prox = proximidade(atual);
    auto melhor = atual;
    int melhorCob = cobertura;
    double melhorProx = prox;
    const int orcamento = 20000;
    int avaliacoes = 0, perturbacoes = 0;
    const int maxPerturbacoes = 30;
    while (melhorCob < alvo && avaliacoes < orcamento) {
        // Tipos com demanda não atendida segundo o fluxo atual.
        auto flow = fluxoTipos(in, atual);
        std::vector<int> servidos(in.k, 0);
        for (int j = 0; j < in.m; ++j)
            for (int t = 0; t < in.k; ++t)
                servidos[t] += flow.quotas[j][t];
        std::vector<char> deficit(in.k);
        for (int t = 0; t < in.k; ++t)
            deficit[t] = servidos[t] < int(in.candsTipo[t].size());
        std::vector<Slots> prioritarios, demais;
        auto registrar = [&](Slots z, int novoTipo) {
            (deficit[novoTipo] ? prioritarios : demais).push_back(std::move(z));
        };
        for (int j = 0; j < in.m; ++j)
            for (int t = 0; t < in.k; ++t) {
                if (hospeda(atual, j, t))
                    continue;
                if (numeroTipos(atual[j]) < p.K) {
                    auto z = atual;
                    z[j] |= 1u << t;
                    registrar(z, t);
                }
                for (int old = 0; old < in.k; ++old)
                    if (hospeda(atual, j, old)) {
                        auto z = atual;
                        z[j] = (z[j] & ~(1u << old)) | (1u << t);
                        registrar(z, t);
                    }
            }
        for (int j = 0; j < in.m; ++j)
            for (int h = j + 1; h < in.m; ++h)
                for (int t = 0; t < in.k; ++t)
                    if (hospeda(atual, j, t) && !hospeda(atual, h, t))
                        for (int u = 0; u < in.k; ++u)
                            if (hospeda(atual, h, u) && !hospeda(atual, j, u)) {
                                auto z = atual;
                                z[j] = (z[j] & ~(1u << t)) | (1u << u);
                                z[h] = (z[h] & ~(1u << u)) | (1u << t);
                                registrar(z, deficit[t] ? t : u);
                            }
        std::shuffle(prioritarios.begin(), prioritarios.end(), rng);
        std::shuffle(demais.begin(), demais.end(), rng);
        bool melhorou = false;
        for (auto* lista : {&prioritarios, &demais}) {
            for (auto& z : *lista) {
                if (avaliacoes >= orcamento)
                    break;
                ++avaliacoes;
                int c = fluxoTipos(in, z).atendidos;
                double pr = proximidade(z);
                if (c > cobertura || (c == cobertura && pr < prox - 1e-12)) {
                    atual = z;
                    cobertura = c;
                    prox = pr;
                    melhorou = true;
                    ++aceitos;
                    break;
                }
            }
            if (melhorou)
                break;
        }
        if (cobertura > melhorCob || (cobertura == melhorCob && prox < melhorProx - 1e-12)) {
            melhor = atual;
            melhorCob = cobertura;
            melhorProx = prox;
        }
        if (melhorou)
            continue;
        // Ótimo local da cobertura: perturba trocando o tipo de uma escola ao acaso.
        if (++perturbacoes > maxPerturbacoes || (prioritarios.empty() && demais.empty()))
            break;
        auto& fonte = !prioritarios.empty() ? prioritarios : demais;
        atual = fonte[std::uniform_int_distribution<int>(0, int(fonte.size()) - 1)(rng)];
        cobertura = fluxoTipos(in, atual).atendidos;
        prox = proximidade(atual);
        ++avaliacoes;
    }
    slots = melhor;
    return melhorCob >= alvo;
}
}  // namespace
Solucao alocarRegret(const Instancia& in, const Slots& slots, double alpha, std::mt19937& rng, bool trace,
                     const Solucao* anterior, int* reparos) {
    std::vector<int> assign(in.n, -1);
    // A newly enabled type must be allowed to use its new school even when
    // that school was empty. Keeping every assignment at unchanged schools
    // made such N3 proposals neutral and therefore unreachable by VND.
    unsigned novosTipos = 0;
    if (anterior)
        for (int j = 0; j < in.m; ++j)
            novosTipos |= slots[j] & ~anterior->typeSlots[j];
    if (anterior)
        for (int i = 0; i < in.n; ++i) {
            int j = anterior->esc[i];
            if (j >= 0 && anterior->typeSlots[j] == slots[j] &&
                !(novosTipos & (1u << in.tipoCand[i])))
                assign[i] = j;
        }
    auto s = montarSolucao(in, slots, assign);
    std::vector<int> pend, b1(in.n, -1), b2(in.n, -1);
    std::vector<Custo> reg(in.n);
    const Custo INF = std::numeric_limits<Custo>::max() / 8;
    auto calcular = [&](int i) {
        b1[i] = b2[i] = -1;
        for (int j = 0; j < in.m; ++j)
            if (hospeda(slots, j, in.tipoCand[i]) && s.carga[j] < in.capEsc[j]) {
                if (b1[i] < 0 || in.d(i, j) < in.d(i, b1[i])) {
                    b2[i] = b1[i];
                    b1[i] = j;
                } else if (b2[i] < 0 || in.d(i, j) < in.d(i, b2[i]))
                    b2[i] = j;
            }
        reg[i] = b1[i] < 0 ? -1 : (b2[i] < 0 ? INF : in.d(i, b2[i]) - in.d(i, b1[i]));
    };
    for (int i = 0; i < in.n; ++i)
        if (assign[i] < 0) {
            pend.push_back(i);
            calcular(i);
        }
    while (!pend.empty()) {
        Custo hi = -1, lo = INF;
        for (int i : pend)
            if (reg[i] >= 0) {
                hi = std::max(hi, reg[i]);
                lo = std::min(lo, reg[i]);
            }
        if (hi < 0)
            break;
        int pos = -1;
        std::vector<int> rcl;
        for (int q = 0; q < int(pend.size()); ++q) {
            int i = pend[q];
            bool eligible =
                hi == INF ? reg[i] == INF : (reg[i] >= 0 && reg[i] >= hi - alpha * (long double)(hi - lo));
            if (eligible) {
                if (alpha > 0)
                    rcl.push_back(q);
                if (pos < 0 || i < pend[pos])
                    pos = q;
            }
        }
        if (alpha > 0)
            pos = rcl[std::uniform_int_distribution<int>(0, int(rcl.size()) - 1)(rng)];
        int i = pend[pos], j = b1[i];
        mover(in, s, i, j);
        if (trace)
            std::cout << "regret " << in.idCand[i] << " tipo=" << in.nomeTipo[in.tipoCand[i]] << " -> "
                      << in.idEsc[j] << " d=" << in.d(i, j) / double(ESCALA)
                      << " vagas=" << in.capEsc[j] - s.carga[j] << "\n";
        pend[pos] = pend.back();
        pend.pop_back();
        if (s.carga[j] == in.capEsc[j])
            for (int c : pend)
                if (b1[c] == j || b2[c] == j)
                    calcular(c);
    }
    // Cada caminho aumenta atendimento em um; ausência de caminhos prova máximo
    // para estes slots. Iterar até não aumentar também cobre liberações indiretas.
    bool changed = true;
    while (changed) {
        changed = false;
        for (int i = 0; i < in.n; ++i)
            if (s.esc[i] < 0 && reparar(in, s, i, trace)) {
                changed = true;
                if (reparos)
                    ++*reparos;
            }
    }
    return s;
}
Solucao construir(const Instancia& in, const Parametros& p, const Certificado& cert, std::mt19937& rng,
                  EstatConstr& est) {
    std::vector<std::vector<double>> near(in.m, std::vector<double>(in.k));
    for (int j = 0; j < in.m; ++j)
        for (int t = 0; t < in.k; ++t) {
            std::vector<Custo> d;
            for (int i : in.candsTipo[t])
                d.push_back(in.d(i, j));
            std::sort(d.begin(), d.end());
            int count = std::min(int(d.size()), in.capEsc[j]);
            near[j][t] = count ? std::accumulate(d.begin(), d.begin() + count, 0.0) / count /
                                     std::max<Custo>(1, in.distMax)
                               : 0;
        }
    Slots chosen;
    int attempts = p.alpha == 0 ? 1 : 4;
    for (int attempt = 0; attempt < attempts; ++attempt) {
        Slots slots(in.m);
        auto flow = fluxoTipos(in, slots);
        while (flow.atendidos < cert.atendidos) {
            struct Pair {
                int j, t;
                double score;
            };
            std::vector<Pair> pairs;
            double high = -1e100, low = 1e100;
            for (int j = 0; j < in.m; ++j)
                if (numeroTipos(slots[j]) < p.K)
                    for (int t = 0; t < in.k; ++t)
                        if (!hospeda(slots, j, t)) {
                            auto trial = slots;
                            trial[j] |= 1u << t;
                            int gain = fluxoTipos(in, trial).atendidos - flow.atendidos;
                            if (gain <= 0)
                                continue;
                            double score = double(gain) / in.candsTipo[t].size() +
                                           double(gain) / in.capEsc[j] - near[j][t];
                            pairs.push_back({j, t, score});
                            high = std::max(high, score);
                            low = std::min(low, score);
                        }
            if (pairs.empty())
                break;
            std::vector<int> rcl;
            for (int q = 0; q < int(pairs.size()); ++q)
                if (pairs[q].score >= high - p.alpha * (high - low) - 1e-12)
                    rcl.push_back(q);
            int q = p.alpha == 0 ? rcl.front()
                                 : rcl[std::uniform_int_distribution<int>(0, int(rcl.size()) - 1)(rng)];
            auto pair = pairs[q];
            slots[pair.j] |= 1u << pair.t;
            flow = fluxoTipos(in, slots);
            if (p.trace)
                std::cout << "slot " << in.idEsc[pair.j] << " + " << in.nomeTipo[pair.t]
                          << " score=" << pair.score << " cobertura=" << flow.atendidos << "\n";
        }
        // A gulosa não desfaz escolhas; antes de reiniciar ou recorrer ao certificado,
        // uma busca local sobre os tipos tenta alcançar o atendimento certificado.
        if (flow.atendidos < cert.atendidos &&
            ajustarTipos(in, p, near, cert.atendidos, slots, rng, est.ajustesTipos)) {
            flow = fluxoTipos(in, slots);
            if (p.trace)
                std::cout << "ajuste de tipos: cobertura=" << flow.atendidos << "\n";
        }
        if (flow.atendidos == cert.atendidos) {
            chosen = slots;
            break;
        }
        ++est.reinicios;
    }
    if (chosen.empty()) {
        chosen = cert.slots;
        est.fallback = true;
        if (p.trace)
            std::cout << "fallback: slots do certificado de capacidade\n";
    }
    auto s = alocarRegret(in, chosen, p.alpha, rng, p.trace, nullptr, &est.reparos);
    if (in.n - s.naoAlocados != cert.atendidos)
        throw std::runtime_error("reparo nao atingiu atendimento certificado");
    validar(in, s, p.K);
    return s;
}
