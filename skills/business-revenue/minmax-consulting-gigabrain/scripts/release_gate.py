#!/usr/bin/env python3
"""Fail-closed release gate for Gigabrain consulting recommendations."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

KNOWN_CHECKS = {"evidence", "consistency", "business_case", "challenge", "robustness"}


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _string_list(value: Any, name: str, blockers: list[str]) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        blockers.append(f"{name} must be a list of non-empty strings")
        return []
    return [x.strip() for x in value]


def _report_valid(report: Any) -> bool:
    return isinstance(report, dict) and report.get("valid") is True


def gate(decision: Any, evidence: Any = None, consistency: Any = None, business: Any = None, challenge: Any = None, robustness: Any = None) -> dict[str, Any]:
    blockers: list[str] = []
    conditions: list[str] = []
    warnings: list[str] = []
    if not isinstance(decision, dict):
        return {"status": "BLOCK", "blockers": ["decision must be an object"], "conditions": [], "warnings": []}
    required = decision.get("required_checks", ["evidence", "robustness"])
    if not isinstance(required, list) or any(not isinstance(x, str) for x in required):
        blockers.append("required_checks must be a list of check names"); required_set = {"evidence", "robustness"}
    else:
        required_set = set(required); unknown = sorted(required_set - KNOWN_CHECKS)
        if unknown: blockers.append("unknown required_checks: " + ", ".join(unknown))
    substantive = decision.get("substantive", True)
    if not isinstance(substantive, bool): blockers.append("substantive must be boolean"); substantive = True
    if substantive: required_set.update({"evidence", "robustness"})
    challenge_mode = decision.get("challenge_mode", "off")
    if challenge_mode not in {"off", "pulse", "conviction", "independent"}: blockers.append("challenge_mode is invalid")
    elif challenge_mode != "off": required_set.add("challenge")
    thresholds = decision.get("thresholds", {})
    if not isinstance(thresholds, dict): blockers.append("thresholds must be an object"); thresholds = {}
    if any(k in thresholds for k in ("min_base_npv", "min_downside_npv")): required_set.add("business_case")
    for name, report in (("evidence", evidence), ("consistency", consistency)):
        if name in required_set and report is None: blockers.append(f"required {name} report is missing")
        elif report is not None and not _report_valid(report): blockers.append(f"{name} validation failed or report is malformed")
    if "business_case" in required_set and business is None: blockers.append("required business_case report is missing")
    if business is not None:
        if not isinstance(business, dict) or business.get("valid", True) is not True: blockers.append("business_case report is invalid or malformed")
        scenarios = business.get("scenarios") if isinstance(business, dict) else None
        if not isinstance(scenarios, dict) or not scenarios: blockers.append("business_case scenarios are missing"); scenarios = {}
        checks = (("min_base_npv", decision.get("base_scenario", "base"), "base"), ("min_downside_npv", decision.get("downside_scenario", "downside"), "downside"))
        for threshold_name, scenario_name, label in checks:
            if threshold_name not in thresholds: continue
            threshold = thresholds[threshold_name]
            if not _finite_number(threshold): blockers.append(f"{threshold_name} must be a finite number"); continue
            scenario = scenarios.get(scenario_name)
            if not isinstance(scenario, dict): blockers.append(f"required {label} scenario {scenario_name!r} is missing"); continue
            value = scenario.get("npv")
            if not _finite_number(value): blockers.append(f"{label} scenario NPV is missing or non-finite"); continue
            if float(value) < float(threshold): blockers.append(f"{label} NPV {float(value):.2f} below threshold {float(threshold):.2f}")
    if "robustness" in required_set and robustness is None: blockers.append("required robustness report is missing")
    if robustness is not None:
        if not isinstance(robustness, dict) or robustness.get("valid") is not True: blockers.append("robustness report is invalid or malformed")
        else:
            score = robustness.get("score")
            if not _finite_number(score): blockers.append("robustness score is missing or non-finite")
            elif float(score) < 90.0 or robustness.get("eligible_to_stop") is not True: blockers.append(f"decision robustness {float(score):.1f} below 90+ release threshold")
    if "challenge" in required_set and challenge is None: blockers.append("required challenge report is missing")
    if challenge is not None:
        if not isinstance(challenge, dict) or challenge.get("valid") is not True: blockers.append("challenge report is invalid or malformed")
        else:
            status = challenge.get("status")
            if status != "ROBUST": blockers.append(f"challenge gate not robust: {status}")
            if challenge.get("accepted_critical"): blockers.append("challenge contains accepted critical risk")
    blockers.extend(_string_list(decision.get("hard_blockers", []), "hard_blockers", blockers))
    unresolved = _string_list(decision.get("unresolved_material_assumptions", []), "unresolved_material_assumptions", blockers)
    conditions.extend(f"unresolved material assumption: {x}" for x in unresolved)
    blockers = list(dict.fromkeys(blockers)); conditions = list(dict.fromkeys(conditions))
    status = "BLOCK" if blockers else ("CONDITIONAL" if conditions else "PASS")
    return {"status": status, "blockers": blockers, "conditions": conditions, "warnings": warnings}


def _load(path: str | None) -> Any:
    if not path: return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Gigabrain release gate")
    parser.add_argument("decision"); parser.add_argument("--evidence"); parser.add_argument("--consistency"); parser.add_argument("--business-case"); parser.add_argument("--challenge"); parser.add_argument("--robustness"); parser.add_argument("--output"); args = parser.parse_args()
    try: result = gate(_load(args.decision), _load(args.evidence), _load(args.consistency), _load(args.business_case), _load(args.challenge), _load(args.robustness))
    except (OSError, json.JSONDecodeError) as exc: result = {"status": "BLOCK", "blockers": [str(exc)], "conditions": [], "warnings": []}
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output: Path(args.output).write_text(text, encoding="utf-8")
    else: print(text, end="")
    return 0 if result["status"] == "PASS" else (1 if result["status"] == "CONDITIONAL" else 2)


if __name__ == "__main__": raise SystemExit(main())
