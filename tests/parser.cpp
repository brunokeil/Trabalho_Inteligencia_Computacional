#include <cassert>
#include <fstream>
#include <iostream>

#include "instancia.hpp"
int main() {
    const char* names[] = {"Modelo_de_Instancia", "instancia2", "instancia_A", "instancia_B"};
    int ns[] = {109, 2550, 4518, 4442};
    int ms[] = {5, 10, 15, 15};
    for (int q = 0; q < 4; ++q) {
        auto in = Instancia::ler(std::string("entrega/") + names[q] + ".txt");
        assert(in.n == ns[q] && in.m == ms[q]);
        assert(in.dist.size() == size_t(in.n * in.m));
        assert(in.k == 6);
        if (q == 1)
            assert(in.idCand[0] == "C1827");
        if (q == 2)
            assert(in.cepCand[0] == "36088-211");
    }
    assert(distanciaDecimal("20.4986") == 20498600);
    assert(distanciaDecimal("0.000001") == 1);
    for (auto s : {"-1", "nan", "1x", "1.0000001", ""}) {
        bool failed = false;
        try {
            distanciaDecimal(s);
        } catch (...) {
            failed = true;
        }
        assert(failed);
    }
    std::cout << "parser: quatro instancias, IDs, CEPs, decimais OK\n";
}
