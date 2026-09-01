#!/usr/bin/env python3
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
loop=(ROOT/'references'/'loop-mode.md').read_text(encoding='utf-8')

required_skill=[
    'Loop Mode is opt-in only','Loop approval is mandatory','do not dispatch workers before user approval',
    'material replan invalidates prior loop approval','minimum sufficient execution topology',
    'layered action, cycle, and terminal verification','latest contract schema','external approved digest',
    '# Contrato de Loop - <o que é>','# Loop Contract - <what it is>',
]
for needle in required_skill:
    assert needle.lower() in text.lower(), needle

required_loop=[
    'TASK LEDGER -> TOPOLOGY GATE -> PLAN AT RIGHT ALTITUDE',
    'The original instruction to "use a loop" is **not** approval',
    'Do not execute the substantive task or any loop cycle in the same turn',
    'MATERIAL REPLAN = NEW APPROVAL','Loop Mode does not imply multi-agent execution','activity != progress',
    'How could the executor make this verifier pass without satisfying the actual objective?',
    'New contracts **must use schema `1.4`**','--approved-digest','scripts/validate_loop_checkpoint.py',
]
for needle in required_loop:
    assert needle.lower() in loop.lower(), needle

SCRIPT=ROOT/'scripts'/'validate_loop_contract.py'
spec=importlib.util.spec_from_file_location('loop_validator',SCRIPT)
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)

legacy={
    'schema_version':'1.0','mode':'loop','objective':'build artifact','terminal_deliverable':'artifact',
    'completion_condition':'validator passes','cycle_observation':'current validation gaps','cycle_action':'repair next gap',
    'verification':{'method':'deterministic_test','evidence':'validator exit 0'},
    'success_exit':'all checks pass','failure_exit':'unrecoverable blocker','budget_exit':'budget reached',
    'budgets':{'max_iterations':6,'max_retries':1,'max_no_progress_cycles':2,'max_wall_minutes':30},
    'no_progress_rule':'two cycles without state change','local_repair_triggers':['single failed check'],
    'material_replan_triggers':['scope changes'],'human_escalation_boundary':'material replan or high consequence action',
    'side_effect_class':'read_only','domain_skills':[],'tools':[],'final_synthesis_requirement':'return verified artifact',
    'approval':{'status':'pending'}
}
assert v.validate(legacy), 'legacy contract must not validate through the new-contract path'
assert not v.validate(legacy,allow_legacy=True), v.validate(legacy,allow_legacy=True)

bad=dict(legacy); bad['budgets']=dict(legacy['budgets']); bad['budgets']['max_iterations']=0
assert any('max_iterations' in x for x in v.validate(bad,allow_legacy=True))

print('PASS: latest-schema default, explicit legacy resume, approval lifecycle, and Loop Mode invariants')
