#include "solucao.hpp"

#include <algorithm>
#include <iostream>
#include <stdexcept>

Solucao montarSolucao(const Instancia& in, const Slots& slots, const std::vector<int>& esc) {
    if (slots.size() != size_t(in.m) || esc.size() != size_t(in.n))
        throw std::runtime_error("dimensao de solucao invalida");
    Solucao s;
    s.typeSlots = slots;
    s.esc = esc;
    s.carga.assign(in.m, 0);
    s.porTipo.assign(in.m, std::vector<int>(in.k));
    for (int i = 0; i < in.n; ++i) {
        int j = esc[i];
        if (j == -1) {
            ++s.naoAlocados;
            continue;
        }
        if (j < 0 || j >= in.m)
            throw std::runtime_error("indice de escola invalido");
        ++s.carga[j];
        ++s.porTipo[j][in.tipoCand[i]];
        s.dist += in.d(i, j);
        if (!hospeda(slots, j, in.tipoCand[i]))
            ++s.incompativeis;
    }
    for (int j = 0; j < in.m; ++j)
        s.excesso += std::max(0, s.carga[j] - in.capEsc[j]);
    return s;
}
Delta deltaMover(const Instancia& in, const Solucao& s, int i, int b) {
    int a = s.esc[i];
    Delta d;
    if (a == b)
        return d;
    if (b >= 0) {
        d.dist += in.d(i, b);
        d.excesso += s.carga[b] >= in.capEsc[b];
    } else
        ++d.naoAlocados;
    if (a >= 0) {
        d.dist -= in.d(i, a);
        d.excesso -= s.carga[a] > in.capEsc[a];
    } else
        --d.naoAlocados;
    return d;
}
void mover(const Instancia& in, Solucao& s, int i, int b) {
    int a = s.esc[i];
    if (a == b)
        return;
    auto d = deltaMover(in, s, i, b);
    s.dist += d.dist;
    s.excesso += d.excesso;
    s.naoAlocados += d.naoAlocados;
    if (a >= 0) {
        --s.carga[a];
        --s.porTipo[a][in.tipoCand[i]];
        s.incompativeis -= !hospeda(s.typeSlots, a, in.tipoCand[i]);
    }
    if (b >= 0) {
        ++s.carga[b];
        ++s.porTipo[b][in.tipoCand[i]];
        s.incompativeis += !hospeda(s.typeSlots, b, in.tipoCand[i]);
    }
    s.esc[i] = b;
}
Custo deltaTroca(const Instancia& in, const Solucao& s, int i, int h) {
    int a = s.esc[i], b = s.esc[h];
    return (b < 0 ? 0 : in.d(i, b)) + (a < 0 ? 0 : in.d(h, a)) - (a < 0 ? 0 : in.d(i, a)) -
           (b < 0 ? 0 : in.d(h, b));
}
void trocar(const Instancia& in, Solucao& s, int i, int h) {
    int a = s.esc[i], b = s.esc[h];
    mover(in, s, i, b);
    mover(in, s, h, a);
}
bool melhorSolucao(const Solucao& a, const Solucao& b) {
    return a.violacoes() != b.violacoes() ? a.violacoes() < b.violacoes() : a.dist < b.dist;
}
void validar(const Instancia& in, const Solucao& s, int K) {
    auto fail = []() { throw std::runtime_error("validacao independente da solucao falhou"); };
    if (s.esc.size() != size_t(in.n) || s.typeSlots.size() != size_t(in.m))
        fail();
    std::vector<int> load(in.m);
    std::vector<std::vector<int>> types(in.m, std::vector<int>(in.k));
    Custo distance = 0;
    int missing = 0, bad = 0, over = 0;
    for (int j = 0; j < in.m; ++j)
        if (numeroTipos(s.typeSlots[j]) > K || (s.typeSlots[j] >> in.k))
            fail();
    for (int i = 0; i < in.n; ++i) {
        int j = s.esc[i];
        if (j == -1) {
            ++missing;
            continue;
        }
        if (j < 0 || j >= in.m)
            fail();
        ++load[j];
        ++types[j][in.tipoCand[i]];
        distance += in.dist[size_t(i) * in.m + j];
        if (!(s.typeSlots[j] & (1u << in.tipoCand[i])))
            ++bad;
    }
    for (int j = 0; j < in.m; ++j)
        over += std::max(0, load[j] - in.capEsc[j]);
    if (load != s.carga || types != s.porTipo || distance != s.dist || missing != s.naoAlocados ||
        bad != s.incompativeis || over != s.excesso)
        fail();
}
void imprimirRelatorio(const Instancia& in, const Solucao& s) {
    for (int j = 0; j < in.m; ++j) {
        std::cout << "  " << in.idEsc[j] << " tipos=";
        for (int t = 0; t < in.k; ++t)
            if (hospeda(s.typeSlots, j, t))
                std::cout << in.nomeTipo[t] << ":" << s.porTipo[j][t] << " ";
        std::cout << " carga=" << s.carga[j] << "/" << in.capEsc[j]
                  << " ocupacao=" << 100.0 * s.carga[j] / in.capEsc[j] << "%\n";
    }
}
