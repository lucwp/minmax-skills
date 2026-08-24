#!/usr/bin/env python3
import argparse,hashlib,json,math
from pathlib import Path
ALLOWED_TYPES={"cover","executive","narrative","decision","scope","sequence","comparison","commercial","proof","next-step"};RELEASE_MODES={"draft","consulting","autonomous"};EVIDENCE_CLASSES={"verified_provider_fact","verified_client_fact","approved_proof","third_party","internal_estimate"};PLACEHOLDERS={"[TO DEFINE]","[A DEFINIR]"}
def present(v):return v is not None and (bool(v.strip()) if isinstance(v,str) else bool(v) if isinstance(v,(list,dict)) else True)
def unresolved(v):
    if isinstance(v,str):return any(m in v.upper() for m in PLACEHOLDERS)
    if isinstance(v,list):return any(unresolved(x) for x in v)
    if isinstance(v,dict):return any(unresolved(x) for x in v.values())
    return False
def num(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def validate(data,profile_path=None,state_path=None):
    e=[];w=[]
    if data.get("schema_version")!="1.0":e.append("schema_version must be '1.0'")
    meta=data.get("meta") or {};mode=meta.get("release_mode") or "consulting"
    for k in ("proposal_title","client_name"):
        if not present(meta.get(k)):e.append(f"meta.{k} is required")
    if mode not in RELEASE_MODES:e.append(f"meta.release_mode must be one of {sorted(RELEASE_MODES)}");mode="consulting"
    if mode=="autonomous":
        if unresolved(data):e.append("autonomous release cannot contain unresolved [TO DEFINE]/[A DEFINIR] markers")
        if not profile_path or not state_path:e.append("autonomous release requires --profile and --state")
        else:
            p=json.loads(profile_path.read_text(encoding="utf-8"));s=json.loads(state_path.read_text(encoding="utf-8"));rev=meta.get("source_profile_revision")
            if p.get("status")!="configured" or s.get("profile_status")!="configured":e.append("autonomous release requires configured profile/state")
            if not isinstance(rev,int) or isinstance(rev,bool) or rev!=s.get("configuration_revision"):e.append("meta.source_profile_revision does not match configuration-state revision")
            h=hashlib.sha256(profile_path.read_bytes()).hexdigest()
            if not s.get("profile_sha256") or s.get("profile_sha256")!=h:e.append("business profile hash does not match configuration state")
    ledger=data.get("evidence_ledger") or [];ev={}
    if not isinstance(ledger,list):e.append("evidence_ledger must be an array");ledger=[]
    for i,x in enumerate(ledger):
        q=f"evidence_ledger[{i}]";eid=x.get("id") if isinstance(x,dict) else None
        if not eid:e.append(f"{q}.id is required");continue
        ev[eid]=x
        if x.get("class") not in EVIDENCE_CLASSES:e.append(f"{q}.class is invalid")
        if x.get("confidence") not in {"verified","estimate","unverified"}:e.append(f"{q}.confidence is invalid")
        if not present(x.get("source_ref")) or not present(x.get("claim")):e.append(f"{q} requires source_ref and claim")
        if mode=="autonomous" and x.get("confidence")=="unverified":e.append(f"{q} cannot be unverified in autonomous release")
        if mode=="autonomous" and x.get("class")=="internal_estimate" and not present(x.get("display_label")):e.append(f"{q}.display_label is required for internal estimates")
    pages=data.get("pages")
    if not isinstance(pages,list) or not pages:e.append("pages must be a non-empty array");pages=[]
    commercial=False;nextstep=False
    for i,p in enumerate(pages):
        q=f"pages[{i}]";t=p.get("type") if isinstance(p,dict) else None
        if t not in ALLOWED_TYPES:e.append(f"{q}.type is invalid")
        for k in ("section","title"):
            if not present(p.get(k)):e.append(f"{q}.{k} is required")
        ids=p.get("evidence_ids") or []
        if not isinstance(ids,list):e.append(f"{q}.evidence_ids must be an array");ids=[]
        for eid in ids:
            if eid not in ev:e.append(f"{q}.evidence_ids references unknown evidence id: {eid}")
        if mode=="autonomous" and t=="proof" and not ids:e.append(f"{q} proof page requires evidence_ids in autonomous release")
        if t=="commercial":
            commercial=True;inv=p.get("investment") or {}
            for k in ("included_scope","assumptions","rationale","components","total"):
                if k not in inv:e.append(f"{q}.investment.{k} is required")
            if mode=="autonomous":
                c=inv.get("calculation")
                if not isinstance(c,dict):e.append(f"{q}.investment.calculation is required in autonomous release")
                else:
                    status=c.get("status")
                    if status=="fixed":
                        total=c.get("total_value")
                        if not num(total):e.append(f"{q}.investment.calculation.total_value must be numeric")
                        vals=[]
                        for j,x in enumerate(inv.get("components") or []):
                            if x.get("include_in_total",True):
                                v=x.get("amount_value")
                                if not num(v):e.append(f"{q}.investment.components[{j}].amount_value is required")
                                else:vals.append(float(v))
                        if vals and num(total) and abs(sum(vals)-float(total))>0.01:e.append(f"{q}.investment fixed component sum does not match calculation.total_value")
                    elif status=="range":
                        if not num(c.get("range_min")) or not num(c.get("range_max")) or c.get("range_min")>c.get("range_max"):e.append(f"{q}.investment range calculation is invalid")
                    elif status=="formula":
                        if not present(c.get("formula")) or not isinstance(c.get("inputs"),dict) or not c.get("inputs") or unresolved(c.get("inputs")):e.append(f"{q}.investment formula calculation is unresolved")
                    elif status=="variable":
                        if not present(c.get("explanation")):e.append(f"{q}.investment variable calculation needs explanation")
                    else:e.append(f"{q}.investment.calculation.status is invalid")
        if t=="next-step":nextstep=True
    if mode=="autonomous":
        if not commercial:e.append("autonomous enterprise proposal requires a commercial page")
        if not nextstep:e.append("autonomous enterprise proposal requires a next-step page")
    else:
        if not commercial:w.append("proposal has no commercial page")
        if not nextstep:w.append("proposal has no next-step page")
    return e,w
def main():
    ap=argparse.ArgumentParser();ap.add_argument("proposal");ap.add_argument("--profile");ap.add_argument("--state");a=ap.parse_args();data=json.loads(Path(a.proposal).read_text(encoding="utf-8"));e,w=validate(data,Path(a.profile).resolve() if a.profile else None,Path(a.state).resolve() if a.state else None)
    for x in w:print(f"WARN: {x}")
    if e:
        for x in e:print(f"FAIL: {x}")
        print(f"RESULT: FAIL ({len(e)} errors, {len(w)} warnings)");return 1
    print(f"RESULT: PASS ({len(w)} warnings)");return 0
if __name__=="__main__":raise SystemExit(main())
