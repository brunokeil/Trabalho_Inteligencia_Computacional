// DCC136: construção GRASP, VND e tabu para localização de locais de prova.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <stdexcept>

#include "busca_local.hpp"
namespace fs = std::filesystem;
namespace {
double now() {
    return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
std::string decimalKm(Custo c) {
    std::ostringstream out;
    if (c < 0) {
        out << '-';
        c = -c;
    }
    out << c / ESCALA << '.' << std::setfill('0') << std::setw(6) << c % ESCALA;
    return out.str();
}
std::string quoted(const std::string& s) {
    std::string r = "\"";
    for (unsigned char c : s) {
        if (c == '"' || c == '\\') {
            r += '\\';
            r += char(c);
        } else if (c < 32) {
            const char* h = "0123456789abcdef";
            r += "\\u00";
            r += h[c >> 4];
            r += h[c & 15];
        } else
            r += char(c);
    }
    return r + '"';
}
template <class T>
void array(std::ostream& o, const std::vector<T>& v) {
    o << '[';
    for (size_t i = 0; i < v.size(); ++i) {
        if (i)
            o << ',';
        o << v[i];
    }
    o << ']';
}
void strings(std::ostream& o, const std::vector<std::string>& v) {
    o << '[';
    for (size_t i = 0; i < v.size(); ++i) {
        if (i)
            o << ',';
        o << quoted(v[i]);
    }
    o << ']';
}
void solution(std::ostream& o, const Instancia& in, const Parametros& p, const Solucao& s) {
    o << "{\"distance\":" << decimalKm(s.dist) << ",\"objective\":" << double(s.custo(p) / ESCALA)
      << ",\"feasible\":" << (s.viavel() ? "true" : "false") << ",\"overflow\":" << s.excesso
      << ",\"unassigned\":" << s.naoAlocados << ",\"incompatible\":" << s.incompativeis << ",\"assign\":";
    array(o, s.esc);
    o << ",\"typeSlots\":";
    array(o, s.typeSlots);
    o << ",\"load\":";
    array(o, s.carga);
    o << ",\"loadByType\":[";
    for (int j = 0; j < in.m; ++j) {
        if (j)
            o << ',';
        array(o, s.porTipo[j]);
    }
    o << "],\"occupancy\":[";
    for (int j = 0; j < in.m; ++j) {
        if (j)
            o << ',';
        o << double(s.carga[j]) / in.capEsc[j];
    }
    o << "]}";
}
struct Run {
    unsigned seed;
    Solucao initial, final;
    EstatConstr construction;
    EstatBL search;
    double tc = 0, tls = 0;
};
void help() {
    std::cout << "Uso: ./alocacao --instancia ARQ --tipos-por-escola {1|2} [opcoes]\n"
                 "--seed INT --runs INT --alpha [0,1] --metodo {vnd|tabu} --ls {first|best}\n"
                 "--saida ARQ.csv|ARQ.json (gera ambos; JSON contem todas as solucoes e curvas)\n"
                 "--p INT --max-iter INT --sem-melhora INT --tempo SEG (0: sem limite temporal)\n"
                 "--tmin INT --tmax INT --n3-periodo INT --n3-amostras INT --adaptar INT\n"
                 "--viz {1|2|3|12|123} --sem-busca --trace --relatorio --exato\n"
                 "--viabilidade-script CAMINHO (padrao: scripts/viabilidade.py ao lado do executavel)\n";
}
}  // namespace
int main(int argc, char** argv) {
    try {
        Parametros p;
        std::string input, output, script;
        unsigned seed = 1;
        int runs = 1;
        bool report = false, exact = false, skip = false, kGiven = false;
        auto integer = [](const std::string& s) {
            size_t pos = 0;
            long long x = std::stoll(s, &pos);
            if (pos != s.size() || x < 0 || x > 2147483647)
                throw std::runtime_error("inteiro invalido: " + s);
            return int(x);
        };
        auto real = [](const std::string& s) {
            size_t pos = 0;
            double x = std::stod(s, &pos);
            if (pos != s.size() || !std::isfinite(x))
                throw std::runtime_error("real invalido: " + s);
            return x;
        };
        for (int a = 1; a < argc; ++a) {
            std::string o = argv[a];
            auto val = [&]() {
                if (a + 1 >= argc)
                    throw std::runtime_error("faltou valor para " + o);
                return std::string(argv[++a]);
            };
            if (o == "--help" || o == "-h") {
                help();
                return 0;
            } else if (o == "--instancia")
                input = val();
            else if (o == "--tipos-por-escola") {
                p.K = integer(val());
                kGiven = true;
            } else if (o == "--seed")
                seed = unsigned(integer(val()));
            else if (o == "--runs")
                runs = integer(val());
            else if (o == "--alpha")
                p.alpha = real(val());
            else if (o == "--metodo")
                p.metodo = val();
            else if (o == "--ls") {
                auto s = val();
                if (s != "first" && s != "best")
                    throw std::runtime_error("ls deve ser first ou best");
                p.first = s == "first";
            } else if (o == "--saida")
                output = val();
            else if (o == "--p")
                p.p = integer(val());
            else if (o == "--max-iter")
                p.maxIter = integer(val());
            else if (o == "--sem-melhora")
                p.semMelhora = integer(val());
            else if (o == "--tmin")
                p.tmin = integer(val());
            else if (o == "--tmax")
                p.tmax = integer(val());
            else if (o == "--n3-periodo")
                p.periodoN3 = integer(val());
            else if (o == "--n3-amostras")
                p.amostrasN3 = integer(val());
            else if (o == "--adaptar")
                p.adaptar = integer(val());
            else if (o == "--tempo")
                p.tempoLimite = real(val());
            else if (o == "--viz")
                p.viz = val();
            else if (o == "--sem-busca")
                skip = true;
            else if (o == "--trace")
                p.trace = true;
            else if (o == "--relatorio")
                report = true;
            else if (o == "--exato")
                exact = true;
            else if (o == "--viabilidade-script")
                script = val();
            else if (!o.empty() && o[0] != '-' && input.empty())
                input = o;
            else
                throw std::runtime_error("opcao desconhecida: " + o);
        }
        if (input.empty()) {
            help();
            return 1;
        }
        if (!kGiven)
            throw std::runtime_error("parametro obrigatorio ausente: --tipos-por-escola {1|2}");
        if ((p.K != 1 && p.K != 2) || runs < 1 || runs > 10000 || p.alpha < 0 || p.alpha > 1 || p.p < 1 ||
            p.maxIter < 1 || p.semMelhora < 1 || p.tmin < 1 || p.tmax < p.tmin || p.periodoN3 < 1 ||
            p.amostrasN3 < 1 || p.adaptar < 1 || p.tempoLimite < 0 || p.viz.empty() ||
            p.viz.find_first_not_of("123") != std::string::npos || (p.metodo != "tabu" && p.metodo != "vnd"))
            throw std::runtime_error("parametros fora do dominio; consulte --help");
        if (script.empty())
            script = (fs::absolute(argv[0]).parent_path() / "scripts/viabilidade.py").string();
        if (!output.empty()) {
            // Both output extensions are written, regardless of the requested one.
            for (const char* ext : {".json", ".csv"}) {
                fs::path target = output;
                target.replace_extension(ext);
                if (fs::weakly_canonical(input) == fs::weakly_canonical(target) ||
                    (fs::exists(target) && fs::equivalent(input, target)))
                    throw std::runtime_error("saida nao pode sobrescrever instancia");
            }
        }
        double start = now();
        auto in = Instancia::ler(input);
        p.ajustar(in);
        double readTime = now() - start;
        start = now();
        auto cert = preChecar(in, p.K, script);
        double preTime = now() - start;
        bool possible = cert.atendidos == in.n;
        std::cout << in.nome << " K=" << p.K << " " << (possible ? "VIAVEL" : "INVIAVEL COMPROVADA")
                  << " atendimento maximo=" << cert.atendidos << "/" << in.n
                  << " nao_alocados_min=" << in.n - cert.atendidos << " pre_check=" << preTime << "s\n"
                  << std::flush;
        std::vector<Run> results;
        int best = 0;
        for (int r = 0; r < runs; ++r) {
            Run x;
            x.seed = seed + unsigned(r);
            std::mt19937 rng(x.seed);
            start = now();
            x.initial = construir(in, p, cert, rng, x.construction);
            x.tc = now() - start;
            x.final = x.initial;
            start = now();
            if (!skip) {
                BuscaLocal bl(in, p, rng);
                x.search = bl.executar(x.final);
            }
            x.tls = now() - start;
            validar(in, x.initial, p.K);
            validar(in, x.final, p.K);
            if (x.final.excesso || x.final.incompativeis || in.n - x.final.naoAlocados != cert.atendidos)
                throw std::runtime_error("solucao final nao preserva atendimento certificado");
            std::cout << "run=" << r + 1 << " seed=" << x.seed << std::fixed << std::setprecision(4)
                      << " inicial=" << decimalKm(x.initial.dist)
                      << " final=" << x.final.dist / double(ESCALA)
                      << " km melhora=" << (x.initial.dist - x.final.dist) / double(ESCALA)
                      << " constr=" << x.tc << "s busca=" << x.tls << "s iter=" << x.search.iteracoes << "\n";
            if (r > 0 && melhorSolucao(x.final, results[best].final))
                best = r;
            results.push_back(std::move(x));
        }
        std::vector<double> costs;
        for (auto& x : results)
            costs.push_back(x.final.dist / double(ESCALA));
        double mean = std::accumulate(costs.begin(), costs.end(), 0.0) / runs, variance = 0;
        for (double x : costs)
            variance += (x - mean) * (x - mean);
        std::cout << "distancia km: min=" << *std::min_element(costs.begin(), costs.end())
                  << " media=" << mean
                  << " desvio_amostral=" << (runs > 1 ? std::sqrt(variance / (runs - 1)) : 0)
                  << " max=" << *std::max_element(costs.begin(), costs.end())
                  << " melhor_seed=" << results[best].seed << "\n";
        if (report)
            imprimirRelatorio(in, results[best].final);
        if (exact && possible) {
            auto ref = montarSolucao(in, results[best].final.typeSlots,
                                     resolverTransporteExato(in, results[best].final.typeSlots));
            validar(in, ref, p.K);
            std::cout << "Referencia exata SOMENTE para os tipos finais fixos: " << ref.dist / double(ESCALA)
                      << " km\n";
        }
        if (!output.empty()) {
            fs::path jp = output, cp = output;
            jp.replace_extension(".json");
            cp.replace_extension(".csv");
            if (!jp.parent_path().empty())
                fs::create_directories(jp.parent_path());
            std::ofstream j(jp), csv(cp);
            if (!j || !csv)
                throw std::runtime_error("nao foi possivel abrir saidas");
            j << std::setprecision(16);
            j << "{\"schema\":1,\"instance\":" << quoted(fs::absolute(input).string())
              << ",\"name\":" << quoted(in.nome) << ",\"K\":" << p.K
              << ",\"feasibility\":" << quoted(possible ? "feasible" : "infeasible")
              << ",\"maximum_assigned\":" << cert.atendidos << ",\"read_seconds\":" << readTime
              << ",\"precheck_seconds\":" << preTime << ",\"method\":" << quoted(p.metodo)
              << ",\"ls\":" << quoted(p.first ? "first" : "best") << ",\"alpha\":" << p.alpha
              << ",\"p\":" << p.p << ",\"viz\":" << quoted(p.viz) << ",\"max_iter\":" << p.maxIter
              << ",\"stagnation\":" << p.semMelhora << ",\"time_limit\":" << p.tempoLimite
              << ",\"tmin\":" << p.tmin << ",\"tmax\":" << p.tmax << ",\"n3_period\":" << p.periodoN3
              << ",\"n3_samples\":" << p.amostrasN3 << ",\"adapt_every\":" << p.adaptar
              << ",\"lambda_initial\":" << double(p.lambda / ESCALA) << ",\"mu\":" << double(p.mu / ESCALA)
              << ",\"skip_search\":" << (skip ? "true" : "false") << ",\"best_run\":" << best
              << ",\"candidateIds\":";
            strings(j, in.idCand);
            j << ",\"schoolIds\":";
            strings(j, in.idEsc);
            j << ",\"typeNames\":";
            strings(j, in.nomeTipo);
            j << ",\"capacities\":";
            array(j, in.capEsc);
            j << ",\"certificate_quotas\":[";
            for (int h = 0; h < in.m; ++h) {
                if (h)
                    j << ',';
                array(j, cert.quotas[h]);
            }
            j << "],\"runs\":[\n";
            csv << "instance,K,feasibility,method,ls,alpha,seed,p,viz,tmin,tmax,max_iter,stagnation,time_"
                   "limit,n3_period,n3_samples,adapt_every,lambda_initial,mu,initial_distance,final_distance,"
                   "initial_objective,final_objective,improvement_abs,improvement_pct,construction_s,search_"
                   "s,precheck_s,iterations,eval_n1,eval_n2,eval_n3,mov_n1,mov_n2,mov_n3,schools_used,"
                   "unassigned,overflow,fallback,restarts,repairs,types_per_school,loads,occupancy\n"
                << std::setprecision(12);
            for (int r = 0; r < runs; ++r) {
                auto& x = results[r];
                auto& e = x.search;
                auto& s = x.final;
                if (r)
                    j << ",\n";
                j << "{\"seed\":" << x.seed << ",\"construction_seconds\":" << x.tc
                  << ",\"search_seconds\":" << x.tls
                  << ",\"fallback\":" << (x.construction.fallback ? "true" : "false")
                  << ",\"restarts\":" << x.construction.reinicios << ",\"repairs\":" << x.construction.reparos
                  << ",\"iterations\":" << e.iteracoes << ",\"evaluations\":[" << e.avaliacoes[0] << ','
                  << e.avaliacoes[1] << ',' << e.avaliacoes[2] << "],\"moves\":[" << e.movimentos[0] << ','
                  << e.movimentos[1] << ',' << e.movimentos[2] << "],\"aspirations\":" << e.aspiracoes
                  << ",\"tabu_rejections\":" << e.tabusRejeitados << ",\"lambda_updates\":" << e.ajustesLambda
                  << ",\"infeasible_iterations\":" << e.iteracoesInviaveis << ",\"initial\":";
                solution(j, in, p, x.initial);
                j << ",\"final\":";
                solution(j, in, p, s);
                j << ",\"convergence\":[";
                for (size_t q = 0; q < e.curva.size(); ++q) {
                    auto& pt = e.curva[q];
                    if (q)
                        j << ',';
                    j << '[' << pt.iter << ',' << decimalKm(pt.melhorDist) << ',' << decimalKm(pt.atualDist)
                      << ',' << pt.naoAlocados << ',' << pt.excessoAtual << ',' << double(pt.lambda / ESCALA)
                      << ']';
                }
                j << "]}";
                int used = int(std::count_if(s.carga.begin(), s.carga.end(), [](int v) { return v > 0; }));
                double improvement = (x.initial.dist - s.dist) / double(ESCALA);
                csv << in.nome << ',' << p.K << ',' << (possible ? "feasible" : "infeasible") << ','
                    << p.metodo << ',' << (p.first ? "first" : "best") << ',' << p.alpha << ',' << x.seed
                    << ',' << p.p << ',' << p.viz << ',' << p.tmin << ',' << p.tmax << ',' << p.maxIter << ','
                    << p.semMelhora << ',' << p.tempoLimite << ',' << p.periodoN3 << ',' << p.amostrasN3
                    << ',' << p.adaptar << ',' << double(p.lambda / ESCALA) << ',' << double(p.mu / ESCALA)
                    << ',' << decimalKm(x.initial.dist) << ',' << decimalKm(s.dist) << ','
                    << double(x.initial.custo(p) / ESCALA) << ',' << double(s.custo(p) / ESCALA) << ','
                    << improvement << ','
                    << (x.initial.dist ? 100 * (x.initial.dist - s.dist) / double(x.initial.dist) : 0) << ','
                    << x.tc << ',' << x.tls << ',' << preTime << ',' << e.iteracoes << ',' << e.avaliacoes[0]
                    << ',' << e.avaliacoes[1] << ',' << e.avaliacoes[2] << ',' << e.movimentos[0] << ','
                    << e.movimentos[1] << ',' << e.movimentos[2] << ',' << used << ',' << s.naoAlocados << ','
                    << s.excesso << ',' << x.construction.fallback << ',' << x.construction.reinicios << ','
                    << x.construction.reparos << ',';
                for (int h = 0; h < in.m; ++h) {
                    if (h)
                        csv << '|';
                    csv << numeroTipos(s.typeSlots[h]);
                }
                csv << ',';
                for (int h = 0; h < in.m; ++h) {
                    if (h)
                        csv << '|';
                    csv << s.carga[h];
                }
                csv << ',';
                for (int h = 0; h < in.m; ++h) {
                    if (h)
                        csv << '|';
                    csv << double(s.carga[h]) / in.capEsc[h];
                }
                csv << '\n';
            }
            j << "\n]}\n";
            if (!j || !csv)
                throw std::runtime_error("falha ao gravar resultados");
            std::cout << "Resultados: " << jp << " e " << cp << "\n";
        }
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Erro: " << e.what() << '\n';
        return 1;
    }
}
