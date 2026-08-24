# Assignment Contracts

## Root Manager Contract

Root owns:
- user intent and conversation;
- routing and topology;
- global Task Ledger;
- worker selection;
- approval boundaries;
- conflict resolution;
- authoritative-state verification;
- final synthesis and claim.

Root does not delegate these responsibilities.

## Planner Contract

Planner receives the smallest context sufficient to decompose the task.

Planner returns:
- objective/completion;
- evidence gaps;
- minimal nodes;
- dependencies;
- ownership;
- model/tool/skill recommendation;
- completion test per load-bearing node;
- recovery triggers.

Planner stops after one plan plus at most one pre-execution repair when the sanity check fails.

Planner does not execute the task, spawn another planner, or continuously self-critique.

## Worker Contract

Worker receives:
- one bounded outcome;
- exact ownership surface;
- direct prerequisites;
- relevant context references;
- tools/skills it may use;
- completion test;
- runtime budget;
- return schema.

Worker may adapt locally but may not redesign global topology.

Worker returns:
- `status: PASS | BLOCKED | PARTIAL`;
- outcome;
- evidence or changed surface;
- completion-test result;
- concise blocker/residual risk.

## Verifier Contract

Use only when deterministic or authoritative verification is insufficient and failure cost justifies another model call.

Verifier receives output plus the minimum criteria/evidence needed to judge it.

Return:
- `PASS | FAIL | UNCERTAIN`;
- concise discriminating evidence;
- exact failing criterion if any.

Verifier does not repair the work unless separately assigned.

## Workstream Owner Exception

A worker may coordinate child nodes only when root explicitly authorizes:
- bounded scope;
- maximum children;
- finite nested turns;
- non-overlapping ownership;
- return contract.

Otherwise delegation depth is one.
