# Termination and Anti-Hang Budgets

Agentic work must use finite turn, retry, recursion, no-progress, and time/cost budgets where runtime controls exist.

Mandatory rules:
- never use unlimited turns, recursion, or retries;
- every worker has a finite budget;
- use external cancellation/timeout when available;
- a timed-out assignment is not retried unchanged;
- planner cannot recursively call planner;
- worker cannot re-invoke the orchestrator;
- verifier cannot enter a self-directed evaluator-repair loop.

Conservative starting heuristics, to be tuned with evals:
- planner: one call + at most one pre-execution repair;
- nested worker: target <= 5 turns, hard ceiling <= 10 if runtime exposes only generic turn limits;
- verifier: one bounded judgment call;
- global recovery/replan: one by default;
- changed-strategy retry for failed node: one;
- no-progress threshold: two consecutive cycles without material progress;
- Loop Mode: always set a finite max-iteration budget before approval.

Progress means new required evidence, completed tool/action, changed artifact/state, passed/failed completion test, resolved dependency, or measurable verifier movement. More reasoning text is not progress.

If runtime lacks cancellation, avoid open-ended prompts and surface partial results rather than creating an unbounded loop.
