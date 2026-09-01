# Assignment Contracts

## Root Manager

Root owns user intent, routing/topology, global Task Ledger, worker selection, approvals, user-visible execution communication, directional decision gates, conflict resolution, authoritative-state verification, and final synthesis. Root is the only public voice during managed execution; follow `user-interaction-protocol.md`.

## Planner

Planner receives the smallest sufficient context and returns objective/completion, evidence gaps, minimal nodes, dependencies, ownership, tool/skill recommendation, completion tests, and recovery triggers.

Planner stops after one plan plus at most one pre-execution repair. It does not execute the task, spawn another planner, or continuously self-critique.

In Loop Mode, planner output is design-stage material only and cannot authorize execution.

## Worker

Worker receives one bounded outcome, exact ownership surface, prerequisites, relevant context refs, allowed tools/skills, completion test, runtime budget, and return schema.

Worker may adapt locally but may not redesign global topology, recursively invoke the orchestrator/Loop Mode, or independently address the user. If a genuine user-owned directional fork appears, return it to root as `decision_request`.

Return:
- `status: PASS | BLOCKED | PARTIAL`;
- outcome;
- evidence/change;
- completion-test result;
- concise blocker/residual risk;
- optional `decision_request`: decision needed, viable options/ambiguity, relevant evidence/trade-off, and whether the answer appears to remain inside current approved boundaries.

## Verifier

Use a model verifier only when deterministic/authoritative verification is insufficient and failure cost justifies another call.

Return `PASS | FAIL | UNCERTAIN`, discriminating evidence, and exact failing criterion. A verifier does not repair unless separately assigned.
