#!/usr/bin/env python3
import argparse,json,subprocess,sys
from pathlib import Path
LEVELS={"experimental","consulting-ready","production-ready"};REQUIRED=("source_of_truth","uncertainty_handling","fail_closed","deterministic_validation","side_effect_safety","idempotency","postcondition_verification","rollback_or_compensation","untrusted_input_boundary","concurrency_control","auditability","termination_budgets","regression_tests");STATUSES={"implemented","not_applicable"}
def skills(root):
 out=[]
 for c in sorted((root/"skills").iterdir()):
  if not c.is_dir() or c.name=="legacy":continue
  for s in sorted(c.iterdir()):
   if s.is_dir() and (s/"SKILL.md").exists():out.append(s)
 return out
def safe(skill,raw):
 try:p=(skill/raw).resolve();p.relative_to(skill.resolve());return p
 except:return None
def validate(skill):
 e=[];w=[];mp=skill/"reliability.json"
 if not mp.exists():return ["missing reliability.json"],w,[]
 try:d=json.loads(mp.read_text(encoding="utf-8"))
 except Exception as x:return [f"invalid reliability.json: {x}"],w,[]
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
  if st not in STATUSES:e.append(f"controls.{k}.status is invalid");continue
  if st=="implemented":
   evidence=c.get("evidence")
   if not isinstance(evidence,list) or not evidence:e.append(f"controls.{k}.evidence is required");continue
   for raw in evidence:
    p=safe(skill,raw)
    if p is None or not p.exists():e.append(f"controls.{k}.evidence path does not exist: {raw}")
  elif not str(c.get("reason") or "").strip():e.append(f"controls.{k}.reason is required when not_applicable")
 tests=d.get("tests") or [];paths=[]
 if level=="production-ready" and not tests:e.append("production-ready skills require regression tests")
 for raw in tests:
  p=safe(skill,raw)
  if p is None or not p.exists():e.append(f"test path does not exist: {raw}")
  elif p.suffix!=".py":e.append(f"test must be Python: {raw}")
  else:paths.append(p)
 return e,w,paths
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--repo-root",default=".");ap.add_argument("--run-tests",action="store_true");a=ap.parse_args();root=Path(a.repo_root).resolve();ss=skills(root);total=0;warn=0
 for s in ss:
  e,w,t=validate(s)
  if a.run_tests and not e:
   for test in t:
    p=subprocess.run([sys.executable,str(test)],cwd=str(s),text=True,capture_output=True);print(p.stdout.rstrip()) if p.stdout else None
    if p.returncode:e.append(f"{test.relative_to(s)} exited {p.returncode}")
  for x in w:print(f"WARN [{s.relative_to(root)}]: {x}")
  for x in e:print(f"FAIL [{s.relative_to(root)}]: {x}")
  if not e:print(f"PASS [{s.relative_to(root)}]")
  total+=len(e);warn+=len(w)
 if total:print(f"RESULT: FAIL ({total} errors, {warn} warnings)");return 1
 print(f"RESULT: PASS ({len(ss)} active skills, {warn} warnings)");return 0
if __name__=="__main__":raise SystemExit(main())
