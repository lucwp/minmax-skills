#!/usr/bin/env python3
"""Calculate Decision Robustness from observable criterion states.

The score measures how robust the chosen decision is to remaining uncertainty.
It is not a probability that the thesis or forecast is true. Criterion statuses
are computed as met=100%, partial=50%, not-met=0%; n/a removes the criterion
from the denominator. Hard gates cap the score below the 90+ stop threshold.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

CRITERIA: dict[str, tuple[str, float]] = {
    "load_bearing_claims_traced": ("evidence_provenance", 6.0),
    "source_conflicts_reconciled": ("evidence_provenance", 4.0),
    "source_quality_and_population_fit_assessed": ("evidence_provenance", 4.0),
    "fact_inference_assumption_separated": ("evidence_provenance", 3.0),
    "evidence_limitations_visible": ("evidence_provenance", 3.0),
    "load_bearing_assumptions_explicit": ("assumption_resilience", 5.0),
    "disconfirming_evidence_sought": ("assumption_resilience", 5.0),
    "decision_flip_counterfactual_identified": ("assumption_resilience", 4.0),
    "assumptions_bounded_or_testable": ("assumption_resilience", 4.0),
    "materiality_triaged": ("assumption_resilience", 2.0),
    "arithmetic_deterministic_when_material": ("economics_quant_sensitivity", 4.0),
    "base_downside_or_range_shown": ("economics_quant_sensitivity", 4.0),
    "switching_value_or_sensitivity_shown": ("economics_quant_sensitivity", 4.0),
    "units_denominators_periods_reconciled": ("economics_quant_sensitivity", 3.0),
    "strongest_credible_alternative_identified": ("alternatives_countercase", 5.0),
    "alternatives_compared_on_common_criteria": ("alternatives_countercase", 5.0),
    "status_quo_or_staging_considered_when_credible": ("alternatives_countercase", 3.0),
    "original_thesis_not_privileged": ("alternatives_countercase", 2.0),
    "feasibility_capacity_dependencies_checked": ("execution_incentives_response", 5.0),
    "incentives_and_actor_response_checked": ("execution_incentives_response", 4.0),
    "ownership_governance_adoption_defined": ("execution_incentives_response", 3.0),
    "reversibility_or_contingency_defined": ("execution_incentives_response", 3.0),
    "critical_uncertainties_have_controls": ("falsifiers_signposts_reversibility", 4.0),
    "kill_scale_switch_criteria_defined": ("falsifiers_signposts_reversibility", 3.0),
    "monitoring_signposts_defined": ("falsifiers_signposts_reversibility", 3.0),
    "strongest_counterevidence_preserved": ("residual_dissent_quality", 2.0),
    "residual_uncertainty_classified": ("residual_dissent_quality", 2.0),
    "confidence_matches_evidence": ("residual_dissent_quality", 1.0),
}

DIMENSION_MAX = {"evidence_provenance": 20.0, "assumption_resilience": 20.0, "economics_quant_sensitivity": 15.0, "alternatives_countercase": 15.0, "execution_incentives_response": 15.0, "falsifiers_signposts_reversibility": 10.0, "residual_dissent_quality": 5.0}
CORE_FLOORS = {"evidence_provenance": 0.80, "assumption_resilience": 0.80, "economics_quant_sensitivity": 0.73, "alternatives_countercase": 0.73, "execution_incentives_response": 0.73, "falsifiers_signposts_reversibility": 0.80}
STATUS_FACTOR = {"met": 1.0, "partial": 0.5, "not-met": 0.0, "na": None}
DECISION_CLASSES = {"recommend", "recommend-with-conditions", "do-not-recommend", "insufficient-evidence"}
RESIDUAL_CLASSES = {"none", "controlled", "judgment-only", "unresolved-empirical"}
OUTSIDE_VIEW = {"done", "not-required", "unavailable", "missing"}


def _bool(payload: dict[str, Any], key: str, errors: list[str], default: bool) -> bool:
    if key not in payload:
        return default
    value = payload.get(key)
    if not isinstance(value, bool):
        errors.append(f"{key} must be boolean")
        return default
    return value


def evaluate(payload: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    caps: list[dict[str, Any]] = []
    if not isinstance(payload, dict):
        return {"valid": False, "score": 0.0, "raw_score": 0.0, "status": "INVALID", "eligible_to_stop": False, "errors": ["robustness input must be an object"], "warnings": [], "caps": []}
    decision_class = payload.get("decision_class")
    if decision_class not in DECISION_CLASSES:
        errors.append("decision_class must be one of " + ", ".join(sorted(DECISION_CLASSES)))
    supplied = payload.get("criteria")
    if not isinstance(supplied, dict):
        errors.append("criteria must be an object")
        supplied = {}
    unknown_criteria = sorted(set(supplied) - set(CRITERIA))
    if unknown_criteria:
        errors.append("unknown criteria: " + ", ".join(unknown_criteria))
    earned = applicable_weight = 0.0
    dimension_earned: dict[str, float] = defaultdict(float)
    dimension_applicable: dict[str, float] = defaultdict(float)
    criterion_report: dict[str, Any] = {}
    for name, (dimension, weight) in CRITERIA.items():
        item = supplied.get(name)
        if not isinstance(item, dict):
            errors.append(f"criteria.{name} must be an object")
            item = {}
        status = item.get("status")
        if status not in STATUS_FACTOR:
            errors.append(f"criteria.{name}.status must be one of {', '.join(STATUS_FACTOR)}")
            status = "not-met"
        evidence = item.get("evidence", "")
        if not isinstance(evidence, str):
            errors.append(f"criteria.{name}.evidence must be a string")
            evidence = ""
        if status in {"met", "partial"} and not evidence.strip():
            errors.append(f"criteria.{name}.evidence is required when status is {status}")
        factor = STATUS_FACTOR[status]
        points = 0.0 if factor is None else weight * factor
        if factor is not None:
            earned += points; applicable_weight += weight; dimension_earned[dimension] += points; dimension_applicable[dimension] += weight
        criterion_report[name] = {"dimension": dimension, "weight": weight, "status": status, "points": points, "evidence": evidence}
    if applicable_weight <= 0:
        errors.append("at least one criterion must be applicable"); raw_score = 0.0
    else:
        raw_score = 100.0 * earned / applicable_weight
    dimension_report: dict[str, Any] = {}
    for name, nominal_max in DIMENSION_MAX.items():
        app = dimension_applicable.get(name, 0.0); got = dimension_earned.get(name, 0.0); pct = None if app <= 0 else 100.0 * got / app
        dimension_report[name] = {"earned": round(got, 2), "applicable_weight": round(app, 2), "nominal_max": nominal_max, "pct": None if pct is None else round(pct, 1)}
    gates = payload.get("hard_gates", {})
    if not isinstance(gates, dict): errors.append("hard_gates must be an object"); gates = {}
    critical_empirical_breaker = _bool(gates, "critical_empirical_breaker", errors, False)
    material_quant_error = _bool(gates, "material_quant_error", errors, False)
    material_evidence_conflict = _bool(gates, "material_evidence_conflict", errors, False)
    decision_contract_missing = _bool(gates, "decision_contract_missing", errors, False)
    load_bearing_claim_unsupported = _bool(gates, "load_bearing_claim_unsupported", errors, False)
    flags = payload.get("flags", {})
    if not isinstance(flags, dict): errors.append("flags must be an object"); flags = {}
    forecast_heavy = _bool(flags, "forecast_heavy", errors, False)
    quant_material = _bool(flags, "quant_material", errors, False)
    material_alternative_required = _bool(flags, "material_alternative_required", errors, True)
    strongest_alternative_evaluated = _bool(flags, "strongest_alternative_evaluated", errors, True)
    execution_heavy = _bool(flags, "execution_heavy", errors, False)
    implementation_feasibility_tested = _bool(flags, "implementation_feasibility_tested", errors, True)
    surviving_critical_uncertainty = _bool(flags, "surviving_critical_uncertainty", errors, False)
    critical_uncertainty_controlled = _bool(flags, "critical_uncertainty_controlled", errors, True)
    accepted_critical_risk = _bool(flags, "accepted_critical_risk", errors, False)
    outside_view_status = flags.get("outside_view_status", "not-required")
    if outside_view_status not in OUTSIDE_VIEW: errors.append("flags.outside_view_status must be one of " + ", ".join(sorted(OUTSIDE_VIEW))); outside_view_status = "missing"
    residual_class = flags.get("residual_uncertainty_class", "none")
    if residual_class not in RESIDUAL_CLASSES: errors.append("flags.residual_uncertainty_class must be one of " + ", ".join(sorted(RESIDUAL_CLASSES))); residual_class = "unresolved-empirical"
    applicability_min = {"evidence_provenance": 16.0, "assumption_resilience": 20.0, "alternatives_countercase": 12.0 if material_alternative_required else 7.0, "falsifiers_signposts_reversibility": 3.0, "residual_dissent_quality": 1.0}
    if quant_material or forecast_heavy: applicability_min["economics_quant_sensitivity"] = 15.0
    if execution_heavy: applicability_min["execution_incentives_response"] = 15.0
    for dimension, minimum in applicability_min.items():
        if dimension_applicable.get(dimension, 0.0) + 1e-9 < minimum: errors.append(f"{dimension} has too many criteria marked na for this decision")
    def cap(reason: str) -> None: caps.append({"max_score": 89.0, "reason": reason})
    if critical_empirical_breaker: cap("unresolved critical empirical breaker")
    if material_quant_error: cap("material quantitative error")
    if material_evidence_conflict: cap("material evidence conflict")
    if decision_contract_missing: cap("decision contract missing")
    if load_bearing_claim_unsupported: cap("load-bearing factual claim unsupported")
    if forecast_heavy and outside_view_status == "missing": cap("forecast-heavy decision lacks outside-view check")
    if material_alternative_required and not strongest_alternative_evaluated: cap("material alternative not evaluated on common criteria")
    if execution_heavy and not implementation_feasibility_tested: cap("implementation feasibility not tested")
    if surviving_critical_uncertainty and not critical_uncertainty_controlled: cap("surviving critical uncertainty lacks falsifier/signpost/switching condition")
    if accepted_critical_risk: cap("accepted critical risk remains decision-relevant")
    if residual_class == "unresolved-empirical": cap("residual uncertainty remains empirically resolvable and decision-flipping")
    for dimension, floor in CORE_FLOORS.items():
        pct = dimension_report[dimension]["pct"]
        if pct is not None and pct + 1e-9 < floor * 100.0: cap(f"{dimension} below 90+ minimum quality floor")
    score = min(raw_score, 89.0) if caps else raw_score
    raw_score = round(raw_score, 1); score = round(score, 1)
    if errors: status = "INVALID"; score = 0.0; eligible = False
    elif score >= 90.0: status = "ROBUST"; eligible = True
    elif score >= 80.0: status = "STRONG_BUT_NOT_ROBUST"; eligible = False
    elif score >= 60.0: status = "WEAK"; eligible = False
    else: status = "INSUFFICIENT"; eligible = False
    if decision_class == "insufficient-evidence" and eligible: warnings.append("90+ means the decision to withhold or condition commitment is robust; it does not mean the unknown outcome is 90% certain")
    construction_target = 95.0
    return {"valid": not errors, "decision_class": decision_class, "score": score, "raw_score": raw_score, "status": status, "eligible_to_stop": eligible, "construction_target": construction_target, "benchmark_grade": bool(not errors and score >= construction_target), "headroom_to_95": round(max(0.0, construction_target - score), 1) if not errors else construction_target, "criteria": criterion_report, "dimensions": dimension_report, "caps": caps, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Score Gigabrain Decision Robustness")
    parser.add_argument("input", help="Decision robustness JSON"); parser.add_argument("--output"); args = parser.parse_args()
    try: report = evaluate(json.loads(Path(args.input).read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc: report = {"valid": False, "score": 0.0, "raw_score": 0.0, "status": "INVALID", "eligible_to_stop": False, "errors": [str(exc)], "warnings": [], "caps": []}
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output: Path(args.output).write_text(text, encoding="utf-8")
    else: print(text, end="")
    return 0 if report.get("valid") else 2


if __name__ == "__main__": raise SystemExit(main())
