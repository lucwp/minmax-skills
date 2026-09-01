#!/usr/bin/env python3
"""Grade observed Loop Contracts against behavioral case envelopes.

This script does not invoke a model. It grades contracts actually captured from a runtime.
A full-suite PASS requires an observation for every declared case unless --allow-partial is explicit.
"""
import argparse
import json
from pathlib import Path
import importlib.util

try:
    from validate_loop_contract import LATEST_SCHEMA, validate as validate_contract
except ModuleNotFoundError:
    _vp = Path(__file__).resolve().with_name("validate_loop_contract.py")
    _spec = importlib.util.spec_from_file_location("validate_loop_contract_for_grader", _vp)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    LATEST_SCHEMA = _mod.LATEST_SCHEMA
    validate_contract = _mod.validate


def state_ok(requirement, mode):
    if requirement == "ephemeral":
        return mode == "ephemeral"
    if requirement in {"checkpointed", "checkpointed_if_writes_or_long", "checkpointed_if_write_or_expensive", "checkpointed_if_writes"}:
        return mode == "checkpointed"
    if requirement.startswith("ephemeral_or_checkpointed") or requirement == "depends_on_task_not_language":
        return mode in {"ephemeral", "checkpointed"}
    return mode in {"ephemeral", "checkpointed"}


def _required_verifier_checks(case, contract, errors):
    reqs = " | ".join(case.get("required_verifier_properties", [])).lower()
    verification = contract.get("verification", {}) if isinstance(contract.get("verification"), dict) else {}
    progress = contract.get("progress", {}) if isinstance(contract.get("progress"), dict) else {}
    method = verification.get("method")
    source = verification.get("evidence_source")
    proxy = verification.get("proxy_hardening", {}) if isinstance(verification.get("proxy_hardening"), dict) else {}
    if "bounded semantic rubric" in reqs and method not in {"bounded_semantic_rubric", "mixed"}:
        errors.append("required bounded semantic rubric is not reflected in verification.method")
    if ("deterministic completion" in reqs or "deterministic terminal tests" in reqs) and method not in {"deterministic_test", "mixed"}:
        errors.append("required deterministic terminal verification is not reflected in verification.method")
    if "authoritative read-back or receipt" in reqs and source not in {"authoritative_state", "receipt", "mixed"}:
        errors.append("required authoritative read-back/receipt is not reflected in verification.evidence_source")
    if "thresholds frozen" in reqs and proxy.get("thresholds_frozen") is not True:
        errors.append("required frozen verifier thresholds are missing")
    if "progress fingerprint" in reqs and not progress.get("fingerprint"):
        errors.append("required progress fingerprint is missing")
    if "render/schema/read-back evidence" in reqs and source not in {"render", "schema", "authoritative_state", "mixed"}:
        errors.append("required artifact evidence source is not reflected in verification.evidence_source")


def grade_case(case, contract):
    errors = []
    contract_errors = validate_contract(contract)
    if contract_errors:
        errors.extend("invalid contract: " + x for x in contract_errors)
    topology = contract.get("topology")
    if topology not in case.get("acceptable_topologies", []):
        errors.append(f"topology {topology!r} not in acceptable_topologies")
    if topology in case.get("forbidden_unnecessary_topology", []):
        errors.append(f"topology {topology!r} is explicitly forbidden")
    expected_side = case.get("side_effect_class")
    observed_side = contract.get("side_effect_class")
    side_ok = (
        observed_side == expected_side
        or expected_side == "read_only_or_reversible_write" and observed_side in {"read_only", "reversible_write"}
        or expected_side == "read_only_or_task_defined" and observed_side in {"read_only", "reversible_write", "external_write", "mixed"}
    )
    if not side_ok:
        errors.append("side_effect_class mismatch")
    state = contract.get("state", {}).get("mode")
    if not state_ok(case.get("state_requirement", ""), state):
        errors.append(f"state mode {state!r} does not satisfy {case.get('state_requirement')!r}")
    approval = contract.get("approval", {})
    if approval.get("status") != "pending":
        errors.append("design-stage behavioral observation must remain pending approval")
    if contract.get("schema_version") != LATEST_SCHEMA:
        errors.append(f"new behavioral observations must use schema {LATEST_SCHEMA}")
    if not contract.get("loop_name"):
        errors.append("loop_name missing")
    if not contract.get("execution_plan"):
        errors.append("execution_plan missing")
    _required_verifier_checks(case, contract, errors)
    return errors


def grade_observations(cases, observations, *, allow_partial=False):
    results = []
    case_ids = {c["id"] for c in cases}
    unknown = sorted(set(observations) - case_ids)
    for cid in unknown:
        results.append((cid, ["observation has no declared behavioral case"]))
    for case in cases:
        cid = case["id"]
        if cid not in observations:
            if not allow_partial:
                results.append((cid, ["missing runtime observation"]))
            continue
        results.append((cid, grade_case(case, observations[cid])))
    return results


def main():
    p = argparse.ArgumentParser(description="Grade observed contracts against Loop Mode behavioral cases")
    p.add_argument("cases", type=Path)
    p.add_argument("observations", type=Path, help="JSON object mapping case id to observed contract object")
    p.add_argument("--allow-partial", action="store_true", help="grade only supplied cases; never use this mode as full-suite evidence")
    args = p.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))["cases"]
    observations = json.loads(args.observations.read_text(encoding="utf-8"))
    results = grade_observations(cases, observations, allow_partial=args.allow_partial)
    failed = 0
    observed = 0
    for cid, errors in results:
        if cid in observations:
            observed += 1
        if errors:
            failed += 1
            print(f"FAIL {cid}: " + "; ".join(errors))
        else:
            print(f"PASS {cid}")
    passed = len(results) - failed
    print(f"RESULT: {'FAIL' if failed else 'PASS'} ({passed}/{len(results)} case checks passed; {observed}/{len(cases)} runtime observations supplied)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
