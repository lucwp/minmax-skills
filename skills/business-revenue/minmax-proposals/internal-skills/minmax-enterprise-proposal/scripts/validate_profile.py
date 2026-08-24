#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ALLOWED_STATUS={"draft","configured","template"}; ALLOWED_OFFER_TYPES={"project","recurring","usage","hybrid","custom"}; ALLOWED_PRICING={"fixed","retainer","per_unit","tiered","usage","milestone","hybrid","custom"}; HEX=re.compile(r"^#[0-9A-Fa-f]{6}$"); FONT=re.compile(r"^[A-Za-z0-9 _,'\".-]{1,200}$"); PLACEHOLDERS={"[TO DEFINE]","[A DEFINIR]"}
def present(v):
    if v is None:return False
    if isinstance(v,str):return bool(v.strip()) and v.strip() not in PLACEHOLDERS
    if isinstance(v,(list,dict)):return bool(v)
    return True
def safe_asset_path(v):
    if not present(v):return True
    p=Path(str(v)); return not p.is_absolute() and ".." not in p.parts
def pricing_defined(p):
    if not isinstance(p,dict):return False
    if p.get("model")=="custom":return present(p.get("notes"))
    return any(present(p.get(k)) for k in ("public_price","range","floor","notes"))
def validate(data):
    errors=[];warnings=[]
    if data.get("schema_version")!="1.0":errors.append("schema_version must be '1.0'")
    status=data.get("status"); strict=status=="configured"
    if status not in ALLOWED_STATUS:errors.append(f"status must be one of {sorted(ALLOWED_STATUS)}")
    business=data.get("business") or {}
    for k in ("name","category","one_liner","default_currency"):
        if not present(business.get(k)):(warnings if status=="template" else errors).append(f"business.{k} is required")
    if not isinstance(business.get("languages"),list) or not business.get("languages"):(errors if strict else warnings).append("business.languages must contain at least one language")
    positioning=data.get("positioning") or {}
    for k in ("ideal_customers","core_problems","buyer_roles","value_proposition"):
        if not present(positioning.get(k)):(errors if strict else warnings).append(f"positioning.{k} is required for configured profiles")
    offers=data.get("offers")
    if not isinstance(offers,list):errors.append("offers must be an array");offers=[]
    if not offers and status!="template":errors.append("at least one offer is required unless status is 'template'")
    seen=set()
    for i,o in enumerate(offers):
        p=f"offers[{i}]"
        if not isinstance(o,dict):errors.append(f"{p} must be an object");continue
        for k in ("id","name","type","business_value","deliverables","boundaries","pricing"):
            if not present(o.get(k)):errors.append(f"{p}.{k} is required")
        if strict and not present(o.get("client_dependencies")):errors.append(f"{p}.client_dependencies is required for configured profiles")
        oid=o.get("id")
        if oid:
            if oid in seen:errors.append(f"duplicate offer id: {oid}")
            seen.add(oid)
            if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$",oid):errors.append(f"{p}.id must be a lowercase hyphen slug")
        if o.get("type") not in ALLOWED_OFFER_TYPES:errors.append(f"{p}.type must be one of {sorted(ALLOWED_OFFER_TYPES)}")
        pricing=o.get("pricing") or {}
        if pricing.get("model") not in ALLOWED_PRICING:errors.append(f"{p}.pricing.model must be one of {sorted(ALLOWED_PRICING)}")
        if not present(pricing.get("currency")):(errors if strict else warnings).append(f"{p}.pricing.currency is required for configured profiles")
        if not pricing_defined(pricing):(errors if strict else warnings).append(f"{p}.pricing needs an explicit price, range, floor, or pricing note")
    commercial=data.get("commercial") or {}; validity=commercial.get("proposal_validity_days")
    if not isinstance(validity,int) or isinstance(validity,bool) or validity<=0:errors.append("commercial.proposal_validity_days must be a positive integer")
    for k in ("default_payment_terms","discount_policy","scope_change_policy"):
        if not present(commercial.get(k)):(errors if strict else warnings).append(f"commercial.{k} is required for configured profiles")
    brand=data.get("brand") or {}
    for k in ("primary_color","accent_color","background_color","surface_color","text_color","muted_color"):
        v=brand.get(k)
        if not present(v):(errors if strict else warnings).append(f"brand.{k} is required for configured profiles")
        elif not HEX.match(v):errors.append(f"brand.{k} must be a 6-digit hex color")
    for k in ("font_display","font_body"):
        v=brand.get(k)
        if present(v) and not FONT.match(v):errors.append(f"brand.{k} contains unsafe CSS font characters")
    for k in ("logo_path","cover_image_path"):
        if not safe_asset_path(brand.get(k)):errors.append(f"brand.{k} must be a safe relative path")
    if strict and not present(brand.get("visual_style")):errors.append("brand.visual_style is required for configured profiles")
    voice=data.get("voice") or {}
    for k in ("default_language","tone","claim_policy"):
        if not present(voice.get(k)):(errors if strict else warnings).append(f"voice.{k} is required for configured profiles")
    defaults=data.get("proposal_defaults") or {}
    for k in ("page_size","approval_mode","default_next_step"):
        if not present(defaults.get(k)):(errors if strict else warnings).append(f"proposal_defaults.{k} is required for configured profiles")
    return errors,warnings
def main():
    if len(sys.argv)!=2:print("Usage: validate_profile.py <business-profile.json>",file=sys.stderr);return 2
    path=Path(sys.argv[1])
    try:data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:print(f"FAIL: invalid JSON: {exc}");return 1
    errors,warnings=validate(data)
    for w in warnings:print(f"WARN: {w}")
    if errors:
        for e in errors:print(f"FAIL: {e}")
        print(f"RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)");return 1
    print(f"RESULT: PASS ({len(warnings)} warnings)");return 0
if __name__=="__main__":raise SystemExit(main())
