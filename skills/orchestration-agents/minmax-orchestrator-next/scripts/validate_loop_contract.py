#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
import re
import sys
from copy import deepcopy
from pathlib import Path

LATEST_SCHEMA = "1.4"
LEGACY_SCHEMAS = {"1.0", "1.1", "1.2", "1.3"}
VERIFY = {"deterministic_test", "authoritative_read", "transaction_receipt", "render_qa", "schema_validation", "bounded_semantic_rubric", "mixed"}
SIDE = {"read_only", "reversible_write", "external_write", "irreversible_high_consequence", "mixed"}
APPROVAL = {"pending", "approved"}
TOPOLOGY = {
    "deterministic_prompt_chain", "router", "single_adaptive_loop", "parallel_sectioning",
    "parallel_independent_review", "orchestrator_workers", "evaluator_optimizer",
}
COMPLEX_TOPOLOGY = {"parallel_sectioning", "parallel_independent_review", "orchestrator_workers", "evaluator_optimizer"}
STATE_MODE = {"ephemeral", "checkpointed"}
HUMAN_LANGUAGE = {"pt-BR", "en", "other"}
LAYERS = ("action", "cycle", "terminal")
STEP_FIELDS_V13 = ("name", "action", "purpose", "output", "next", "effect")
STEP_FIELDS_V14 = STEP_FIELDS_V13 + ("requires_human_approval",)
STEP_EFFECT = {"read_only", "reversible_write", "external_write", "irreversible_high_consequence"}
SIDE_LEVEL = {"read_only": 0, "reversible_write": 1, "external_write": 2, "irreversible_high_consequence": 3, "mixed": 3}
BENEFIT_TYPES = {
    "classification_branching", "adaptive_action_selection", "true_parallelism", "context_isolation",
    "specialist_capability", "independent_risk_reduction", "dynamic_decomposition", "iterative_critique_gain",
}
COST_TYPES = {"coordination", "context", "latency", "token", "integration", "verification", "worker"}
PROGRESS_EVIDENCE = {
    "new_required_evidence", "resolved_dependency", "verified_artifact_change", "authoritative_state_change",
    "completed_action", "verifier_movement", "removed_blocker",
}
TERMINAL_ACTORS = {"deterministic_system", "authoritative_source", "transaction_system", "independent_reviewer"}
EVIDENCE_SOURCES = {"test", "authoritative_state", "receipt", "render", "schema", "independent_rubric", "mixed"}
GENERIC_STEP = re.compile(r"^(research|analy[sz]e|analysis|validate|validation|improve|iterate|review|optimi[sz]e|check|pesquisar|analisar|validar|melhorar|iterar|revisar|otimizar)[.! ]*$", re.I)
GENERIC_LOOP_NAME = re.compile(r"^(loop|optimization loop|improvement loop|loop mode execution|evaluator[- ]optimizer|loop\s*#?\s*\d+|loop\s+\d+)$", re.I)
READ_ONLY_WRITE_HINTS = re.compile(
    r"\b(send|email|e-mail|publish|post|deploy|delete|remove|submit|message|invite|book|schedule|purchase|buy|charge|refund|transfer|upload|push|commit|merge|rename|archive|trash|enviar|publicar|postar|deletar|excluir|agendar|comprar|cobrar|reembolsar|transferir|subir|renomear|arquivar)\b",
    re.I,
)
READ_ONLY_EXTERNAL_OBJECT_HINTS = re.compile(
    r"\b(create|edit|modify|change|update|move|alter|criar|editar|modificar|alterar|mover|atualizar)\b.*\b(calendar event|calendar|crm|record|drive|repository|repo|branch|pull request|issue|ticket|account|contact|deal|opportunity|external file|external document|database|evento(?: de)? calend[aá]rio|registro|reposit[oó]rio|arquivo externo|documento externo|banco de dados)\b",
    re.I,
)


def present(v):
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, dict)):
        return bool(v)
    return True


def posint(v):
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def nonnegint(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def positive_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0


def canonical_contract_payload(d):
    """Return the immutable approval payload. Approval metadata and the digest field itself are excluded."""
    payload = deepcopy(d)
    payload.pop("contract_digest", None)
    payload.pop("approval", None)
    return payload


def compute_contract_digest(d):
    raw = json.dumps(canonical_contract_payload(d), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _validate_common(d, e):
    if d.get("mode") != "loop":
        e.append("mode must be 'loop'")
    for k in (
        "objective", "terminal_deliverable", "completion_condition", "cycle_observation", "cycle_action",
        "success_exit", "failure_exit", "budget_exit", "no_progress_rule", "human_escalation_boundary",
        "final_synthesis_requirement",
    ):
        if not present(d.get(k)):
            e.append(f"{k} is required")

    v = d.get("verification")
    if not isinstance(v, dict):
        e.append("verification must be an object")
    else:
        if v.get("method") not in VERIFY:
            e.append(f"verification.method must be one of {sorted(VERIFY)}")
        if not present(v.get("evidence")):
            e.append("verification.evidence is required")

    b = d.get("budgets")
    if not isinstance(b, dict):
        e.append("budgets must be an object")
    else:
        if not posint(b.get("max_iterations")):
            e.append("budgets.max_iterations must be a positive integer")
        if not nonnegint(b.get("max_retries")):
            e.append("budgets.max_retries must be a non-negative integer")
        if not posint(b.get("max_no_progress_cycles")):
            e.append("budgets.max_no_progress_cycles must be a positive integer")
        wall = b.get("max_wall_minutes")
        cost = b.get("max_cost")
        if wall is None and cost is None:
            e.append("budgets must include max_wall_minutes or max_cost")
        if wall is not None and not positive_num(wall):
            e.append("budgets.max_wall_minutes must be a positive finite number")
        if cost is not None and not positive_num(cost):
            e.append("budgets.max_cost must be a positive finite number")

    for k in ("local_repair_triggers", "material_replan_triggers"):
        value = d.get(k)
        if not isinstance(value, list) or not value:
            e.append(f"{k} must be a non-empty array")

    side = d.get("side_effect_class")
    if side not in SIDE:
        e.append(f"side_effect_class must be one of {sorted(SIDE)}")

    if not isinstance(d.get("domain_skills", []), list):
        e.append("domain_skills must be an array")
    if not isinstance(d.get("tools", []), list):
        e.append("tools must be an array")


def _validate_v11(d, e):
    topology = d.get("topology")
    if topology not in TOPOLOGY:
        e.append(f"topology must be one of {sorted(TOPOLOGY)}")
    if not present(d.get("topology_rationale")):
        e.append("topology_rationale is required")

    p = d.get("progress")
    if not isinstance(p, dict):
        e.append("progress must be an object")
    else:
        if not present(p.get("evidence_definition")):
            e.append("progress.evidence_definition is required")
        if "fingerprint" not in p:
            e.append("progress.fingerprint must be present (null/empty allowed when impractical)")

    v = d.get("verification")
    if isinstance(v, dict):
        layers = v.get("layers")
        if not isinstance(layers, dict):
            e.append("verification.layers must be an object")
        else:
            for layer in LAYERS:
                if not present(layers.get(layer)):
                    e.append(f"verification.layers.{layer} is required")
        if not present(v.get("independent_terminal_verifier")):
            e.append("verification.independent_terminal_verifier is required")
        if not present(v.get("proxy_hardening")):
            e.append("verification.proxy_hardening is required")

    state = d.get("state")
    if not isinstance(state, dict):
        e.append("state must be an object")
    else:
        mode = state.get("mode")
        if mode not in STATE_MODE:
            e.append(f"state.mode must be one of {sorted(STATE_MODE)}")
        if mode == "checkpointed":
            for k in ("store", "version_marker", "resume_strategy"):
                if not present(state.get(k)):
                    e.append(f"state.{k} is required for checkpointed mode")
        if mode == "ephemeral" and d.get("side_effect_class") in {"reversible_write", "external_write", "irreversible_high_consequence", "mixed"}:
            e.append("state.mode must be checkpointed for state-changing/mixed Loop Mode work")

    if not present(d.get("approved_boundaries")):
        e.append("approved_boundaries is required")


def _validate_v12(d, e):
    name = d.get("loop_name")
    if not present(name):
        e.append("loop_name is required")
    elif not isinstance(name, str) or len(name.strip()) < 4:
        e.append("loop_name must be descriptive, not a token label")

    lang = d.get("human_language")
    if lang not in HUMAN_LANGUAGE:
        e.append(f"human_language must be one of {sorted(HUMAN_LANGUAGE)}")

    plan = d.get("execution_plan")
    if not isinstance(plan, list) or len(plan) < 2:
        e.append("execution_plan must contain at least 2 material steps")
        return
    if len(plan) > 7:
        e.append("execution_plan must contain no more than 7 material steps; merge non-material steps")
    names = []
    for i, step in enumerate(plan):
        prefix = f"execution_plan[{i}]"
        if not isinstance(step, dict):
            e.append(f"{prefix} must be an object")
            continue
        for field in ("name", "action", "purpose", "output", "next"):
            if not present(step.get(field)):
                e.append(f"{prefix}.{field} is required")
        step_name = step.get("name")
        if isinstance(step_name, str) and step_name.strip():
            names.append(step_name.strip().lower())
    if len(names) != len(set(names)):
        e.append("execution_plan step names must be distinct")


def _validate_v13_semantics(d, e):
    # Contract identity and self-integrity.
    cid = d.get("contract_id")
    if not isinstance(cid, str) or len(cid.strip()) < 8:
        e.append("contract_id must be a stable identifier of at least 8 characters")
    expected_digest = compute_contract_digest(d)
    if d.get("contract_digest") != expected_digest:
        e.append("contract_digest does not match the canonical contract payload")

    # Naming and rendering contract.
    name = d.get("loop_name")
    if isinstance(name, str) and GENERIC_LOOP_NAME.fullmatch(name.strip()):
        e.append("loop_name is too generic; name the job the loop performs")

    # Execution semantics and side-effect envelope.
    plan = d.get("execution_plan")
    if isinstance(plan, list):
        for i, step in enumerate(plan):
            if not isinstance(step, dict):
                continue
            prefix = f"execution_plan[{i}]"
            for field in STEP_FIELDS_V13:
                if not present(step.get(field)):
                    e.append(f"{prefix}.{field} is required for schema 1.3+")
            for field in ("name", "action"):
                value = step.get(field)
                if isinstance(value, str) and GENERIC_STEP.fullmatch(value.strip()):
                    e.append(f"{prefix}.{field} is too generic; state the concrete operation")
            effect = step.get("effect")
            if effect not in STEP_EFFECT:
                e.append(f"{prefix}.effect must be one of {sorted(STEP_EFFECT)}")
            else:
                side = d.get("side_effect_class")
                if side in SIDE_LEVEL and SIDE_LEVEL[effect] > SIDE_LEVEL[side]:
                    e.append(f"{prefix}.effect exceeds side_effect_class={side}")
            action_text = str(step.get("action", ""))
            if d.get("side_effect_class") == "read_only" and (READ_ONLY_WRITE_HINTS.search(action_text) or READ_ONLY_EXTERNAL_OBJECT_HINTS.search(action_text)):
                e.append(f"{prefix}.action appears state-changing but side_effect_class is read_only")

    # Complexity gate: deterministic evidence that escalation has a concrete reason.
    gate = d.get("complexity_gate")
    if not isinstance(gate, dict):
        e.append("complexity_gate must be an object for schema 1.3+")
    else:
        simpler = gate.get("simpler_topology_considered")
        if simpler not in TOPOLOGY | {"none"}:
            e.append("complexity_gate.simpler_topology_considered must be a topology or 'none'")
        benefit_types = gate.get("benefit_types")
        if not isinstance(benefit_types, list) or not benefit_types:
            e.append("complexity_gate.benefit_types must be a non-empty array")
        else:
            unknown = set(benefit_types) - BENEFIT_TYPES
            if unknown:
                e.append(f"complexity_gate.benefit_types has unknown values {sorted(unknown)}")
        added_costs = gate.get("added_costs")
        if not isinstance(added_costs, list):
            e.append("complexity_gate.added_costs must be an array")
        else:
            unknown = set(added_costs) - COST_TYPES
            if unknown:
                e.append(f"complexity_gate.added_costs has unknown values {sorted(unknown)}")
        for k in ("limitation", "expected_gain"):
            if not present(gate.get(k)):
                e.append(f"complexity_gate.{k} is required")
        decision = gate.get("decision")
        if decision not in {"stay_simple", "escalate"}:
            e.append("complexity_gate.decision must be 'stay_simple' or 'escalate'")
        topology = d.get("topology")
        if topology in COMPLEX_TOPOLOGY:
            if decision != "escalate":
                e.append("complex topology requires complexity_gate.decision=escalate")
            if simpler in {None, "none", topology}:
                e.append("complex topology requires a genuinely simpler topology to be considered")
        elif decision == "escalate" and topology not in COMPLEX_TOPOLOGY:
            e.append("complexity_gate.decision=escalate is inconsistent with a simple topology")

        # Topology-specific evidence, so prestige/importance cannot be the only rationale.
        benefits = set(benefit_types or [])
        topology = d.get("topology")
        required_by_topology = {
            "parallel_sectioning": {"true_parallelism", "context_isolation"},
            "parallel_independent_review": {"independent_risk_reduction"},
            "orchestrator_workers": {"true_parallelism", "context_isolation", "specialist_capability", "dynamic_decomposition", "independent_risk_reduction"},
            "evaluator_optimizer": {"iterative_critique_gain"},
        }
        if topology in required_by_topology and not (benefits & required_by_topology[topology]):
            e.append(f"{topology} requires a matching concrete complexity_gate benefit type")

    # Progress must be structured and budget-consistent.
    progress = d.get("progress")
    if isinstance(progress, dict):
        allowed = progress.get("allowed_evidence_types")
        if not isinstance(allowed, list) or not allowed:
            e.append("progress.allowed_evidence_types must be a non-empty array")
        else:
            unknown = set(allowed) - PROGRESS_EVIDENCE
            if unknown:
                e.append(f"progress.allowed_evidence_types has invalid values {sorted(unknown)}")
        mnp = progress.get("max_no_progress_cycles")
        if not posint(mnp):
            e.append("progress.max_no_progress_cycles must be a positive integer")
        budgets = d.get("budgets") if isinstance(d.get("budgets"), dict) else {}
        if posint(mnp) and mnp != budgets.get("max_no_progress_cycles"):
            e.append("progress.max_no_progress_cycles must equal budgets.max_no_progress_cycles")
        evidence_text = str(progress.get("evidence_definition", ""))
        if re.search(r"\b(more reasoning|additional reasoning|more thinking|mais racioc[ií]nio|pensar mais)\b", evidence_text, re.I):
            e.append("progress.evidence_definition cannot treat reasoning-only activity as progress")
        rule_text = str(d.get("no_progress_rule", ""))
        if re.search(r"\b(unlimited|indefinite|forever|sem limite|indefinid[oa]|até ficar perfeito|until perfect)\b", rule_text, re.I):
            e.append("no_progress_rule cannot be unbounded")
        threshold_patterns = [
            r"(?:after|ap[oó]s)\s+(\d+)\s+(?:consecutive\s+)?(?:no[- ]progress\s+)?(?:cycles?|ciclos?)",
            r"(\d+)\s+(?:consecutive\s+)?(?:cycles?|ciclos?)\s+(?:without|sem)\s+(?:material\s+)?progress",
            r"(?:no[- ]progress|sem progresso)\D{0,24}(\d+)\s+(?:cycles?|ciclos?)",
        ]
        thresholds = []
        for pattern in threshold_patterns:
            thresholds.extend(int(x) for x in re.findall(pattern, rule_text, re.I))
        if not thresholds:
            e.append(f"schema {LATEST_SCHEMA} no_progress_rule must state the consecutive no-progress cycle limit explicitly")
        elif any(x != budgets.get("max_no_progress_cycles") for x in thresholds):
            e.append("no_progress_rule no-progress threshold must equal budgets.max_no_progress_cycles")

    # Verifier independence and proxy hardening become structured hard gates.
    verification = d.get("verification")
    if isinstance(verification, dict):
        actor = verification.get("terminal_actor")
        if actor not in TERMINAL_ACTORS:
            e.append(f"verification.terminal_actor must be one of {sorted(TERMINAL_ACTORS)}; executor self-report is not terminal evidence")
        source = verification.get("evidence_source")
        if source not in EVIDENCE_SOURCES:
            e.append(f"verification.evidence_source must be one of {sorted(EVIDENCE_SOURCES)}")
        verifier_text = str(verification.get("independent_terminal_verifier", ""))
        if re.search(r"executor\s+(says|reports|confirms)|self[- ]report|executor self", verifier_text, re.I):
            e.append("verification.independent_terminal_verifier cannot be executor self-report")
        ph = verification.get("proxy_hardening")
        if not isinstance(ph, dict):
            e.append("verification.proxy_hardening must be a structured object for schema 1.3+")
        else:
            attack = ph.get("attack_path")
            if not isinstance(attack, str) or len(attack.strip()) < 16 or attack.strip().lower() in {"be careful", "x", "todo", "tbd"}:
                e.append("verification.proxy_hardening.attack_path must describe a plausible verifier-gaming path")
            protected = ph.get("protected_elements")
            if not isinstance(protected, list) or not protected or any(not isinstance(x,str) or len(x.strip()) < 3 or x.strip().lower() in {"x","todo","tbd"} for x in protected):
                e.append("verification.proxy_hardening.protected_elements must contain substantive protected elements")
            if ph.get("thresholds_frozen") is not True:
                e.append("verification.proxy_hardening.thresholds_frozen must be true")
            if ph.get("executor_can_modify_verifier") is not False:
                e.append("verification.proxy_hardening.executor_can_modify_verifier must be false")

    # Approval metadata is validated below against an external approved digest when approved.
    approval = d.get("approval")
    if not isinstance(approval, dict):
        e.append("approval must be an object")
    else:
        status = approval.get("status")
        if status not in APPROVAL:
            e.append(f"approval.status must be one of {sorted(APPROVAL)}")
        if status == "approved":
            if not present(approval.get("approval_reference")):
                e.append("approved contract requires approval.approval_reference")
            if approval.get("approved_contract_digest") != d.get("contract_digest"):
                e.append("approval.approved_contract_digest must equal contract_digest")


def has_autonomous_external_write(d):
    plan = d.get("execution_plan")
    if not isinstance(plan, list):
        return False
    return any(
        isinstance(step, dict)
        and step.get("effect") == "external_write"
        and step.get("requires_human_approval") is False
        for step in plan
    )


def _validate_v14_semantics(d, e):
    plan = d.get("execution_plan")
    effects = []
    autonomous_external = False
    if isinstance(plan, list):
        for i, step in enumerate(plan):
            if not isinstance(step, dict):
                continue
            prefix = f"execution_plan[{i}]"
            for field in STEP_FIELDS_V14:
                if field not in step or (field != "requires_human_approval" and not present(step.get(field))):
                    e.append(f"{prefix}.{field} is required for schema 1.4")
            human_gate = step.get("requires_human_approval")
            if not isinstance(human_gate, bool):
                e.append(f"{prefix}.requires_human_approval must be boolean")
            effect = step.get("effect")
            if effect in STEP_EFFECT:
                effects.append(effect)
                if effect == "irreversible_high_consequence" and human_gate is not True:
                    e.append(f"{prefix} irreversible_high_consequence requires a human approval gate before the action")
                if effect == "external_write" and human_gate is False:
                    autonomous_external = True
            name = step.get("name")
            if isinstance(name, str) and ("\n" in name or "\r" in name or len(name.strip()) > 100):
                e.append(f"{prefix}.name must be a single concise line")

    loop_name = d.get("loop_name")
    if isinstance(loop_name, str) and ("\n" in loop_name or "\r" in loop_name or "\t" in loop_name or len(loop_name.strip()) > 100):
        e.append("loop_name must be a single concise line")

    side = d.get("side_effect_class")
    if side == "mixed" and effects and len(set(effects)) < 2:
        e.append("side_effect_class=mixed requires at least two distinct planned step effect classes")

    approval = d.get("approval") if isinstance(d.get("approval"), dict) else {}
    if approval.get("status") == "approved" and autonomous_external:
        if not present(approval.get("external_write_preauthorization_ref")):
            e.append("approved autonomous external_write requires approval.external_write_preauthorization_ref")


def validate(d, *, allow_legacy=False, approved_digest=None, external_write_preauthorization_ref=None):
    e = []
    version = d.get("schema_version")
    if version != LATEST_SCHEMA:
        if version in LEGACY_SCHEMAS and allow_legacy:
            pass
        elif version in LEGACY_SCHEMAS:
            e.append(f"schema_version {version} is legacy; new validation requires {LATEST_SCHEMA} unless --legacy-resume is explicit")
        else:
            e.append(f"schema_version must be '{LATEST_SCHEMA}'")

    _validate_common(d, e)
    if version in {"1.1", "1.2", "1.3", "1.4"}:
        _validate_v11(d, e)
    if version in {"1.2", "1.3", "1.4"}:
        _validate_v12(d, e)
    if version in {"1.3", "1.4"}:
        _validate_v13_semantics(d, e)
    if version == "1.4":
        _validate_v14_semantics(d, e)

    approval = d.get("approval")
    if isinstance(approval, dict) and approval.get("status") == "approved":
        if approved_digest is None:
            e.append("approved contract validation requires externally supplied approved digest")
        else:
            if approved_digest != d.get("contract_digest"):
                e.append("external approved digest does not match contract_digest; approval is invalidated")
            if approval.get("approved_contract_digest") != approved_digest:
                e.append("approval.approved_contract_digest does not match external approved digest")
    if version == LATEST_SCHEMA and isinstance(approval, dict) and approval.get("status") == "approved" and has_autonomous_external_write(d):
        internal_ref = approval.get("external_write_preauthorization_ref")
        if external_write_preauthorization_ref is None:
            e.append("approved autonomous external_write validation requires externally supplied external-write preauthorization reference")
        elif internal_ref != external_write_preauthorization_ref:
            e.append("approval.external_write_preauthorization_ref does not match external preauthorization reference")
    return e


def _parse_args(argv):
    p = argparse.ArgumentParser(description="Validate a MinMax Loop Contract")
    p.add_argument("contract", type=Path)
    p.add_argument("--legacy-resume", action="store_true", help="explicitly validate a legacy 1.0/1.1/1.2 contract for resume/migration only")
    p.add_argument("--approved-digest", help="digest captured by the root approval boundary; required for approved contracts")
    p.add_argument("--external-write-preauthorization-ref", help="root-captured explicit preauthorization reference for approved autonomous external writes")
    p.add_argument("--print-digest", action="store_true", help="print the canonical digest for the current contract payload")
    p.add_argument("--stamp-digest", action="store_true", help="write the current canonical digest into contract_digest before validating")
    return p.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv or sys.argv[1:])
    try:
        d = json.loads(args.contract.read_text(encoding="utf-8"))
    except Exception as x:
        print(f"FAIL: invalid JSON: {x}")
        return 1
    if args.stamp_digest:
        d["contract_digest"] = compute_contract_digest(d)
        args.contract.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.print_digest:
        print(compute_contract_digest(d))
    e = validate(d, allow_legacy=args.legacy_resume, approved_digest=args.approved_digest, external_write_preauthorization_ref=args.external_write_preauthorization_ref)
    for x in e:
        print(f"FAIL: {x}")
    print(f"RESULT: {'FAIL' if e else 'PASS'} ({len(e)} errors)")
    return 1 if e else 0


if __name__ == "__main__":
    raise SystemExit(main())
