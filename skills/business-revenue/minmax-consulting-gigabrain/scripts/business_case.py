#!/usr/bin/env python3
"""Deterministic scenario business-case calculator with strict input validation."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


class BusinessCaseError(ValueError):
    pass


def _number(value: Any, context: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool):
        raise BusinessCaseError(f"{context} must be numeric")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise BusinessCaseError(f"{context} must be numeric") from exc
    if not math.isfinite(out):
        raise BusinessCaseError(f"{context} must be finite")
    if minimum is not None and out < minimum:
        raise BusinessCaseError(f"{context} must be >= {minimum}")
    return out


def npv(flows: list[float], rate: float) -> float:
    if rate <= -1.0:
        raise BusinessCaseError("discount_rate must be greater than -1.0")
    return sum(cf / ((1.0 + rate) ** t) for t, cf in enumerate(flows))


def _sign_changes(flows: list[float]) -> int:
    signs = [1 if x > 0 else -1 for x in flows if x != 0]
    return sum(1 for a, b in zip(signs, signs[1:]) if a != b)


def irr(flows: list[float], lo: float = -0.99, hi: float = 10.0) -> float | None:
    if _sign_changes(flows) != 1:
        return None
    def f(rate: float) -> float:
        return sum(cf / ((1.0 + rate) ** t) for t, cf in enumerate(flows))
    f_lo, f_hi = f(lo), f(hi)
    if f_lo == 0:
        return lo
    if f_hi == 0:
        return hi
    if f_lo * f_hi > 0:
        return None
    for _ in range(250):
        mid = (lo + hi) / 2.0
        f_mid = f(mid)
        if abs(f_mid) < 1e-10:
            return mid
        if f_lo * f_mid <= 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2.0


def payback(flows: list[float]) -> float | None:
    cumulative = 0.0
    for t, cf in enumerate(flows):
        before = cumulative
        cumulative += cf
        if cumulative >= 0:
            if t == 0:
                return 0.0
            if cf <= 0:
                return float(t)
            return (t - 1) + (-before / cf)
    return None


def scenario(cfg: dict[str, Any], name: str, raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise BusinessCaseError(f"scenario {name!r} must be an object")
    initial = _number(raw.get("initial_investment", cfg.get("initial_investment", 0)), f"{name}.initial_investment", minimum=0.0)
    rate = _number(raw.get("discount_rate", cfg.get("discount_rate", 0.1)), f"{name}.discount_rate")
    if rate <= -1.0:
        raise BusinessCaseError(f"{name}.discount_rate must be greater than -1.0")
    years_raw = raw.get("years")
    if not isinstance(years_raw, list) or not years_raw:
        raise BusinessCaseError(f"{name}.years must be a non-empty list")
    flows = [-initial]
    years: list[dict[str, float | int]] = []
    warnings: list[str] = []
    for idx, year in enumerate(years_raw, start=1):
        if not isinstance(year, dict):
            raise BusinessCaseError(f"{name}.years[{idx - 1}] must be an object")
        revenue = _number(year.get("revenue", 0), f"{name}.years[{idx - 1}].revenue")
        cogs = _number(year.get("cogs", 0), f"{name}.years[{idx - 1}].cogs")
        opex = _number(year.get("opex", 0), f"{name}.years[{idx - 1}].opex")
        capex = _number(year.get("capex", 0), f"{name}.years[{idx - 1}].capex")
        working_capital = _number(year.get("working_capital_change", 0), f"{name}.years[{idx - 1}].working_capital_change")
        cash_flow = revenue - cogs - opex - capex - working_capital
        flows.append(cash_flow)
        years.append({"year": idx, "revenue": revenue, "cash_flow": cash_flow})
        if revenue < 0:
            warnings.append(f"year {idx}: negative revenue; verify sign convention")
        if any(x < 0 for x in (cogs, opex, capex)):
            warnings.append(f"year {idx}: negative cost/capex input; verify sign convention")
    changes = _sign_changes(flows)
    if changes > 1:
        warnings.append("nonconventional cash flows: IRR suppressed because multiple roots may exist")
    return {"cash_flows": flows, "years": years, "discount_rate": rate, "npv": npv(flows, rate), "irr": irr(flows), "payback_years": payback(flows), "warnings": warnings}


def calculate(cfg: Any) -> dict[str, Any]:
    if not isinstance(cfg, dict):
        raise BusinessCaseError("business-case config must be an object")
    if "discount_rate" in cfg:
        base_rate = _number(cfg["discount_rate"], "discount_rate")
        if base_rate <= -1.0:
            raise BusinessCaseError("discount_rate must be greater than -1.0")
    if "initial_investment" in cfg:
        _number(cfg["initial_investment"], "initial_investment", minimum=0.0)
    scenarios = cfg.get("scenarios")
    if not isinstance(scenarios, dict) or not scenarios:
        raise BusinessCaseError("scenarios must be a non-empty object")
    out: dict[str, Any] = {"valid": True, "scenarios": {}, "warnings": []}
    for name, raw in scenarios.items():
        if not isinstance(name, str) or not name.strip():
            raise BusinessCaseError("scenario names must be non-empty strings")
        out["scenarios"][name] = scenario(cfg, name, raw)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate a validated Gigabrain business case")
    parser.add_argument("config")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
        result = calculate(cfg)
        exit_code = 0
    except (OSError, json.JSONDecodeError, BusinessCaseError) as exc:
        result = {"valid": False, "error": str(exc)}
        exit_code = 2
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
