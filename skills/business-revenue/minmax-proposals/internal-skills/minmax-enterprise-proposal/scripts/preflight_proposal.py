#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
PLACEHOLDER=re.compile(r"\{\{|\}\}|\[CONFIGURE WITH|<TODO|TODO:",re.I);UNRESOLVED=re.compile(r"\[(?:TO DEFINE|A DEFINIR)\]",re.I);DANGEROUS=re.compile(r"<script\b|javascript:",re.I);REPEAT=re.compile(r"RECOMMENDED.{0,140}Recommended|Recommended.{0,140}RECOMMENDED",re.I|re.S);VISUAL={"browser_render","pdf_render","screenshot_diff"}
def run_checks(text,proposal,visual_report=None):
    e=[];w=[];mode=(proposal.get("meta") or {}).get("release_mode") or "consulting"
    if PLACEHOLDER.search(text):e.append("unresolved template placeholder found in HTML")
    if DANGEROUS.search(text):e.append("dangerous script/javascript content found in HTML")
    if UNRESOLVED.search(text):(e if mode=="autonomous" else w).append("HTML contains unresolved markers")
    if REPEAT.search(text):e.append("repeated recommendation state detected; keep one visual carrier")
    pages=re.findall(r'<section class="page(?: [^"]*)?">',text);expected=len(proposal.get("pages") or [])
    if expected and len(pages)!=expected:e.append(f"rendered page count mismatch: html={len(pages)} json={expected}")
    if mode=="autonomous":
        if not isinstance(visual_report,dict):e.append("autonomous release requires a visual QA report")
        else:
            if visual_report.get("status")!="PASS":e.append("visual QA status must be PASS")
            if visual_report.get("method") not in VISUAL:e.append("visual QA method invalid")
            if visual_report.get("overflow") is not False:e.append("visual QA must explicitly report overflow=false")
            if visual_report.get("clipping") is not False:e.append("visual QA must explicitly report clipping=false")
            missing=visual_report.get("missing_assets")
            if not isinstance(missing,list) or missing:e.append("visual QA must report no missing assets")
    return e,w
def main():
    ap=argparse.ArgumentParser();ap.add_argument("html");ap.add_argument("proposal");ap.add_argument("--visual-qa-report");a=ap.parse_args();text=Path(a.html).read_text();proposal=json.loads(Path(a.proposal).read_text());visual=json.loads(Path(a.visual_qa_report).read_text()) if a.visual_qa_report else None;e,w=run_checks(text,proposal,visual)
    for x in w:print(f"WARN: {x}")
    for x in e:print(f"FAIL: {x}")
    print(f"RESULT: {'FAIL' if e else 'PASS'} ({len(e)} errors, {len(w)} warnings)");return 1 if e else 0
if __name__=="__main__":raise SystemExit(main())
