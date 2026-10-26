#!/usr/bin/env python3
"""Compatibilidade: prepara os downloads atuais sem alterar originais.

A conversão antiga dependia de 52 downloads que não estão mais nesta árvore.
Use preparar_instancias.py para a coleção atual e consulte auditoria_atual.csv.
"""
from preparar_instancias import main
if __name__ == '__main__':
    main()
