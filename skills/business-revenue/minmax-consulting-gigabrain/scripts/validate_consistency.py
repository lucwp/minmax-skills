#!/usr/bin/env python3
"""Validate unit, currency, denominator, taxonomy, and period comparability."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

REQUIRED_FIELDS = ("comparison_group","unit","currency","base_year","price_basis","measure_type","geography","period","taxonomy","taxonomy_version","denominator_id")
BASE_CONSISTENCY_FIELDS = ("unit","currency","base_year","price_basis","measure_type","geography","taxonomy","taxonomy_version","denominator_id")
PRICE_BASES = {"nominal","real","current","constant","chained","not-applicable"}
MEASURE_TYPES = {"stock","flow","index","share","count","rate","price"}
COMPARISON_MODES = {"point_in_time","time_series"}
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
PERIOD_RE = re.compile(r"^(?:\d{4}|\d{4}-Q[1-4]|\d{4}-M(?:0[1-9]|1[0-2])|\d{4}-\d{2}-\d{2})$")
MAX_ROWS = 10000

def _read(path: str | Path) -> tuple[list[dict[str,str]], list[str]]:
    errors=[]; p=Path(path)
    if not p.exists() or not p.is_file(): return [], [f"input file not found: {p}"]
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader=csv.DictReader(f); headers=[h.strip() for h in (reader.fieldnames or [])]
        if not headers: return [], ["CSV has no header"]
        if len(headers)!=len(set(headers)): return [], ["CSV headers must be unique"]
        missing=[x for x in REQUIRED_FIELDS if x not in headers]
        if missing: return [], ["CSV missing required columns: "+", ".join(missing)]
        reader.fieldnames=headers; rows=[]
        for line_number,row in enumerate(reader,start=2):
            if line_number-1>MAX_ROWS: errors.append(f"CSV exceeds {MAX_ROWS} data rows"); break
            if None in row: errors.append(f"row {line_number} has extra cells"); continue
            clean={k:("" if v is None else v.strip()) for k,v in row.items()}
            if any(clean.values()): rows.append(clean)
    return rows, errors

def check(path: str | Path) -> dict:
    data, errors = _read(path); warnings=[]
    if not data: errors.append("consistency ledger must contain at least one record"); return {"valid":False,"record_count":0,"comparison_group_count":0,"mismatches":{},"errors":errors,"warnings":warnings}
    groups={}; record_ids=set()
    for i,row in enumerate(data,start=2):
        group=row.get("comparison_group","").strip()
        if not group: errors.append(f"row {i}: missing comparison_group"); continue
        if "record_id" in row:
            rid=row.get("record_id","").strip()
            if not rid: errors.append(f"row {i}: blank record_id")
            elif rid in record_ids: errors.append(f"row {i}: duplicate record_id {rid}")
            record_ids.add(rid)
        mode=row.get("comparison_mode","point_in_time").strip() or "point_in_time"
        if mode not in COMPARISON_MODES: errors.append(f"row {i}: comparison_mode must be one of {', '.join(sorted(COMPARISON_MODES))}"); mode="point_in_time"
        unit=row.get("unit","").strip(); currency=row.get("currency","").strip().upper(); base_year=row.get("base_year","").strip(); price_basis=row.get("price_basis","").strip(); measure_type=row.get("measure_type","").strip(); geography=row.get("geography","").strip(); period=row.get("period","").strip(); taxonomy=row.get("taxonomy","").strip(); taxonomy_version=row.get("taxonomy_version","").strip(); denominator=row.get("denominator_id","").strip()
        if not unit: errors.append(f"row {i}: unit is required")
        if currency and not CURRENCY_RE.fullmatch(currency): errors.append(f"row {i}: currency must be a three-letter ISO-style code")
        if not geography: errors.append(f"row {i}: geography is required")
        if not denominator: errors.append(f"row {i}: denominator_id is required")
        if price_basis not in PRICE_BASES: errors.append(f"row {i}: invalid price_basis {price_basis!r}")
        if measure_type not in MEASURE_TYPES: errors.append(f"row {i}: invalid measure_type {measure_type!r}")
        if not PERIOD_RE.fullmatch(period): errors.append(f"row {i}: period must be YYYY, YYYY-Qn, YYYY-Mnn, or YYYY-MM-DD")
        if taxonomy and not taxonomy_version: errors.append(f"row {i}: taxonomy_version is required when taxonomy is set")
        if taxonomy_version and not taxonomy: errors.append(f"row {i}: taxonomy is required when taxonomy_version is set")
        if currency:
            if not re.fullmatch(r"\d{4}",base_year): errors.append(f"row {i}: monetary rows require a four-digit base_year")
            elif not 1800<=int(base_year)<=2200: errors.append(f"row {i}: base_year is out of range")
            if price_basis=="not-applicable": errors.append(f"row {i}: monetary rows require an applicable price_basis")
        else:
            if base_year: errors.append(f"row {i}: non-monetary rows must not set base_year")
            if price_basis!="not-applicable": errors.append(f"row {i}: non-monetary rows must use price_basis 'not-applicable'")
        normalized={"unit":unit,"currency":currency,"base_year":base_year,"price_basis":price_basis,"measure_type":measure_type,"geography":geography,"period":period,"taxonomy":taxonomy,"taxonomy_version":taxonomy_version,"denominator_id":denominator}
        state=groups.setdefault(group,{"modes":set(),"values":{k:set() for k in normalized}}); state["modes"].add(mode)
        for key,value in normalized.items(): state["values"][key].add(value)
    mismatches={}
    for group,state in sorted(groups.items()):
        modes=state["modes"]; group_bad={}
        if len(modes)>1: group_bad["comparison_mode"]=sorted(modes); errors.append(f"{group}: mixes comparison_mode values"); mode="point_in_time"
        else: mode=next(iter(modes)) if modes else "point_in_time"
        fields=list(BASE_CONSISTENCY_FIELDS)
        if mode=="point_in_time": fields.append("period")
        for field in fields:
            observed=state["values"][field]
            if len(observed)>1: group_bad[field]=sorted(observed)
        if group_bad: mismatches[group]=group_bad; errors.append(f"{group}: incompatible comparison fields: {', '.join(sorted(group_bad))}")
        if mode=="time_series" and len(state["values"]["period"])<2: warnings.append(f"{group}: time_series group contains fewer than two periods")
    return {"valid":not errors,"record_count":len(data),"comparison_group_count":len(groups),"mismatches":mismatches,"errors":errors,"warnings":warnings}

def main() -> int:
    parser=argparse.ArgumentParser(description="Validate Gigabrain comparison consistency"); parser.add_argument("input"); parser.add_argument("--output"); args=parser.parse_args(); result=check(args.input); text=json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.output: Path(args.output).write_text(text,encoding="utf-8")
    else: print(text,end="")
    return 0 if result["valid"] else 1

if __name__=="__main__": raise SystemExit(main())
