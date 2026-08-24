#!/usr/bin/env python3
import argparse,hashlib,json,shutil,subprocess,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
MAX_ZIP=25*1024*1024;MAX_ASSET=8*1024*1024;ALLOWED={".svg",".png",".jpg",".jpeg",".webp"}
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def validate_asset(p):
 if p.is_symlink() or not p.is_file():raise ValueError(f"asset must be regular non-symlink file: {p.name}")
 if p.name.startswith(".") or p.suffix.lower() not in ALLOWED:raise ValueError(f"unsupported brand asset: {p.name}")
 if p.stat().st_size>MAX_ASSET:raise ValueError(f"brand asset too large: {p.name}")
def run(script,profile):
 r=subprocess.run([sys.executable,str(script),str(profile)]); 
 if r.returncode:raise SystemExit("FAIL: profile validation failed")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--orchestrator-dir",required=True);ap.add_argument("--profile",required=True);ap.add_argument("--brand-assets");g=ap.add_mutually_exclusive_group(required=True);g.add_argument("--in-place",action="store_true");g.add_argument("--output-dir");a=ap.parse_args();src=Path(a.orchestrator_dir).resolve();profile_path=Path(a.profile).resolve();run(Path(__file__).with_name("validate_profile.py"),profile_path);profile=load(profile_path)
 if a.in_place:root=src;outzip=None;mode="in_place"
 else:
  out=Path(a.output_dir).resolve();root=out/"minmax-proposals";shutil.rmtree(root,ignore_errors=True);out.mkdir(parents=True,exist_ok=True);shutil.copytree(src,root);outzip=out/"skill.zip";mode="replacement_bundle"
 enterprise=root/"internal-skills/minmax-enterprise-proposal";dest=enterprise/"assets/brand";copied=[]
 if a.brand_assets:
  source=Path(a.brand_assets).resolve();items=sorted(source.iterdir())
  for p in items:validate_asset(p)
  shutil.rmtree(dest,ignore_errors=True);dest.mkdir(parents=True,exist_ok=True)
  for p in items:shutil.copy2(p,dest/p.name);copied.append(p.name)
 for k in ("logo_path","cover_image_path"):
  raw=(profile.get("brand") or {}).get(k) or "";name=Path(raw).name if raw else ""
  if name in copied:profile.setdefault("brand",{})[k]=f"assets/brand/{name}"
 pp=enterprise/"references/business-profile.json";pp.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+"\n");statep=enterprise/"references/configuration-state.json";old=load(statep) if statep.exists() else {};rev=int(old.get("configuration_revision",0))+1;state={"schema_version":"1.0","configuration_revision":rev,"configured_at":datetime.now(timezone.utc).isoformat(),"profile_status":profile.get("status","draft"),"business_name":(profile.get("business") or {}).get("name"),"update_mode":mode,"brand_assets":copied,"profile_sha256":hashlib.sha256(pp.read_bytes()).hexdigest()};statep.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n");run(enterprise/"scripts/validate_profile.py",pp);bundle=root/"scripts/validate_bundle.py";r=subprocess.run([sys.executable,str(bundle),str(root)]); 
 if r.returncode:raise SystemExit("FAIL: bundle validation failed")
 if outzip:
  with zipfile.ZipFile(outzip,"w",zipfile.ZIP_DEFLATED) as z:
   for f in sorted(root.rglob("*")):
    if f.is_file():z.write(f,f.relative_to(root.parent))
  if outzip.stat().st_size>MAX_ZIP:raise SystemExit("FAIL: packaged skill exceeds 25 MiB")
 print(f"CONFIGURATION_REVISION: {rev}");return 0
if __name__=="__main__":raise SystemExit(main())
