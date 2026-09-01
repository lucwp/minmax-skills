#!/usr/bin/env python3
import copy, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v',ROOT/'scripts'/'validate_interaction_evals.py'); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
data=json.loads((ROOT/'evals'/'interaction'/'cases.json').read_text(encoding='utf-8'))
assert not v.validate(data), v.validate(data)
assert data['scoring']['pass_score']==100
mut=copy.deepcopy(data); mut['cases'][0]['required_checks']=[]
assert v.validate(mut)
mut=copy.deepcopy(data); mut['cases'][1]['forbidden_checks']=[mut['cases'][1]['required_checks'][0]]
assert any('require and forbid' in x for x in v.validate(mut))
mut=copy.deepcopy(data); mut['cases']=mut['cases'][:-1]
assert any('missing mandatory cases' in x for x in v.validate(mut))
print('PASS: interaction eval specification is complete, substantive, contradiction-safe, and strict at 100/100')
