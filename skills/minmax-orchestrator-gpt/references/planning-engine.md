# Planning Engine

## Purpose

Use this only for Route C or unusually complex Route B work. The planning engine uses Plan -> Work -> Solve separation with dependency-aware scheduling.

## Phase 1 — Task Ledger

Capture only:
- `objective`;
- `completion_condition`;
- `known_authoritative_facts`;
- `missing_evidence`;
- `constraints`;
- `approval_boundaries`.

Do not copy the entire conversation.

## Phase 2 — Minimal Plan

Create the smallest set of work units that covers the request.

For each candidate node ask:
- Does it have a distinct outcome?
- Does it require a different tool/context/specialist?
- Can it execute independently or does it have a real dependency?
- Would merging it with another node reduce overhead without harming reliability?

If a node has no independent value, merge it.

## Phase 3 — Dependency Compilation

Represent only material dependencies:

```text
node A: depends_on=[]
node B: depends_on=[A]
node C: depends_on=[]
```

Ready queue = all nodes whose dependencies are complete.

Parallelize ready nodes only when:
- ownership is non-overlapping;
- runtime supports safe parallel execution;
- context/tool costs do not erase the benefit.

## Phase 4 — Delegation Gate

Before creating a worker, compare:

`expected benefit` vs `context transfer + worker run + integration + verification`

If benefit is unclear, keep the node at root.

## Phase 5 — Work

Workers execute bounded nodes. The global plan remains stable during healthy progress.

Workers can adapt locally to tool observations but cannot add global nodes or spawn children unless root explicitly authorizes it.

## Phase 6 — Root Solve/Synthesis

Root receives condensed worker outputs and:
- checks required completion signals;
- resolves conflicts;
- fetches authoritative live state when needed;
- produces one integrated answer/artifact/action.

## Recovery

Maintain only:
- `done`;
- `active`;
- `blocked`;
- `invalidated_assumption`;
- `failed_completion_test`;
- `next_ready`.

Trigger one bounded recovery/replan by default when:
- stall threshold is reached;
- a dependency becomes impossible;
- a material assumption changes;
- completion test fails;
- ownership boundary was wrong.

Recovery output must identify:
- what changed;
- which nodes are invalid;
- replacement/narrowed nodes;
- updated dependencies;
- whether continuation is still economical.

Do not regenerate the entire plan if only one node changed.

## Planning Output

Return structure, not essay:

```text
Objective:
Completion:
Assumptions/evidence gaps:
Nodes:
  A: outcome / deps / owner / model / tool / completion
  B: ...
Parallel ready set:
Critical dependency:
Recovery triggers:
```

The exact token length is a tuning parameter, not a scientific rule. Prefer the shortest plan that preserves execution correctness.
