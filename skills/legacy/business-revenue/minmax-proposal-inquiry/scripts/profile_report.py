#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def present(v):
    if v is None: return False
    if isinstance(v, str): return bool(v.strip()) and v.strip() not in {"[TO DEFINE]", "[A DEFINIR]"}
    if isinstance(v, (list, dict)): return bool(v)
    return True


def score_profile(d):
    b=d.get("business") or {}; p=d.get("positioning") or {}; offers=d.get("offers") or []; c=d.get("commercial") or {}; proof=d.get("proof") or {}; brand=d.get("brand") or {}; voice=d.get("voice") or {}; defaults=d.get("proposal_defaults") or {}
    checks=[]
    checks.append(("Business identity", all(present(b.get(k)) for k in ("name","category","one_liner","default_currency"))))
    checks.append(("Offer architecture", bool(offers) and all(present(o.get("name")) and present(o.get("business_value")) and present(o.get("deliverables")) for o in offers)))
    checks.append(("Offer boundaries and dependencies", bool(offers) and all(present(o.get("boundaries")) and present(o.get("client_dependencies")) for o in offers)))
    pricing=bool(offers) and all(present((o.get("pricing") or {}).get("model")) and present((o.get("pricing") or {}).get("currency")) for o in offers)
    checks.append(("Pricing and discount authority", pricing and present(c.get("discount_policy"))))
    checks.append(("ICP and buyer logic", present(p.get("ideal_customers")) and present(p.get("buyer_roles")) and present(p.get("core_problems"))))
    checks.append(("Proof and claim governance", present(voice.get("claim_policy")) and isinstance(proof, dict)))
    checks.append(("Brand identity and visual direction", present(brand.get("primary_color")) and present(brand.get("accent_color")) and present(brand.get("visual_style"))))
    checks.append(("Voice and terminology", present(voice.get("default_language")) and present(voice.get("tone"))))
    checks.append(("Proposal workflow/defaults", present(defaults.get("page_size")) and present(defaults.get("approval_mode")) and present(defaults.get("default_next_step"))))
    checks.append(("Commercial terms and validity", present(c.get("default_payment_terms")) and isinstance(c.get("proposal_validity_days"), int)))
    scored=[(name,2 if ok else 1,"" if ok else "Incomplete or contains unresolved values") for name,ok in checks]
    total=sum(s for _,s,_ in scored)
    readiness="configured" if total>=17 else "usable with gaps" if total>=13 else "draft" if total>=8 else "insufficient"
    return scored,total,readiness


def main():
    if len(sys.argv) not in (2,4):
        print("Usage: profile_report.py <business-profile.json> [business-profile.md profile-gaps.md]", file=sys.stderr); return 2
    profile_path=Path(sys.argv[1]); d=json.loads(profile_path.read_text(encoding="utf-8")); scored,total,readiness=score_profile(d)
    summary_path=Path(sys.argv[2]) if len(sys.argv)==4 else profile_path.with_suffix(".md")
    gaps_path=Path(sys.argv[3]) if len(sys.argv)==4 else profile_path.with_name("profile-gaps.md")
    b=d.get("business") or {}; p=d.get("positioning") or {}; offers=d.get("offers") or []; c=d.get("commercial") or {}; brand=d.get("brand") or {}; voice=d.get("voice") or {}
    lines=[f"# Business Proposal Profile — {b.get('name') or '[TO DEFINE]'}","",f"**Status:** {d.get('status','draft')}",f"**Category:** {b.get('category') or '[TO DEFINE]'}",f"**One-liner:** {b.get('one_liner') or '[TO DEFINE]'}",f"**Default currency:** {b.get('default_currency') or '[TO DEFINE]'}","","## Positioning","",f"**Value proposition:** {p.get('value_proposition') or '[TO DEFINE]'}","","## Offers",""]
    for o in offers:
        pr=o.get("pricing") or {}; lines += [f"### {o.get('name') or '[Unnamed offer]'}",f"- Type: {o.get('type') or '[TO DEFINE]'}",f"- Business value: {o.get('business_value') or '[TO DEFINE]'}",f"- Deliverables: {', '.join(o.get('deliverables') or []) or '[TO DEFINE]'}",f"- Boundaries: {', '.join(o.get('boundaries') or []) or '[TO DEFINE]'}",f"- Pricing: {pr.get('model') or '[TO DEFINE]'} · {pr.get('currency') or b.get('default_currency') or '[TO DEFINE]'} · {pr.get('unit') or '[TO DEFINE]'}",""]
    lines += ["## Commercial defaults","",f"- Payment terms: {c.get('default_payment_terms') or '[TO DEFINE]'}",f"- Validity: {c.get('proposal_validity_days') or '[TO DEFINE]'} days",f"- Discount policy: {c.get('discount_policy') or '[TO DEFINE]'}","","## Brand and voice","",f"- Logo path: {brand.get('logo_path') or '[TO DEFINE]'}",f"- Primary / accent: {brand.get('primary_color') or '[TO DEFINE]'} / {brand.get('accent_color') or '[TO DEFINE]'}",f"- Language: {voice.get('default_language') or '[TO DEFINE]'}"]
    summary_path.write_text("\n".join(lines)+"\n", encoding="utf-8")
    gap_lines=["# Proposal Profile Gaps","",f"**Score:** {total}/20",f"**Readiness:** {readiness}","","## Domain review",""]
    for name,score,note in scored: gap_lines.append(f"- **{name}: {score}/2** — Severity: {'None' if score==2 else 'High'}{' — '+note if note else ''}")
    gaps_path.write_text("\n".join(gap_lines)+"\n", encoding="utf-8")
    print(f"SCORE: {total}/20 — {readiness}"); print(f"WROTE: {summary_path}"); print(f"WROTE: {gaps_path}"); return 0


if __name__ == "__main__": raise SystemExit(main())
