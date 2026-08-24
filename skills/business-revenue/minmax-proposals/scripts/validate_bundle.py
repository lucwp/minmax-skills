#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    required = [
        root / "SKILL.md",
        root / "internal-skills" / "minmax-proposal-inquiry" / "INSTRUCTIONS.md",
        root / "internal-skills" / "minmax-enterprise-proposal" / "INSTRUCTIONS.md",
        root / "internal-skills" / "minmax-enterprise-proposal" / "references" / "business-profile.json",
        root / "internal-skills" / "minmax-enterprise-proposal" / "references" / "configuration-state.json",
    ]
    for path in required:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(root)}")

    public_entrypoints = [p for p in root.rglob("SKILL.md") if p.is_file()]
    if public_entrypoints != [root / "SKILL.md"]:
        fail("bundle must contain exactly one public SKILL.md at root")

    state_path = root / "internal-skills" / "minmax-enterprise-proposal" / "references" / "configuration-state.json"
    profile_path = root / "internal-skills" / "minmax-enterprise-proposal" / "references" / "business-profile.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON configuration: {exc}")

    if state.get("profile_status") != profile.get("status"):
        fail("configuration-state profile_status does not match business-profile status")
    if state.get("schema_version") != "1.0" or profile.get("schema_version") != "1.0":
        fail("unsupported configuration schema_version")

    print("PASS: single-package MinMax proposal bundle is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
