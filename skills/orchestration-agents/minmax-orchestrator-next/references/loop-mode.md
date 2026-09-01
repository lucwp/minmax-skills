# Loop Mode

## Purpose

Use Loop Mode only when the user explicitly asks to execute the current task with a loop or equivalent bounded iterative autonomous/semi-autonomous behavior.

This mode incorporates the load-bearing principles of Max Milian's `loop-engineering` project: machine-checkable completion, independent verification, explicit exits, finite budgets, context economy, durable state when required, and human gates for consequential actions. If that external skill is unavailable, use this reference as the compatibility protocol and do not claim it was invoked.

- Source: https://github.com/maxmilian/loop-engineering
- Author: Max Milian (`maxmilian`)
- License: MIT

MinMax Orchestrator NEXT remains the root control plane for routing, topology, approvals, user-visible execution communication, directional decision gates, domain-skill authority, side effects, recovery, and final synthesis. During Loop Mode execution, always apply `user-interaction-protocol.md`.

## Hard lifecycle

Loop Mode has two stages:

`DESIGN STAGE -> USER APPROVAL -> EXECUTION STAGE`

The design stage may perform read-only inspection/retrieval needed to design a correct loop. It must not perform the substantive task, mutate target state, create the requested final deliverable, or start iterative execution.

### Design stage

Always run:

`TASK LEDGER -> TOPOLOGY GATE -> PLAN AT RIGHT ALTITUDE -> COMPILE INTERNAL CONTRACT -> PREFLIGHT -> RENDER HUMAN CONTRACT -> USER APPROVAL -> STOP`

### Execution stage

Only after explicit approval of the presented contract:

`CHECKPOINT IF REQUIRED -> EXECUTE CYCLE -> ACTION VERIFY -> CYCLE VERIFY -> RECORD PROGRESS -> CHECKPOINT IF REQUIRED -> TRANSITION -> TERMINAL VERIFY -> SYNTHESIZE`

The original instruction to "use a loop" is **not** approval of the loop contract. Silence is not approval. Prior generic authorization is not approval of a newly compiled plan.

## 1. TASK LEDGER

Capture:

- objective;
- terminal deliverable;
- authoritative inputs and evidence gaps;
- material scope, constraints, and exclusions;
- hard dependencies;
- completion condition;
- approval and side-effect boundaries;
- unresolved user-owned directional decisions after authoritative retrieval.

Do not use vague objectives such as "keep improving until perfect".

## 2. TOPOLOGY GATE

Always load `loop-topology.md` in Loop Mode and choose exactly one primary topology class:

- `deterministic_prompt_chain`;
- `router`;
- `single_adaptive_loop`;
- `parallel_sectioning`;
- `parallel_independent_review`;
- `orchestrator_workers`;
- `evaluator_optimizer`.

Use the minimum sufficient complexity. Classify by the dominant mechanism that creates reliable progress rather than a rigid first-match tree. `single_adaptive_loop` is the default for open-ended loops whose main mechanism is adaptive action selection and that do not justify a more expensive topology.

Loop Mode does not imply multi-agent execution. Task complexity alone does not justify orchestrator-workers. Evaluator-optimizer requires a gradable artifact and useful critique/repair economics; choose it when critique -> repair -> re-evaluate is the load-bearing mechanism, even if one executor could technically run the iterations.

## 3. PLAN AT THE RIGHT ALTITUDE

Use `planning-engine.md` when material dependencies exist.

Freeze approval-relevant outcomes and boundaries, but do not over-specify implementation details that depend on future observations.

The execution path may adapt locally without replanning when it remains inside the frozen contract.

## 4. COMPILE INTERNAL CONTRACT

New contracts **must use schema `1.4`**. Schemas `1.0`–`1.3` are legacy and may be validated only through an explicit resume/migration path. Never emit an older schema for a new loop and never downgrade a contract to avoid current hard gates.

Minimum `1.4` shape:

```text
schema_version
mode
contract_id
contract_digest
loop_name
human_language
objective
terminal_deliverable
completion_condition

execution_plan:
  - name
    action
    purpose
    output
    next
    effect
    requires_human_approval

topology
topology_rationale

complexity_gate:
  simpler_topology_considered
  limitation
  benefit_types
  expected_gain
  added_costs
  decision

authoritative_inputs
cycle_observation
cycle_action

progress:
  evidence_definition
  allowed_evidence_types
  fingerprint
  max_no_progress_cycles

verification:
  method
  evidence
  layers:
    action
    cycle
    terminal
  independent_terminal_verifier
  terminal_actor
  evidence_source
  proxy_hardening:
    attack_path
    protected_elements
    thresholds_frozen
    executor_can_modify_verifier

success_exit
failure_exit
budget_exit
budgets
no_progress_rule
local_repair_triggers
material_replan_triggers
human_escalation_boundary
side_effect_class

state:
  mode
  store
  version_marker
  resume_strategy

approved_boundaries
domain_skills
tools
final_synthesis_requirement
approval
```

### Contract identity and approval binding

Before rendering the Human Contract:

1. assign a stable `contract_id`;
2. compute `contract_digest` from the canonical immutable contract payload using `scripts/validate_loop_contract.py --stamp-digest`;
3. present the Human Contract generated from that payload;
4. when the user approves, the **root approval boundary** captures that digest outside the executor-editable contract;
5. set `approval.status=approved`, preserve the user approval reference, and bind `approval.approved_contract_digest` to that captured digest;
6. before execution or resume, validate with `--approved-digest <captured_digest>`;
7. if an approved `external_write` step may run without a per-step human gate, capture the explicit preauthorization reference outside executor-editable state and validate with `--external-write-preauthorization-ref <captured_ref>`.

A matching string inside the contract is not sufficient evidence of approval. If the external approved digest no longer matches, approval is invalidated and execution stops.

### Semantic hard gates

Schema `1.4` structures the load-bearing semantics instead of leaving them as prose-only claims:

- every execution step declares its side-effect `effect`; it cannot exceed the global side-effect envelope;
- complex topologies require a structured Complexity Gate with a concrete benefit type and a genuinely simpler alternative considered;
- progress must use approved evidence types and its no-progress limit must equal the frozen budget;
- terminal verification declares an independent actor and evidence source; executor self-report is not a terminal actor;
- proxy hardening identifies an attack path, protected verifier elements, frozen thresholds, and whether the executor may modify the verifier.

### Machine-checkable completion

Prefer objective completion evidence: tests, schemas, expected files, render QA, authoritative state, receipts, or named-source coverage.

When deterministic verification is impossible, use a bounded semantic rubric with explicit pass/fail criteria.

### Progress evidence

`activity != progress`.

Progress requires at least one material change such as new required evidence, a resolved dependency, a verified artifact change, an authoritative state change, a completed action, verifier movement, or a removed blocker. Reasoning text alone is not progress. Use a compact **progress fingerprint** when practical to detect repeated states, actions, or unchanged verifier conditions.

### Proxy hardening

For every contract ask: `How could the executor make this verifier pass without satisfying the actual objective?`

Protect the verifier structurally whenever possible. A prose reminder such as “be careful” is not proxy hardening.

### Finite budgets

Define finite iteration, retry, no-progress, and time/cost limits appropriate to runtime capabilities. Never use an unbounded “until perfect” instruction.

### Step-level side-effect gates

Every schema `1.4` execution step declares `effect` and `requires_human_approval`. An `irreversible_high_consequence` step must always set `requires_human_approval=true` and stop at that gate before acting. An approved `external_write` step that is allowed to run without a per-step human gate requires `approval.external_write_preauthorization_ref` **and** a matching root-captured `--external-write-preauthorization-ref`; a string written by the executor is not proof of preauthorization. Loop approval alone is not a substitute for explicit external-write preauthorization. The reference validator also rejects obvious external mutations hidden inside a `read_only` action.

## 5. STATE POLICY

Load `loop-state.md` and select `ephemeral` or `checkpointed`.

Use checkpointed state for long-running work, HITL interruption, expensive completed work, writes, parallel work, context-reset risk, or external receipts/read-back. Runtime checkpoint state is separate from the immutable contract and must validate with `scripts/validate_loop_checkpoint.py` against both the contract and the external approved digest.

Do not use conversation history as the only durable memory.

## 6. LAYERED VERIFICATION

Define three semantics:

### Action Verification

Confirms the just-executed action produced its intended immediate effect.

### Cycle Verification

Confirms material progress occurred, invariants remain intact, and another cycle is still justified.

### Terminal Verification

Independently confirms the terminal deliverable satisfies the global completion condition.

Do not accept executor self-report as terminal evidence when a better verifier is available.

## 7. PREFLIGHT

Before asking for approval, verify:

### Contract

- loop name, objective, deliverable, scope, success/failure/budget exits;
- finite budgets;
- material dependencies and frozen boundaries.

### Human clarity

- the loop has a descriptive task-specific name;
- the user-facing language is explicit (`pt-BR`, `en`, or another identified language);
- every material step makes action, purpose, output, and handoff/next logic understandable;
- generic labels such as `research`, `analyze`, `improve`, or `validate` are not carrying the plan by themselves;
- a user can understand the execution path without knowing topology or orchestration terminology;
- Portuguese rendering satisfies the embedded MinMax PT-BR Output principles; English rendering satisfies the embedded Humanizer principles;
- clarity is repaired before approval if the contract is technically valid but hard to follow.

### Topology

- topology class is explicit;
- a simpler topology was considered;
- any parallelism/delegation has concrete benefit;
- evaluator-optimizer has stable criteria if selected;
- the root performs a bounded **semantic task-truth check** for claims the deterministic validator cannot prove (for example, whether true parallelism or specialist isolation actually exists). Structured benefit fields are evidence of an explicit decision, not proof that the claimed task condition is true.

### Verification

- method/evidence are defined;
- action/cycle/terminal semantics exist;
- terminal evidence is sufficiently independent;
- proxy-hardening is adequate;
- thresholds/coverage cannot be silently weakened.

### State

- ephemeral/checkpointed mode is appropriate;
- resume strategy exists when checkpointed.

### Context

- only high-signal context is carried forward;
- no unnecessary history/DAG copies are planned.

### Interaction

- root owns user-visible execution communication;
- material progress boundaries will produce concise updates where the runtime permits;
- workers cannot independently address the user;
- recoverable facts are retrieved before asking;
- unresolved user-owned directional choices have a `decision_pause` path;
- runtime limitations are not presented as live-progress capabilities.

### Safety

- side-effect class is explicit;
- state-changing work follows `production-safety.md` and action manifests where required;
- child workers cannot recursively invoke the Orchestrator or Loop Mode;
- blast-radius/human boundaries are bounded.

If a load-bearing preflight item fails, repair the contract once where possible. Otherwise present the blocker instead of asking approval for a knowingly invalid contract.

Validate machine-readable contracts with `scripts/validate_loop_contract.py` when practical.

## 8. RENDER HUMAN CONTRACT

Load `loop-contract-rendering.md` and render from the validated Internal Contract.

The Human Contract must preserve a clear mental model and all approval-relevant boundaries without dumping internal schema or architecture theory. Its first line must always be the largest Markdown header (`H1`): `# Contrato de Loop - <o que é>` for pt-BR or `# Loop Contract - <what it is>` for English. Never demote this title to plain text or a smaller heading level. It must start from the task-specific loop name and render the execution path so the user can see, for every material step, what happens, why, what it produces, and how that output leads forward.

For Brazilian Portuguese, apply the embedded MinMax PT-BR Output standard in `loop-contract-rendering.md`. For English, apply its embedded Humanizer standard. Treat this as a hard rendering gate, not optional polishing.

Then stop. Do not execute the substantive task or any loop cycle in the same turn.

## 9. APPROVAL HANDLING

Approval must unambiguously refer to the presented contract, such as "aprovado", "pode executar", or equivalent.

After approval, capture the presented contract digest at the root approval boundary, validate the approved contract against that external digest, and freeze:

- objective;
- terminal deliverable;
- material scope;
- authoritative constraints and hard dependencies;
- success criteria;
- hard budgets;
- tool/skill risk class;
- side-effect envelope;
- human boundaries.

If the user edits the contract before approval, revise and re-present it.

## 10. EXECUTE CYCLE

Each cycle must be small enough to verify.

1. reconstruct the minimum current state;
2. observe the current completion gap;
3. select the smallest useful approved action;
4. execute it;
5. run action verification;
6. run cycle verification;
7. record progress evidence/fingerprint;
8. emit/aggregate the appropriate user-visible progress event where the runtime permits;
9. checkpoint when required;
10. choose exactly one transition.

Allowed transitions:

- `success`;
- `continue`;
- `local_repair`;
- `decision_pause`;
- `material_replan`;
- `fail_escalate`;
- `budget_exit`.

Use Route A/B/C internally as appropriate. Loop Mode does not force delegation.

## 11. TRANSITIONS

### success

Terminal verifier establishes completion -> exit.

### continue

Measurable progress exists and the next approved action remains valid -> next cycle.

### local_repair

A verifier fails but repair stays inside frozen boundaries -> make one changed-strategy repair by default, then re-verify.

### decision_pause

A genuine user-owned directional choice is required but the current approved boundaries do not yet need to change -> root asks the user and pauses. Preserve the approved contract/digest. If checkpointing is required, represent the interruption with existing checkpoint `status=blocked` and a concise decision blocker. Resume directly after the answer when it stays inside frozen boundaries; if the answer crosses a frozen boundary, transition to `material_replan`.

### material_replan

A frozen approval boundary must change -> pause immediately.

### fail_escalate

Unrecoverable blocker, ambiguous unsafe write, missing primitive, or human boundary -> stop with best verified partial state.

### budget_exit

Any hard budget trips -> stop with best verified partial state.

## 12. MATERIAL REPLAN = NEW APPROVAL

A fresh approval is mandatory when a replan changes any of:

- objective or terminal deliverable;
- material scope/dependency topology;
- success or terminal verification criteria;
- hard iteration/time/cost budget;
- tool/skill class in a way that changes capability or risk;
- side-effect/write envelope;
- human approval boundary.

Use:

`PAUSE -> REPLAN -> PREFLIGHT -> RENDER REVISION -> STOP -> WAIT FOR APPROVAL`

A `decision_pause` that stays inside frozen boundaries is not a material replan and does not require a new approval. Prefer containment and frozen permissions to repeated permission prompts.

## 13. SIDE EFFECTS

Loop Mode never expands the autonomous write envelope.

For state-changing work, follow `production-safety.md`, validate an action manifest when required, and read authoritative state before retrying an ambiguous write.

Autonomous `external_write` requires explicit preauthorization. `irreversible_high_consequence` always stops at a human approval boundary.

Loop approval is not blanket approval for separately gated domain actions.

## 14. FINAL SYNTHESIS

When the loop exits, root returns one integrated result containing (and keeps the user informed during substantive execution according to `user-interaction-protocol.md`):

- what completed;
- terminal verification evidence;
- any remaining gap or budget/approval exit;
- the final artifact/action/result.

Do not dump cycle transcripts, internal checkpoints, or chain-of-thought unless explicitly requested and otherwise permitted.
