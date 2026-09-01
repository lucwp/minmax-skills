# Planning Engine

## Purpose

Use for Route C, unusually complex Route B work, or Loop Mode plans with material dependencies. Separate `Plan -> Work -> Solve` and plan at the altitude where future observations do not invalidate unnecessary implementation detail.

## Task Ledger

Capture only:

- objective;
- terminal deliverable/completion condition;
- known authoritative facts;
- missing evidence;
- material scope and constraints;
- hard dependencies;
- approval/side-effect boundaries;
- unresolved user-owned directional decisions after authoritative retrieval;
- finite budgets when Loop Mode applies.

## Topology before graph

In Loop Mode, load `loop-topology.md` and choose the minimum sufficient topology before compiling work units. Do not create a DAG merely because the task is complex.

## Stable Contract, Adaptive Path

Freeze upfront:

- objective;
- terminal deliverable;
- material scope;
- authoritative constraints;
- hard dependencies;
- success criteria;
- budgets;
- tool/skill risk class;
- side-effect envelope;
- human boundaries.

Plan deliverables and material dependencies upfront. Defer implementation details whose correctness depends on evidence that will only exist during execution.

The plan is an operational hypothesis, not a rigid script. Local adaptation is allowed while all frozen approval boundaries remain unchanged. Do not pre-ask implementation choices the agent owns; use `user-interaction-protocol.md` to pause only for genuine user-owned directional decisions.

## Minimal Plan

Create the smallest work units that cover the request. Merge nodes that have no distinct outcome, tool/context boundary, dependency, verification value, or ownership value.

For Loop Mode, each material work unit must be renderable in plain language as: action -> purpose -> output -> what the output enables next. This is a clarity requirement, not a request to over-specify implementation details that depend on future evidence.

Represent only material dependencies:

```text
A: depends_on=[]
B: depends_on=[A]
C: depends_on=[]
```

Parallelize ready nodes only when ownership is non-overlapping, runtime supports safe parallelism, and context/tool/integration overhead does not erase the benefit.

## Delegation Gate

Compare:

`expected benefit`

against:

`context transfer + worker run + integration + verification`

If benefit is unclear, keep the node at root.

## Internal Work-Unit Contracts

For evaluator-optimizer work or large complex chunks, an internal completion contract may be created before executing the chunk:

1. executor states the expected chunk outcome;
2. completion evidence is defined;
3. verifier checks whether that evidence actually represents the chunk objective;
4. executor works against the contract;
5. verifier tests the result.

Do not use work-unit contracts for small tasks.

No additional human approval is required when objective, material scope, global verifier, hard budget, tool/skill risk class, and side-effect envelope remain unchanged.

## Recovery

Track only high-signal execution state such as `done`, `active`, `blocked`, `invalidated`, `evidence`, `verification_status`, and `next_ready`.

Prefer local repair. Global replan only when a material assumption changes, dependency becomes impossible, completion fails outside local repair, no-progress threshold trips, or ownership/tool selection is wrong.

In Loop Mode, any replan that crosses a frozen approval boundary must pause and be re-approved.

## Planning output

```text
Objective:
Terminal deliverable:
Completion:
Authoritative facts / evidence gaps:
Frozen boundaries:
Topology:
Topology rationale:
Nodes or adaptive work model:
Parallel ready set (only if material):
Critical dependencies:
Recovery triggers:
Unresolved user decisions / owner:
Approval boundaries:
```
