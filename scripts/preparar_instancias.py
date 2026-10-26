#!/usr/bin/env python3
"""Prepara os downloads atuais sem alterar originais nem inventar dados ausentes."""
import csv, hashlib, json, re
from pathlib import Path
from validar import read_instance
ROOT = Path(__file__).resolve().parents[1]

def main():
    source = ROOT / 'instances'
    out = source / 'preparadas'
    out.mkdir(exist_ok=True)
    seen, rows = {}, []
    for path in sorted(source.glob('*.txt')):
        original = path.read_bytes()
        text = original.decode('utf-8-sig')
        # Only split the two explicitly labeled headers; never modify data values.
        text, changes = re.subn(r'(NUM_CANDIDATOS:\s*\d+)[ \t]+(NUM_ESCOLAS:)', r'\1\n\2', text)
        row = {'arquivo': path.name, 'sha256_original': hashlib.sha256(original).hexdigest(),
               'ajuste': 'separacao de cabecalhos' if changes else 'nenhum'}
        if not text.lstrip().startswith('NUM_CANDIDATOS:'):
            row.update(status='excluido', motivo='arquivo contem somente caminho externo, sem dados')
        else:
            # Validate a temporary normalized copy before publishing it as input.
            temp = out / (path.name + '.tmp')
            temp.write_text(text, encoding='utf-8')
            try:
                cs, ss, caps, ds = read_instance(temp)
                # Semantic digest also recognizes differently formatted duplicates.
                normalized = json.dumps([cs, ss, [[str(x) for x in r] for r in ds]], separators=(',', ':'))
                digest = hashlib.sha256(normalized.encode()).hexdigest()
                row.update(n=len(cs), m=len(ss), capacidade=sum(caps), sha256_dados=digest)
                if digest in seen:
                    row.update(status='duplicado', motivo=seen[digest])
                else:
                    target=out/path.name
                    target.write_text(text, encoding='utf-8')
                    seen[digest]=path.name
                    row.update(status='pronto', motivo='')
            except Exception as exc:
                row.update(status='excluido', motivo=f'{type(exc).__name__}: {exc}')
            finally:
                temp.unlink()
        rows.append(row)
    keys=['arquivo','status','motivo','ajuste','n','m','capacidade','sha256_original','sha256_dados']
    with (source/'auditoria_atual.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
    counts={k:sum(r['status']==k for r in rows) for k in ('pronto','duplicado','excluido')}
    (source/'auditoria_atual.json').write_text(json.dumps({'counts':counts,'files':rows},indent=2,ensure_ascii=False))
    print(counts)
    for r in rows:
        if r['status']!='pronto' or r['ajuste']!='nenhum':print(r['arquivo'],r['status'],r['ajuste'],r['motivo'])

if __name__=='__main__':main()
