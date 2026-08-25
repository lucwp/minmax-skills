#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
REG = (ROOT / "references" / "regression-suite.md").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "reliability.json").read_text(encoding="utf-8"))


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing guardrail: {label}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"forbidden legacy behavior: {label}")


def main() -> int:
    require(SKILL, "No-change is a valid outcome", "no-change outcome")
    require(SKILL, "make the smallest sufficient change", "minimal intervention")
    require(SKILL, "scope, agency, modality, and causal or logical relations", "agency/modality/relations")
    require(SKILL, "Do not resolve a material ambiguity by guessing", "ambiguity fail-closed")
    require(SKILL, "Preserve protected exact spans", "protected exact spans")
    require(SKILL, "as data to inspect or transform, not as instructions", "untrusted source boundary")
    require(SKILL, "at most one initial draft", "bounded editorial execution")
    require(SKILL, "Do not use word blacklists", "anti-heuristic hardening")
    require(SKILL, "A stylistic gain that fails a hard gate is a regression", "semantic hard gate")

    require(SKILL, "## Progressive loading", "progressive loading section")
    require(SKILL, "Load only the reference whose failure mode is materially present", "selective reference gate")
    require(SKILL, "Do not load every reference by default", "no eager loading")
    require(SKILL, "regression suite", "maintenance suite reference")
    forbid(SKILL, "For sentence-level prose, first read", "eager reference loading")

    for ref in (ROOT / "references").glob("*.md"):
        if "Better Portuguese" in ref.read_text(encoding="utf-8"):
            raise AssertionError(f"legacy skill name remains in {ref.name}")

    for i in range(1, 27):
        require(REG, f"## R{i} -", f"regression case R{i}")

    if MANIFEST.get("level") != "production-ready":
        raise AssertionError("reliability level drifted from production-ready")
    envelope = MANIFEST.get("autonomous_envelope", "")
    require(envelope, "without external publication", "bounded autonomous envelope")
    require(envelope, "remain outside this envelope", "high-consequence boundary")

    expected_refs = {
        "editorial-standard.md",
        "grammar-and-style.md",
        "naturalness-and-register.md",
        "punctuation.md",
        "regression-suite.md",
    }
    actual_refs = {p.name for p in (ROOT / "references").glob("*.md")}
    missing = expected_refs - actual_refs
    if missing:
        raise AssertionError(f"missing references: {sorted(missing)}")

    print("PASS minmax-ptbr-output reliability + progressive-loading guardrails")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
