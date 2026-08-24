#!/usr/bin/env python3
import json,sys
from pathlib import Path
PLACEHOLDERS={"[TO DEFINE]","[A DEFINIR]"}; CRITICAL={"Business identity","Offer architecture","Offer boundaries and dependencies","Pricing and discount authority","Proof and claim governance","Commercial terms and validity"}
def present(v):
    if v is None:return False
    if isinstance(v,str):return bool(v.strip()) and v.strip() not in PLACEHOLDERS
    if isinstance(v,(list,dict)):return bool(v)
    return True
def domain_score(values):
    values=list(values); return 2 if values and all(values) else 1 if any(values) else 0
def pricing_ready(o):
    p=o.get("pricing") or {}; policy=present(p.get("model")) and present(p.get("currency")); value=present(p.get("notes")) if p.get("model")=="custom" else any(present(p.get(k)) for k in ("public_price","range","floor","notes")); return policy and value
def score_profile(data):
    b=data.get("business") or {};p=data.get("positioning") or {};offers=data.get("offers") or [];c=data.get("commercial") or {};proof=data.get("proof") or {};brand=data.get("brand") or {};voice=data.get("voice") or {};d=data.get("proposal_defaults") or {}
    scores=[("Business identity",domain_score(present(b.get(k)) for k in ("name","category","one_liner","default_currency","languages"))),("Offer architecture",domain_score([bool(offers),bool(offers) and all(present(o.get("name")) and present(o.get("business_value")) and present(o.get("deliverables")) for o in offers)])),("Offer boundaries and dependencies",domain_score([bool(offers) and all(present(o.get("boundaries")) for o in offers),bool(offers) and all(present(o.get("client_dependencies")) for o in offers)])),("Pricing and discount authority",domain_score([bool(offers) and all(pricing_ready(o) for o in offers),present(c.get("discount_policy"))])),("ICP and buyer logic",domain_score(present(p.get(k)) for k in ("ideal_customers","buyer_roles","core_problems","value_proposition"))),("Proof and claim governance",domain_score([present(voice.get("claim_policy")),isinstance(proof,dict)])),("Brand identity and visual direction",domain_score([present(brand.get("primary_color")),present(brand.get("accent_color")),present(brand.get("visual_style"))])),("Voice and terminology",domain_score([present(voice.get("default_language")),present(voice.get("tone"))])),("Proposal workflow/defaults",domain_score([present(d.get("page_size")),present(d.get("approval_mode")),present(d.get("default_next_step"))])),("Commercial terms and validity",domain_score([present(c.get("default_payment_terms")),isinstance(c.get("proposal_validity_days"),int) and not isinstance(c.get("proposal_validity_days"),bool) and c.get("proposal_validity_days",0)>0,present(c.get("scope_change_policy"))]))]
    total=sum(s for _,s in scores);m=dict(scores);critical=all(m.get(n)==2 for n in CRITICAL);nozero=all(s>0 for _,s in scores);readiness="configured" if total>=17 and critical and nozero else "usable with gaps" if total>=13 and nozero else "draft" if total>=8 else "insufficient";return scores,total,readiness
def main():
    if len(sys.argv)<2:return 2
    data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"));scores,total,readiness=score_profile(data);print(f"SCORE: {total}/20 - {readiness}");return 0
if __name__=="__main__":raise SystemExit(main())
