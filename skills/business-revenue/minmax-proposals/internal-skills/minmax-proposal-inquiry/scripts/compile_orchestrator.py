#!/usr/bin/env python3
import argparse,hashlib,json,shutil,subprocess,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
MAX_ZIP_BYTES=25*1024*1024;MAX_ASSET_BYTES=8*1024*1024;ALLOWED={".svg",".png",".jpg",".jpeg",".webp"}
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def validate_asset(p):
    if p.is_symlink() or not p.is_file() or p.name.startswith(".") or p.suffix.lower() not in ALLOWED or p.stat().st_size>MAX_ASSET_BYTES:raise ValueError(f"unsafe or unsupported brand asset: {p.name}")
def copy_assets(src,dest):
    if not src or not src.exists():return []
    if not src.is_dir():raise ValueError("--brand-assets must point to a directory")
    items=sorted(src.iterdir());[validate_asset(x) for x in items]
    if dest.exists():shutil.rmtree(dest)
    dest.mkdir(parents=True,exist_ok=True)
    for x in items:shutil.copy2(x,dest/x.name)
    return [x.name for x in items]
def run(script,profile):
    p=subprocess.run([sys.executable,str(script),str(profile)],text=True,capture_output=True);print(p.stdout.rstrip()) if p.stdout else None
    if p.returncode:raise SystemExit("FAIL: profile validation failed")
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--orchestrator-dir",required=True);ap.add_argument("--profile",required=True);ap.add_argument("--brand-assets");g=ap.add_mutually_exclusive_group(required=True);g.add_argument("--in-place",action="store_true");g.add_argument("--output-dir");a=ap.parse_args();root=Path(a.orchestrator_dir).resolve();source=Path(a.profile).resolve();run(Path(__file__).resolve().parent/"validate_profile.py",source);profile=load(source)
    if a.in_place:target=root;mode="in_place";zipout=None
    else:
        out=Path(a.output_dir).resolve();target=out/"minmax-proposals";shutil.rmtree(target,ignore_errors=True);out.mkdir(parents=True,exist_ok=True);shutil.copytree(root,target);mode="replacement_bundle";zipout=out/"skill.zip"
    ent=target/"internal-skills"/"minmax-enterprise-proposal";refs=ent/"references";refs.mkdir(parents=True,exist_ok=True);copied=copy_assets(Path(a.brand_assets).resolve(),ent/"assets"/"brand") if a.brand_assets else []
    brand=profile.setdefault("brand",{})
    for k in ("logo_path","cover_image_path"):
        n=Path(brand.get(k) or "").name
        if n in copied:brand[k]=f"assets/brand/{n}"
    pp=refs/"business-profile.json";pp.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");sp=refs/"configuration-state.json";old=load(sp).get("configuration_revision",0) if sp.exists() else 0;rev=int(old)+1;h=hashlib.sha256(pp.read_bytes()).hexdigest();state={"schema_version":"1.0","configuration_revision":rev,"configured_at":datetime.now(timezone.utc).isoformat(),"profile_status":profile.get("status","draft"),"business_name":(profile.get("business") or {}).get("name"),"update_mode":mode,"brand_assets":copied,"profile_sha256":h};sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");run(ent/"scripts"/"validate_profile.py",pp)
    if zipout:
        with zipfile.ZipFile(zipout,"w",zipfile.ZIP_DEFLATED) as z:
            for f in sorted(target.rglob("*")):
                if f.is_file():z.write(f,f.relative_to(target.parent))
        if zipout.stat().st_size>MAX_ZIP_BYTES:raise SystemExit("FAIL: packaged skill exceeds 25 MiB")
        print(f"PACKAGED_SKILL: {zipout}")
    print(f"CONFIGURATION_REVISION: {rev}")
if __name__=="__main__":raise SystemExit(main())
