#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ALLOWED_STATUS={"draft","configured","template"}; ALLOWED_OFFER_TYPES={"project","recurring","usage","hybrid","custom"}; ALLOWED_PRICING={"fixed","retainer","per_unit","tiered","usage","milestone","hybrid","custom"}; HEX=re.compile(r"^#[0-9A-Fa-f]{6}$")
def present(v): return False if v is None else bool(v.strip()) if isinstance(v,str) else bool(v) if isinstance(v,(list,dict)) else True
def validate(data):
    errors=[]; warnings=[]
    if data.get("schema_version")!="1.0": errors.append("schema_version must be '1.0'")
    status=data.get("status")
    if status not in ALLOWED_STATUS: errors.append(f"status must be one of {sorted(ALLOWED_STATUS)}")
    business=data.get("business") or {}
    for key in ("name","category","one_liner","default_currency"):
        if not present(business.get(key)): warnings.append(f"business.{key} is empty in template profile") if status=="template" else errors.append(f"business.{key} is required")
    if not business.get("languages"): warnings.append("business.languages should contain at least one language")
    positioning=data.get("positioning") or {}
    for key in ("ideal_customers","core_problems","buyer_roles"):
        if not present(positioning.get(key)): warnings.append(f"positioning.{key} is empty; proposal specificity may suffer")
    offers=data.get("offers")
    if not isinstance(offers,list): errors.append("offers must be an array"); offers=[]
    if not offers and status!="template": errors.append("at least one offer is required unless status is 'template'")
    seen=set()
    for i,o in enumerate(offers):
        p=f"offers[{i}]"
        for key in ("id","name","type","business_value","deliverables","boundaries","pricing"):
            if not present(o.get(key)): errors.append(f"{p}.{key} is required")
        oid=o.get("id")
        if oid in seen: errors.append(f"duplicate offer id: {oid}")
        if oid: seen.add(oid)
        if o.get("type") not in ALLOWED_OFFER_TYPES: errors.append(f"{p}.type must be one of {sorted(ALLOWED_OFFER_TYPES)}")
        pricing=o.get("pricing") or {}
        if pricing.get("model") not in ALLOWED_PRICING: errors.append(f"{p}.pricing.model must be one of {sorted(ALLOWED_PRICING)}")
    commercial=data.get("commercial") or {}
    if not isinstance(commercial.get("proposal_validity_days"),int) or commercial.get("proposal_validity_days",0)<=0: errors.append("commercial.proposal_validity_days must be a positive integer")
    brand=data.get("brand") or {}
    for key in ("primary_color","accent_color","background_color","surface_color","text_color","muted_color"):
        v=brand.get(key)
        if present(v) and not HEX.match(v): errors.append(f"brand.{key} must be a 6-digit hex color")
    return errors,warnings

def main():
    if len(sys.argv)!=2: print("Usage: validate_profile.py <business-profile.json>",file=sys.stderr); return 2
    path=Path(sys.argv[1])
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: print(f"FAIL: invalid JSON: {exc}",file=sys.stderr); return 1
    errors,warnings=validate(data)
    for w in warnings: print(f"WARN: {w}")
    if errors:
        for e in errors: print(f"FAIL: {e}")
        print(f"RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)"); return 1
    print(f"RESULT: PASS ({len(warnings)} warnings)"); return 0
if __name__=="__main__": raise SystemExit(main())
