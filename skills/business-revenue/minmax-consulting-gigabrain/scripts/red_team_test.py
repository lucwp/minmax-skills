#!/usr/bin/env python3
"""Focused regression battery for the Gigabrain Challenge Engine.

Covers only red-team mechanics: Decision Robustness scoring, bounded challenge
modes, 90+ stop behavior, independence honesty, false-ROBUST prevention,
release coupling, benchmark gates, and malformed-input fail-closed behavior.
It intentionally does not retest generic evidence, consistency, or business-case
validators; those are operational dependencies, not red-team test targets.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Callable

import benchmark_gate
import challenge_gate
import decision_robustness
import release_gate

ROOT = Path(__file__).resolve().parents[1]

class Battery:
    def __init__(self) -> None: self.rows: list[tuple[str,str,bool,str]]=[]
    def check(self, category: str, name: str, fn: Callable[[], bool | tuple[bool,str]]) -> None:
        try:
            result=fn(); ok,detail=result if isinstance(result,tuple) else (bool(result),""); self.rows.append((category,name,bool(ok),str(detail)))
        except Exception as exc: self.rows.append((category,name,False,f"EXCEPTION {type(exc).__name__}: {exc}"))
    def summary(self) -> dict:
        total=len(self.rows); passed=sum(1 for _,_,ok,_ in self.rows if ok); by_category={}
        for category,_,ok,_ in self.rows:
            bucket=by_category.setdefault(category,{"total":0,"passed":0,"failed":0}); bucket["total"]+=1; bucket["passed" if ok else "failed"]+=1
        return {"total":total,"passed":passed,"failed":total-passed,"pass_rate_pct":round((passed/total*100.0) if total else 0.0,1),"by_category":by_category}

def robustness_payload(*,weak=False,breaker=False,score_nas=None):
    score_nas=score_nas or set(); criteria={}
    for name in decision_robustness.CRITERIA: criteria[name]={"status":"na","evidence":""} if name in score_nas else {"status":"met","evidence":f"fixture evidence: {name}"}
    if weak:
        for name in ("load_bearing_assumptions_explicit","disconfirming_evidence_sought","decision_flip_counterfactual_identified"): criteria[name]={"status":"partial","evidence":f"incomplete fixture: {name}"}
    return {"decision_class":"recommend-with-conditions","criteria":criteria,"hard_gates":{"critical_empirical_breaker":breaker},"flags":{"forecast_heavy":False,"outside_view_status":"not-required","quant_material":False,"material_alternative_required":True,"strongest_alternative_evaluated":True,"execution_heavy":True,"implementation_feasibility_tested":True,"surviving_critical_uncertainty":breaker,"critical_uncertainty_controlled":not breaker,"accepted_critical_risk":False,"residual_uncertainty_class":"unresolved-empirical" if breaker else "controlled"}}

def challenge_payload(*,status="open",mode="conviction",round_number=1):
    resolved=status in {"resolved","non-decision-relevant","accepted-risk"}
    return {"mode":mode,"round":round_number,"max_rounds":1 if mode=="pulse" else (2 if mode=="independent" else 3),"forecast_heavy":False,"outside_view_status":"not-required","outside_view_note":"","strongest_alternative_evaluated":True,"independent_challenger_used":False,"decision_state":"unchanged" if resolved else "narrowed","challenges":[{"id":"CH-1","severity":"critical","load_bearing":True,"status":status,"evidence_basis":"verified" if status=="resolved" else "reasoning-only","falsifier":"retention below 85%" if not resolved else "","decision_flip_condition":"downside crosses board threshold" if not resolved else "","resolution":"verified evidence closes the issue" if resolved else ""}]}

def main() -> int:
    b=Battery(); rng=random.Random(20260824); robust=decision_robustness.evaluate(robustness_payload()); weak=decision_robustness.evaluate(robustness_payload(weak=True)); broken=decision_robustness.evaluate(robustness_payload(breaker=True))
    b.check("robustness","healthy decision reaches 90+",lambda: robust["valid"] and robust["score"]>=90 and robust["eligible_to_stop"])
    b.check("robustness","weak decision stays below 90",lambda: weak["valid"] and weak["score"]<90 and not weak["eligible_to_stop"])
    b.check("robustness","critical breaker caps below 90",lambda: broken["valid"] and broken["score"]<90 and not broken["eligible_to_stop"])
    b.check("robustness","accepted critical risk caps below 90",lambda: decision_robustness.evaluate({**robustness_payload(),"flags":{**robustness_payload()["flags"],"accepted_critical_risk":True}})["score"]<90)
    b.check("robustness","unresolved empirical uncertainty caps below 90",lambda: decision_robustness.evaluate({**robustness_payload(),"flags":{**robustness_payload()["flags"],"residual_uncertainty_class":"unresolved-empirical"}})["score"]<90)
    b.check("robustness","material alternative cannot be skipped",lambda: decision_robustness.evaluate({**robustness_payload(),"flags":{**robustness_payload()["flags"],"strongest_alternative_evaluated":False}})["score"]<90)
    b.check("robustness","execution-heavy cannot mark execution dimension n/a",lambda: not decision_robustness.evaluate(robustness_payload(score_nas={"feasibility_capacity_dependencies_checked","incentives_and_actor_response_checked","ownership_governance_adoption_defined","reversibility_or_contingency_defined"}))["valid"])
    b.check("robustness","non-object robustness input invalid",lambda: not decision_robustness.evaluate([])["valid"])
    open_conviction=challenge_payload(status="open"); resolved_conviction=challenge_payload(status="resolved",round_number=2)
    b.check("challenge","open critical continues",lambda: challenge_gate.evaluate(open_conviction,weak)["status"]=="CONTINUE")
    b.check("challenge","resolved sub-90 continues",lambda: challenge_gate.evaluate(resolved_conviction,weak)["status"]=="CONTINUE")
    b.check("challenge","resolved 90+ becomes robust",lambda: challenge_gate.evaluate(resolved_conviction,robust)["status"]=="ROBUST")
    b.check("challenge","90+ stops before max rounds",lambda: challenge_gate.evaluate({**resolved_conviction,"round":1},robust)["status"]=="ROBUST")
    b.check("challenge","pulse cannot exceed one round",lambda: not challenge_gate.evaluate({**challenge_payload(mode="pulse"),"max_rounds":2},weak)["valid"])
    b.check("challenge","conviction cannot exceed three rounds",lambda: not challenge_gate.evaluate({**open_conviction,"max_rounds":4},weak)["valid"])
    b.check("challenge","independent cannot exceed two rounds",lambda: not challenge_gate.evaluate({**challenge_payload(status="resolved",mode="independent"),"max_rounds":3,"independent_challenger_used":True,"isolation_note":"isolated context"},robust)["valid"])
    b.check("challenge","active challenge requires at least one challenge",lambda: not challenge_gate.evaluate({**open_conviction,"challenges":[]},weak)["valid"])
    b.check("challenge","duplicate challenge IDs invalid",lambda: not challenge_gate.evaluate({**open_conviction,"challenges":open_conviction["challenges"]*2},weak)["valid"])
    b.check("challenge","accepted critical risk is unresolved",lambda: challenge_gate.evaluate(challenge_payload(status="accepted-risk",round_number=3),robust)["status"]=="UNRESOLVED")
    b.check("challenge","fake independent never robust",lambda: challenge_gate.evaluate(challenge_payload(status="resolved",mode="independent"),robust)["status"]!="ROBUST")
    independent={**challenge_payload(status="resolved",mode="independent"),"independent_challenger_used":True,"isolation_note":"separate context; recommendation narrative withheld"}
    b.check("challenge","real independent with isolation can be robust",lambda: challenge_gate.evaluate(independent,robust)["status"]=="ROBUST")
    b.check("challenge","independent used without isolation note invalid",lambda: not challenge_gate.evaluate({**independent,"isolation_note":""},robust)["valid"])
    forecast_missing={**resolved_conviction,"forecast_heavy":True,"outside_view_status":"missing"}
    b.check("challenge","forecast-heavy missing outside view not robust",lambda: challenge_gate.evaluate(forecast_missing,robust)["status"]!="ROBUST")
    b.check("challenge","alternative required in conviction",lambda: challenge_gate.evaluate({**resolved_conviction,"strongest_alternative_evaluated":False},robust)["status"]!="ROBUST")
    b.check("challenge","non-object challenge input invalid",lambda: not challenge_gate.evaluate([],robust)["valid"])
    decision={"substantive":False,"required_checks":["robustness","challenge"],"challenge_mode":"conviction","hard_blockers":[],"unresolved_material_assumptions":[]}; robust_challenge=challenge_gate.evaluate(resolved_conviction,robust); continuing_challenge=challenge_gate.evaluate(open_conviction,weak)
    b.check("release","active challenge requires challenge report",lambda: release_gate.gate(decision,robustness=robust)["status"]=="BLOCK")
    b.check("release","robust challenge and 90+ robustness pass",lambda: release_gate.gate(decision,challenge=robust_challenge,robustness=robust)["status"]=="PASS")
    b.check("release","continuing challenge blocks release",lambda: release_gate.gate(decision,challenge=continuing_challenge,robustness=weak)["status"]=="BLOCK")
    b.check("release","sub-90 robustness blocks release",lambda: release_gate.gate(decision,challenge=robust_challenge,robustness=weak)["status"]=="BLOCK")
    accepted_report=challenge_gate.evaluate(challenge_payload(status="accepted-risk",round_number=3),robust); b.check("release","accepted critical risk cannot release",lambda: release_gate.gate(decision,challenge=accepted_report,robustness=robust)["status"]=="BLOCK")
    benchmark_pass={"target_mean":95,"target_min":90,"target_p10":90,"min_cases":20,"certification_mode":True,"cases":[{"case_id":f"RT{i:02d}","one_shot":True,"score":96 if i<19 else 95,"hard_gate_miss":False,"false_robust":False,"wrong_decision":False,"blind_scored":True,"independent_reviewer":True} for i in range(20)]}
    b.check("benchmark","95 mean benchmark passes",lambda: benchmark_gate.evaluate(benchmark_pass)["status"]=="PASS")
    b.check("benchmark","single sub-90 case fails",lambda: benchmark_gate.evaluate({**benchmark_pass,"cases":[*benchmark_pass["cases"][:-1],{**benchmark_pass["cases"][-1],"score":89}]})["status"]=="FAIL")
    b.check("benchmark","mean below 95 fails",lambda: benchmark_gate.evaluate({**benchmark_pass,"cases":[{**x,"score":94} for x in benchmark_pass["cases"]]})["status"]=="FAIL")
    b.check("benchmark","false robust fails",lambda: benchmark_gate.evaluate({**benchmark_pass,"cases":[{**benchmark_pass["cases"][0],"false_robust":True},*benchmark_pass["cases"][1:]]})["status"]=="FAIL")
    b.check("benchmark","hard gate miss fails",lambda: benchmark_gate.evaluate({**benchmark_pass,"cases":[{**benchmark_pass["cases"][0],"hard_gate_miss":True},*benchmark_pass["cases"][1:]]})["status"]=="FAIL")
    b.check("benchmark","wrong decision class fails",lambda: benchmark_gate.evaluate({**benchmark_pass,"cases":[{**benchmark_pass["cases"][0],"wrong_decision":True},*benchmark_pass["cases"][1:]]})["status"]=="FAIL")
    b.check("benchmark","certification requires blind scoring",lambda: not benchmark_gate.evaluate({**benchmark_pass,"cases":[{**benchmark_pass["cases"][0],"blind_scored":False},*benchmark_pass["cases"][1:]]})["valid"])
    b.check("benchmark","certification requires independent reviewer",lambda: not benchmark_gate.evaluate({**benchmark_pass,"cases":[{**benchmark_pass["cases"][0],"independent_reviewer":False},*benchmark_pass["cases"][1:]]})["valid"])
    skill=(ROOT/"SKILL.md").read_text(encoding="utf-8"); challenge_ref=(ROOT/"references"/"challenge-engine.md").read_text(encoding="utf-8"); lifecycle=(ROOT/"references"/"engagement-lifecycle.md").read_text(encoding="utf-8")
    b.check("static","challenge default OFF",lambda: "default is `OFF`" in skill or "Default. Run no additional" in challenge_ref)
    b.check("static","conviction bounded to three",lambda: "maximum three rounds" in challenge_ref.lower())
    b.check("static","independence honesty explicit",lambda: "do not claim independence" in challenge_ref.lower() or "do not claim independent" in challenge_ref.lower())
    b.check("static","one primary max one secondary",lambda: "one primary technique and at most one secondary" in challenge_ref.lower())
    b.check("static","90 stop threshold documented",lambda: "90" in challenge_ref and "stop" in challenge_ref.lower())
    b.check("static","anti-loop rule present",lambda: "do not recursively" in challenge_ref.lower() or "do not loop" in challenge_ref.lower())
    b.check("static","release gate wired to challenge",lambda: "--challenge" in skill and "challenge" in (ROOT/"scripts"/"release_gate.py").read_text(encoding="utf-8"))
    b.check("static","lifecycle challenge remains opt-in",lambda: "only when the user activated it" in lifecycle)
    fuzz_failures=[]; atoms=[None,True,False,0,1,-1,1.5,"","x",[],{},float("nan"),float("inf")]
    for i in range(5000):
        payload=rng.choice(atoms)
        try:
            report=challenge_gate.evaluate(payload,rng.choice([None,robust,weak,payload]))
            if not isinstance(report,dict) or "status" not in report: fuzz_failures.append(f"challenge-{i}: malformed report")
        except Exception as exc: fuzz_failures.append(f"challenge-{i}: {type(exc).__name__}")
        payload=rng.choice(atoms)
        try:
            report=decision_robustness.evaluate(payload)
            if not isinstance(report,dict) or "valid" not in report: fuzz_failures.append(f"robustness-{i}: malformed report")
        except Exception as exc: fuzz_failures.append(f"robustness-{i}: {type(exc).__name__}")
        try:
            report=release_gate.gate(rng.choice(atoms),challenge=rng.choice(atoms),robustness=rng.choice(atoms))
            if not isinstance(report,dict) or report.get("status") not in {"PASS","CONDITIONAL","BLOCK"}: fuzz_failures.append(f"release-{i}: malformed report")
        except Exception as exc: fuzz_failures.append(f"release-{i}: {type(exc).__name__}")
    b.check("fuzz","15000 red-team-path randomized payloads fail safely",lambda:(not fuzz_failures,"; ".join(fuzz_failures[:10])))
    summary=b.summary(); print(json.dumps(summary,indent=2,sort_keys=True))
    for category,name,ok,detail in b.rows:
        if not ok: print(f"FAIL [{category}] {name}: {detail}")
    if summary["failed"]==0: print("RED_TEAM_TEST_PASS"); return 0
    print("RED_TEAM_TEST_FAIL"); return 1

if __name__=="__main__": raise SystemExit(main())
