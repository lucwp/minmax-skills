#!/usr/bin/env python3
import json
import sys
from pathlib import Path

TOPOLOGIES={
    "deterministic_prompt_chain","router","single_adaptive_loop","parallel_sectioning",
    "parallel_independent_review","orchestrator_workers","evaluator_optimizer",
}
SIDE={"read_only","reversible_write","external_write","irreversible_high_consequence","mixed","read_only_or_reversible_write","read_only_or_task_defined"}
REQUIRED={
    "id","prompt_class","acceptable_topologies","forbidden_unnecessary_topology",
    "required_verifier_properties","state_requirement","side_effect_class",
    "approval_requirements","expected_terminal_behavior",
}
MANDATORY_CASES={
    "simple_sequential_task","breadth_first_research","complex_coding","subjective_design",
    "business_strategy","artifact_production","external_write","long_running_resumable",
    "adversarial_invalid_premise",
}


def substantive_text(v, minimum=12):
    return isinstance(v,str) and len(v.strip()) >= minimum and v.strip().lower() not in {"x","todo","tbd","n/a"}


def substantive_list(v, minimum=8):
    return isinstance(v,list) and bool(v) and all(substantive_text(x, minimum) for x in v)


def validate(data):
    errors=[]
    if data.get("schema_version")!="1.0":
        errors.append("schema_version must be 1.0")
    scoring=data.get("scoring",{})
    dims=["topology_fit","verification_quality","complexity_efficiency","safety_boundaries","contract_usability"]
    if sum(scoring.get(k,0) for k in dims)!=100:
        errors.append("scoring dimensions must sum to 100")
    if scoring.get("pass_score")!=95:
        errors.append("pass_score must be 95")
    cases=data.get("cases")
    if not isinstance(cases,list) or not cases:
        return errors+["cases must be a non-empty array"]
    ids=set()
    for i,c in enumerate(cases):
        prefix=f"cases[{i}]"
        missing=REQUIRED-set(c)
        if missing:
            errors.append(f"{prefix} missing {sorted(missing)}")
        cid=c.get("id")
        if cid in ids:
            errors.append(f"duplicate case id: {cid}")
        ids.add(cid)
        if not substantive_text(c.get("prompt_class")):
            errors.append(f"{prefix}.prompt_class must be substantive")
        acceptable=c.get("acceptable_topologies",[])
        forbidden=c.get("forbidden_unnecessary_topology",[])
        if not acceptable:
            errors.append(f"{prefix}.acceptable_topologies must not be empty")
        unknown=(set(acceptable)|set(forbidden))-TOPOLOGIES
        if unknown:
            errors.append(f"{prefix} unknown topologies {sorted(unknown)}")
        overlap=set(acceptable)&set(forbidden)
        if overlap:
            errors.append(f"{prefix} topology both acceptable and forbidden: {sorted(overlap)}")
        if not substantive_list(c.get("required_verifier_properties")):
            errors.append(f"{prefix}.required_verifier_properties must contain substantive requirements")
        if not substantive_text(c.get("state_requirement"), minimum=5):
            errors.append(f"{prefix}.state_requirement must be substantive")
        if c.get("side_effect_class") not in SIDE:
            errors.append(f"{prefix}.side_effect_class must be a valid side-effect class")
        if not substantive_list(c.get("approval_requirements")):
            errors.append(f"{prefix}.approval_requirements must contain substantive requirements")
        if not substantive_text(c.get("expected_terminal_behavior"), minimum=18):
            errors.append(f"{prefix}.expected_terminal_behavior must be substantive")
    missing_cases=MANDATORY_CASES-ids
    if missing_cases:
        errors.append(f"missing mandatory cases {sorted(missing_cases)}")
    return errors


def main():
    path=Path(sys.argv[1] if len(sys.argv)>1 else "evals/loop-mode/cases.json")
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1
    errors=validate(data)
    for error in errors:
        print(f"FAIL: {error}")
    print(f"RESULT: {'FAIL' if errors else 'PASS'} ({len(errors)} errors)")
    return 1 if errors else 0


if __name__=="__main__":
    raise SystemExit(main())
