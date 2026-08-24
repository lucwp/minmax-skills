#!/usr/bin/env python3
import importlib.util,json,tempfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=ROOT/"internal-skills"/"minmax-enterprise-proposal";I=ROOT/"internal-skills"/"minmax-proposal-inquiry"
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
pv=load("pv",E/"scripts"/"validate_profile.py");pr=load("pr",I/"scripts"/"profile_report.py");vv=load("vv",E/"scripts"/"validate_proposal.py");pf=load("pf",E/"scripts"/"preflight_proposal.py")
def profile():
 return {"schema_version":"1.0","status":"configured","business":{"name":"N","category":"B2B","one_liner":"X","default_currency":"USD","languages":["en"]},"positioning":{"ideal_customers":["B2B"],"core_problems":["X"],"buyer_roles":["CRO"],"value_proposition":"Y"},"offers":[{"id":"offer","name":"Offer","type":"project","business_value":"Y","deliverables":["D"],"boundaries":["B"],"client_dependencies":["Sponsor"],"pricing":{"model":"fixed","currency":"USD","public_price":10000,"floor":10000}}],"commercial":{"proposal_validity_days":30,"default_payment_terms":"50/50","discount_policy":"No below floor","scope_change_policy":"Re-estimate"},"proof":{},"brand":{"primary_color":"#111827","accent_color":"#2563EB","background_color":"#F8FAFC","surface_color":"#FFFFFF","text_color":"#111827","muted_color":"#64748B","visual_style":["minimal"]},"voice":{"default_language":"en","tone":["specific"],"claim_policy":"Verified only"},"proposal_defaults":{"page_size":"A4-landscape","approval_mode":"thesis_first","default_next_step":"Contract"}}
p=profile();e,_=pv.validate(p);assert not e,e
bad=profile();bad["commercial"]["discount_policy"]="";e,_=pv.validate(bad);assert any("discount_policy" in x for x in e)
_,_,r=pr.score_profile(profile());assert r=="configured",r
weak=profile();weak["offers"][0]["boundaries"]=[];_,_,r=pr.score_profile(weak);assert r!="configured"
with tempfile.TemporaryDirectory() as td:
 d=Path(td);pp=d/"p.json";sp=d/"s.json";pp.write_text(json.dumps(p));sp.write_text(json.dumps({"configuration_revision":1,"profile_status":"configured","profile_sha256":hashlib.sha256(pp.read_bytes()).hexdigest()}));proposal={"schema_version":"1.0","meta":{"proposal_title":"P","client_name":"C","release_mode":"autonomous","source_profile_revision":1},"evidence_ledger":[],"pages":[{"type":"cover","section":"P","title":"P"},{"type":"commercial","section":"I","title":"I","investment":{"included_scope":["X"],"assumptions":["Y"],"rationale":"R","components":[{"label":"Fee","amount_value":10000}],"total":"USD 10k","calculation":{"status":"fixed","currency":"USD","total_value":10000}}},{"type":"next-step","section":"N","title":"N","next_step":"Go"}]};e,_=vv.validate(proposal,pp,sp);assert not e,e;proposal["pages"][1]["investment"]["components"][0]["amount_value"]=9000;e,_=vv.validate(proposal,pp,sp);assert any("component sum" in x for x in e)
print("PASS: MinMax Proposals reliability regression tests")
