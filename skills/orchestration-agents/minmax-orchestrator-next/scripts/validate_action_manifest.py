#!/usr/bin/env python3
import json, math, sys
from pathlib import Path
ACTION_CLASSES={"read_only","reversible_write","external_write","irreversible_high_consequence"}
AUTONOMY_MODES={"supervised","autonomous"}
VERIFY_METHODS={"authoritative_read","deterministic_test","transaction_receipt"}
COMPENSATION={"rollback","inverse_action","follow_up","not_possible"}
def present(v):
    if v is None:return False
    if isinstance(v,str):return bool(v.strip())
    if isinstance(v,(list,dict)):return bool(v)
    return True
def finite_nonnegative(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>=0
def positive_int(v):return isinstance(v,int) and not isinstance(v,bool) and v>0
def validate(d):
    e=[];w=[]
    if d.get("schema_version")!="1.0":e.append("schema_version must be '1.0'")
    for k in ("run_id","objective"):
        if not present(d.get(k)):e.append(f"{k} is required")
    a=d.get("autonomy_mode");c=d.get("action_class")
    if a not in AUTONOMY_MODES:e.append(f"autonomy_mode must be one of {sorted(AUTONOMY_MODES)}")
    if c not in ACTION_CLASSES:e.append(f"action_class must be one of {sorted(ACTION_CLASSES)}")
    t=d.get("targets")
    if not isinstance(t,list) or not t:e.append("targets must be a non-empty array")
    if c=="irreversible_high_consequence" and a=="autonomous":e.append("irreversible_high_consequence actions cannot run autonomously")
    if c not in {"reversible_write","external_write","irreversible_high_consequence"}:return e,w
    for k in ("idempotency_key","audit_log"):
        if not present(d.get(k)):e.append(f"{k} is required for state-changing actions")
    for k in ("write_set","concurrency_keys","expected_postconditions"):
        v=d.get(k)
        if not isinstance(v,list) or not v:e.append(f"{k} must be a non-empty array for state-changing actions")
    v=d.get("verification")
    if not isinstance(v,dict):e.append("verification must be an object for state-changing actions")
    else:
        if v.get("method") not in VERIFY_METHODS:e.append(f"verification.method must be one of {sorted(VERIFY_METHODS)}")
        if not present(v.get("source")):e.append("verification.source is required")
    lim=d.get("limits")
    if not isinstance(lim,dict):e.append("limits must be an object for state-changing actions")
    else:
        if not positive_int(lim.get("max_writes")):e.append("limits.max_writes must be a positive integer")
        if not positive_int(lim.get("max_records")):e.append("limits.max_records must be a positive integer")
        ext=lim.get("max_external_targets",0);cost=lim.get("max_cost",0)
        if not isinstance(ext,int) or isinstance(ext,bool) or ext<0:e.append("limits.max_external_targets must be a non-negative integer")
        if not finite_nonnegative(cost):e.append("limits.max_cost must be a finite non-negative number")
        if c=="external_write" and a=="autonomous" and ext<=0:e.append("autonomous external_write requires limits.max_external_targets > 0")
    comp=d.get("compensation")
    if not isinstance(comp,dict):e.append("compensation must be an object for state-changing actions")
    else:
        s=comp.get("strategy")
        if s not in COMPENSATION:e.append(f"compensation.strategy must be one of {sorted(COMPENSATION)}")
        if s=="not_possible" and not bool(comp.get("irreversibility_acknowledged")):e.append("compensation.irreversibility_acknowledged=true is required when strategy=not_possible")
        if s!="not_possible" and not present(comp.get("details")):e.append("compensation.details is required")
    if a=="autonomous" and c=="external_write" and not present(d.get("preauthorization_ref")):e.append("autonomous external_write requires preauthorization_ref")
    if not isinstance(d.get("untrusted_inputs",[]),list):e.append("untrusted_inputs must be an array")
    return e,w
def main():
    if len(sys.argv)!=2:print("Usage: validate_action_manifest.py <action-manifest.json>",file=sys.stderr);return 2
    try:d=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except Exception as x:print(f"FAIL: invalid JSON: {x}");return 1
    e,w=validate(d)
    for x in w:print(f"WARN: {x}")
    for x in e:print(f"FAIL: {x}")
    print(f"RESULT: {'FAIL' if e else 'PASS'} ({len(e)} errors, {len(w)} warnings)")
    return 1 if e else 0
if __name__=="__main__":raise SystemExit(main())
