#!/usr/bin/env python3
import argparse,json,subprocess,sys
from pathlib import Path
LEVELS={"experimental","consulting-ready","production-ready"};REQUIRED=("source_of_truth","uncertainty_handling","fail_closed","deterministic_validation","side_effect_safety","idempotency","postcondition_verification","rollback_or_compensation","untrusted_input_boundary","concurrency_control","auditability","termination_budgets","regression_tests");STATUSES={"implemented","not_applicable"}
def active(root):
 out=[];s=root/"skills"
 for cat in sorted(s.iterdir()):
  if not cat.is_dir() or cat.name=="legacy":continue
  for skill in sorted(cat.iterdir()):
   if skill.is_dir() and (skill/"SKILL.md").exists():out.append(skill)
 return out
def safe(skill,raw):
 if not isinstance(raw,str) or not raw.strip():return None
 p=(skill/raw).resolve()
 try:p.relative_to(skill.resolve());return p
 except ValueError:return None
def validate(skill):
 e=[];w=[];m=skill/"reliability.json"
 if not m.exists():return ["missing reliability.json"],w,[]
 try:d=json.loads(m.read_text())
 except Exception as exc:return [f"invalid reliability.json: {exc}"],w,[]
 if d.get("schema_version")!="1.0":e.append("schema_version must be '1.0'")
 level=d.get("level")
 if level not in LEVELS:e.append(f"level must be one of {sorted(LEVELS)}")
 if not str(d.get("scope") or "").strip():e.append("scope is required")
 if level=="production-ready" and not str(d.get("autonomous_envelope") or "").strip():e.append("production-ready skills require autonomous_envelope")
 controls=d.get("controls") if isinstance(d.get("controls"),dict) else {}
 for k in REQUIRED:
  c=controls.get(k)
  if not isinstance(c,dict):e.append(f"controls.{k} is required");continue
  st=c.get("status")
  if st not in STATUSES:e.append(f"controls.{k}.status invalid");continue
  if st=="implemented":
   ev=c.get("evidence")
   if not isinstance(ev,list) or not ev:e.append(f"controls.{k}.evidence required");continue
   for raw in ev:
    p=safe(skill,raw)
    if p is None or not p.exists():e.append(f"controls.{k}.evidence path missing/unsafe: {raw}")
  elif not str(c.get("reason") or "").strip():e.append(f"controls.{k}.reason required when not_applicable")
 tests=d.get("tests") or [];paths=[]
 if level=="production-ready" and not tests:e.append("production-ready skills require regression tests")
 for raw in tests:
  p=safe(skill,raw)
  if p is None or not p.exists():e.append(f"test path missing/unsafe: {raw}")
  elif p.suffix!=".py":e.append(f"test must be Python: {raw}")
  else:paths.append(p)
 return e,w,paths
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--repo-root",default=".");ap.add_argument("--run-tests",action="store_true");a=ap.parse_args();root=Path(a.repo_root).resolve();skills=active(root);total=0
 if not skills:print("FAIL: no active skills found");return 1
 for skill in skills:
  e,w,tests=validate(skill);rel=skill.relative_to(root)
  if a.run_tests and not e:
   for t in tests:
    r=subprocess.run([sys.executable,str(t)],cwd=str(skill))
    if r.returncode:e.append(f"{t.relative_to(skill)} exited {r.returncode}")
  for x in e:print(f"FAIL [{rel}]: {x}")
  if not e:print(f"PASS [{rel}]")
  total+=len(e)
 print(f"RESULT: {'FAIL' if total else 'PASS'} ({len(skills)} active skills, {total} errors)");return 1 if total else 0
if __name__=="__main__":raise SystemExit(main())
