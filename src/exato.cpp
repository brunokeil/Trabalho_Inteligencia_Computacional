#include "exato.hpp"

#include <unistd.h>

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <limits>
#include <numeric>
#include <queue>
#include <stdexcept>

Certificado fluxoTipos(const Instancia& in, const Slots& slots) {
    int N = in.k + in.m + 2, source = N - 2, sink = N - 1;
    std::vector<std::vector<int>> c(N, std::vector<int>(N));
    for (int t = 0; t < in.k; ++t) {
        c[source][t] = int(in.candsTipo[t].size());
        for (int j = 0; j < in.m; ++j)
            if (hospeda(slots, j, t))
                c[t][in.k + j] = in.n;
    }
    for (int j = 0; j < in.m; ++j)
        c[in.k + j][sink] = in.capEsc[j];
    Certificado result;
    result.slots = slots;
    result.quotas.assign(in.m, std::vector<int>(in.k));
    for (;;) {
        std::vector<int> parent(N, -1);
        parent[source] = source;
        std::queue<int> q;
        q.push(source);
        while (!q.empty() && parent[sink] < 0) {
            int a = q.front();
            q.pop();
            for (int b = 0; b < N; ++b)
                if (c[a][b] > 0 && parent[b] < 0) {
                    parent[b] = a;
                    q.push(b);
                }
        }
        if (parent[sink] < 0)
            break;
        int f = in.n;
        for (int b = sink; b != source; b = parent[b])
            f = std::min(f, c[parent[b]][b]);
        for (int b = sink; b != source; b = parent[b]) {
            c[parent[b]][b] -= f;
            c[b][parent[b]] += f;
        }
        result.atendidos += f;
    }
    for (int j = 0; j < in.m; ++j)
        for (int t = 0; t < in.k; ++t)
            result.quotas[j][t] = c[in.k + j][t];
    return result;
}
namespace {
std::string quote(const std::string& s) {
    std::string r = "'";
    for (char c : s)
        r += c == '\'' ? "'\\''" : std::string(1, c);
    return r + "'";
}
struct Temp {
    std::string path;
    Temp() {
        char name[] = "/tmp/dcc136-XXXXXX";
        int fd = mkstemp(name);
        if (fd < 0)
            throw std::runtime_error("mkstemp falhou");
        close(fd);
        path = name;
    }
    ~Temp() {
        std::remove(path.c_str());
    }
};
}  // namespace
Certificado preChecar(const Instancia& in, int K, const std::string& script) {
    Temp input, output;
    {
        std::ofstream f(input.path);
        f << in.m << ' ' << in.k << ' ' << K << '\n';
        for (int c : in.capEsc)
            f << c << ' ';
        f << '\n';
        for (auto& v : in.candsTipo)
            f << v.size() << ' ';
    }
    std::string cmd = "python3 " + quote(script) + " " + quote(input.path) + " " + quote(output.path);
    if (std::system(cmd.c_str()) != 0)
        throw std::runtime_error(
            "pre-checagem inconclusiva; verifique Python/SciPy e scripts/viabilidade.py");
    Certificado result;
    int m = 0, k = 0, kk = 0;
    std::ifstream f(output.path);
    f >> result.atendidos >> m >> k >> kk;
    if (!f || m != in.m || k != in.k || kk != K)
        throw std::runtime_error("certificado invalido");
    result.slots.assign(m, 0);
    result.quotas.assign(m, std::vector<int>(k));
    int total = 0;
    std::vector<int> dem(k);
    for (int j = 0; j < m; ++j) {
        int load = 0;
        for (int t = 0; t < k; ++t) {
            int x = -1;
            f >> x;
            if (!f || x < 0)
                throw std::runtime_error("quota invalida");
            result.quotas[j][t] = x;
            load += x;
            dem[t] += x;
            if (x)
                result.slots[j] |= 1u << t;
        }
        if (load > in.capEsc[j] || numeroTipos(result.slots[j]) > K)
            throw std::runtime_error("certificado excede capacidade/K");
        total += load;
    }
    for (int t = 0; t < k; ++t)
        if (dem[t] > int(in.candsTipo[t].size()))
            throw std::runtime_error("certificado excede demanda");
    if (total != result.atendidos)
        throw std::runtime_error("total certificado invalido");
    return result;
}
// Reaproveita os caminhos aumentantes comprimidos do transporte original.
// Agora inclui todos os candidatos/escolas e filtra cada arco por compatibilidade.
std::vector<int> resolverTransporteExato(const Instancia& in, const Slots& slots) {
    const Custo INF = std::numeric_limits<Custo>::max() / 4;
    int m = in.m;
    std::vector<int> esc(in.n, -1), load(m);
    std::vector<std::vector<Custo>> w(m, std::vector<Custo>(m));
    std::vector<std::vector<int>> arg(m, std::vector<int>(m));
    for (int i = 0; i < in.n; ++i) {
        for (auto& v : w)
            std::fill(v.begin(), v.end(), INF);
        for (int h = 0; h < i; ++h)
            if (esc[h] >= 0) {
                int a = esc[h];
                for (int b = 0; b < m; ++b)
                    if (b != a && hospeda(slots, b, in.tipoCand[h])) {
                        auto d = in.d(h, b) - in.d(h, a);
                        if (d < w[a][b]) {
                            w[a][b] = d;
                            arg[a][b] = h;
                        }
                    }
            }
        std::vector<Custo> d(m, INF);
        std::vector<int> pred(m, -1);
        for (int b = 0; b < m; ++b)
            if (hospeda(slots, b, in.tipoCand[i]))
                d[b] = in.d(i, b);
        for (int it = 0; it < m - 1; ++it) {
            bool changed = false;
            for (int a = 0; a < m; ++a)
                for (int b = 0; b < m; ++b)
                    if (d[a] < INF && w[a][b] < INF && d[a] + w[a][b] < d[b]) {
                        d[b] = d[a] + w[a][b];
                        pred[b] = a;
                        changed = true;
                    }
            if (!changed)
                break;
        }
        int b = -1;
        for (int j = 0; j < m; ++j)
            if (load[j] < in.capEsc[j] && d[j] < INF && (b < 0 || d[j] < d[b]))
                b = j;
        if (b < 0)
            throw std::runtime_error("transporte com tipos fixos inviavel");
        ++load[b];
        while (pred[b] >= 0) {
            int a = pred[b];
            esc[arg[a][b]] = b;
            b = a;
        }
        esc[i] = b;
    }
    return esc;
}
