# Termination and Anti-Hang Budgets

## Runtime Principle

Agentic work must use finite turn, retry, recursion, and time budgets. When the runtime exposes cancellation, per-call timeouts, nested-run limits, or abort controls, use them. Exact workspace numbers below are local defaults and should be tuned with evals.

## Mandatory Rules

- Never use unlimited turns, recursion, or retries.
- Every nested worker has its own finite turn budget.
- Use external cancellation/timeout whenever runtime supports it.
- A timed-out assignment is not retried unchanged.
- Planner cannot recursively call planner.
- Worker cannot re-invoke the orchestrator.
- Verifier cannot enter an evaluator-repair loop by itself.

## Suggested Workspace Defaults — Heuristics

These are conservative starting points, not universal optima:
- planner: one call + at most one pre-execution repair;
- nested worker: target <= 5 turns, hard ceiling <= 10 when runtime only exposes a generic runner limit;
- verifier: one bounded judgment call;
- execution-time global recovery/replan: one by default;
- changed-strategy retry for a failed node: one;
- stall threshold: two consecutive no-progress observations by default;
- wall-clock timeout: choose a runtime-appropriate finite value; do not encode a long wait when cancellation is unavailable.

## Progress Definition

Progress must be observable:
- new required evidence;
- completed tool/action;
- changed artifact/state;
- passed/failed completion test;
- resolved dependency.

More reasoning text without new state is not progress.

## On Stall or Timeout

1. cancel/abandon the active node when possible;
2. preserve completed work;
3. diagnose context/scope/tool/capability failure;
4. make one changed-strategy retry or one bounded replan;
5. if still blocked, return best verified partial result and blocker.

## Single-Call Hang Limitation

Prompt instructions cannot interrupt a model call that is already stuck inside the runtime. Only external runtime cancellation/timeout can do that.

Therefore, when no watchdog exists:
- avoid open-ended planner prompts;
- prefer one-shot structured outputs;
- narrow xhigh calls;
- do not ask the model to "keep thinking until solved";
- surface a partial result rather than creating an unbounded loop.
