# Decision output contract

Inspired by A-005 and answer-first consulting practice. This contract is original to this package.

## Executive decision

Lead with one of:
- `RECOMMEND`
- `RECOMMEND WITH CONDITIONS`
- `DO NOT RECOMMEND`
- `INSUFFICIENT EVIDENCE TO DECIDE`

Then state the action in one sentence.

## Required sections

### Why
2-4 load-bearing reasons only. Each reason must connect evidence to decision implication.

### Evidence map
For each load-bearing reason label supporting statements as `FACT`, `INFERENCE`, `ASSUMPTION`, `ESTIMATE`, `CALCULATION`, or `FORECAST`.

### Economics / value
Show the relevant base, downside, sensitivity and switching value. State which inputs are externally sourced versus assumed.

### What could make this wrong
Name the strongest counterevidence, unresolved uncertainty and the assumption most likely to flip the recommendation.

### Alternatives
Show at least one credible alternative when the decision is material. Explain why it loses under current evidence.

### Risks and mitigations
Prioritize by decision impact. Avoid generic risk registers.

### Kill / scale criteria
State objective conditions to stop, pause, reprice, redesign or scale.

### Next actions
Owner + action + timing/milestone + evidence/result required.


## Decision robustness

For substantive decisions, score the chosen action under `references/one-shot-standard.md`. Target **90+ in the first response**. Do not interpret the score as outcome probability.

If the score is below 90 after the single bounded repair pass, either:

- lower the commitment strength;
- convert the answer to a staged/conditional decision;
- return `INSUFFICIENT EVIDENCE TO DECIDE`; or
- expose the unresolved blocker.

When surfaced client-facing, use one line:

`Decision Robustness: 93/100 - robust; remaining uncertainty is controlled by <gate/signpost>.`

Do not print the full scorecard unless the user asks for it or the work is QA/benchmarking.

## Challenge result, only when activated

Do not add a red-team section when Challenge Engine mode is `OFF`. When active, keep the client-facing summary compact:

- mode used: `PULSE`, `CONVICTION`, or `INDEPENDENT`;
- strongest decision-flipping attack;
- strongest credible alternative/countercase;
- what evidence or threshold would settle the issue;
- conviction delta: `UNCHANGED`, `NARROWED`, `REVISED`, `REVERSED`, or `UNDECIDED`;
- residual dissent;
- Decision Robustness score;
- stop state from the challenge gate.

Do not expose a long internal debate transcript unless the user requests it. Preserve the complete challenge ledger in engagement state when persistence is available.

## Confidence

Use `HIGH / MEDIUM / LOW` based on evidence quality and sensitivity, not rhetorical certainty.

Lower confidence when:
- a load-bearing claim is single-source;
- definitions do not reconcile;
- data is stale for the market speed;
- the model is highly sensitive near the decision threshold;
- implementation feasibility is untested;
- the source population differs materially from the target population.
