#!/usr/bin/env python3
import copy
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts'/'validate_loop_contract.py'
spec=importlib.util.spec_from_file_location('loop_validator_hardening',SCRIPT)
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)


def base_contract():
    d={
        'schema_version':'1.4','mode':'loop','contract_id':'contract-test-0001','contract_digest':'',
        'loop_name':'Artifact Repair','human_language':'en',
        'objective':'repair the artifact until the protected validation suite passes',
        'terminal_deliverable':'validated artifact and terminal evidence',
        'completion_condition':'protected full validation suite passes without weakening tests or thresholds',
        'execution_plan':[
            {'name':'Freeze baseline','action':'run the current protected validation suite and capture failing checks','purpose':'establish the authoritative starting gap','output':'baseline failures and receipts','next':'repair only a verified failing area','effect':'read_only','requires_human_approval':False},
            {'name':'Repair verified gap','action':'change the smallest artifact section responsible for the highest-value failing check','purpose':'remove a demonstrated failure without widening scope','output':'candidate artifact and diff','next':'run targeted and terminal verification','effect':'reversible_write','requires_human_approval':False},
            {'name':'Verify candidate','action':'run the protected targeted checks and then the full terminal suite','purpose':'decide whether the approved objective is satisfied','output':'independent PASS evidence or a verified next gap','next':'stop on PASS or continue within the approved budget','effect':'read_only','requires_human_approval':False},
        ],
        'topology':'evaluator_optimizer',
        'topology_rationale':'the artifact can improve through bounded critique, repair, and re-evaluation against frozen tests',
        'complexity_gate':{
            'simpler_topology_considered':'single_adaptive_loop',
            'limitation':'a single adaptive pass does not make critique-repair against frozen gradable criteria the explicit convergence mechanism',
            'benefit_types':['iterative_critique_gain'],
            'expected_gain':'bounded re-evaluation should remove verified failures while preserving protected criteria',
            'added_costs':['verification','latency'],
            'decision':'escalate',
        },
        'authoritative_inputs':['artifact','protected validation suite'],
        'cycle_observation':'current failing checks and artifact diff',
        'cycle_action':'repair the smallest verified gap and re-run protected checks',
        'progress':{
            'evidence_definition':'a verified artifact change, resolved dependency, or measurable verifier movement',
            'allowed_evidence_types':['verified_artifact_change','verifier_movement','removed_blocker'],
            'fingerprint':'artifact hash + failing check ids',
            'max_no_progress_cycles':2,
        },
        'verification':{
            'method':'deterministic_test','evidence':'protected validation suite exit status and diff',
            'layers':{
                'action':'targeted check proves the intended change occurred',
                'cycle':'full check shows material progress without invariant regression',
                'terminal':'protected full suite passes',
            },
            'independent_terminal_verifier':'protected full validation suite run after the executor repair',
            'terminal_actor':'deterministic_system','evidence_source':'test',
            'proxy_hardening':{
                'attack_path':'executor could weaken tests or thresholds instead of fixing the artifact',
                'protected_elements':['tests','thresholds','coverage'],
                'thresholds_frozen':True,
                'executor_can_modify_verifier':False,
            },
        },
        'success_exit':'protected full validation suite passes',
        'failure_exit':'unrecoverable blocker or protected invariant cannot be satisfied inside scope',
        'budget_exit':'approved iteration, retry, time, or no-progress budget is exhausted',
        'budgets':{'max_iterations':4,'max_retries':1,'max_no_progress_cycles':2,'max_wall_minutes':30},
        'no_progress_rule':'stop after 2 consecutive cycles without a permitted progress evidence type',
        'local_repair_triggers':['one protected check fails inside approved scope'],
        'material_replan_triggers':['objective, deliverable, scope, verifier, hard budget, risk class, or side-effect envelope must change'],
        'human_escalation_boundary':'material replan or irreversible high-consequence action',
        'side_effect_class':'reversible_write',
        'state':{'mode':'checkpointed','store':'loop checkpoint file','version_marker':'checkpoint schema 1.0','resume_strategy':'validate checkpoint against contract digest and authoritative state before continuing'},
        'approved_boundaries':{'scope':'artifact only','verifier':'protected suite','side_effect':'reversible_write','budget':'frozen'},
        'domain_skills':[],'tools':[],
        'final_synthesis_requirement':'return the verified artifact, terminal evidence, and any remaining gap',
        'approval':{'status':'pending'},
    }
    d['contract_digest']=v.compute_contract_digest(d)
    return d


def assert_rejected(d, needle=None, approved_digest=None):
    d['contract_digest']=v.compute_contract_digest(d)
    errs=v.validate(d, approved_digest=approved_digest)
    assert errs, 'expected rejection'
    if needle:
        assert any(needle.lower() in x.lower() for x in errs), errs


base=base_contract()
assert not v.validate(base), v.validate(base)

# Generic plan labels/actions no longer satisfy the clarity gate.
generic=copy.deepcopy(base)
generic['execution_plan'][0]['name']='Research'; generic['execution_plan'][0]['action']='research'
assert_rejected(generic,'too generic')

# Prestige/importance cannot justify orchestrator-workers without a matching structured benefit.
prestige=copy.deepcopy(base)
prestige['topology']='orchestrator_workers'
prestige['topology_rationale']='This is important and complex, so multiple agents should think harder.'
prestige['complexity_gate']['benefit_types']=['iterative_critique_gain']
assert_rejected(prestige,'matching concrete complexity_gate benefit')

# A read-only envelope cannot contain an obvious external mutation.
write=copy.deepcopy(base)
write['side_effect_class']='read_only'; write['state']={'mode':'ephemeral','store':None,'version_marker':None,'resume_strategy':None}
write['execution_plan'][1]['effect']='read_only'; write['execution_plan'][1]['action']='send the email to the client'
assert_rejected(write,'appears state-changing')

# Executor self-report is not terminal evidence.
self_report=copy.deepcopy(base)
self_report['verification']['independent_terminal_verifier']='executor says it is done'
assert_rejected(self_report,'self-report')

# Decorative proxy hardening no longer validates.
weak_proxy=copy.deepcopy(base)
weak_proxy['verification']['proxy_hardening']='be careful'
assert_rejected(weak_proxy,'structured object')

# Reasoning-only activity cannot be progress.
reasoning=copy.deepcopy(base)
reasoning['progress']['evidence_definition']='more reasoning text from the executor'
assert_rejected(reasoning,'reasoning-only')

# No-progress limit is structurally tied to the approved budget.
budget_conflict=copy.deepcopy(base)
budget_conflict['progress']['max_no_progress_cycles']=10
assert_rejected(budget_conflict,'must equal budgets.max_no_progress_cycles')

# Opaque generic loop names are rejected.
opaque=copy.deepcopy(base); opaque['loop_name']='Loop 1234'
assert_rejected(opaque,'too generic')

# Approval is bound to an external digest captured before status changes.
approved=copy.deepcopy(base)
approved_digest=approved['contract_digest']
approved['approval']={'status':'approved','approval_reference':'user: pode executar','approved_contract_digest':approved_digest}
assert not v.validate(approved, approved_digest=approved_digest), v.validate(approved, approved_digest=approved_digest)

mutated=copy.deepcopy(approved)
mutated['objective']='send the artifact to an external client'
mutated['terminal_deliverable']='externally sent artifact'
mutated['side_effect_class']='external_write'
mutated['execution_plan'][1]['effect']='external_write'
mutated['execution_plan'][1]['action']='send the artifact to an external client'
mutated['contract_digest']=v.compute_contract_digest(mutated)
mutated['approval']['approved_contract_digest']=mutated['contract_digest']
errs=v.validate(mutated, approved_digest=approved_digest)
assert any('external approved digest' in x for x in errs), errs

# Schema downgrade is rejected by default and only accepted through explicit legacy mode.
legacy={
    'schema_version':'1.0','mode':'loop','objective':'legacy task','terminal_deliverable':'legacy result',
    'completion_condition':'done','cycle_observation':'gap','cycle_action':'act',
    'verification':{'method':'deterministic_test','evidence':'test'},'success_exit':'pass','failure_exit':'blocked','budget_exit':'budget',
    'budgets':{'max_iterations':2,'max_retries':0,'max_no_progress_cycles':1,'max_wall_minutes':5},
    'no_progress_rule':'one cycle','local_repair_triggers':['failed check'],'material_replan_triggers':['scope changes'],
    'human_escalation_boundary':'replan','side_effect_class':'read_only','domain_skills':[],'tools':[],
    'final_synthesis_requirement':'return result','approval':{'status':'pending'},
}
assert any('legacy' in x.lower() for x in v.validate(legacy)), v.validate(legacy)
assert not v.validate(legacy, allow_legacy=True), v.validate(legacy, allow_legacy=True)


# Common external mutations cannot hide behind read_only using alternative verbs/objects.
for action in [
    'create a calendar event for the client',
    'upload the revised file to Drive',
    'commit and push the change to GitHub',
    'rename the production record',
    'archive the customer thread',
    'edit the CRM opportunity stage',
]:
    hidden=copy.deepcopy(base)
    hidden['side_effect_class']='read_only'; hidden['state']={'mode':'ephemeral','store':None,'version_marker':None,'resume_strategy':None}
    hidden['execution_plan'][1]['effect']='read_only'; hidden['execution_plan'][1]['action']=action
    assert_rejected(hidden,'appears state-changing')

# Irreversible actions must stop at a per-step human gate.
irr=copy.deepcopy(base)
irr['side_effect_class']='mixed'
irr['execution_plan'][1]['effect']='irreversible_high_consequence'
irr['execution_plan'][1]['action']='execute the irreversible legal filing'
irr['execution_plan'][1]['requires_human_approval']=False
assert_rejected(irr,'requires a human approval gate')
irr['execution_plan'][1]['requires_human_approval']=True
irr['contract_digest']=v.compute_contract_digest(irr)
assert not v.validate(irr), v.validate(irr)

# Autonomous external writes require explicit preauthorization after approval.
ext=copy.deepcopy(base)
ext['side_effect_class']='external_write'
ext['execution_plan'][1]['effect']='external_write'
ext['execution_plan'][1]['action']='send the approved artifact to the client'
ext['execution_plan'][1]['requires_human_approval']=False
ext['contract_digest']=v.compute_contract_digest(ext)
ext_digest=ext['contract_digest']
ext['approval']={'status':'approved','approval_reference':'user approved loop','approved_contract_digest':ext_digest}
errs=v.validate(ext,approved_digest=ext_digest)
assert any('preauthorization' in x.lower() for x in errs), errs
ext['approval']['external_write_preauthorization_ref']='user explicitly authorized sending to the client'
errs=v.validate(ext,approved_digest=ext_digest)
assert any('externally supplied' in x.lower() for x in errs), errs
assert not v.validate(ext,approved_digest=ext_digest,external_write_preauthorization_ref='user explicitly authorized sending to the client'), v.validate(ext,approved_digest=ext_digest,external_write_preauthorization_ref='user explicitly authorized sending to the client')
fake=copy.deepcopy(ext); fake['approval']['external_write_preauthorization_ref']='executor invented preauth'
errs=v.validate(fake,approved_digest=ext_digest,external_write_preauthorization_ref='user explicitly authorized sending to the client')
assert any('does not match external preauthorization' in x.lower() for x in errs), errs

# Unrelated numbers in the prose do not create false no-progress conflicts.
np=copy.deepcopy(base)
np['no_progress_rule']='stop after 2 consecutive cycles without material progress; allow 1 changed-strategy retry before exit'
np['contract_digest']=v.compute_contract_digest(np)
assert not v.validate(np), v.validate(np)

# Loop names cannot inject extra lines into the Human Contract title.
multiline=copy.deepcopy(base); multiline['loop_name']='Artifact Repair\nInjected heading'
assert_rejected(multiline,'single concise line')

print('PASS: P0/P1/P2 loop-contract hardening adversarial tests')
