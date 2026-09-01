# Loop Topology Gate

## Purpose

Choose the minimum sufficient loop topology before compiling a Loop Contract. Topology is a control-flow decision, not a prestige signal.

Core rule:

`expected outcome gain + parallelism gain + risk reduction`

must materially exceed:

`coordination + context + worker + latency + token + integration + verification cost`

When the gain is uncertain, choose the simpler topology.

## Topology classes

### deterministic_prompt_chain

Use when the required steps are known, ordered, and mostly deterministic.

- keep execution sequential;
- do not add autonomy merely because the task has several steps;
- use deterministic verification at the relevant boundaries.

### router

Use when different input classes require substantially different processes and the classification can be made with useful confidence.

- route once when possible;
- keep branches independently bounded;
- do not use a router when one adaptive executor can handle the variation cheaply.

### single_adaptive_loop

Use when one executor can observe the current gap, choose the next useful action, verify progress, and continue toward a bounded endpoint.

This is the default for open-ended Loop Mode work that does not justify multiple workers or an evaluator-optimizer topology.

### parallel_sectioning

Use when work units are genuinely independent and parallel execution materially shortens the critical path or provides valuable context isolation.

- partition by non-overlapping outcome or evidence set;
- avoid parallelizing tightly coupled steps;
- root integrates the results.

### parallel_independent_review

Use only when independent judgments materially reduce risk or variance.

Examples: high-consequence review, ambiguous qualitative scoring, or robustness checks where correlated reasoning is a known failure mode.

Do not use merely to "think more" or manufacture consensus.

### orchestrator_workers

Use when at least one concrete coordination benefit exists and simpler topologies are insufficient, for example:

- subtasks cannot be fully known upfront;
- substantial breadth requires separate context windows;
- multiple specialist tools/domains must be explored;
- true parallelism reduces the critical path;
- independent specialist ownership prevents likely rework.

Task complexity alone is not sufficient. Every worker must still pass the Delegation Gate. Child workers must not recursively invoke the Orchestrator or Loop Mode.

### evaluator_optimizer

Use only when all are true:

1. there is an artifact/output that can improve iteratively;
2. relatively stable, gradable criteria exist;
3. critical feedback is likely to improve the artifact;
4. the expected improvement justifies extra calls.

Good fits include design, premium copy/artifacts, documents, code with QA, and other work where `critique -> repair -> re-evaluate` produces verifiable gain.

Do not use evaluator-optimizer when a deterministic verification pass is sufficient. The evaluator must not enter an unbounded repair loop.

## Selection logic

Classify by the **dominant mechanism that creates reliable progress**, then apply the Complexity Gate. Do not use a first-match decision tree: several classes may be technically possible for the same task.

Use these questions as discriminators:

- If the path is known and ordered, prefer `deterministic_prompt_chain`.
- If classification selects among materially different processes, use `router`.
- If progress mainly comes from one executor observing the gap and choosing the next action, use `single_adaptive_loop`.
- If progress mainly comes from independent sections completing concurrently, use `parallel_sectioning`.
- If the value is variance/risk reduction from independent judgments, use `parallel_independent_review`.
- If the value is dynamic decomposition, specialist ownership, breadth, or context isolation, use `orchestrator_workers`.
- If the value is repeated critique -> repair -> re-evaluate against stable gradable criteria, use `evaluator_optimizer`, even though a single executor could technically perform the iterations.

When two classes remain plausible, choose the simpler one unless the more complex class has a concrete expected gain that exceeds its added cost. Choose the smallest class that captures the load-bearing control flow.

## Complexity Gate

Before selecting a topology above `single_adaptive_loop`, record:

- what a simpler topology cannot do reliably;
- the concrete expected gain;
- the added coordination/verification cost;
- why the gain is expected to exceed that cost.

Reject escalation when the only rationale is task importance, task length, "more thinking", model prestige, or vague robustness.

## Loop Contract fields

The Internal Contract must contain:

```text
topology
topology_rationale
```

`topology_rationale` must explain why the chosen class is sufficient and, for complex topologies, why the nearest simpler class is not.
