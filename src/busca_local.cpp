#include "busca_local.hpp"

#include <algorithm>
#include <chrono>
#include <iostream>
#include <limits>
#include <unordered_map>

namespace {
struct Move {
    int kind = 0, i = -1, b = -1, h = -1;
    long double delta = std::numeric_limits<long double>::infinity();
    bool aspiration = false;
    Solucao next;
};
uint64_t pairKey(int a, int b) {
    if (a > b)
        std::swap(a, b);
    return (uint64_t(unsigned(a)) << 32) | unsigned(b);
}
}  // namespace
EstatBL BuscaLocal::executar(Solucao& s) {
    EstatBL est;
    Solucao best = s;
    auto start = std::chrono::steady_clock::now();
    int stagnant = 0, feasibleStreak = 0, infeasibleStreak = 0;
    const long double base = p.lambda, minLambda = std::max<long double>(1, in.distMax / 10.0L),
                      maxLambda = base * 16;
    std::vector<std::vector<int>> relTabu(in.n, std::vector<int>(in.m + 1)),
        typeTabu(in.m, std::vector<int>(in.k));
    std::unordered_map<uint64_t, int> swapTabu;
    std::vector<int> neighborhoods;
    for (char c : p.viz)
        neighborhoods.push_back(c - '0');
    int vnd = 0;
    auto log = [&](int iter) {
        est.curva.push_back({iter, best.dist, s.dist, best.naoAlocados, s.excesso, p.lambda});
    };
    log(0);
    for (int iter = 1; iter <= p.maxIter && stagnant < p.semMelhora; ++iter) {
        if (p.tempoLimite > 0 &&
            std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count() >= p.tempoLimite)
            break;
        bool tabu = p.metodo == "tabu";
        if (!tabu && vnd >= int(neighborhoods.size()))
            break;
        Move chosen;
        auto consider = [&](Move mv, int violations, Custo dist, bool forbidden) {
            bool asp = forbidden && violations == 0 && (!best.viavel() || dist < best.dist);
            if (forbidden && !asp) {
                ++est.tabusRejeitados;
                return false;
            }
            if (!tabu && mv.delta >= 0)
                return false;
            if (mv.delta < chosen.delta) {
                mv.aspiration = asp;
                chosen = std::move(mv);
                return !tabu && p.first;
            }
            return false;
        };
        bool n1 = tabu ? p.viz.find('1') != std::string::npos : neighborhoods[vnd] == 1;
        bool n2 = tabu ? p.viz.find('2') != std::string::npos : neighborhoods[vnd] == 2;
        bool n3 = tabu ? (p.viz.find('3') != std::string::npos &&
                          (iter % p.periodoN3 == 0 || (stagnant > 0 && stagnant % p.periodoN3 == 0)))
                       : neighborhoods[vnd] == 3;
        if (n1) {
            bool stop = false;
            for (int i = 0; i < in.n && !stop; ++i) {
                std::vector<int> dest;
                for (int j = 0; j < in.m; ++j)
                    if (j != s.esc[i] && hospeda(s.typeSlots, j, in.tipoCand[i]))
                        dest.push_back(j);
                std::sort(dest.begin(), dest.end(), [&](int a, int b) {
                    return in.d(i, a) != in.d(i, b) ? in.d(i, a) < in.d(i, b) : a < b;
                });
                if (int(dest.size()) > p.p)
                    dest.resize(p.p);
                if (tabu && s.esc[i] >= 0)
                    dest.push_back(-1);
                for (int b : dest) {
                    auto d = deltaMover(in, s, i, b);
                    ++est.avaliacoes[0];
                    Move mv;
                    mv.kind = 1;
                    mv.i = i;
                    mv.b = b;
                    mv.delta = d.custo(p);
                    if (consider(mv, s.violacoes() + d.excesso + d.naoAlocados, s.dist + d.dist,
                                 tabu && relTabu[i][b + 1] >= iter)) {
                        stop = true;
                        break;
                    }
                }
            }
        }
        if (n2) {
            // Reaproveita ganhos por par de escolas. Top-4 admite alternativas tabu;
            // para VND top-1 já contém a melhor troca de cada par e tipo.
            struct Gain {
                Custo gain;
                int i;
            };
            int M = in.m + 1;
            std::vector<std::vector<Gain>> bucket(in.k * M * M);
            auto idx = [&](int t, int a, int b) { return (t * M + a) * M + b; };
            int keep = tabu ? 4 : 1;
            for (int i = 0; i < in.n; ++i) {
                int a = s.esc[i] + 1, t = in.tipoCand[i];
                for (int b = 0; b < M; ++b)
                    if (b != a && (b == 0 || hospeda(s.typeSlots, b - 1, t))) {
                        ++est.avaliacoes[1];
                        Custo gain = (a ? in.d(i, a - 1) : 0) - (b ? in.d(i, b - 1) : 0);
                        auto& v = bucket[idx(t, a, b)];
                        v.push_back({gain, i});
                        std::sort(v.begin(), v.end(), [](Gain x, Gain y) {
                            return x.gain != y.gain ? x.gain > y.gain : x.i < y.i;
                        });
                        if (int(v.size()) > keep)
                            v.pop_back();
                    }
            }
            bool stop = false;
            for (int t = 0; t < in.k && !stop; ++t)
                for (int a = 0; a < M && !stop; ++a)
                    for (int b = a + 1; b < M && !stop; ++b)
                        for (auto x : bucket[idx(t, a, b)]) {
                            for (auto y : bucket[idx(t, b, a)]) {
                                ++est.avaliacoes[1];
                                Move mv;
                                mv.kind = 2;
                                mv.i = x.i;
                                mv.h = y.i;
                                mv.delta = -(x.gain + y.gain);
                                auto it = swapTabu.find(pairKey(x.i, y.i));
                                bool forbidden = tabu && it != swapTabu.end() && it->second >= iter;
                                if (consider(mv, s.violacoes(), s.dist + Custo(mv.delta), forbidden)) {
                                    stop = true;
                                    break;
                                }
                            }
                            if (stop)
                                break;
                        }
        }
        if (n3) {
            std::vector<Slots> trials;
            for (int j = 0; j < in.m; ++j) {
                for (int t = 0; t < in.k; ++t)
                    if (!hospeda(s.typeSlots, j, t)) {
                        if (numeroTipos(s.typeSlots[j]) < p.K) {
                            auto z = s.typeSlots;
                            z[j] |= 1u << t;
                            trials.push_back(z);
                        }
                        for (int old = 0; old < in.k; ++old)
                            if (hospeda(s.typeSlots, j, old)) {
                                auto z = s.typeSlots;
                                z[j] = (z[j] & ~(1u << old)) | (1u << t);
                                trials.push_back(z);
                            }
                    }
                for (int h = j + 1; h < in.m; ++h)
                    for (int t = 0; t < in.k; ++t)
                        if (hospeda(s.typeSlots, j, t) && !hospeda(s.typeSlots, h, t))
                            for (int u = 0; u < in.k; ++u)
                                if (hospeda(s.typeSlots, h, u) && !hospeda(s.typeSlots, j, u)) {
                                    auto z = s.typeSlots;
                                    z[j] = (z[j] & ~(1u << t)) | (1u << u);
                                    z[h] = (z[h] & ~(1u << u)) | (1u << t);
                                    trials.push_back(z);
                                }
            }
            std::shuffle(trials.begin(), trials.end(), rng);
            int evaluated = 0;
            for (auto& slots : trials) {
                ++est.avaliacoes[2];
                if (fluxoTipos(in, slots).atendidos < in.n - best.naoAlocados)
                    continue;
                bool forbidden = false;
                for (int j = 0; j < in.m; ++j)
                    for (int t = 0; t < in.k; ++t)
                        if (hospeda(slots, j, t) && !hospeda(s.typeSlots, j, t) && typeTabu[j][t] >= iter)
                            forbidden = true;
                Move mv;
                mv.kind = 3;
                mv.next = alocarRegret(in, slots, 0, rng, false, &s);
                mv.delta = mv.next.custo(p) - s.custo(p);
                int violations = mv.next.violacoes();
                Custo distance = mv.next.dist;
                bool stop = consider(std::move(mv), violations, distance, tabu && forbidden);
                ++evaluated;
                if (stop || evaluated >= p.amostrasN3)
                    break;
            }
        }
        est.iteracoes = iter;
        if (chosen.kind == 0) {
            if (tabu)
                break;
            ++vnd;
            ++stagnant;
            log(iter);
            continue;
        }
        int tenure = std::uniform_int_distribution<int>(p.tmin, p.tmax)(rng);
        if (chosen.kind == 1) {
            int a = s.esc[chosen.i];
            relTabu[chosen.i][a + 1] = iter + tenure;
            mover(in, s, chosen.i, chosen.b);
        }
        if (chosen.kind == 2) {
            swapTabu[pairKey(chosen.i, chosen.h)] = iter + tenure;
            trocar(in, s, chosen.i, chosen.h);
        }
        if (chosen.kind == 3) {
            for (int j = 0; j < in.m; ++j)
                for (int t = 0; t < in.k; ++t)
                    if (hospeda(s.typeSlots, j, t) && !hospeda(chosen.next.typeSlots, j, t))
                        typeTabu[j][t] = iter + tenure;
            s = std::move(chosen.next);
        }
        ++est.movimentos[chosen.kind - 1];
        est.aspiracoes += chosen.aspiration;
        if (p.trace)
            std::cout << "iter=" << iter << " N" << chosen.kind << " delta=" << double(chosen.delta / ESCALA)
                      << " dist=" << s.dist / double(ESCALA) << " excesso=" << s.excesso
                      << " nao_alocados=" << s.naoAlocados << "\n";
        if (s.excesso == 0 && s.incompativeis == 0 && melhorSolucao(s, best)) {
            best = s;
            stagnant = 0;
        } else
            ++stagnant;
        if (!tabu)
            vnd = 0;
        if (tabu) {
            if (s.viavel()) {
                ++feasibleStreak;
                infeasibleStreak = 0;
            } else {
                ++infeasibleStreak;
                feasibleStreak = 0;
                ++est.iteracoesInviaveis;
            }
            if (infeasibleStreak >= p.adaptar) {
                p.lambda = std::min(maxLambda, p.lambda * 2);
                infeasibleStreak = 0;
                ++est.ajustesLambda;
            }
            if (feasibleStreak >= p.adaptar) {
                p.lambda = std::max(minLambda, p.lambda / 2);
                feasibleStreak = 0;
                ++est.ajustesLambda;
            }
        }
        log(iter);
    }
    s = best;
    validar(in, s, p.K);
    return est;
}
