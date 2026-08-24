#!/usr/bin/env python3
import argparse,hashlib,json,math
from pathlib import Path
ALLOWED_TYPES={"cover","executive","narrative","decision","scope","sequence","comparison","commercial","proof","next-step"};RELEASE={"draft","consulting","autonomous"};CLASSES={"verified_provider_fact","verified_client_fact","approved_proof","third_party","internal_estimate"};CONF={"verified","estimate","unverified"};PLACE={"[TO DEFINE]","[A DEFINIR]"}
def present(v):return False if v is None else bool(v.strip()) if isinstance(v,str) else bool(v) if isinstance(v,(list,dict)) else True
def unresolved(v):
    if isinstance(v,str):return any(x in v.upper() for x in PLACE)
    if isinstance(v,list):return any(unresolved(x) for x in v)
    if isinstance(v,dict):return any(unresolved(x) for x in v.values())
    return False
def num(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def validate(data,profile_path=None,state_path=None):
    e=[];w=[]
    if data.get("schema_version")!="1.0":e.append("schema_version must be '1.0'")
    meta=data.get("meta") or {}; mode=meta.get("release_mode") or "consulting"
    for k in ("proposal_title","client_name"):
        if not present(meta.get(k)):e.append(f"meta.{k} is required")
    if mode not in RELEASE:e.append(f"meta.release_mode must be one of {sorted(RELEASE)}");mode="consulting"
    if mode=="autonomous":
        if unresolved(data):e.append("autonomous release cannot contain unresolved [TO DEFINE]/[A DEFINIR] markers")
        if not profile_path or not state_path:e.append("autonomous release requires --profile and --state")
        else:
            try:p=json.loads(profile_path.read_text());s=json.loads(state_path.read_text())
            except Exception as exc:e.append(f"profile/state unreadable: {exc}");p={};s={}
            if p.get("status")!="configured":e.append("autonomous release requires profile.status=configured")
            if s.get("profile_status")!="configured":e.append("autonomous release requires state.profile_status=configured")
            rev=meta.get("source_profile_revision")
            if not isinstance(rev,int) or isinstance(rev,bool) or rev<=0:e.append("meta.source_profile_revision must be a positive integer in autonomous release")
            elif rev!=s.get("configuration_revision"):e.append("meta.source_profile_revision does not match configuration-state revision")
            h=hashlib.sha256(profile_path.read_bytes()).hexdigest()
            if s.get("profile_sha256")!=h:e.append("business profile hash does not match configuration state")
    ledger=data.get("evidence_ledger") or [];ev={}
    if not isinstance(ledger,list):e.append("evidence_ledger must be an array");ledger=[]
    for i,x in enumerate(ledger):
        if not isinstance(x,dict):e.append(f"evidence_ledger[{i}] must be an object");continue
        eid=x.get("id")
        if not present(eid):e.append(f"evidence_ledger[{i}].id is required");continue
        if eid in ev:e.append(f"duplicate evidence id: {eid}")
        ev[eid]=x
        if x.get("class") not in CLASSES:e.append(f"evidence_ledger[{i}].class invalid")
        if x.get("confidence") not in CONF:e.append(f"evidence_ledger[{i}].confidence invalid")
        if not present(x.get("source_ref")):e.append(f"evidence_ledger[{i}].source_ref is required")
        if mode=="autonomous" and x.get("confidence")=="unverified":e.append(f"evidence_ledger[{i}] cannot be unverified in autonomous release")
        if mode=="autonomous" and x.get("class")=="internal_estimate" and not present(x.get("display_label")):e.append(f"evidence_ledger[{i}].display_label is required for internal estimates")
    pages=data.get("pages")
    if not isinstance(pages,list) or not pages:e.append("pages must be a non-empty array");pages=[]
    commercial=nextstep=False
    for i,page in enumerate(pages):
        pre=f"pages[{i}]";ptype=page.get("type") if isinstance(page,dict) else None
        if ptype not in ALLOWED_TYPES:e.append(f"{pre}.type invalid")
        if not isinstance(page,dict):continue
        for k in ("section","title"):
            if not present(page.get(k)):e.append(f"{pre}.{k} is required")
        ids=page.get("evidence_ids") or []
        for eid in ids:
            if eid not in ev:e.append(f"{pre}.evidence_ids references unknown evidence id: {eid}")
        if mode=="autonomous" and ptype=="proof" and not ids:e.append(f"{pre} proof page requires evidence_ids in autonomous release")
        if ptype=="commercial":
            commercial=True;inv=page.get("investment") or {}
            for k in ("included_scope","assumptions","rationale","components","total"):
                if k not in inv:e.append(f"{pre}.investment.{k} is required")
            if mode=="autonomous":
                calc=inv.get("calculation") or {};status=calc.get("status")
                if status=="fixed":
                    total=calc.get("total_value");vals=[]
                    if not num(total):e.append(f"{pre}.investment.calculation.total_value must be numeric for fixed totals")
                    for j,c in enumerate(inv.get("components") or []):
                        if c.get("include_in_total",True):
                            v=c.get("amount_value")
                            if not num(v):e.append(f"{pre}.investment.components[{j}].amount_value is required for fixed autonomous totals")
                            else:vals.append(float(v))
                    if num(total) and vals and abs(sum(vals)-float(total))>0.01:e.append(f"{pre}.investment fixed component sum does not match calculation.total_value")
                elif status not in {"range","formula","variable"}:e.append(f"{pre}.investment.calculation is required in autonomous release")
        if ptype=="next-step":nextstep=True
    if mode=="autonomous":
        if not commercial:e.append("autonomous enterprise proposal requires a commercial page")
        if not nextstep:e.append("autonomous enterprise proposal requires a next-step page")
    return e,w
def main():
    ap=argparse.ArgumentParser();ap.add_argument("proposal");ap.add_argument("--profile");ap.add_argument("--state");a=ap.parse_args();data=json.loads(Path(a.proposal).read_text());e,w=validate(data,Path(a.profile) if a.profile else None,Path(a.state) if a.state else None)
    for x in w:print(f"WARN: {x}")
    for x in e:print(f"FAIL: {x}")
    print(f"RESULT: {'FAIL' if e else 'PASS'} ({len(e)} errors, {len(w)} warnings)");return 1 if e else 0
if __name__=="__main__":raise SystemExit(main())
