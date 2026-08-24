#!/usr/bin/env python3
"""Validate a compact source ledger and claim ledger.

The validator is intentionally fail-closed for malformed or incomplete ledgers.
It validates mechanical traceability, not substantive truth.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path
from typing import Iterable

ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{0,95}$")
SOURCE_FIELDS = ("source_id", "publication_date", "retrieval_date")
CLAIM_FIELDS = ("claim_id", "claim_type", "source_ids", "calculation_id", "assumption_ids", "confidence")
EVIDENCE_REQUIRED = {"quantitative_fact", "quantitative_estimate", "calculation", "forecast", "qualitative_fact"}
VALID_TYPES = EVIDENCE_REQUIRED | {"opinion", "recommendation"}
VALID_CONFIDENCE = {"high", "medium", "low", "not-assessed"}
MAX_ROWS = 10000
MAX_CELL = 20000
MAX_BYTES = 5 * 1024 * 1024

class ValidationError(ValueError): pass

def _read_rows(path: str | Path, required_fields: Iterable[str]) -> list[dict[str, str]]:
    p = Path(path)
    if not p.exists() or not p.is_file(): raise ValidationError(f"input file not found: {p}")
    if p.stat().st_size > MAX_BYTES: raise ValidationError(f"input exceeds {MAX_BYTES} bytes: {p}")
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader=csv.DictReader(f); headers=reader.fieldnames or []; normalized=[h.strip() for h in headers]
        if not normalized: raise ValidationError(f"CSV has no header: {p}")
        if len(normalized)!=len(set(normalized)): raise ValidationError(f"CSV headers must be unique: {p}")
        missing=[x for x in required_fields if x not in normalized]
        if missing: raise ValidationError(f"CSV missing required columns: {', '.join(missing)}")
        reader.fieldnames=normalized; out=[]
        for line_number,row in enumerate(reader,start=2):
            if line_number-1>MAX_ROWS: raise ValidationError(f"CSV exceeds {MAX_ROWS} data rows")
            if None in row: raise ValidationError(f"row {line_number} has extra cells")
            clean={}
            for key,value in row.items():
                cell="" if value is None else value.strip()
                if len(cell)>MAX_CELL: raise ValidationError(f"row {line_number}, column {key} is too long")
                if "\x00" in cell: raise ValidationError(f"row {line_number}, column {key} contains NUL")
                clean[key]=cell
            if any(clean.values()): out.append(clean)
        return out

def _split_ids(value: str, context: str, errors: list[str]) -> list[str]:
    parts=[x.strip() for x in (value or "").split(";") if x.strip()]; seen=set()
    for part in parts:
        if not ID_RE.fullmatch(part): errors.append(f"{context}: invalid identifier {part!r}")
        if part in seen: errors.append(f"{context}: duplicate identifier {part}")
        seen.add(part)
    return parts

def _parse_publication(value: str) -> tuple[str, date | int | None]:
    if value=="not-stated": return "not-stated",None
    if re.fullmatch(r"\d{4}",value):
        year=int(value)
        if not 1800<=year<=2200: raise ValueError("year out of range")
        return "year",year
    return "date",date.fromisoformat(value)

def audit(source_path: str | Path, claim_path: str | Path, as_of: date | None=None) -> dict:
    errors=[]; warnings=[]; as_of=as_of or date.today()
    try: src_rows=_read_rows(source_path,SOURCE_FIELDS); clm_rows=_read_rows(claim_path,CLAIM_FIELDS)
    except ValidationError as exc: return {"valid":False,"source_count":0,"claim_count":0,"uncited_claim_ids":[],"errors":[str(exc)],"warnings":[]}
    if not src_rows: errors.append("source ledger must contain at least one source")
    if not clm_rows: errors.append("claim ledger must contain at least one claim")
    source_ids=[]
    for i,row in enumerate(src_rows,start=2):
        sid=row.get("source_id","").strip()
        if not ID_RE.fullmatch(sid): errors.append(f"source row {i}: invalid source_id")
        source_ids.append(sid); pub_text=row.get("publication_date","").strip(); ret_text=row.get("retrieval_date","").strip()
        if not pub_text: errors.append(f"{sid or f'source row {i}'}: publication_date is required"); pub_kind,pub_value="invalid",None
        else:
            try: pub_kind,pub_value=_parse_publication(pub_text)
            except ValueError: errors.append(f"{sid or f'source row {i}'}: invalid publication_date"); pub_kind,pub_value="invalid",None
        if not ret_text: errors.append(f"{sid or f'source row {i}'}: retrieval_date is required"); ret_value=None
        else:
            try: ret_value=date.fromisoformat(ret_text)
            except ValueError: errors.append(f"{sid or f'source row {i}'}: invalid retrieval_date"); ret_value=None
        if ret_value and ret_value>as_of: errors.append(f"{sid}: retrieval_date {ret_value.isoformat()} is after as-of {as_of.isoformat()}")
        if ret_value and pub_kind=="date" and isinstance(pub_value,date) and pub_value>ret_value: errors.append(f"{sid}: publication_date is after retrieval_date")
        if ret_value and pub_kind=="year" and isinstance(pub_value,int) and pub_value>ret_value.year: errors.append(f"{sid}: publication year is after retrieval year")
    duplicates=sorted({x for x in source_ids if x and source_ids.count(x)>1})
    if duplicates: errors.append("duplicate source IDs: "+", ".join(duplicates))
    known=set(source_ids); claim_ids=[]; uncited=[]; cited=set()
    for i,row in enumerate(clm_rows,start=2):
        cid=row.get("claim_id","").strip(); ctype=row.get("claim_type","").strip(); claim_ids.append(cid)
        if not ID_RE.fullmatch(cid): errors.append(f"claim row {i}: invalid claim_id")
        if ctype not in VALID_TYPES: errors.append(f"{cid or f'claim row {i}'}: invalid claim_type {ctype!r}")
        source_refs=_split_ids(row.get("source_ids",""),f"{cid}.source_ids",errors); cited.update(source_refs)
        if ctype in EVIDENCE_REQUIRED and not source_refs: uncited.append(cid); errors.append(f"{cid}: evidence-bearing claim requires source_ids")
        missing=sorted(set(source_refs)-known)
        if missing: errors.append(f"{cid}: unknown source IDs: {', '.join(missing)}")
        calc=row.get("calculation_id","").strip()
        if calc and not ID_RE.fullmatch(calc): errors.append(f"{cid}: invalid calculation_id {calc!r}")
        assumption_refs=_split_ids(row.get("assumption_ids",""),f"{cid}.assumption_ids",errors)
        if ctype in {"calculation","forecast"} and not calc: errors.append(f"{cid}: {ctype} requires calculation_id")
        if ctype=="forecast" and not assumption_refs: errors.append(f"{cid}: forecast requires assumption_ids")
        confidence=row.get("confidence","").strip()
        if confidence not in VALID_CONFIDENCE: errors.append(f"{cid}: confidence is required and must be one of {', '.join(sorted(VALID_CONFIDENCE))}")
    duplicate_claims=sorted({x for x in claim_ids if x and claim_ids.count(x)>1})
    if duplicate_claims: errors.append("duplicate claim IDs: "+", ".join(duplicate_claims))
    unused=sorted(known-cited)
    if unused: warnings.append(f"{len(unused)} source ledger entries are not mapped to a claim")
    return {"valid":not errors,"source_count":len(src_rows),"claim_count":len(clm_rows),"uncited_claim_ids":sorted(set(uncited)),"unused_source_ids":unused,"errors":errors,"warnings":warnings}

def main() -> int:
    parser=argparse.ArgumentParser(description="Validate Gigabrain evidence ledgers"); parser.add_argument("sources"); parser.add_argument("claims"); parser.add_argument("--output"); args=parser.parse_args(); result=audit(args.sources,args.claims); text=json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.output: Path(args.output).write_text(text,encoding="utf-8")
    else: print(text,end="")
    return 0 if result["valid"] else 1

if __name__=="__main__": raise SystemExit(main())
