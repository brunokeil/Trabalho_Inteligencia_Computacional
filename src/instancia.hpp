// Leitura e pré-processamento das instâncias do Problema de Localização de
// Locais de Prova (variante do SSCFLP com tipos de prova).
#pragma once

#include <string>
#include <vector>

// Inteiros em milionésimos de km (1 mm): preservam até seis casas decimais.
using Custo = long long;
constexpr Custo ESCALA = 1000000;
Custo distanciaDecimal(const std::string& s);

struct Sala {
    int cap;  // capacidade da sala
    int id;   // índice original da sala na escola (1-based, ordem do arquivo)
};

struct Instancia {
    std::string nome;
    int n = 0;  // nº de candidatos
    int m = 0;  // nº de escolas (locais de prova)
    int k = 0;  // nº de tipos de prova

    std::vector<std::string> nomeTipo;  // nome de cada tipo (M1, M2, ...)

    // Candidatos
    std::vector<std::string> idCand, idEsc;
    std::vector<double> latCand, lonCand, latEsc, lonEsc;
    std::vector<int> tipoCand;
    std::vector<std::string> cepCand;

    // Escolas
    std::vector<int> capEsc;  // Q_j
    std::vector<std::string> cepEsc;
    std::vector<std::vector<Sala>> salas;    // salas de cada escola, capacidade DECRESCENTE
    std::vector<std::vector<int>> capAcum;   // capAcum[j][r] = soma das r maiores salas de j
    std::vector<std::vector<int>> salasNec;  // salasNec[j][L] = nº mínimo de salas p/ carga L

    // Matriz de distâncias n x m (row-major), em milionésimos de km
    std::vector<Custo> dist;
    Custo distMax = 0;

    // Índices auxiliares por tipo
    std::vector<std::vector<int>> candsTipo;  // candidatos de cada tipo

    Custo d(int i, int j) const {
        return dist[(size_t)i * m + j];
    }

    // Nº mínimo de salas que a escola j precisa abrir para acomodar 'carga'
    // candidatos. Abrir as maiores salas primeiro é ótimo para minimizar a
    // quantidade de salas. Acima da capacidade, todas as salas ficam abertas.
    int salasPara(int j, int carga) const {
        if (carga <= 0)
            return 0;
        if (carga > capEsc[j])
            return (int)salas[j].size();
        return salasNec[j][carga];
    }

    static Instancia ler(const std::string& caminho);
};
