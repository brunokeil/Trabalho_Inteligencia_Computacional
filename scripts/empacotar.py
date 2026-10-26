#!/usr/bin/env python3
"""Empacota somente a entrega atual, sem caches, binários ou resultados antigos."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'entrega/Trabalho1-entrega.zip'
root_files=['README.md','Makefile','requirements.txt','requirements-tested.txt',
            'Trabalho 1 - 2026-3 - Implementacao (1).pdf']
docs=['relatorio.tex','relatorio.pdf','sbc-template.sty','apresentacao.html','apresentacao_template.html',
      'resultados_atual_texto.tex','resultados_atual_tabela.tex','resultados_atual_completo.tex',
      'exemplo8_K1.md','exemplo8_K1-trace.txt','algoritmos.md','slides.md','auditoria.md',
      'testes_atual.log.txt','sanitizadores_atual.log.txt','campanha_final_vnd.log.txt',
      'campanha_final_tabu.log.txt','compilacao_relatorio.log.txt','verificacao_apresentacao.json']
paths=[ROOT/p for p in root_files]+[ROOT/'docs'/p for p in docs]
for folder in ['src','scripts','tests','instances','resultados/final_vnd','resultados/final_tabu']:
    paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and not any(x.startswith('.') or x=='__pycache__' for x in p.relative_to(ROOT).parts) and p.suffix not in ('.pyc','.tmp'))
paths.extend(p for p in (ROOT/'entrega').glob('*.txt'))
paths.extend(p for p in (ROOT/'resultados').glob('final_*') if p.is_file())
paths.extend(p for p in (ROOT/'resultados').glob('exemplo8_K1.*') if p.is_file())
# Missing required artifacts are errors, never silently omitted.
assert all(p.exists() for p in paths), [str(p) for p in paths if not p.exists()]
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(set(paths)):
        z.write(p,Path('Trabalho1')/p.relative_to(ROOT))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    names=set(z.namelist())
    for p in ['docs/relatorio.pdf','docs/relatorio.tex','docs/apresentacao.html','src/main.cpp','Makefile','resultados/final_resumo.csv']:
        assert 'Trabalho1/'+p in names
    print(f'{out}: {len(names)} arquivos, {out.stat().st_size/1e6:.2f} MB; integridade OK')
sha=hashlib.sha256(out.read_bytes()).hexdigest()
(out.with_suffix('.zip.sha256')).write_text(f'{sha}  {out.name}\n')
