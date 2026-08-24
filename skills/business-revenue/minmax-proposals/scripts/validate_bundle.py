#!/usr/bin/env python3
import hashlib,json,subprocess,sys
from pathlib import Path
def fail(m):print(f"FAIL: {m}");raise SystemExit(1)
def main():
 root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve();required=[root/"SKILL.md",root/"reliability.json",root/"internal-skills/minmax-proposal-inquiry/INSTRUCTIONS.md",root/"internal-skills/minmax-enterprise-proposal/INSTRUCTIONS.md",root/"internal-skills/minmax-enterprise-proposal/references/business-profile.json",root/"internal-skills/minmax-enterprise-proposal/references/configuration-state.json"]
 for p in required:
  if not p.exists():fail(f"missing required file: {p.relative_to(root)}")
 if [p for p in root.rglob("SKILL.md") if p.is_file()] != [root/"SKILL.md"]:fail("bundle must contain exactly one public SKILL.md at root")
 pp=required[-2];sp=required[-1]
 try:profile=json.loads(pp.read_text());state=json.loads(sp.read_text())
 except Exception as exc:fail(f"invalid JSON configuration: {exc}")
 if state.get("profile_status")!=profile.get("status"):fail("configuration-state profile_status does not match business-profile status")
 if profile.get("status")!="template":
  h=hashlib.sha256(pp.read_bytes()).hexdigest()
  if state.get("profile_sha256")!=h:fail("configuration-state profile_sha256 does not match business-profile.json")
 validator=root/"internal-skills/minmax-enterprise-proposal/scripts/validate_profile.py";proc=subprocess.run([sys.executable,str(validator),str(pp)])
 if proc.returncode:fail("compiled enterprise profile validation failed")
 print("PASS: single-package MinMax proposal bundle is structurally and configuration-valid");return 0
if __name__=="__main__":raise SystemExit(main())
