#!/usr/bin/env python3
import copy
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bv',ROOT/'scripts'/'validate_behavioral_evals.py')
bv=importlib.util.module_from_spec(spec); spec.loader.exec_module(bv)
data=json.loads((ROOT/'evals'/'loop-mode'/'cases.json').read_text(encoding='utf-8'))
assert not bv.validate(data), bv.validate(data)
mut=copy.deepcopy(data)
for c in mut['cases']:
    c['prompt_class']='x'; c['required_verifier_properties']=['x']; c['approval_requirements']=['x']; c['expected_terminal_behavior']='x'; c['state_requirement']='x'
errs=bv.validate(mut)
assert errs, 'semantic descriptions collapsed to x should fail spec validation'
assert any('substantive' in x for x in errs), errs
print('PASS: behavioral spec validator rejects placeholder semantics')
