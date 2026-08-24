#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"\{\{|\}\}|\[CONFIGURE WITH|<TODO|TODO:", re.I)


def main():
    if len(sys.argv) != 3:
        print("Usage: preflight_proposal.py <proposal.html> <proposal.json>", file=sys.stderr)
        return 2
    html_path = Path(sys.argv[1]); json_path = Path(sys.argv[2]); errors = []; warnings = []
    if not html_path.exists() or html_path.stat().st_size < 1000:
        errors.append("HTML file missing or unexpectedly small"); text = ""
    else:
        text = html_path.read_text(encoding="utf-8")
    try:
        proposal = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"proposal JSON unreadable: {exc}"); proposal = {}
    if text and PLACEHOLDER.search(text): errors.append("unresolved template placeholder found in HTML")
    pages = re.findall(r'<section class="page(?: [^"]*)?">', text)
    expected = len(proposal.get("pages") or [])
    if expected and len(pages) != expected: errors.append(f"rendered page count mismatch: html={len(pages)} json={expected}")
    if "[TO DEFINE]" in text: warnings.append("HTML contains [TO DEFINE]; acceptable only if intentionally unresolved")
    if "data:" not in text: warnings.append("no embedded image assets found; acceptable for text-only brand configuration")
    if re.search(r"RECOMMENDED.{0,120}Recommended", text, flags=re.I | re.S): warnings.append("possible repeated recommendation label; run content consistency pass")
    for w in warnings: print(f"WARN: {w}")
    if errors:
        for e in errors: print(f"FAIL: {e}")
        print(f"RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)"); return 1
    print(f"RESULT: PASS ({len(warnings)} warnings)"); return 0


if __name__ == "__main__": raise SystemExit(main())
