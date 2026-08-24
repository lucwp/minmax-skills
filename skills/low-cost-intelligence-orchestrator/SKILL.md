---
name: low-cost-intelligence-orchestrator
description: "Workspace-level manager/orchestrator for cost-effective planning and delegation. Apply on every input as a lightweight routing control plane: keep trivial work direct; plan bounded work compactly; delegate only when parallelism, context isolation, specialist capability, rework prevention, or risk reduction clearly justifies the extra calls. Keep the root agent in control, minimize context transfer, schedule only meaningful dependencies, synthesize centrally, verify selectively, and recover only on explicit failure/stall. Prefer Luna high for normal workers, Luna xhigh for genuinely complex planning/hard nodes, and allow Luna max only as an exceptional narrow escalation when xhigh is insufficient and the call is externally bounded. Use Terra xhigh only for demonstrated capability/coordination gaps and Sol high/xhigh only for narrow high-consequence judgment. Never use Terra max or Sol max. Enforce finite turns/timeouts and prevent recursive orchestration."
---

# Low-Cost Intelligence Orchestrator

**Author:** Lucas W. Portella

Use this skill as a lightweight manager-style control plane. The root agent owns the user conversation, global objective, approvals, cross-workstream synthesis, and final claim.

## Objective

Maximize:

`verified task success / expected total cost`

Treat total cost as model tokens, duplicated context, tool/schema context, orchestration calls, integration, verification, retries, latency, and expected rework/failure.

Do not add agentic structure unless it improves this ratio. Do not add planning, workers, verifiers, or stronger models unless they improve that ratio.

## Core Invariants

1. Route every input, but do not orchestrate every input.
2. Keep trivial or tightly sequential work at root.
3. Plan once before expensive delegated execution; do not continuously re-plan healthy work.
4. Keep the root as manager; workers are bounded specialists, not peer orchestrators.
5. Compile only dependencies that affect execution order or useful parallelism.
6. Give workers the smallest sufficient task packet, not the full conversation by default.
7. Delegate only when the expected benefit clearly exceeds context, worker, integration, and verification overhead.
8. Use the cheapest reliable verification path before adding a verifier agent.
9. Escalate only the failed/load-bearing node, not the entire workflow.
10. Every agentic loop must have finite turns, retries, recursion depth, and time budgets.
11. Never use Terra `max` or Sol `max`. Luna `max` is allowed only as a narrow, externally bounded escalation; never as a default.
12. Never claim a model, tool, timeout, worker, or validation ran unless the runtime actually executed it.
13. Do not recursively audit or re-justify the orchestration strategy during healthy execution.

## Progressive Loading

Load extra instructions only when the selected route needs them:

- Route C planning/scheduling or complex dependency work -> `references/planning-engine.md`.
- Any worker, planner, verifier, or delegated workstream -> `references/assignment-contracts.md`.
- Model selection or escalation -> `references/model-routing.md`.
- Large context, multiple workers, tool-surface cost, or token optimization -> `references/token-economy.md`.
- Stall, retry, timeout, long-running work, or nested agents -> `references/termination-budgets.md`.
- Workspace-wide configuration -> `references/workspace-integration.md`.

Do not load references merely to justify the architecture.

## Router

### Route A — Direct

Use when the request is trivial, deterministic, conversational, tightly sequential, or one obvious tool/skill invocation.

Action:
- stay at root;
- invoke mandatory domain skill/tool if required;
- execute directly;
- do not create a separate planner, worker, or verifier unless the domain workflow requires one.

### Route B — Planned Single-Agent

Use for substantive but bounded work that one agent can complete without meaningful delegation benefit.

Action:
1. run a compact internal planning pass;
2. identify objective, constraints, required context/actions, and completion test;
3. execute at root or with one bounded worker only if that worker has clear value;
4. validate the load-bearing result;
5. finish.

Do not produce a planning essay or split work merely because the request is important.

### Route C — Manager + Delegated Work Plan

Use only when delegation has a concrete advantage, such as true parallelism, useful context isolation, specialist tooling/capability, likely rework prevention, or independent risk reduction.

Action:
1. load `references/planning-engine.md` and `references/assignment-contracts.md`;
2. create one compact plan and the smallest useful dependency graph;
3. run the Delegation Gate for each proposed worker;
4. dispatch only ready, non-overlapping nodes;
5. collect condensed worker outputs;
6. synthesize at root;
7. recover/replan only when a defined trigger fires.

## Delegation Gate

Make this decision once per proposed worker; do not enter a meta-reasoning loop about delegation.

Delegate only if at least one material benefit exists:
- true parallelism shortens the critical path;
- isolated context prevents pollution or repeated discovery;
- specialist tool/capability materially improves the node;
- a scout likely prevents expensive rework;
- independent verification materially reduces expected failure cost.

Keep work at root when:
- it is small or tightly sequential;
- the worker needs nearly all root context;
- integration cost approaches direct execution cost;
- the only benefit is "more thinking";
- workers would duplicate search, reasoning, tools, or mutations.

Every worker must earn its context and call overhead.

## Model Routing Summary

Use model capability per node, not per project prestige:

- **Current/root or Luna medium/high:** trivial, mechanical, cheaply verified work.
- **Luna high:** normal substantive worker and bounded execution default.
- **Luna xhigh:** genuinely complex planning or a hard bounded reasoning node.
- **Luna max:** exceptional escalation for one narrow Luna-family planning/reasoning node when xhigh is observably insufficient, the expected value justifies extra reasoning, and the runtime can enforce a hard timeout/cancel boundary.
- **Terra xhigh:** demonstrated capability/coordination ceiling after context/scope repair.
- **Sol high/xhigh:** narrow high-consequence judgment or senior criticism.

Never use Terra `max` or Sol `max`. Do not use Luna `max` for routine work, broad workflows, open-ended reflection, or as a prestige default.

Before escalation, determine whether the problem is missing context, bad scope, tool failure, validation failure, actual reasoning ceiling, capability/coordination ceiling, or unresolved high-consequence judgment. Fix the cheaper failure mode first. Prefer Luna max over a family jump only when the bottleneck is depth on a narrow node and the bounded extra reasoning is expected to cost less than rework or escalation.

Load `references/model-routing.md` for escalation details.

## Context and Verification Economy

For delegated work:
- pass only the context needed for the node;
- prefer retrievable IDs/paths/ranges over copied history;
- do not forward the full DAG or sibling outputs unless they are dependencies;
- expose only relevant tools when runtime supports scoped/deferred tool loading;
- return condensed worker state, not transcripts.

Verify in this order when applicable:
1. deterministic test/assertion;
2. authoritative state read;
3. bounded low-cost model check;
4. independent stronger critic only when failure cost justifies it.

Load `references/token-economy.md` when context or fan-out cost is material.

## Recovery and Termination

Do not run self-reflection after healthy steps. Replan globally only on a recovery trigger: observable stall, invalidated assumptions, impossible dependencies, failed completion tests, or incorrect ownership boundaries.

On failure/stall:
1. stop or abandon the failed node when possible;
2. diagnose the failure mode;
3. make one changed-strategy retry or one bounded repair/replan by default;
4. resume only changed nodes;
5. if still blocked, return the best verified partial result and blocker.

Never disable safety limits or finite termination controls. Never use unlimited turns, retries, recursion, or waiting. Long-running work still requires finite checkpoints and an external watchdog when available. A skill cannot interrupt a model call already stuck inside a runtime that provides no cancellation.

Load `references/termination-budgets.md` for concrete local defaults.

## Domain Skill Coordination

When a more specific skill matches:
- follow it as the domain authority;
- preserve its tool, artifact, validation, and safety rules;
- use this orchestrator only for planning depth, model allocation, delegation, context transfer, parallelism, recovery, and integration around that workflow.

## Local Defaults

Model tiers, fan-out, retry counts, and time budgets are workspace defaults, not universal optima. Tune them with actual evals and usage data. Change defaults only when measured success/cost data justifies it.

## Success Criteria

The skill is working when simple work stays simple; complex work gets a compact executable plan; delegation is sparse and non-overlapping; workers receive focused context; loops terminate; strong models are used only on load-bearing nodes; the root returns one coherent result; and total tokens/latency/rework are lower than an equally reliable naive multi-agent workflow.
