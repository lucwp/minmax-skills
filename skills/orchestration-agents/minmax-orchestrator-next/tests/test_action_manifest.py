#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/'scripts'/'validate_action_manifest.py'
spec=importlib.util.spec_from_file_location('validator',SCRIPT);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def ok(d):e,_=v.validate(d);assert not e,e
def bad(d,n):e,_=v.validate(d);assert any(n in x for x in e),e
def base(c='reversible_write',a='autonomous'):
 return {'schema_version':'1.0','run_id':'r1','objective':'update safely','autonomy_mode':a,'action_class':c,'targets':['x'],'write_set':['x'],'idempotency_key':'k','expected_postconditions':['ok'],'verification':{'method':'authoritative_read','source':'api'},'compensation':{'strategy':'rollback','details':'restore'},'limits':{'max_writes':1,'max_records':1,'max_external_targets':0,'max_cost':0},'preauthorization_ref':'p','untrusted_inputs':[],'audit_log':'log','concurrency_keys':['x']}
ok({'schema_version':'1.0','run_id':'r','objective':'read','autonomy_mode':'autonomous','action_class':'read_only','targets':['x']})
ok(base())
x=base('external_write');x['limits']['max_external_targets']=1;x['compensation']={'strategy':'not_possible','irreversibility_acknowledged':True};ok(x)
bad(base('irreversible_high_consequence'),'cannot run autonomously')
print('PASS: action-manifest regression tests')
