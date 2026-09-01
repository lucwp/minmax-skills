#!/usr/bin/env python3
import argparse, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v',ROOT/'scripts'/'validate_interaction_evals.py')
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)

def grade_case(case,obs):
    e=[]
    if not isinstance(obs,dict): return ['observation must be an object']
    seen=obs.get('observed_checks')
    if not isinstance(seen,list): return ['observed_checks must be an array']
    seen=set(seen)
    for req in case['required_checks']:
        if req not in seen: e.append(f'missing required check: {req}')
    for bad in case['forbidden_checks']:
        if bad in seen: e.append(f'forbidden behavior observed: {bad}')
    return e

def grade(spec_data,observations,allow_partial=False):
    out=[]
    for c in spec_data['cases']:
        cid=c['id']
        if cid not in observations:
            if not allow_partial: out.append((cid,['missing observation']))
            continue
        out.append((cid,grade_case(c,observations[cid])))
    return out

def score(results):
    if not results: return 0
    passed=sum(1 for _,e in results if not e)
    return round(100*passed/len(results))

def main():
    p=argparse.ArgumentParser(); p.add_argument('spec',type=Path); p.add_argument('observations',type=Path); p.add_argument('--allow-partial',action='store_true'); a=p.parse_args()
    s=json.loads(a.spec.read_text(encoding='utf-8')); o=json.loads(a.observations.read_text(encoding='utf-8'))
    verr=v.validate(s)
    if verr:
        for x in verr: print(f'FAIL: invalid spec: {x}')
        return 1
    r=grade(s,o,a.allow_partial)
    for cid,e in r:
        for x in e: print(f'FAIL {cid}: {x}')
    sc=score(r); print(f'SCORE: {sc}/100')
    return 0 if sc==s['scoring']['pass_score'] and all(not e for _,e in r) else 1
if __name__=='__main__': raise SystemExit(main())
