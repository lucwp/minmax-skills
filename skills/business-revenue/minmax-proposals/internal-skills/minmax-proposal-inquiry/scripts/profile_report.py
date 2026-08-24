#!/usr/bin/env python3
import json,sys
from pathlib import Path
PLACEHOLDERS={"[TO DEFINE]","[A DEFINIR]"}
CRITICAL={"Business identity","Offer architecture","Offer boundaries and dependencies","Pricing and discount authority","Proof and claim governance","Commercial terms and validity"}
def present(v):
    if v is None:return False
    if isinstance(v,str):return bool(v.strip()) and v.strip() not in PLACEHOLDERS
    if isinstance(v,(list,dict)):return bool(v)
    return True
def domain_score(values):
    values=list(values)
    if values and all(values):return 2
    if any(values):return 1
    return 0
def pricing_ready(o):
    p=o.get("pricing") or {}; policy=present(p.get("model")) and present(p.get("currency")); value=present(p.get("notes")) if p.get("model")=="custom" else any(present(p.get(k)) for k in ("public_price","range","floor","notes")); return policy and value
def score_profile(data):
    b=data.get("business") or {}; p=data.get("positioning") or {}; offers=data.get("offers") or []; c=data.get("commercial") or {}; proof=data.get("proof") or {}; brand=data.get("brand") or {}; voice=data.get("voice") or {}; d=data.get("proposal_defaults") or {}
    scores=[]
    scores.append(("Business identity",domain_score(present(b.get(k)) for k in ("name","category","one_liner","default_currency","languages"))))
    scores.append(("Offer architecture",domain_score([bool(offers),bool(offers) and all(present(o.get("name")) and present(o.get("business_value")) and present(o.get("deliverables")) for o in offers)])))
    scores.append(("Offer boundaries and dependencies",domain_score([bool(offers) and all(present(o.get("boundaries")) for o in offers),bool(offers) and all(present(o.get("client_dependencies")) for o in offers)])))
    scores.append(("Pricing and discount authority",domain_score([bool(offers) and all(pricing_ready(o) for o in offers),present(c.get("discount_policy"))])))
    scores.append(("ICP and buyer logic",domain_score(present(p.get(k)) for k in ("ideal_customers","buyer_roles","core_problems","value_proposition"))))
    scores.append(("Proof and claim governance",domain_score([present(voice.get("claim_policy")),isinstance(proof,dict)])))
    scores.append(("Brand identity and visual direction",domain_score([present(brand.get("primary_color")),present(brand.get("accent_color")),present(brand.get("visual_style"))])))
    scores.append(("Voice and terminology",domain_score([present(voice.get("default_language")),present(voice.get("tone"))])))
    scores.append(("Proposal workflow/defaults",domain_score([present(d.get("page_size")),present(d.get("approval_mode")),present(d.get("default_next_step"))])))
    scores.append(("Commercial terms and validity",domain_score([present(c.get("default_payment_terms")),isinstance(c.get("proposal_validity_days"),int) and not isinstance(c.get("proposal_validity_days"),bool) and c.get("proposal_validity_days",0)>0,present(c.get("scope_change_policy"))])))
    total=sum(s for _,s in scores); sm=dict(scores); critical=all(sm.get(n)==2 for n in CRITICAL); no_empty=all(s>0 for _,s in scores)
    readiness="configured" if total>=17 and critical and no_empty else "usable with gaps" if total>=13 and no_empty else "draft" if total>=8 else "insufficient"
    return scores,total,readiness
def main():
    if len(sys.argv) not in (2,4):print("Usage: profile_report.py <business-profile.json> [business-profile.md profile-gaps.md]",file=sys.stderr);return 2
    path=Path(sys.argv[1]); data=json.loads(path.read_text(encoding="utf-8")); scores,total,readiness=score_profile(data)
    summary=Path(sys.argv[2]) if len(sys.argv)==4 else path.with_suffix(".md"); gaps=Path(sys.argv[3]) if len(sys.argv)==4 else path.with_name("profile-gaps.md")
    b=data.get("business") or {}; summary.write_text(f"# Business Proposal Profile - {b.get('name') or '[TO DEFINE]'}\n\n**Declared status:** {data.get('status','draft')}\n**Derived readiness:** {readiness}\n**Score:** {total}/20\n",encoding="utf-8")
    lines=["# Proposal Profile Gaps","",f"**Score:** {total}/20",f"**Readiness:** {readiness}","","## Domain review",""]
    for name,score in scores:
        severity="None" if score==2 else "Critical" if name in CRITICAL and score<2 else "High" if score==0 else "Medium"; note="" if score==2 else " - incomplete, contradictory, or unresolved"; lines.append(f"- **{name}: {score}/2** - Severity: {severity}{note}")
    gaps.write_text("\n".join(lines)+"\n",encoding="utf-8"); print(f"SCORE: {total}/20 - {readiness}"); return 0
if __name__=="__main__":raise SystemExit(main())
