#!/usr/bin/env python3
import json
import math
import sys
from pathlib import Path

ACTION_CLASSES = {"read_only", "reversible_write", "external_write", "irreversible_high_consequence"}
AUTONOMY_MODES = {"supervised", "autonomous"}
VERIFY_METHODS = {"authoritative_read", "deterministic_test", "transaction_receipt"}
COMPENSATION = {"rollback", "inverse_action", "follow_up", "not_possible"}

def present(value):
    if value is None: return False
    if isinstance(value, str): return bool(value.strip())
    if isinstance(value, (list, dict)): return bool(value)
    return True

def finite_nonnegative(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0

def positive_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0

def validate(data):
    errors=[]; warnings=[]
    if data.get("schema_version") != "1.0": errors.append("schema_version must be '1.0'")
    for key in ("run_id", "objective"):
        if not present(data.get(key)): errors.append(f"{key} is required")
    autonomy=data.get("autonomy_mode"); action_class=data.get("action_class")
    if autonomy not in AUTONOMY_MODES: errors.append(f"autonomy_mode must be one of {sorted(AUTONOMY_MODES)}")
    if action_class not in ACTION_CLASSES: errors.append(f"action_class must be one of {sorted(ACTION_CLASSES)}")
    targets=data.get("targets")
    if not isinstance(targets,list) or not targets: errors.append("targets must be a non-empty array")
    if action_class == "irreversible_high_consequence" and autonomy == "autonomous": errors.append("irreversible_high_consequence actions cannot run autonomously")
    is_write=action_class in {"reversible_write","external_write","irreversible_high_consequence"}
    if not is_write: return errors,warnings
    for key in ("idempotency_key","audit_log"):
        if not present(data.get(key)): errors.append(f"{key} is required for state-changing actions")
    write_set=data.get("write_set")
    if not isinstance(write_set,list) or not write_set: errors.append("write_set must be a non-empty array for state-changing actions")
    concurrency_keys=data.get("concurrency_keys")
    if not isinstance(concurrency_keys,list) or not concurrency_keys: errors.append("concurrency_keys must be a non-empty array for state-changing actions")
    expected=data.get("expected_postconditions")
    if not isinstance(expected,list) or not expected: errors.append("expected_postconditions must be a non-empty array for state-changing actions")
    verification=data.get("verification")
    if not isinstance(verification,dict): errors.append("verification must be an object for state-changing actions")
    else:
        if verification.get("method") not in VERIFY_METHODS: errors.append(f"verification.method must be one of {sorted(VERIFY_METHODS)}")
        if not present(verification.get("source")): errors.append("verification.source is required")
    limits=data.get("limits")
    if not isinstance(limits,dict): errors.append("limits must be an object for state-changing actions")
    else:
        if not positive_int(limits.get("max_writes")): errors.append("limits.max_writes must be a positive integer")
        if not positive_int(limits.get("max_records")): errors.append("limits.max_records must be a positive integer")
        ext=limits.get("max_external_targets",0)
        if not isinstance(ext,int) or isinstance(ext,bool) or ext < 0: errors.append("limits.max_external_targets must be a non-negative integer")
        cost=limits.get("max_cost",0)
        if not finite_nonnegative(cost): errors.append("limits.max_cost must be a finite non-negative number")
        if action_class == "external_write" and autonomy == "autonomous" and ext <= 0: errors.append("autonomous external_write requires limits.max_external_targets > 0")
    compensation=data.get("compensation")
    if not isinstance(compensation,dict): errors.append("compensation must be an object for state-changing actions")
    else:
        strategy=compensation.get("strategy")
        if strategy not in COMPENSATION: errors.append(f"compensation.strategy must be one of {sorted(COMPENSATION)}")
        if strategy == "not_possible" and not bool(compensation.get("irreversibility_acknowledged")): errors.append("compensation.irreversibility_acknowledged=true is required when strategy=not_possible")
        if strategy != "not_possible" and not present(compensation.get("details")): errors.append("compensation.details is required")
    if autonomy == "autonomous" and action_class == "external_write" and not present(data.get("preauthorization_ref")): errors.append("autonomous external_write requires preauthorization_ref")
    if not isinstance(data.get("untrusted_inputs",[]),list): errors.append("untrusted_inputs must be an array")
    return errors,warnings

def main():
    if len(sys.argv)!=2:
        print("Usage: validate_action_manifest.py <action-manifest.json>",file=sys.stderr); return 2
    path=Path(sys.argv[1])
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: print(f"FAIL: invalid JSON: {exc}"); return 1
    errors,warnings=validate(data)
    for warning in warnings: print(f"WARN: {warning}")
    if errors:
        for error in errors: print(f"FAIL: {error}")
        print(f"RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)"); return 1
    print(f"RESULT: PASS ({len(warnings)} warnings)"); return 0
if __name__ == "__main__": raise SystemExit(main())
