#!/usr/bin/env python3
"""Aggregate benchmark scores and enforce the Gigabrain release target."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def percentile_nearest_rank(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    rank = max(1, math.ceil(pct * len(ordered)))
    return ordered[rank - 1]


def evaluate(payload: Any) -> dict[str, Any]:
    errors: list[str] = []
    failures: list[str] = []
    if not isinstance(payload, dict):
        return {"valid": False, "status": "FAIL", "errors": ["benchmark payload must be an object"]}

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return {"valid": False, "status": "FAIL", "errors": ["cases must be a non-empty list"]}

    target_mean = payload.get("target_mean", 95)
    target_min = payload.get("target_min", 90)
    target_p10 = payload.get("target_p10", 90)
    min_cases = payload.get("min_cases", 20)
    certification_mode = payload.get("certification_mode", True)
    if not isinstance(certification_mode, bool):
        errors.append("certification_mode must be boolean")
        certification_mode = True
    for key, value in (("target_mean", target_mean), ("target_min", target_min), ("target_p10", target_p10)):
        if not _finite(value) or float(value) < 0 or float(value) > 100:
            errors.append(f"{key} must be a finite number between 0 and 100")
    if not isinstance(min_cases, int) or isinstance(min_cases, bool) or min_cases < 1:
        errors.append("min_cases must be an integer >= 1")
        min_cases = 20

    ids: set[str] = set()
    scores: list[float] = []
    one_shot_scores: list[float] = []
    hard_gate_misses = 0
    false_robust = 0
    wrong_decisions = 0

    for i, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"cases[{i}] must be an object")
            continue
        cid = case.get("case_id")
        if not isinstance(cid, str) or not cid.strip():
            errors.append(f"cases[{i}].case_id must be non-empty")
            cid = f"ROW-{i}"
        if cid in ids:
            errors.append(f"duplicate case_id: {cid}")
        ids.add(cid)
        score = case.get("score")
        if not _finite(score) or float(score) < 0 or float(score) > 100:
            errors.append(f"{cid}: score must be between 0 and 100")
            continue
        score = float(score)
        scores.append(score)
        if case.get("one_shot", True) is True:
            one_shot_scores.append(score)
        elif case.get("one_shot") is not False:
            errors.append(f"{cid}: one_shot must be boolean")
        for field in ("hard_gate_miss", "false_robust", "wrong_decision"):
            if not isinstance(case.get(field, False), bool):
                errors.append(f"{cid}: {field} must be boolean")
        if certification_mode:
            if case.get("blind_scored") is not True:
                errors.append(f"{cid}: certified benchmark requires blind_scored=true")
            if case.get("independent_reviewer") is not True:
                errors.append(f"{cid}: certified benchmark requires independent_reviewer=true")
        hard_gate_misses += int(case.get("hard_gate_miss", False) is True)
        false_robust += int(case.get("false_robust", False) is True)
        wrong_decisions += int(case.get("wrong_decision", False) is True)

    if errors:
        return {"valid": False, "status": "FAIL", "errors": errors}

    mean = sum(scores) / len(scores)
    minimum = min(one_shot_scores) if one_shot_scores else 0.0
    p10 = percentile_nearest_rank(one_shot_scores, 0.10) if one_shot_scores else 0.0

    if len(scores) < min_cases:
        failures.append(f"benchmark has {len(scores)} cases; requires at least {min_cases}")
    if mean + 1e-9 < float(target_mean):
        failures.append(f"mean score {mean:.2f} below target {float(target_mean):.2f}")
    if minimum + 1e-9 < float(target_min):
        failures.append(f"minimum one-shot score {minimum:.2f} below target {float(target_min):.2f}")
    if p10 + 1e-9 < float(target_p10):
        failures.append(f"p10 one-shot score {p10:.2f} below target {float(target_p10):.2f}")
    if hard_gate_misses:
        failures.append(f"{hard_gate_misses} hard-gate misses")
    if false_robust:
        failures.append(f"{false_robust} false-ROBUST outcomes")
    if wrong_decisions:
        failures.append(f"{wrong_decisions} wrong decision-class outcomes")

    return {
        "valid": True,
        "status": "PASS" if not failures else "FAIL",
        "cases": len(scores),
        "mean": round(mean, 2),
        "minimum_one_shot": round(minimum, 2),
        "p10_one_shot": round(p10, 2),
        "hard_gate_misses": hard_gate_misses,
        "false_robust": false_robust,
        "wrong_decisions": wrong_decisions,
        "certification_mode": certification_mode,
        "targets": {"mean": float(target_mean), "minimum_one_shot": float(target_min), "p10_one_shot": float(target_p10), "min_cases": min_cases},
        "failures": failures,
        "errors": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Gigabrain benchmark release gate")
    parser.add_argument("input")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        report = evaluate(json.loads(Path(args.input).read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        report = {"valid": False, "status": "FAIL", "errors": [str(exc)]}
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if report.get("valid") and report.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
