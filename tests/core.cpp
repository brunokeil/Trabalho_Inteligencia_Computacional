#include <cassert>
#include <functional>
#include <iostream>
#include <limits>
#include <random>

#include "busca_local.hpp"
int main() {
    std::mt19937 rng(123);
    auto in = Instancia::ler("entrega/Modelo_de_Instancia.txt");
    Slots slots(in.m);
    for (int j = 0; j < in.m; ++j)
        slots[j] = (1u << (j % in.k)) | (1u << ((j + 1) % in.k));
    auto s = montarSolucao(in, slots, std::vector<int>(in.n, -1));
    Parametros p;
    p.K = 2;
    p.ajustar(in);
    for (int it = 0; it < 10000; ++it) {
        int i = int(rng() % in.n), b = int(rng() % (in.m + 1)) - 1;
        if (b >= 0 && !hospeda(slots, b, in.tipoCand[i]))
            continue;
        auto before = s;
        auto d = deltaMover(in, s, i, b);
        mover(in, s, i, b);
        auto full = montarSolucao(in, slots, s.esc);
        assert(full.dist == before.dist + d.dist && full.excesso == before.excesso + d.excesso &&
               full.naoAlocados == before.naoAlocados + d.naoAlocados);
        validar(in, s, 2);
        int h = int(rng() % in.n);
        if (in.tipoCand[i] == in.tipoCand[h]) {
            auto cost = s.dist;
            auto delta = deltaTroca(in, s, i, h);
            trocar(in, s, i, h);
            assert(s.dist == cost + delta);
            validar(in, s, 2);
        }
    }
    // Capacidade não pode ser contada duas vezes em escola que recebe dois tipos.
    Instancia shared;
    shared.n = 4;
    shared.m = 2;
    shared.k = 2;
    shared.capEsc = {2, 2};
    shared.candsTipo = {{0, 1}, {2, 3}};
    assert(fluxoTipos(shared, Slots{3, 0}).atendidos == 2);
    // Referência exata conferida por enumeração completa da instância manual.
    auto tiny = Instancia::ler("entrega/exemplo8.txt");
    Slots tinySlots = {2, 1, 3};
    Custo optimum = std::numeric_limits<Custo>::max();
    std::vector<int> load(tiny.m);
    std::function<void(int, Custo)> enumerate = [&](int i, Custo distance) {
        if (i == tiny.n) {
            optimum = std::min(optimum, distance);
            return;
        }
        for (int j = 0; j < tiny.m; ++j)
            if (hospeda(tinySlots, j, tiny.tipoCand[i]) && load[j] < tiny.capEsc[j]) {
                ++load[j];
                enumerate(i + 1, distance + tiny.d(i, j));
                --load[j];
            }
    };
    enumerate(0, 0);
    auto reference = montarSolucao(tiny, tinySlots, resolverTransporteExato(tiny, tinySlots));
    validar(tiny, reference, 2);
    assert(reference.dist == optimum && optimum == 42 * ESCALA);
    int repairs = 0;
    auto tinySolution = alocarRegret(tiny, tinySlots, 0, rng, false, nullptr, &repairs);
    assert(tinySolution.dist == 49 * ESCALA && repairs == 1);
    auto broken = s;
    broken.dist++;
    bool rejected = false;
    try {
        validar(in, broken, 2);
    } catch (...) {
        rejected = true;
    }
    assert(rejected);
    for (const char* name : {"Modelo_de_Instancia", "instancia2", "instancia_A", "instancia_B"}) {
        auto instance = Instancia::ler(std::string("entrega/") + name + ".txt");
        for (int K : {1, 2}) {
            auto cert = preChecar(instance, K, "scripts/viabilidade.py");
            int expected = instance.n;
            if (K == 1 && instance.n == 109)
                expected = 91;
            if (K == 1 && instance.n == 2550)
                expected = 2530;
            assert(cert.atendidos == expected);
            for (unsigned seed : {0u, 1u, 42u}) {
                std::mt19937 gen(seed);
                Parametros par;
                par.K = K;
                par.alpha = .3;
                par.ajustar(instance);
                EstatConstr st;
                auto solution = construir(instance, par, cert, gen, st);
                validar(instance, solution, K);
                assert(!st.fallback);
                assert(solution.excesso == 0 && solution.naoAlocados == instance.n - expected);
            }
            std::cout << name << " K=" << K << " certificados/construcao OK\n" << std::flush;
        }
    }
    std::cout << "deltas e validador OK\n";
}
