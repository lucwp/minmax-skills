#!/usr/bin/env python3
import argparse
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

MAX_ZIP_BYTES = 25 * 1024 * 1024


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def copy_assets(src: Path | None, dest: Path):
    copied = []
    if not src or not src.exists():
        return copied
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for item in sorted(src.iterdir()):
        if item.is_file():
            target = dest / item.name
            shutil.copy2(item, target)
            copied.append(item.name)
    return copied


def normalize_asset_paths(profile: dict, copied: list[str]):
    brand = profile.setdefault("brand", {})
    for key in ("logo_path", "cover_image_path"):
        raw = brand.get(key) or ""
        name = Path(raw).name if raw else ""
        if name and name in copied:
            brand[key] = f"assets/brand/{name}"


def locate_enterprise(root: Path) -> Path:
    target = root / "internal-skills" / "minmax-enterprise-proposal"
    if not (root / "SKILL.md").exists():
        raise SystemExit("FAIL: --orchestrator-dir must point to the minmax-proposals skill root")
    if not (target / "INSTRUCTIONS.md").exists():
        raise SystemExit("FAIL: internal minmax-enterprise-proposal skill not found")
    return target


def validate_profile_shape(profile: dict):
    if profile.get("schema_version") != "1.0":
        raise SystemExit("FAIL: unsupported profile schema_version")
    if profile.get("status") not in {"draft", "configured"}:
        raise SystemExit("FAIL: compiled profile status must be draft or configured")


def write_state(enterprise: Path, profile: dict, copied: list[str], mode: str):
    now = datetime.now(timezone.utc).isoformat()
    state_path = enterprise / "references" / "configuration-state.json"
    previous_revision = 0
    if state_path.exists():
        try:
            previous_revision = int(load_json(state_path).get("configuration_revision", 0))
        except Exception:
            previous_revision = 0
    revision = previous_revision + 1
    business_name = (profile.get("business") or {}).get("name") or "[TO DEFINE]"
    state = {
        "schema_version": "1.0",
        "configuration_revision": revision,
        "configured_at": now,
        "profile_status": profile.get("status", "draft"),
        "business_name": business_name,
        "update_mode": mode,
        "brand_assets": copied,
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cfg = [
        "# Runtime configuration",
        "",
        f"Business: {business_name}",
        f"Profile status: {profile.get('status', 'draft')}",
        f"Configuration revision: {revision}",
        f"Configured at: {now}",
        f"Brand assets copied: {', '.join(copied) if copied else 'none'}",
        "",
        "This internal worker is configured by the MinMax Proposal Inquiry worker.",
        "Reusable business configuration lives in references/business-profile.json and assets/brand/.",
        "Core proposal methodology must not be rewritten by business onboarding.",
    ]
    (enterprise / "CONFIGURATION.md").write_text("\n".join(cfg) + "\n", encoding="utf-8")
    return revision


def validate_bundle(root: Path):
    public_entrypoints = [p for p in root.rglob("SKILL.md") if p.is_file()]
    if public_entrypoints != [root / "SKILL.md"]:
        raise SystemExit("FAIL: rebuilt package must contain exactly one root SKILL.md")
    required = [
        root / "internal-skills" / "minmax-proposal-inquiry" / "INSTRUCTIONS.md",
        root / "internal-skills" / "minmax-enterprise-proposal" / "INSTRUCTIONS.md",
    ]
    for path in required:
        if not path.exists():
            raise SystemExit(f"FAIL: missing {path.relative_to(root)}")


def package_skill(root: Path, output_zip: Path):
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(root.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(root.parent)
                zf.write(file_path, arcname)
    size = output_zip.stat().st_size
    if size > MAX_ZIP_BYTES:
        raise SystemExit(f"FAIL: packaged skill exceeds 25 MiB limit ({size} bytes)")
    return size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orchestrator-dir", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--brand-assets")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--in-place", action="store_true")
    mode.add_argument("--output-dir")
    args = ap.parse_args()

    source_root = Path(args.orchestrator_dir).resolve()
    profile_path = Path(args.profile).resolve()
    locate_enterprise(source_root)
    if not profile_path.exists():
        raise SystemExit("FAIL: profile not found")

    profile = load_json(profile_path)
    validate_profile_shape(profile)

    if args.in_place:
        target_root = source_root
        update_mode = "in_place"
        output_zip = None
    else:
        output_root = Path(args.output_dir).resolve()
        target_root = output_root / "minmax-proposals"
        if target_root.exists():
            shutil.rmtree(target_root)
        output_root.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_root, target_root)
        update_mode = "replacement_bundle"
        output_zip = output_root / "skill.zip"

    enterprise = locate_enterprise(target_root)
    enterprise_refs = enterprise / "references"
    enterprise_refs.mkdir(parents=True, exist_ok=True)

    copied = []
    if args.brand_assets:
        brand_assets = Path(args.brand_assets).resolve()
        if brand_assets.exists():
            copied = copy_assets(brand_assets, enterprise / "assets" / "brand")

    normalize_asset_paths(profile, copied)
    (enterprise_refs / "business-profile.json").write_text(
        json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    revision = write_state(enterprise, profile, copied, update_mode)
    validate_bundle(target_root)

    print(f"UPDATED_ROOT: {target_root}")
    print(f"ENTERPRISE_PROFILE_STATUS: {profile.get('status')}")
    print(f"CONFIGURATION_REVISION: {revision}")

    if output_zip:
        size = package_skill(target_root, output_zip)
        print(f"PACKAGED_SKILL: {output_zip}")
        print(f"ARCHIVE_BYTES: {size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
