#!/usr/bin/env python3
import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('g',ROOT/'scripts'/'grade_interaction_observations.py'); g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
data=json.loads((ROOT/'evals'/'interaction'/'cases.json').read_text(encoding='utf-8'))
perfect={c['id']:{'observed_checks':list(c['required_checks'])} for c in data['cases']}
r=g.grade(data,perfect); assert g.score(r)==100 and all(not e for _,e in r), r
bad=json.loads(json.dumps(perfect)); c=data['cases'][0]; bad[c['id']]['observed_checks'].remove(c['required_checks'][0]); bad[c['id']]['observed_checks'].append(c['forbidden_checks'][0])
r=g.grade(data,bad); assert g.score(r)<100 and r[0][1]
missing=dict(perfect); missing.pop(data['cases'][-1]['id']); r=g.grade(data,missing,allow_partial=False); assert any(e for _,e in r)
print('PASS: interaction observation grader reaches 100/100 only with complete required behavior and no forbidden behavior')
