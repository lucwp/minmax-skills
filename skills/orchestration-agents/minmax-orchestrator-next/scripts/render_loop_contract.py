#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

LABELS = {
    "pt-BR": {
        "title": "# Contrato de Loop - {name}",
        "snapshot": "## Resumo para aprovação",
        "outcome": "Resultado",
        "deliverable": "Entregável",
        "pass": "PASS",
        "autonomy": "Autonomia",
        "budget": "Orçamento",
        "scope": "## Escopo e evidências",
        "execution": "## Plano de execução",
        "what": "O que acontece",
        "why": "Por quê",
        "produces": "Produz",
        "then": "Depois",
        "verification": "## Verificação e convergência",
        "boundaries": "## Limites e saídas",
        "can": "Pode",
        "cannot": "Não pode",
        "success": "SUCCESS",
        "failure": "FAILURE",
        "budget_exit": "BUDGET",
        "replan": "REPLAN",
        "approval": "## Aprovação",
        "approval_text": "A aprovação autoriza somente este contrato. Qualquer replanejamento material exige uma nova aprovação.",
    },
    "en": {
        "title": "# Loop Contract - {name}",
        "snapshot": "## Approval snapshot",
        "outcome": "Outcome",
        "deliverable": "Deliverable",
        "pass": "PASS",
        "autonomy": "Autonomy",
        "budget": "Budget",
        "scope": "## Scope and evidence",
        "execution": "## Execution plan",
        "what": "What happens",
        "why": "Why",
        "produces": "Produces",
        "then": "Then",
        "verification": "## Verification and convergence",
        "boundaries": "## Boundaries and exits",
        "can": "Can",
        "cannot": "Cannot",
        "success": "SUCCESS",
        "failure": "FAILURE",
        "budget_exit": "BUDGET",
        "replan": "REPLAN",
        "approval": "## Approval",
        "approval_text": "Approval authorizes only this contract. Any material replan requires a new approval.",
    },
}


def _join(v):
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    if isinstance(v, dict):
        return "; ".join(f"{k}: {v[k]}" for k in sorted(v))
    return str(v)


def render(d):
    lang = d.get("human_language", "en")
    if lang not in LABELS:
        raise ValueError(f"reference renderer has no label map for human_language={lang!r}; render this language explicitly instead of falling back to English")
    labels = LABELS[lang]
    name = str(d.get("loop_name", "Unnamed"))
    b = d.get("budgets", {})
    lines = [labels["title"].format(name=name), "", labels["snapshot"], ""]
    lines += [
        f"**{labels['outcome']}:** {d.get('objective','')}",
        f"**{labels['deliverable']}:** {d.get('terminal_deliverable','')}",
        f"**{labels['pass']}:** {d.get('completion_condition','')}",
        f"**{labels['autonomy']}:** {d.get('side_effect_class','')}",
        f"**{labels['budget']}:** {b.get('max_iterations','?')} cycles; {b.get('max_retries','?')} retries; {b.get('max_no_progress_cycles','?')} no-progress cycles.",
        "",
        labels["scope"],
        "",
        _join(d.get("authoritative_inputs", [])) or "—",
        "",
        labels["execution"],
        "",
    ]
    for i, step in enumerate(d.get("execution_plan", []), 1):
        lines += [
            f"### {i}. {step.get('name','')}",
            f"**{labels['what']}:** {step.get('action','')}",
            f"**{labels['why']}:** {step.get('purpose','')}",
            f"**{labels['produces']}:** {step.get('output','')}",
            f"**{labels['then']}:** {step.get('next','')}",
            "",
        ]
    v = d.get("verification", {})
    lines += [
        labels["verification"], "",
        f"**{labels['pass']}:** {d.get('success_exit','')}",
        f"Verifier: {v.get('independent_terminal_verifier','')}",
        f"Progress: {d.get('progress',{}).get('evidence_definition','')}",
        f"No-progress: {d.get('no_progress_rule','')}",
        "",
        labels["boundaries"], "",
        f"**{labels['can']}:** {_join(d.get('approved_boundaries',{}))}",
        f"**{labels['cannot']}:** {_join(d.get('material_replan_triggers',[]))}",
        f"**{labels['success']}:** {d.get('success_exit','')}",
        f"**{labels['failure']}:** {d.get('failure_exit','')}",
        f"**{labels['budget_exit']}:** {d.get('budget_exit','')}",
        f"**{labels['replan']}:** {_join(d.get('material_replan_triggers',[]))}",
        "",
        labels["approval"], "",
        labels["approval_text"],
    ]
    return "\n".join(lines).rstrip() + "\n"


def main():
    p = argparse.ArgumentParser(description="Reference renderer for a Human Loop Contract")
    p.add_argument("contract", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    d = json.loads(args.contract.read_text(encoding="utf-8"))
    text = render(d)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
