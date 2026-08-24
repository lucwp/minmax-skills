#!/usr/bin/env python3
"""Backward-compatible wrapper. Prefer update_enterprise_worker.py."""
import argparse
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runtime-skill-dir", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--brand-assets")
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    script = Path(__file__).with_name("update_enterprise_worker.py")
    cmd = ["python", str(script), "--runtime-skill-dir", args.runtime_skill_dir, "--profile", args.profile, "--output-dir", args.output_dir]
    if args.brand_assets:
        cmd.extend(["--brand-assets", args.brand_assets])
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
