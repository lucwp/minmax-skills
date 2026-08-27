# Planning Engine

## Purpose

Use for Route C, unusually complex Route B work, or Loop Mode plans with material dependencies. Separate Plan -> Work -> Solve.

## Task Ledger

Capture only:
- objective;
- completion condition;
- known authoritative facts;
- missing evidence;
- constraints;
- approval boundaries.

## Minimal Plan

Create the smallest work units that cover the request. Merge nodes that have no distinct outcome, tool/context boundary, dependency, or ownership value.

Represent only material dependencies:

```text
A: depends_on=[]
B: depends_on=[A]
C: depends_on=[]
```

Parallelize ready nodes only when ownership is non-overlapping, runtime supports safe parallelism, and context/tool overhead does not erase the benefit.

## Delegation Gate

Compare:

`expected benefit` vs `context transfer + worker run + integration + verification`

If benefit is unclear, keep the node at root.

## Stable plan

During healthy execution the global plan stays stable. Workers may adapt locally but cannot add global nodes or spawn children unless root explicitly authorizes it.

## Recovery

Track only `done`, `active`, `blocked`, `invalidated_assumption`, `failed_completion_test`, and `next_ready`.

Prefer local repair. Global replan only when a material assumption changes, dependency becomes impossible, completion fails outside local repair, no-progress threshold trips, or ownership/tool selection is wrong.

In Loop Mode, any replan that crosses a frozen approval boundary must pause and be re-approved.

## Planning output

```text
Objective:
Completion:
Assumptions/evidence gaps:
Nodes:
  A: outcome / deps / owner / tool/skill / completion
Parallel ready set:
Critical dependency:
Recovery triggers:
Approval boundaries:
```
