#!/usr/bin/env python3
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
cp_spec=importlib.util.spec_from_file_location('cpv',ROOT/'scripts'/'validate_loop_checkpoint.py')
cpv=importlib.util.module_from_spec(cp_spec); cp_spec.loader.exec_module(cpv)

contract={
    'schema_version':'1.4','contract_id':'contract-test-0001','contract_digest':'sha256:approved',
    'topology':'single_adaptive_loop','side_effect_class':'reversible_write',
    'approved_boundaries':{'scope':'frozen'},
    'approval':{'status':'approved','approval_reference':'user: pode executar','approved_contract_digest':'sha256:approved'},
    'budgets':{'max_iterations':4,'max_retries':1,'max_no_progress_cycles':2,'max_wall_minutes':30},
}
checkpoint={
    'schema_version':'1.0','run_id':'run-0001','contract_id':'contract-test-0001','contract_version':'1.4',
    'contract_digest':'sha256:approved','approval_reference':'user: pode executar','approved_contract_digest':'sha256:approved',
    'topology':'single_adaptive_loop','side_effect_class':'reversible_write','approved_boundaries':{'scope':'frozen'},
    'done':[],'active':['node-a'],'blocked':[],'invalidated':[],'evidence':[],'verification_status':'not_run',
    'remaining_budgets':{'iterations':4,'retries':1,'no_progress_cycles':2,'wall_minutes':30,'cost':None},
    'write_receipts':[],'next_ready':['node-a'],'status':'active',
}
assert not cpv.validate(checkpoint,contract=contract,approved_digest='sha256:approved'), cpv.validate(checkpoint,contract=contract,approved_digest='sha256:approved')

bad=dict(checkpoint); bad['contract_digest']='sha256:mutated'; bad['approved_contract_digest']='sha256:mutated'
assert cpv.validate(bad,contract=contract,approved_digest='sha256:approved')

bad_budget={**checkpoint,'remaining_budgets':dict(checkpoint['remaining_budgets'])}; bad_budget['remaining_budgets']['iterations']=99
assert any('exceeds approved' in x for x in cpv.validate(bad_budget,contract=contract,approved_digest='sha256:approved'))


# Autonomous external-write preauthorization must also survive resume from root-captured evidence.
ext_contract=dict(contract)
ext_contract['side_effect_class']='external_write'
ext_contract['execution_plan']=[{'name':'Send','action':'send approved message','purpose':'deliver approved message','output':'receipt','next':'verify receipt','effect':'external_write','requires_human_approval':False},{'name':'Verify','action':'read delivery receipt','purpose':'confirm postcondition','output':'authoritative receipt','next':'stop','effect':'read_only','requires_human_approval':False}]
ext_contract['approval']=dict(contract['approval']); ext_contract['approval']['external_write_preauthorization_ref']='preauth-123'
ext_cp=dict(checkpoint); ext_cp['side_effect_class']='external_write'; ext_cp['external_write_preauthorization_ref']='preauth-123'
errs=cpv.validate(ext_cp,contract=ext_contract,approved_digest='sha256:approved')
assert any('externally supplied external-write preauthorization' in x for x in errs), errs
assert not cpv.validate(ext_cp,contract=ext_contract,approved_digest='sha256:approved',external_write_preauthorization_ref='preauth-123'), cpv.validate(ext_cp,contract=ext_contract,approved_digest='sha256:approved',external_write_preauthorization_ref='preauth-123')
bad_ext=dict(ext_cp); bad_ext['external_write_preauthorization_ref']='fake'
assert cpv.validate(bad_ext,contract=ext_contract,approved_digest='sha256:approved',external_write_preauthorization_ref='preauth-123')

print('PASS: checkpoint identity, approval/preauthorization binding, and remaining-budget hardening')
