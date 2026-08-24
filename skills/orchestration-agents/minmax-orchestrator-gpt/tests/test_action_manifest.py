#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"validate_action_manifest.py"
spec=importlib.util.spec_from_file_location("validator",SCRIPT); validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
def assert_pass(data):
    errors,_=validator.validate(data); assert not errors,errors
def assert_fail(data,needle):
    errors,_=validator.validate(data); assert errors,"expected failure"; assert any(needle in e for e in errors),errors
def base(action_class="reversible_write",autonomy="autonomous"):
    return {"schema_version":"1.0","run_id":"run-123","objective":"Update one CRM record safely","autonomy_mode":autonomy,"action_class":action_class,"targets":["crm:account:123"],"write_set":["crm:account:123"],"idempotency_key":"crm-account-123-status-v2","expected_postconditions":["crm:account:123.status == active"],"verification":{"method":"authoritative_read","source":"CRM account read endpoint"},"compensation":{"strategy":"rollback","details":"Restore previous status"},"limits":{"max_writes":1,"max_records":1,"max_external_targets":0,"max_cost":0},"preauthorization_ref":"ops-policy-17","untrusted_inputs":["customer supplied notes"],"audit_log":"logs/run-123.jsonl","concurrency_keys":["crm:account:123"]}
assert_pass({"schema_version":"1.0","run_id":"read-1","objective":"Read current pipeline state","autonomy_mode":"autonomous","action_class":"read_only","targets":["crm:pipeline"]})
assert_pass(base())
external=base("external_write"); external["limits"]["max_external_targets"]=1; external["compensation"]={"strategy":"not_possible","irreversibility_acknowledged":True}; assert_pass(external)
assert_fail(base("irreversible_high_consequence"),"cannot run autonomously")
bad=base("external_write"); bad["limits"]["max_external_targets"]=1; bad["compensation"]={"strategy":"not_possible","irreversibility_acknowledged":True}; bad["preauthorization_ref"]=""; assert_fail(bad,"preauthorization_ref")
bad=base(); bad["idempotency_key"]=""; assert_fail(bad,"idempotency_key")
bad=base(); bad["verification"]={"method":"model_judgment","source":"worker opinion"}; assert_fail(bad,"verification.method")
print("PASS: action-manifest regression tests")
