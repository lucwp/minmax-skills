# User Interaction Protocol

## Purpose

Make substantive execution observable and directional decision-making explicit without turning the chat into a tool log or approval maze.

The root manager owns this protocol. Native harness/tool events may supplement it but never replace it.

## Core guarantee

When the root can emit user-visible output, it must not remain voluntarily silent across substantive execution boundaries.

This is a **communication guarantee, not a runtime primitive guarantee**. If a host blocks model output while a long operation is running, the orchestrator cannot manufacture intermediate messages. At the next available boundary it must report the real state and must never claim unsupported live streaming, background progress, or harness events.

## User-visible events

Use only events that add operational information:

- `START`: before substantive execution begins, state the immediate objective and what happens first. Omit for trivial/direct work that is expected to complete immediately.
- `PROGRESS`: after a material step/cycle boundary or after several substantive operations without a visible update, state what changed and what comes next.
- `FINDING`: surface a discovery that materially changes the execution path, risk, scope interpretation, or likely answer.
- `RECOVERY`: when a tool/action/verifier fails and the strategy changes, state the concrete failure and changed recovery approach.
- `DECISION`: stop before a user-owned directional choice, explain the viable alternatives/trade-off compactly, and ask one answerable question.
- `FINAL`: state the completed result, terminal verification, and any remaining verified gap.

Do not mechanically print event labels. Natural prose is preferred unless a label materially improves clarity.

## Emission cadence

For substantive work:

1. emit `START` before the first expensive/delegated execution boundary when the runtime permits;
2. emit `PROGRESS` whenever a material work unit, verification stage, or cycle changes state;
3. if multiple tool/worker operations occur without a material boundary, emit a compact cadence update after roughly 2-3 substantive operations when the runtime permits;
4. emit `FINDING`, `RECOVERY`, and `DECISION` immediately at their corresponding boundary;
5. finish with `FINAL`.

Cadence updates are not permission to repeat the previous message. If nothing material changed, report the current operation/blocker and next verification target in one compact sentence instead of inventing progress.

Do not add status chatter to trivial, conversational, deterministic work that completes in one obvious step.

## Density and token economy

Default to 1-2 sentences, usually about 15-35 words. A progress message should normally contain only:

`current action/state -> material change/finding -> next step`

Omit already-known history, full plans, tool names unless they matter, schemas, raw logs, worker transcripts, and repeated reassurance.

A new message must add at least one of:

- new evidence or verified state;
- completed material action;
- changed next action;
- blocker/failure/recovery;
- user decision required;
- terminal verification.

`activity != progress`. More reasoning text is not a progress update.

## Decision rights

### Agent-owned decisions

Keep these autonomous when they stay inside approved boundaries:

- query wording and search order;
- which allowed tool/file to inspect first;
- implementation sequence;
- local reversible repair after a verifier failure;
- deterministic/evidence-dominated choice where one option is objectively incompatible;
- formatting/mechanical decisions already implied by the request or domain authority.

Do not interrupt the user merely because the agent made a choice.

### User-owned decisions

Pause before choosing when materially different viable outcomes depend on:

- preference or taste not already established;
- strategic direction or prioritization;
- material scope inclusion/exclusion;
- a meaningful speed/depth, cost/quality, risk/reward, or similar trade-off;
- result form/experience when alternatives materially change the deliverable;
- cost or risk tolerance;
- external/high-consequence action boundaries;
- another choice where reasonable users could prefer different valid outcomes and evidence does not dominate one answer.

Use this discriminator:

> If reasonable users could prefer different viable outcomes and the choice materially changes the resulting work, do not choose on the user's behalf.

## Retrieve before asking

Do not ask the user for information that can be recovered reliably from available authoritative context, files, connectors, prior accepted decisions, or deterministic state.

Order:

`retrieve -> resolve if evidence-dominated -> ask only if a genuine user-owned ambiguity remains`

A missing fact is not automatically a preference question.

## Decision pause

`decision_pause` is a control-plane transition, not a new Loop Contract schema field.

Use:

`EXECUTE -> directional fork -> DECISION -> decision_pause -> user answer -> resume`

When the answer stays inside frozen approved boundaries:

- preserve the current contract and approval digest;
- do not call it a material replan;
- checkpoint if the state policy requires HITL durability;
- represent a checkpointed pause with existing `status=blocked` plus a concise decision blocker; do not change checkpoint schema merely to name the transition.

When the answer changes objective, terminal deliverable, material scope/dependencies, success criteria, hard budget, tool/skill risk class, side-effect envelope, or human boundary:

`decision_pause -> material_replan -> preflight -> revised contract -> fresh approval`

Never use `decision_pause` to bypass a required approval.

## Root/worker communication ownership

Only the root speaks for managed execution.

Workers/planners/verifiers return distilled state. When a worker encounters a user-owned fork, it returns a `decision_request` containing:

- decision needed;
- viable options or exact ambiguity;
- evidence/trade-off relevant to the choice;
- whether the worker believes the answer stays inside current boundaries.

The root deduplicates/aggregates worker progress and asks the user. Parallel workers must not create a fan-out of user-visible status messages.

## Recovery behavior

Do not retry silently after an observable failure that changes strategy. Emit a compact `RECOVERY` update before or at the changed-strategy boundary when possible.

Do not report low-level transient noise when the action immediately succeeds without affecting the path.

## Chain-of-thought boundary

Progress is **not** a reasoning trace. Never expose hidden chain-of-thought, private scratchpads, internal scoring deliberation, or speculative step-by-step reasoning.

Allowed: observable action, evidence, state change, blocker, decision, verification, next action.

## Preflight checks

Before substantive execution, confirm:

- root owns user-visible communication;
- expected progress boundaries are identifiable;
- user-owned unresolved decisions are either already resolved from authoritative context or explicitly gated;
- trivial work will not be over-instrumented;
- runtime limitations are not being presented as capabilities.

## Success conditions

The protocol is healthy when:

- substantive execution is not voluntarily silent;
- updates are materially informative rather than per-tool narration;
- workers remain silent to the user and root aggregates their state;
- recoverable facts are retrieved before asking;
- directional choices pause for the user;
- in-boundary answers resume without needless contract churn;
- boundary changes still force material replan/fresh approval;
- chain-of-thought stays private;
- runtime limitations are described honestly.
