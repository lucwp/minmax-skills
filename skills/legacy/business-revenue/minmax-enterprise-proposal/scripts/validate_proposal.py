#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ALLOWED_TYPES = {"cover", "executive", "narrative", "decision", "scope", "sequence", "comparison", "commercial", "proof", "next-step"}

def present(value):
    if value is None: return False
    if isinstance(value, str): return bool(value.strip())
    if isinstance(value, (list, dict)): return bool(value)
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_proposal.py <proposal.json>", file=sys.stderr); return 2
    path = Path(sys.argv[1])
    try: data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: print(f"FAIL: invalid JSON: {exc}"); return 1
    errors=[]; warnings=[]
    if data.get("schema_version") != "1.0": errors.append("schema_version must be '1.0'")
    meta=data.get("meta") or {}
    for key in ("proposal_title","client_name"):
        if not present(meta.get(key)): errors.append(f"meta.{key} is required")
    pages=data.get("pages")
    if not isinstance(pages,list) or not pages: errors.append("pages must be a non-empty array"); pages=[]
    has_commercial=False; has_next=False
    for idx,page in enumerate(pages):
        p=f"pages[{idx}]"
        if not isinstance(page,dict): errors.append(f"{p} must be an object"); continue
        ptype=page.get("type")
        if ptype not in ALLOWED_TYPES: errors.append(f"{p}.type must be one of {sorted(ALLOWED_TYPES)}")
        for key in ("section","title"):
            if not present(page.get(key)): errors.append(f"{p}.{key} is required")
        if ptype == "commercial":
            has_commercial=True; inv=page.get("investment") or {}
            for key in ("included_scope","assumptions","rationale","components","total"):
                if key not in inv: errors.append(f"{p}.investment.{key} is required")
        if ptype == "next-step":
            has_next=True
            if not present(page.get("next_step")): errors.append(f"{p}.next_step is required")
    if not has_commercial: warnings.append("proposal has no commercial page")
    if not has_next: warnings.append("proposal has no next-step page")
    for w in warnings: print(f"WARN: {w}")
    if errors:
        for e in errors: print(f"FAIL: {e}")
        print(f"RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)"); return 1
    print(f"RESULT: PASS ({len(warnings)} warnings)"); return 0

if __name__ == "__main__": raise SystemExit(main())
