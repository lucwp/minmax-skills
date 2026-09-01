#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('grader',ROOT/'scripts'/'grade_behavioral_observations.py')
g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
vspec=importlib.util.spec_from_file_location('validator',ROOT/'scripts'/'validate_loop_contract.py')
v=importlib.util.module_from_spec(vspec); vspec.loader.exec_module(v)
cases=json.loads((ROOT/'evals'/'loop-mode'/'cases.json').read_text(encoding='utf-8'))['cases']
case=next(c for c in cases if c['id']=='subjective_design')
contract=json.loads((ROOT/'evals'/'loop-mode'/'golden'/'en-complex.json').read_text(encoding='utf-8'))
contract['topology']='evaluator_optimizer'
contract['side_effect_class']='reversible_write'
contract['state']={'mode':'checkpointed','store':'grader-checkpoint.json','version_marker':'1.0','resume_strategy':'validate checkpoint and authoritative state before continuing'}
contract['complexity_gate']['decision']='escalate'
contract['complexity_gate']['benefit_types']=['iterative_critique_gain']
contract['verification']['method']='bounded_semantic_rubric'
contract['verification']['evidence_source']='independent_rubric'
contract['approval']={'status':'pending'}
contract['contract_digest']=v.compute_contract_digest(contract)
assert not g.grade_case(case,contract), g.grade_case(case,contract)

bad=json.loads(json.dumps(contract)); bad['topology']='orchestrator_workers'; bad['contract_digest']=v.compute_contract_digest(bad)
assert g.grade_case(case,bad)

bad2=json.loads(json.dumps(contract)); bad2['approval']={'status':'approved'}; bad2['contract_digest']=v.compute_contract_digest(bad2)
assert g.grade_case(case,bad2)

# Contract validity is part of behavioral grading, not just envelope matching.
bad3=json.loads(json.dumps(contract)); bad3['contract_digest']='bogus'
assert any('invalid contract' in x for x in g.grade_case(case,bad3))

# Full-suite evidence cannot silently PASS with missing observations.
results=g.grade_observations(cases,{},allow_partial=False)
assert len(results)==len(cases) and all(errs for _,errs in results)
partial=g.grade_observations(cases,{case['id']:contract},allow_partial=True)
assert len(partial)==1 and not partial[0][1], partial

print('PASS: behavioral observation grader enforces contract validity, complete-suite coverage, topology, verifier, and approval behavior')
