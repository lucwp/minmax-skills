# Loop Mode

## Purpose

Use this mode only when the user explicitly asks to execute the current task **with a loop** or equivalent language that clearly requests iterative autonomous/semi-autonomous execution.

Examples that activate Loop Mode:
- "faça isso com um loop";
- "use loop mode";
- "execute em loop até passar os critérios";
- "rode um autonomous loop para esta tarefa";
- "use loop-engineering para executar isso".

Do **not** activate Loop Mode merely because the user:
- mentions the word `loop` while discussing architecture;
- asks what a loop is;
- asks to review/design a loop rather than execute the underlying task;
- describes an iterative process without asking the orchestrator to run the task iteratively.

Explicit user intent is the activation gate.

## Source and attribution

This protocol integrates the core control-loop principles from Max Milian's `loop-engineering` skill:

- Repository: https://github.com/maxmilian/loop-engineering
- Author/source: Max Milian (`maxmilian`)
- License: MIT

When the runtime has the `loop-engineering` skill installed and callable, use it as the specialist authority for loop design/review. The MinMax Orchestrator remains the root control plane for task routing, domain-skill coordination, side-effect governance, and final synthesis.

When the external skill is not installed or callable, use the protocol below as the compatibility fallback. Do not claim the external skill was invoked when it was not.

## Loop Mode pipeline

Loop Mode changes the execution lifecycle, not the domain authority.

Always execute this sequence:

`PLAN -> COMPILE LOOP -> PREFLIGHT -> EXECUTE CYCLE -> VERIFY -> CONTINUE / REPAIR / EXIT -> SYNTHESIZE`

Do not start substantive task execution before `PLAN`, `COMPILE LOOP`, and `PREFLIGHT` are complete.

### 1. PLAN

Create one stable execution plan before the first cycle. Use `planning-engine.md` when the task is complex enough to need dependency compilation.

The plan must identify:
- objective;
- authoritative inputs and missing evidence;
- constraints and non-goals;
- work units/dependencies where material;
- domain skills/tools required;
- side-effect/approval boundaries;
- terminal deliverable;
- completion condition.

The plan is the task specification fed into the loop. Do not replace it with a vague instruction such as "keep improving".

### 2. COMPILE LOOP

Convert the plan into a bounded loop contract with these fields:

```text
Loop objective:
Cycle observation:
Cycle action:
Verification:
Success exit:
Failure exit:
Budget exit:
No-progress rule:
Repair/replan trigger:
Human escalation boundary:
Durable state:
Final synthesis requirement:
```

Required properties:

- **Machine-checkable success:** define observable evidence that establishes completion. Where fully deterministic checks are impossible, define an explicit evidence rubric and bounded semantic review.
- **Independent verification:** prefer tests, schemas, renders, authoritative read-back, diffs, receipts, or other verifiers over the model's self-report.
- **Proxy hardening:** identify how the executor could make the verifier green without satisfying the actual objective, then close that path when practical.
- **Finite budgets:** set iteration/retry/time/token or equivalent runtime caps appropriate to the task. Never use an unbounded "until perfect" loop.
- **No-progress detection:** stop or repair when repeated cycles produce no material state/evidence change.
- **Escalation:** define where the loop stops for missing evidence, unsupported runtime primitives, or human approval.

### 3. PREFLIGHT

Before the first execution cycle, verify that the loop contract is executable.

Preflight must confirm:
- success and failure exits are explicit;
- at least one finite budget exists and no relevant budget is unlimited;
- verification is defined;
- the user-requested deliverable can be produced with available tools/skills;
- required authoritative inputs are available or a retrieval step exists;
- side effects comply with `production-safety.md`;
- irreversible/high-consequence actions remain behind human approval;
- the executor cannot recursively invoke Loop Mode or the orchestrator as a child loop.

If preflight fails, repair the contract once when possible. If a load-bearing input or runtime primitive is unavailable, stop with the verified partial result/blocker instead of starting a knowingly invalid loop.

### 4. EXECUTE CYCLE

Each cycle must be small enough to verify. Execute the next ready unit of the stable plan.

Inside a cycle:
1. reconstruct the minimum required current state;
2. observe the completion signal/current gap;
3. perform the smallest high-value action;
4. record material state/evidence change;
5. run the defined verifier;
6. choose exactly one transition: `success`, `continue`, `repair`, `fail/escalate`, or `budget exit`.

Use Route A/B/C logic **inside** execution as appropriate. Loop Mode does not force worker delegation or multi-agent fan-out.

### 5. VERIFY AND TRANSITION

After every meaningful cycle:

- `success`: terminal verifier confirms the completion condition -> exit the loop;
- `continue`: progress exists and the next planned action remains valid -> run the next cycle;
- `repair`: verifier failed or a material assumption changed -> perform one bounded changed-strategy repair/replan, then continue only changed nodes;
- `fail/escalate`: unrecoverable blocker, ambiguous unsafe write, unavailable required primitive, or human boundary -> stop;
- `budget exit`: any hard cap is reached -> stop with best verified partial state.

Do not interpret additional reasoning text as progress. Progress requires new evidence, changed artifact/state, completed action, resolved dependency, or verifier movement.

## Plan stability and replanning

The initial plan remains stable during healthy execution. Do not regenerate the whole plan every cycle.

Replan only when at least one trigger fires:
- a completion test fails for a reason not handled locally;
- an assumption is invalidated;
- a dependency becomes impossible;
- the current strategy produces no progress across the configured threshold;
- ownership/tool/skill selection is demonstrably wrong;
- new authoritative evidence materially changes the task.

Prefer local repair over global replanning.

## Context and durable state

Treat context as finite. For long or multi-cycle work:
- persist/reconstruct only the state needed for continuation;
- prefer file paths, IDs, citations, diffs, manifests, and structured progress records over conversation replay;
- compact completed work into evidence-backed state summaries;
- do not forward full transcripts to workers;
- re-read authoritative/durable state rather than trusting stale conversational memory.

## Side effects

Loop Mode does not expand the autonomous write envelope.

For state-changing actions, follow `production-safety.md` and `action-manifest-schema.md`. External writes require the same preauthorization rules as normal orchestrated work. Irreversible/high-consequence actions always stop at the human boundary.

Never repeat a state-changing action after an ambiguous outcome until authoritative state has been read back.

## Final synthesis

When the loop exits, the root agent must synthesize one user-facing result that states:
- what was completed;
- the terminal verification evidence;
- any material remaining gap or budget/approval exit;
- the final artifact/action/result.

Do not dump the cycle transcript unless the user asks for it.
