#!/usr/bin/env python3
"""Validate bounded Challenge Engine state and enforce the 90+ stop rule.

The gate validates process completeness, finite challenge budget, and the
Decision Robustness stopping condition. It does not determine whether the
underlying argument or evidence is substantively true.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MODES = {"off", "pulse", "conviction", "independent"}
SEVERITIES = {"critical", "major", "minor"}
STATUSES = {"open", "resolved", "accepted-risk", "non-decision-relevant"}
EVIDENCE = {"verified", "reasoning-only", "unknown"}
OUTSIDE_VIEW = {"done", "not-required", "unavailable", "missing"}
DECISION_STATES = {"unchanged", "narrowed", "revised", "reversed", "undecided"}
MODE_CAPS = {"off": 0, "pulse": 1, "conviction": 3, "independent": 2}


def _require_bool(payload: dict[str, Any], key: str, errors: list[str]) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        errors.append(f"{key} must be boolean")
        return False
    return value


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _robustness_valid(report: Any) -> bool:
    return isinstance(report, dict) and report.get("valid") is True and isinstance(report.get("score"), (int, float)) and not isinstance(report.get("score"), bool) and isinstance(report.get("eligible_to_stop"), bool)


def evaluate(payload: Any, robustness: Any = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(payload, dict):
        return {"valid": False, "status": "INVALID", "mode": "off", "errors": ["challenge ledger must be an object"], "warnings": [], "open_critical": [], "accepted_critical": [], "robustness_score": None}
    mode = payload.get("mode", "off")
    if mode not in MODES:
        errors.append(f"mode must be one of {', '.join(sorted(MODES))}"); mode = "off"
    if mode == "off":
        return {"valid": not errors, "status": "NOT_RUN" if not errors else "INVALID", "mode": mode, "errors": errors, "warnings": warnings, "open_critical": [], "accepted_critical": [], "robustness_score": robustness.get("score") if _robustness_valid(robustness) else None}
    if robustness is None: errors.append("active Challenge Engine requires a Decision Robustness report")
    elif not _robustness_valid(robustness): errors.append("Decision Robustness report is invalid or malformed")
    round_number = payload.get("round"); max_rounds = payload.get("max_rounds")
    if not isinstance(round_number, int) or isinstance(round_number, bool) or round_number < 1: errors.append("round must be an integer >= 1"); round_number = 1
    if not isinstance(max_rounds, int) or isinstance(max_rounds, bool) or max_rounds < 1: errors.append("max_rounds must be an integer >= 1"); max_rounds = MODE_CAPS[mode]
    cap = MODE_CAPS[mode]
    if max_rounds > cap: errors.append(f"{mode} max_rounds cannot exceed {cap}")
    if round_number > max_rounds: errors.append("round cannot exceed max_rounds")
    forecast_heavy = _require_bool(payload, "forecast_heavy", errors)
    alternative_evaluated = _require_bool(payload, "strongest_alternative_evaluated", errors)
    independent_used = _require_bool(payload, "independent_challenger_used", errors)
    outside_view = payload.get("outside_view_status")
    if outside_view not in OUTSIDE_VIEW: errors.append("outside_view_status must be one of " + ", ".join(sorted(OUTSIDE_VIEW))); outside_view = "missing"
    if outside_view == "unavailable" and not _nonempty_text(payload.get("outside_view_note")): errors.append("outside_view_note is required when outside_view_status is unavailable")
    decision_state = payload.get("decision_state")
    if decision_state not in DECISION_STATES: errors.append("decision_state must be one of " + ", ".join(sorted(DECISION_STATES)))
    if mode == "independent" and independent_used and not _nonempty_text(payload.get("isolation_note")): errors.append("isolation_note is required when an independent challenger was used")
    challenges = payload.get("challenges")
    if not isinstance(challenges, list): errors.append("challenges must be a list"); challenges = []
    elif not challenges: errors.append("an active Challenge Engine run must contain at least one challenge")
    ids: set[str] = set(); open_critical: list[str] = []; accepted_critical: list[str] = []; untestable_critical: list[str] = []
    for index, item in enumerate(challenges):
        context = f"challenges[{index}]"
        if not isinstance(item, dict): errors.append(f"{context} must be an object"); continue
        cid = item.get("id")
        if not _nonempty_text(cid): errors.append(f"{context}.id must be a non-empty string"); cid = f"ROW-{index}"
        elif cid in ids: errors.append(f"duplicate challenge id: {cid}")
        ids.add(cid)
        severity = item.get("severity")
        if severity not in SEVERITIES: errors.append(f"{context}.severity must be one of {', '.join(sorted(SEVERITIES))}")
        load_bearing = item.get("load_bearing")
        if not isinstance(load_bearing, bool): errors.append(f"{context}.load_bearing must be boolean"); load_bearing = False
        status = item.get("status")
        if status not in STATUSES: errors.append(f"{context}.status must be one of {', '.join(sorted(STATUSES))}")
        evidence_basis = item.get("evidence_basis")
        if evidence_basis not in EVIDENCE: errors.append(f"{context}.evidence_basis must be one of {', '.join(sorted(EVIDENCE))}")
        if status in {"resolved", "accepted-risk", "non-decision-relevant"} and not _nonempty_text(item.get("resolution")): errors.append(f"{context}.resolution is required for status {status}")
        falsifier = item.get("falsifier", ""); flip = item.get("decision_flip_condition", "")
        if severity == "critical" and load_bearing:
            if status == "open": open_critical.append(str(cid))
            elif status == "accepted-risk": accepted_critical.append(str(cid))
            if status in {"open", "accepted-risk"} and not _nonempty_text(falsifier) and not _nonempty_text(flip): untestable_critical.append(str(cid)); warnings.append(f"{cid}: unresolved critical load-bearing challenge has no falsifier or decision_flip_condition")
    if mode in {"conviction", "independent"} and not alternative_evaluated: warnings.append("strongest credible alternative has not been evaluated")
    if forecast_heavy and outside_view in {"missing", "not-required"}: warnings.append("forecast-heavy decision lacks an outside-view check")
    if mode == "independent" and not independent_used: warnings.append("independent mode was selected but no independent challenger was actually used")
    robustness_score = robustness.get("score") if _robustness_valid(robustness) else None
    robustness_stop = bool(_robustness_valid(robustness) and robustness.get("eligible_to_stop") is True and float(robustness_score) >= 90.0)
    if errors: status = "INVALID"
    elif accepted_critical: status = "UNRESOLVED"
    else:
        requirements_open = bool(open_critical or untestable_critical)
        if mode in {"conviction", "independent"} and not alternative_evaluated: requirements_open = True
        if forecast_heavy and outside_view in {"missing", "not-required"}: requirements_open = True
        if mode == "independent" and not independent_used: requirements_open = True
        if robustness_stop and not requirements_open: status = "ROBUST"
        elif round_number < max_rounds: status = "CONTINUE"
        elif open_critical or untestable_critical: status = "STOP_BUDGET"
        else: status = "UNRESOLVED"
    return {"valid": not errors, "status": status, "mode": mode, "round": round_number, "max_rounds": max_rounds, "open_critical": sorted(open_critical), "accepted_critical": sorted(accepted_critical), "untestable_critical": sorted(untestable_critical), "robustness_score": robustness_score, "stop_threshold": 90.0, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Gigabrain challenge ledger")
    parser.add_argument("input", help="Challenge ledger JSON"); parser.add_argument("--robustness", help="Decision Robustness report JSON"); parser.add_argument("--output", help="Optional JSON output path"); args = parser.parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8")); robustness = json.loads(Path(args.robustness).read_text(encoding="utf-8")) if args.robustness else None; report = evaluate(payload, robustness)
    except (OSError, json.JSONDecodeError) as exc:
        report = {"valid": False, "status": "INVALID", "mode": "off", "errors": [str(exc)], "warnings": [], "open_critical": [], "accepted_critical": [], "robustness_score": None}
    rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output: Path(args.output).write_text(rendered, encoding="utf-8")
    else: print(rendered, end="")
    return 0 if report["valid"] else 2


if __name__ == "__main__": raise SystemExit(main())
