#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

SIDE = {"read_only", "reversible_write", "external_write", "irreversible_high_consequence", "mixed"}
STATUS = {"active", "blocked", "success", "failure", "budget_exit", "paused_replan"}
VERIFICATION_STATUS = {"not_run", "partial", "pass", "fail", "blocked"}


def present(v):
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, dict)):
        return bool(v)
    return True


def nonneg(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v >= 0


def validate(checkpoint, contract=None, approved_digest=None, external_write_preauthorization_ref=None):
    e = []
    if checkpoint.get("schema_version") != "1.0":
        e.append("checkpoint schema_version must be 1.0")
    for k in ("run_id", "contract_id", "contract_version", "contract_digest", "approval_reference", "approved_contract_digest", "topology", "side_effect_class", "verification_status", "status"):
        if not present(checkpoint.get(k)):
            e.append(f"{k} is required")
    if checkpoint.get("approved_contract_digest") != checkpoint.get("contract_digest"):
        e.append("approved_contract_digest must equal contract_digest")
    if approved_digest is None:
        e.append("checkpoint validation requires externally supplied approved digest")
    elif checkpoint.get("contract_digest") != approved_digest:
        e.append("checkpoint contract_digest does not match external approved digest")
    if checkpoint.get("side_effect_class") not in SIDE:
        e.append("side_effect_class is invalid")
    if checkpoint.get("verification_status") not in VERIFICATION_STATUS:
        e.append("verification_status is invalid")
    if checkpoint.get("status") not in STATUS:
        e.append("status is invalid")

    for k in ("approved_boundaries", "remaining_budgets"):
        if not isinstance(checkpoint.get(k), dict) or not checkpoint.get(k):
            e.append(f"{k} must be a non-empty object")
    for k in ("done", "active", "blocked", "invalidated", "evidence", "write_receipts", "next_ready"):
        if not isinstance(checkpoint.get(k), list):
            e.append(f"{k} must be an array")

    rb = checkpoint.get("remaining_budgets") if isinstance(checkpoint.get("remaining_budgets"), dict) else {}
    for k in ("iterations", "retries", "no_progress_cycles"):
        if k not in rb or not nonneg(rb.get(k)):
            e.append(f"remaining_budgets.{k} must be a finite non-negative number")
    if "wall_minutes" in rb and rb.get("wall_minutes") is not None and not nonneg(rb.get("wall_minutes")):
        e.append("remaining_budgets.wall_minutes must be null or a finite non-negative number")
    if "cost" in rb and rb.get("cost") is not None and not nonneg(rb.get("cost")):
        e.append("remaining_budgets.cost must be null or a finite non-negative number")

    if contract is not None:
        if checkpoint.get("contract_id") != contract.get("contract_id"):
            e.append("checkpoint contract_id does not match contract")
        if checkpoint.get("contract_version") != contract.get("schema_version"):
            e.append("checkpoint contract_version does not match contract schema_version")
        if checkpoint.get("contract_digest") != contract.get("contract_digest"):
            e.append("checkpoint contract_digest does not match contract")
        if checkpoint.get("topology") != contract.get("topology"):
            e.append("checkpoint topology does not match contract")
        if checkpoint.get("side_effect_class") != contract.get("side_effect_class"):
            e.append("checkpoint side_effect_class does not match contract")
        approval = contract.get("approval") if isinstance(contract.get("approval"), dict) else {}
        if approval.get("status") == "approved" and checkpoint.get("approval_reference") != approval.get("approval_reference"):
            e.append("checkpoint approval_reference does not match approved contract")
        autonomous_external = any(
            isinstance(step, dict) and step.get("effect") == "external_write" and step.get("requires_human_approval") is False
            for step in contract.get("execution_plan", []) if isinstance(contract.get("execution_plan"), list)
        )
        if approval.get("status") == "approved" and autonomous_external:
            cp_ref = checkpoint.get("external_write_preauthorization_ref")
            contract_ref = approval.get("external_write_preauthorization_ref")
            if not present(cp_ref):
                e.append("checkpoint external_write_preauthorization_ref is required for autonomous external writes")
            if cp_ref != contract_ref:
                e.append("checkpoint external_write_preauthorization_ref does not match approved contract")
            if external_write_preauthorization_ref is None:
                e.append("checkpoint validation requires externally supplied external-write preauthorization reference")
            elif cp_ref != external_write_preauthorization_ref:
                e.append("checkpoint external_write_preauthorization_ref does not match external preauthorization reference")
        if checkpoint.get("approved_boundaries") != contract.get("approved_boundaries"):
            e.append("checkpoint approved_boundaries do not match immutable contract")
        budgets = contract.get("budgets") if isinstance(contract.get("budgets"), dict) else {}
        limits = {
            "iterations": budgets.get("max_iterations"),
            "retries": budgets.get("max_retries"),
            "no_progress_cycles": budgets.get("max_no_progress_cycles"),
            "wall_minutes": budgets.get("max_wall_minutes"),
            "cost": budgets.get("max_cost"),
        }
        for key, limit in limits.items():
            value = rb.get(key)
            if value is not None and limit is not None and value > limit:
                e.append(f"remaining_budgets.{key} exceeds approved contract budget")
    return e


def main():
    p = argparse.ArgumentParser(description="Validate a checkpoint against its immutable approved Loop Contract")
    p.add_argument("checkpoint", type=Path)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--approved-digest", required=True)
    p.add_argument("--external-write-preauthorization-ref")
    args = p.parse_args()
    try:
        cp = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: invalid JSON: {exc}")
        return 1
    errors = validate(cp, contract=contract, approved_digest=args.approved_digest, external_write_preauthorization_ref=args.external_write_preauthorization_ref)
    for error in errors:
        print(f"FAIL: {error}")
    print(f"RESULT: {'FAIL' if errors else 'PASS'} ({len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
