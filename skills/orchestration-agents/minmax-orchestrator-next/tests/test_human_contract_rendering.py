#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GOLDEN=ROOT/'evals'/'loop-mode'/'golden'
spec=importlib.util.spec_from_file_location('renderer',ROOT/'scripts'/'render_loop_contract.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)

pairs=sorted(GOLDEN.glob('*.json'))
assert len(pairs)==6, pairs
for path in pairs:
    d=json.loads(path.read_text(encoding='utf-8'))
    actual=r.render(d)
    expected=path.with_suffix('.md').read_text(encoding='utf-8')
    assert actual==expected, path.name
    first=actual.splitlines()[0]
    if d['human_language']=='pt-BR':
        assert first.startswith('# Contrato de Loop - '), first
        assert not first.startswith('## '), first
        for label in ['Resumo para aprovação','Escopo e evidências','Plano de execução','Verificação e convergência','Limites e saídas','Não pode','Aprovação']:
            assert label in actual, (path.name,label)
        assert 'Approval snapshot' not in actual
        assert 'Boundaries and exits' not in actual
    else:
        assert first.startswith('# Loop Contract - '), first
        assert not first.startswith('## '), first
        for label in ['Approval snapshot','Scope and evidence','Execution plan','Verification and convergence','Boundaries and exits','Cannot','Approval']:
            assert label in actual, (path.name,label)
    for step in d['execution_plan']:
        assert step['action'] in actual and step['purpose'] in actual and step['output'] in actual and step['next'] in actual

# Unsupported languages must not silently fall back to English labels.
other=json.loads(pairs[0].read_text(encoding='utf-8')); other['human_language']='other'
try:
    r.render(other)
    raise AssertionError('expected unsupported-language failure')
except ValueError as exc:
    assert 'no label map' in str(exc)

print('PASS: six golden Human Contracts preserve localized H1 title/logic and unsupported languages do not silently fall back to English')
