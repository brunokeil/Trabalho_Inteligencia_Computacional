#!/usr/bin/env python3
"""Empacota fontes, dados, resultados, documentação e histórico disponível."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'entrega/Trabalho1-entrega.zip'
excluded={'.git','build','.cache','__pycache__','.DS_Store'}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if not p.is_file() or p==out or any(x in excluded for x in rel.parts) or p.name=='alocacao' or p.suffix in {'.aux','.log','.out','.toc','.fls','.fdb_latexmk'}:continue
        z.write(p,Path('Trabalho1')/rel)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    print(f'{out}: {len(z.namelist())} arquivos, {out.stat().st_size/1e6:.2f} MB; integridade OK')
