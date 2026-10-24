#include "instancia.hpp"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <functional>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>

namespace {
std::string trim(const std::string& s) {
    const auto a = s.find_first_not_of(" \t\r\n");
    return a == std::string::npos ? "" : s.substr(a, s.find_last_not_of(" \t\r\n") - a + 1);
}
std::vector<std::string> split(const std::string& s, char sep) {
    std::vector<std::string> r;
    size_t a = 0;
    for (;;) {
        auto b = s.find(sep, a);
        r.push_back(trim(s.substr(a, b - a)));
        if (b == std::string::npos)
            break;
        a = b + 1;
    }
    return r;
}
int integer(const std::string& s, int max = 1000000) {
    if (s.empty() || s.find_first_not_of("0123456789") != std::string::npos)
        throw std::runtime_error("inteiro invalido: " + s);
    auto v = std::stoll(s);
    if (v > max)
        throw std::runtime_error("inteiro fora do limite: " + s);
    return int(v);
}
double coord(const std::string& s, double bound) {
    size_t p = 0;
    double v = std::stod(s, &p);
    if (p != s.size() || !std::isfinite(v) || std::abs(v) > bound)
        throw std::runtime_error("coordenada invalida: " + s);
    return v;
}
}  // namespace
Custo distanciaDecimal(const std::string& s) {
    auto v = split(s, '.');
    if (v.empty() || v.size() > 2 || v[0].empty())
        throw std::runtime_error("distancia invalida: " + s);
    Custo a = integer(v[0], 1000000) * ESCALA;
    if (v.size() == 2) {
        if (v[1].empty() || v[1].size() > 6)
            throw std::runtime_error("distancia exige 1 a 6 decimais: " + s);
        int f = integer(v[1]);
        for (size_t k = v[1].size(); k < 6; ++k)
            f *= 10;
        a += f;
    }
    return a;
}
Instancia Instancia::ler(const std::string& caminho) {
    std::ifstream f(caminho);
    if (!f)
        throw std::runtime_error("nao foi possivel abrir " + caminho);
    std::vector<std::string> linhas;
    std::string l;
    while (std::getline(f, l)) {
        l = trim(l);
        if (!l.empty() && l[0] != '#')
            linhas.push_back(l);
    }
    size_t p = 0;
    auto next = [&]() {
        if (p >= linhas.size())
            throw std::runtime_error("arquivo truncado na linha util " + std::to_string(p + 1));
        return linhas[p++];
    };
    auto header = [&](const std::string& key) {
        auto v = split(next(), ':');
        if (v.size() != 2 || v[0] != key)
            throw std::runtime_error("cabecalho esperado: " + key);
        return integer(v[1], 100000);
    };
    Instancia in;
    in.nome = caminho.substr(caminho.find_last_of("/\\") + 1);
    in.n = header("NUM_CANDIDATOS");
    in.m = header("NUM_ESCOLAS");
    if (in.n <= 0 || in.m <= 0 || 1LL * in.n * in.m > 100000000)
        throw std::runtime_error("dimensoes invalidas/excessivas");
    if (linhas.size() != size_t(2 + 2 * in.n + in.m))
        throw std::runtime_error("contagens de candidatos/escolas/matriz nao conferem com cabecalho");
    std::map<std::string, int> idx;
    std::set<std::string> ids;
    const std::set<std::string> permitidos = {"M1", "M2", "M3h", "M3e", "M3d", "M3s"};
    for (int i = 0; i < in.n; ++i) {
        auto v = split(next(), ',');
        if (v.size() != 5)
            throw std::runtime_error("candidato exige 5 campos");
        if (v[0].empty() || !ids.insert(v[0]).second || v[1].empty())
            throw std::runtime_error("ID candidato duplicado/vazio ou CEP vazio");
        if (!permitidos.count(v[2]))
            throw std::runtime_error("tipo desconhecido: " + v[2]);
        if (!idx.count(v[2])) {
            idx[v[2]] = int(in.nomeTipo.size());
            in.nomeTipo.push_back(v[2]);
        }
        in.idCand.push_back(v[0]);
        in.cepCand.push_back(v[1]);
        in.tipoCand.push_back(idx[v[2]]);
        in.latCand.push_back(coord(v[3], 90));
        in.lonCand.push_back(coord(v[4], 180));
    }
    in.k = int(in.nomeTipo.size());
    ids.clear();
    in.salas.resize(in.m);
    in.capEsc.resize(in.m);
    for (int j = 0; j < in.m; ++j) {
        auto v = split(next(), ',');
        if (v.size() != 6)
            throw std::runtime_error("escola exige 6 campos");
        if (v[0].empty() || !ids.insert(v[0]).second || v[1].empty())
            throw std::runtime_error("ID escola duplicado/vazio ou CEP vazio");
        in.idEsc.push_back(v[0]);
        in.cepEsc.push_back(v[1]);
        in.latEsc.push_back(coord(v[2], 90));
        in.lonEsc.push_back(coord(v[3], 180));
        int nr = integer(v[4]);
        auto caps = split(v[5], ';');
        if (nr <= 0 || caps.size() != size_t(nr))
            throw std::runtime_error("num_salas difere da lista de capacidades");
        for (int r = 0; r < nr; ++r) {
            int c = integer(caps[r]);
            if (c <= 0 || in.capEsc[j] > 1000000 - c)
                throw std::runtime_error("capacidade invalida/excessiva");
            in.salas[j].push_back({c, r + 1});
            in.capEsc[j] += c;
        }
    }
    for (int i = 0; i < in.n; ++i) {
        auto v = split(next(), ',');
        if (v.size() != size_t(in.m))
            throw std::runtime_error("numero de colunas da matriz incorreto");
        for (auto& s : v) {
            Custo d = distanciaDecimal(s);
            in.dist.push_back(d);
            in.distMax = std::max(in.distMax, d);
        }
    }
    in.capAcum.resize(in.m);
    in.salasNec.resize(in.m);
    for (int j = 0; j < in.m; ++j) {
        auto& s = in.salas[j];
        std::stable_sort(s.begin(), s.end(), [](const Sala& a, const Sala& b) { return a.cap > b.cap; });
        in.capAcum[j].assign(s.size() + 1, 0);
        for (size_t r = 0; r < s.size(); ++r)
            in.capAcum[j][r + 1] = in.capAcum[j][r] + s[r].cap;
        in.salasNec[j].assign(in.capEsc[j] + 1, 0);
        int r = 0;
        for (int L = 1; L <= in.capEsc[j]; ++L) {
            while (in.capAcum[j][r] < L)
                ++r;
            in.salasNec[j][L] = r;
        }
    }
    in.candsTipo.assign(in.k, {});
    for (int i = 0; i < in.n; ++i)
        in.candsTipo[in.tipoCand[i]].push_back(i);
    return in;
}
