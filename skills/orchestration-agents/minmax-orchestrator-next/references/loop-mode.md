# Loop Mode

## Purpose

Use Loop Mode only when the user explicitly asks to execute the current task with a loop or equivalent iterative autonomous/semi-autonomous behavior.

This mode integrates the control-loop principles of Max Milian's `loop-engineering` skill:

- Source: https://github.com/maxmilian/loop-engineering
- Author: Max Milian (`maxmilian`)
- License: MIT

When `loop-engineering` is installed and callable, use it as the specialist authority for loop design/review. MinMax Orchestrator NEXT remains the root control plane for task routing, domain-skill coordination, approvals, side-effect governance, and final synthesis. If the external skill is unavailable, use this reference as the compatibility protocol and do not claim it was invoked.

## Hard lifecycle

Loop Mode has two stages:

`DESIGN STAGE -> USER APPROVAL -> EXECUTION STAGE`

The design stage may perform read-only inspection/retrieval needed to design a correct loop. It must not perform the substantive task, mutate target state, create the requested final deliverable, or start iterative execution.

### Design stage

Always run:

`PLAN -> COMPILE LOOP -> PREFLIGHT -> PRESENT FOR APPROVAL -> STOP`

### Execution stage

Only after explicit approval of the presented contract:

`EXECUTE CYCLE -> VERIFY -> CONTINUE / LOCAL REPAIR / PAUSE FOR REPLAN / EXIT -> SYNTHESIZE`

The original instruction to "use a loop" is **not** approval of the loop contract. Silence is not approval. Prior generic authorization is not approval of a newly compiled plan.

Approval must unambiguously refer to the presented plan/loop, such as "aprovado", "pode executar", "pode seguir com esse loop", or equivalent.

## 1. PLAN

Create one stable execution plan. Use `planning-engine.md` when material dependencies exist.

Capture:
- objective;
- terminal deliverable;
- authoritative inputs and evidence gaps;
- constraints and non-goals;
- work units/dependencies;
- domain skills/tools;
- side-effect/approval boundaries;
- completion condition.

The plan becomes the task specification sent into the loop. Never use a vague objective such as "keep improving until perfect".

## 2. COMPILE LOOP

Convert the plan into an explicit bounded contract:

```text
Loop objective:
Terminal deliverable:
Authoritative inputs:
Cycle observation:
Cycle action:
Verification:
Success exit:
Failure exit:
Budget exit:
Iteration/retry/time budgets:
No-progress rule:
Local-repair rule:
Material-replan triggers:
Human escalation boundary:
Side-effect envelope:
Durable state:
Final synthesis requirement:
```

Required properties:

### Machine-checkable completion
Prefer objective completion evidence. Examples:
- tests pass;
- expected files exist and validators pass;
- render QA passes defined criteria;
- authoritative state matches intended postcondition;
- required entities are covered with named sources.

When deterministic verification is impossible, define a bounded semantic rubric with explicit pass/fail criteria.

### Independent verification
Prefer tests, schemas, renders, authoritative read-back, diffs, receipts, or dedicated validators over executor self-report.

### Proxy hardening
Ask: "How could the executor make the verifier green without satisfying the actual goal?" Protect the verifier/test/config from being weakened where practical.

### Finite budgets
Define finite iteration, retry, no-progress, and time/cost limits appropriate to runtime capabilities. Never use an unbounded "until perfect" instruction.

### Durable state
For long loops, persist/reconstruct compact state outside conversational history using files, IDs, manifests, diffs, or structured progress records.

## 3. PREFLIGHT

Before asking for approval, confirm:
- objective and terminal deliverable are explicit;
- success, failure, and budget exits exist;
- verification exists and is sufficiently independent;
- finite budgets exist;
- no-progress detection exists;
- required inputs are available or retrievable;
- required tools/skills are available or a fallback is defined;
- side effects comply with `production-safety.md`;
- irreversible/high-consequence actions remain human-gated;
- child workers cannot recursively invoke the orchestrator or Loop Mode;
- the contract does not authorize broader work than the user's request.

If preflight fails, repair the contract once where possible. If a load-bearing input/runtime primitive is missing, present the blocker rather than asking approval for a knowingly invalid loop.

When a machine-readable contract is useful, validate it with `scripts/validate_loop_contract.py` before presenting it.

## 4. PRESENT FOR APPROVAL

Present a compact execution-complete contract containing:
- objective and deliverable;
- work plan / material dependencies;
- tools and domain skills;
- success and verification criteria;
- iteration/retry/time/cost budgets where relevant;
- no-progress rule;
- repair/replan rules;
- side-effect envelope and human boundaries;
- all terminal exits.

Then stop. Do not execute the substantive task or any loop cycle in that same turn.

The approval gate applies even if all intended execution is read-only. It is a Loop Mode contract gate, not merely a write-safety gate.

## 5. APPROVAL HANDLING

After the user approves:
- bind approval to the presented contract;
- treat objective, deliverable, material scope, success criteria, hard budgets, tool/skill risk class, and side-effect envelope as frozen approval boundaries;
- begin execution only within those boundaries.

If the user edits the contract before approval, revise and re-present it.

If approval is ambiguous, do not execute; ask only for the minimum confirmation needed.

## 6. EXECUTE CYCLE

Each cycle must be small enough to verify.

1. reconstruct the minimum current state;
2. observe the current completion gap;
3. perform the smallest high-value approved action;
4. record material state/evidence change;
5. run the defined verifier;
6. choose exactly one transition: `success`, `continue`, `local_repair`, `material_replan`, `fail/escalate`, or `budget_exit`.

Use Route A/B/C internally as appropriate. Loop Mode does not imply multi-agent execution.

## 7. VERIFY AND TRANSITION

- `success`: terminal verifier establishes completion -> exit.
- `continue`: measurable progress exists and next approved action remains valid -> next cycle.
- `local_repair`: verifier fails but repair stays inside approved boundaries -> one changed-strategy repair, then re-verify.
- `material_replan`: a frozen approval boundary must change -> pause execution immediately.
- `fail/escalate`: unrecoverable blocker, ambiguous unsafe write, missing primitive, or human boundary -> stop.
- `budget_exit`: any hard budget trips -> stop with best verified partial state.

Reasoning text alone is not progress. Progress requires new evidence, changed artifact/state, completed action, resolved dependency, or verifier movement.

## 8. MATERIAL REPLAN = NEW APPROVAL

A local repair may continue without new approval only if all frozen approval boundaries remain unchanged.

A fresh approval is mandatory if a replan changes any of:
- objective;
- terminal deliverable;
- material scope or dependency topology;
- success/verification criteria;
- hard iteration/time/cost budget;
- tool/skill class in a way that changes capability or risk;
- side-effect/write envelope;
- human approval boundary.

When material replanning is required:

`PAUSE -> REPLAN -> PREFLIGHT -> PRESENT REVISION -> STOP -> WAIT FOR APPROVAL`

## 9. SIDE EFFECTS

Loop Mode never expands the autonomous write envelope.

For state-changing work, follow `production-safety.md` and validate an action manifest. Never retry an ambiguous write until authoritative read-back proves whether the original effect occurred.

Loop approval is not blanket approval for separately gated external or high-consequence actions.

## 10. FINAL SYNTHESIS

When the loop exits, root returns one integrated result containing:
- what was completed;
- terminal verification evidence;
- any remaining gap or budget/approval exit;
- the final artifact/action/result.

Do not dump cycle transcripts unless requested.
