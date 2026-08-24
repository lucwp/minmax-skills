#!/usr/bin/env python3
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def copy_assets(src: Path | None, dest: Path):
    copied=[]
    if not src or not src.exists(): return copied
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.is_file():
            target=dest/item.name; shutil.copy2(item,target); copied.append(item.name)
    return copied


def normalize_asset_paths(profile: dict, copied: list[str]):
    brand=profile.setdefault("brand", {})
    for key in ("logo_path","cover_image_path"):
        raw=brand.get(key) or ""; name=Path(raw).name if raw else ""
        if name and name in copied: brand[key]=f"assets/brand/{name}"


def write_state(target: Path, profile: dict, copied: list[str], mode: str):
    now=datetime.now(timezone.utc).isoformat(); state_path=target/"references"/"configuration-state.json"; previous_revision=0
    if state_path.exists():
        try: previous_revision=int(load_json(state_path).get("configuration_revision",0))
        except Exception: previous_revision=0
    revision=previous_revision+1; business_name=(profile.get("business") or {}).get("name") or "[TO DEFINE]"
    state={"schema_version":"1.0","configuration_revision":revision,"configured_at":now,"profile_status":profile.get("status","draft"),"business_name":business_name,"update_mode":mode,"brand_assets":copied}
    state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    cfg=["# Runtime configuration","",f"Business: {business_name}",f"Profile status: {profile.get('status','draft')}",f"Configuration revision: {revision}",f"Configured at: {now}",f"Brand assets copied: {', '.join(copied) if copied else 'none'}","","This worker is configured by minmax-proposal-inquiry. Reusable business configuration lives in references/business-profile.json and assets/brand/.","Core proposal methodology is managed separately and must not be rewritten by business onboarding."]
    (target/"CONFIGURATION.md").write_text("\n".join(cfg)+"\n",encoding="utf-8")


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--runtime-skill-dir",required=True); ap.add_argument("--profile",required=True); ap.add_argument("--brand-assets"); mode=ap.add_mutually_exclusive_group(required=True); mode.add_argument("--in-place",action="store_true"); mode.add_argument("--output-dir"); args=ap.parse_args()
    runtime=Path(args.runtime_skill_dir).resolve(); profile_path=Path(args.profile).resolve()
    if runtime.name!="minmax-enterprise-proposal" or not (runtime/"SKILL.md").exists(): raise SystemExit("FAIL: --runtime-skill-dir must point to minmax-enterprise-proposal")
    if not profile_path.exists(): raise SystemExit("FAIL: profile not found")
    profile=load_json(profile_path)
    if profile.get("schema_version")!="1.0": raise SystemExit("FAIL: unsupported profile schema_version")
    if profile.get("status") not in {"draft","configured"}: raise SystemExit("FAIL: compiled profile status must be draft or configured")
    if args.in_place: target=runtime; update_mode="in_place"
    else:
        output_root=Path(args.output_dir).resolve(); target=output_root/"minmax-enterprise-proposal"
        if target.exists(): shutil.rmtree(target)
        output_root.mkdir(parents=True,exist_ok=True); shutil.copytree(runtime,target); update_mode="replacement_build"
    (target/"references").mkdir(parents=True,exist_ok=True)
    copied=[]; brand_assets=Path(args.brand_assets).resolve() if args.brand_assets else None
    if brand_assets and brand_assets.exists():
        brand_dir=target/"assets"/"brand"
        if brand_dir.exists(): shutil.rmtree(brand_dir)
        copied=copy_assets(brand_assets,brand_dir)
    normalize_asset_paths(profile,copied)
    (target/"references"/"business-profile.json").write_text(json.dumps(profile,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    write_state(target,profile,copied,update_mode)
    print(f"UPDATED: {target}"); print(f"STATUS: {profile.get('status')}"); return 0


if __name__=="__main__": raise SystemExit(main())
