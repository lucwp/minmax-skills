#!/usr/bin/env python3
import json, math, sys
from pathlib import Path
VERIFY={"deterministic_test","authoritative_read","transaction_receipt","render_qa","schema_validation","bounded_semantic_rubric","mixed"}
SIDE={"read_only","reversible_write","external_write","irreversible_high_consequence","mixed"}
APPROVAL={"pending","approved"}
def present(v):
    if v is None:return False
    if isinstance(v,str):return bool(v.strip())
    if isinstance(v,(list,dict)):return bool(v)
    return True
def posint(v):return isinstance(v,int) and not isinstance(v,bool) and v>0
def nonnegint(v):return isinstance(v,int) and not isinstance(v,bool) and v>=0
def positive_num(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>0
def validate(d):
    e=[]
    if d.get("schema_version")!="1.0":e.append("schema_version must be '1.0'")
    if d.get("mode")!="loop":e.append("mode must be 'loop'")
    for k in ("objective","terminal_deliverable","completion_condition","cycle_observation","cycle_action","success_exit","failure_exit","budget_exit","no_progress_rule","human_escalation_boundary","final_synthesis_requirement"):
        if not present(d.get(k)):e.append(f"{k} is required")
    v=d.get("verification")
    if not isinstance(v,dict):e.append("verification must be an object")
    else:
        if v.get("method") not in VERIFY:e.append(f"verification.method must be one of {sorted(VERIFY)}")
        if not present(v.get("evidence")):e.append("verification.evidence is required")
    b=d.get("budgets")
    if not isinstance(b,dict):e.append("budgets must be an object")
    else:
        if not posint(b.get("max_iterations")):e.append("budgets.max_iterations must be a positive integer")
        if not nonnegint(b.get("max_retries")):e.append("budgets.max_retries must be a non-negative integer")
        if not posint(b.get("max_no_progress_cycles")):e.append("budgets.max_no_progress_cycles must be a positive integer")
        wall=b.get("max_wall_minutes");cost=b.get("max_cost")
        if wall is None and cost is None:e.append("budgets must include max_wall_minutes or max_cost")
        if wall is not None and not positive_num(wall):e.append("budgets.max_wall_minutes must be a positive finite number")
        if cost is not None and not positive_num(cost):e.append("budgets.max_cost must be a positive finite number")
    for k in ("local_repair_triggers","material_replan_triggers"):
        v=d.get(k)
        if not isinstance(v,list) or not v:e.append(f"{k} must be a non-empty array")
    side=d.get("side_effect_class")
    if side not in SIDE:e.append(f"side_effect_class must be one of {sorted(SIDE)}")
    a=d.get("approval")
    if not isinstance(a,dict):e.append("approval must be an object")
    else:
        status=a.get("status")
        if status not in APPROVAL:e.append(f"approval.status must be one of {sorted(APPROVAL)}")
        if status=="approved" and not present(a.get("approval_reference")):e.append("approved contract requires approval.approval_reference")
    if not isinstance(d.get("domain_skills",[]),list):e.append("domain_skills must be an array")
    if not isinstance(d.get("tools",[]),list):e.append("tools must be an array")
    return e
def main():
    if len(sys.argv)!=2:print("Usage: validate_loop_contract.py <loop-contract.json>",file=sys.stderr);return 2
    try:d=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except Exception as x:print(f"FAIL: invalid JSON: {x}");return 1
    e=validate(d)
    for x in e:print(f"FAIL: {x}")
    print(f"RESULT: {'FAIL' if e else 'PASS'} ({len(e)} errors)")
    return 1 if e else 0
if __name__=="__main__":raise SystemExit(main())
