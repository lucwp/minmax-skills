#!/usr/bin/env python3
import json, sys
from pathlib import Path
REQUIRED={'id','prompt_class','required_checks','forbidden_checks','expected_behavior'}
MANDATORY={
'substantive_execution_visibility','anti_tool_call_spam','deduplicate_progress','worker_voice_ownership','strategic_preference_fork','retrieve_before_ask','in_boundary_decision_pause','boundary_changing_decision','chain_of_thought_protection','runtime_without_intermediate_output','simple_direct_task','recovery_visibility','long_execution_cadence','parallel_worker_aggregation','directional_vs_technical'}

def substantive(v,n=12): return isinstance(v,str) and len(v.strip())>=n and v.strip().lower() not in {'x','todo','tbd','n/a'}
def checks(v): return isinstance(v,list) and bool(v) and all(isinstance(x,str) and len(x.strip())>=4 for x in v)
def validate(data):
    e=[]
    if data.get('schema_version')!='1.0': e.append('schema_version must be 1.0')
    s=data.get('scoring',{}); dims=['progress_visibility','decision_rights','token_efficiency','root_ownership','runtime_honesty']
    if sum(s.get(k,0) for k in dims)!=100: e.append('scoring dimensions must sum to 100')
    if s.get('pass_score')!=100: e.append('pass_score must be 100 for strict interaction hardening')
    cases=data.get('cases')
    if not isinstance(cases,list) or not cases: return e+['cases must be a non-empty array']
    ids=set()
    for i,c in enumerate(cases):
        p=f'cases[{i}]'; miss=REQUIRED-set(c)
        if miss: e.append(f'{p} missing {sorted(miss)}')
        cid=c.get('id')
        if cid in ids: e.append(f'duplicate case id: {cid}')
        ids.add(cid)
        if not substantive(c.get('prompt_class')): e.append(f'{p}.prompt_class must be substantive')
        if not checks(c.get('required_checks')): e.append(f'{p}.required_checks must be substantive')
        f=c.get('forbidden_checks')
        if not isinstance(f,list) or any(not isinstance(x,str) or len(x.strip())<4 for x in f): e.append(f'{p}.forbidden_checks must be an array of substantive checks')
        if set(c.get('required_checks',[])) & set(f or []): e.append(f'{p} cannot require and forbid the same check')
        if not substantive(c.get('expected_behavior'),18): e.append(f'{p}.expected_behavior must be substantive')
    missing=MANDATORY-ids
    if missing: e.append(f'missing mandatory cases {sorted(missing)}')
    return e

def main():
    path=Path(sys.argv[1] if len(sys.argv)>1 else 'evals/interaction/cases.json')
    try: data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc: print(f'FAIL: {exc}'); return 1
    e=validate(data)
    for x in e: print(f'FAIL: {x}')
    print(f"RESULT: {'FAIL' if e else 'PASS'} ({len(e)} errors)")
    return 1 if e else 0
if __name__=='__main__': raise SystemExit(main())
