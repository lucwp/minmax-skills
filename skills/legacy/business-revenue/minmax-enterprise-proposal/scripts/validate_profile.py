#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ALLOWED_STATUS={"draft","configured","template"}; ALLOWED_OFFER_TYPES={"project","recurring","usage","hybrid","custom"}; ALLOWED_PRICING={"fixed","retainer","per_unit","tiered","usage","milestone","hybrid","custom"}; HEX=re.compile(r"^#[0-9A-Fa-f]{6}$")
def present(v):
    if v is None:return False
    if isinstance(v,str):return bool(v.strip())
    if isinstance(v,(list,dict)):return bool(v)
    return True
def validate(data):
    errors=[]; warnings=[]
    if data.get('schema_version')!='1.0':errors.append("schema_version must be '1.0'")
    status=data.get('status')
    if status not in ALLOWED_STATUS:errors.append(f"status must be one of {sorted(ALLOWED_STATUS)}")
    b=data.get('business') or {}
    for key in ('name','category','one_liner','default_currency'):
        if not present(b.get(key)): warnings.append(f'business.{key} is empty in template profile') if status=='template' else errors.append(f'business.{key} is required')
    if not isinstance(b.get('languages',[]),list) or not b.get('languages'):warnings.append('business.languages should contain at least one language')
    p=data.get('positioning') or {}
    for key in ('ideal_customers','core_problems','buyer_roles'):
        if not present(p.get(key)):warnings.append(f'positioning.{key} is empty; proposal specificity may suffer')
    if not present(p.get('value_proposition')):warnings.append('positioning.value_proposition is empty')
    offers=data.get('offers')
    if not isinstance(offers,list):errors.append('offers must be an array');offers=[]
    if not offers and status!='template':errors.append("at least one offer is required unless status is 'template'")
    seen=set()
    for i,o in enumerate(offers):
        prefix=f'offers[{i}]'
        if not isinstance(o,dict):errors.append(f'{prefix} must be an object');continue
        for key in ('id','name','type','business_value','deliverables','boundaries','pricing'):
            if not present(o.get(key)):errors.append(f'{prefix}.{key} is required')
        oid=o.get('id')
        if oid:
            if oid in seen:errors.append(f'duplicate offer id: {oid}')
            seen.add(oid)
            if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$',oid):errors.append(f'{prefix}.id must be a lowercase hyphen slug')
        if o.get('type') not in ALLOWED_OFFER_TYPES:errors.append(f'{prefix}.type must be one of {sorted(ALLOWED_OFFER_TYPES)}')
        pricing=o.get('pricing') or {}
        if pricing.get('model') not in ALLOWED_PRICING:errors.append(f'{prefix}.pricing.model must be one of {sorted(ALLOWED_PRICING)}')
        if not present(pricing.get('currency')):warnings.append(f'{prefix}.pricing.currency is empty')
        if pricing.get('model')!='custom' and not any(present(pricing.get(k)) for k in ('public_price','range','floor','notes')):warnings.append(f'{prefix}.pricing has no price/range/floor/notes; future proposals will require clarification')
        if not present(o.get('client_dependencies')):warnings.append(f'{prefix}.client_dependencies is empty')
    c=data.get('commercial') or {}; validity=c.get('proposal_validity_days')
    if not isinstance(validity,int) or validity<=0:errors.append('commercial.proposal_validity_days must be a positive integer')
    for key in ('default_payment_terms','discount_policy','scope_change_policy'):
        if not present(c.get(key)):warnings.append(f'commercial.{key} is empty')
    brand=data.get('brand') or {}
    for key in ('primary_color','accent_color','background_color','surface_color','text_color','muted_color'):
        v=brand.get(key)
        if not present(v):warnings.append(f'brand.{key} is empty; neutral renderer default will be used')
        elif not HEX.match(v):errors.append(f'brand.{key} must be a 6-digit hex color')
    radius=brand.get('border_radius_px')
    if radius is not None and (not isinstance(radius,int) or radius<0 or radius>80):errors.append('brand.border_radius_px must be an integer between 0 and 80')
    voice=data.get('voice') or {}
    if not present(voice.get('default_language')):warnings.append('voice.default_language is empty')
    if not present(voice.get('claim_policy')):warnings.append('voice.claim_policy is empty')
    proof=data.get('proof') or {}
    for item in proof.get('customer_logos',[]) or []:
        if item.get('permission')=='unknown':warnings.append(f"customer logo permission unknown: {item.get('name','[unnamed]')}")
    for item in proof.get('testimonials',[]) or []:
        if item.get('permission')=='unknown':warnings.append(f"testimonial permission unknown: {item.get('id','[unnamed]')}")
    return errors,warnings
def main():
    if len(sys.argv)!=2:print('Usage: validate_profile.py <business-profile.json>',file=sys.stderr);return 2
    path=Path(sys.argv[1])
    if not path.exists():print(f'FAIL: profile not found: {path}',file=sys.stderr);return 2
    try:data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:print(f'FAIL: invalid JSON: {exc}',file=sys.stderr);return 1
    errors,warnings=validate(data)
    for w in warnings:print(f'WARN: {w}')
    if errors:
        for e in errors:print(f'FAIL: {e}')
        print(f'RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)');return 1
    print(f'RESULT: PASS ({len(warnings)} warnings)');return 0
if __name__=='__main__':raise SystemExit(main())
