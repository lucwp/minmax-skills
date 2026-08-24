# One-Shot Robustness Standard

Last reviewed: 2026-08-24

Purpose: make the first substantive consulting answer decision-robust enough that red teaming is an optional enhancement rather than a repair mechanism.

## Target

For every substantive decision, enforce a **Decision Robustness Score (DRS) floor of 90 in the first response** and use **95 as the construction target**.

- `90-94.9`: robust enough to release; improve only if a cheap same-pass fix exists.
- `95+`: benchmark-grade headroom for normal production variance.

Do not spend materially more time merely to move 93 to 95. The construction target exists to improve the base rate, not to create another reasoning loop.

This does **not** mean the outcome is 90% certain. It means the decision is robust to what remains uncertain.

A correct one-shot answer may therefore be:

- `RECOMMEND`;
- `RECOMMEND WITH CONDITIONS`;
- `DO NOT RECOMMEND`;
- `INSUFFICIENT EVIDENCE TO DECIDE`.

When critical evidence is missing, a high-quality answer should change the commitment, not invent certainty. "Do not commit until X is measured" can be more robust than a forced yes/no recommendation.

## The one-shot pass

Do this inside the same response. It is not an additional agent round and must not trigger the Challenge Engine.

1. **Freeze the decision.** State what choice must be made, by whom, over what horizon, and against which explicit criteria.
2. **Triage materiality.** Ignore precision that cannot change the decision. Identify only decision-flipping unknowns.
3. **Build the minimum evidence contract.** Separate fact, inference, assumption, estimate, calculation, forecast, and recommendation. Trace load-bearing facts to sources.
4. **Find the 1-3 load-bearing assumptions.** Ask what must be true for the proposed action to outperform the strongest credible alternative.
5. **Run the cheapest disconfirming check.** Seek contradictory evidence, denominator/unit mismatches, causal alternatives, or sensitivity near the threshold.
6. **Quantify what is material.** Use deterministic calculation for arithmetic, scenario thresholds, portfolio constraints, or break-even/switching values when applicable.
7. **Compare the strongest alternative on the same criteria.** Include `do nothing`, `stage`, `delay`, `reprice`, or `preserve optionality` when they are credible options.
8. **Check execution and actor response when material.** Test capacity, dependencies, decision rights, incentives, adoption, competitor/regulator/customer response, and reversibility.
9. **Convert uncertainty into controls.** Give each surviving critical uncertainty a falsifier, signpost, switching condition, experiment, or explicit statement that it is currently untestable.
10. **Score Decision Robustness.** Use `scripts/decision_robustness.py` when structured state is available.

## One bounded repair pass

If the first DRS estimate is below 90, do **one mandatory** repair pass inside the same response:

- identify the lowest-scoring applicable dimension with the largest decision impact;
- repair only that dimension and any directly coupled blocker;
- do not restart the whole engagement;
- do not add frameworks merely to increase apparent completeness;
- do not launch recursive self-critique.

If the score still cannot reach 90 because evidence is genuinely unavailable, **change the decision class**. Prefer a robust conditional/staged/insufficient-evidence recommendation over an overconfident answer.


### Headroom micro-repair

If DRS is already `90-94.9`, allow at most one **micro-repair** only when all of the following are true:

- it uses evidence or calculations already available in the current pass;
- it repairs one missing or partial criterion with real decision value;
- it requires no new research, subagent, council, framework stack, or red-team round;
- it does not make the client-facing answer materially longer merely to earn points.

Otherwise release the 90+ answer. Never convert a 93 into a ten-minute process just to display 95.

Examples:

- Unknown scalable CAC blocks full rollout -> recommend staged rollout with a CAC gate.
- Unknown causal attribution blocks a USD 5m rollout -> recommend controlled test, not a confident attribution.
- Missing office rent worth <0.1% of deal value -> use a provisional assumption and continue because it is non-material.

## DRS dimensions

The nominal 100-point model is:

| Dimension | Weight | What 90+ quality looks like |
|---|---:|---|
| Evidence & provenance | 20 | load-bearing facts traceable; conflicts and source limitations visible |
| Assumption resilience | 20 | load-bearing assumptions explicit, challenged, and bounded |
| Economics / quant / sensitivity | 15 | arithmetic deterministic where material; downside and switching values visible |
| Alternatives / countercase | 15 | strongest credible alternative evaluated on common criteria |
| Execution / incentives / response | 15 | feasibility, dependencies, actor incentives and likely response addressed when material |
| Falsifiers / signposts / reversibility | 10 | surviving critical uncertainty converted into observable controls |
| Residual dissent quality | 5 | what remains uncertain is preserved without pretending false consensus |

The script does **not** accept free-form dimension scores. It calculates DRS from observable criterion states:

- `met` = 100% of the criterion weight;
- `partial` = 50%;
- `not-met` = 0%;
- `na` = removed from the applicable denominator.

Every `met` or `partial` criterion requires a short evidence note in the robustness artifact. This makes score inflation more visible than a self-assigned "19/20". Non-applicable criteria are normalized out, but must not be used to hide a weak area.

Core criteria include claim traceability, source-conflict reconciliation, source/population fit, load-bearing assumptions, disconfirming evidence, counterfactual flip, deterministic arithmetic, downside/ranges, switching values, unit/denominator reconciliation, strongest alternative, common-criteria comparison, feasibility/capacity, incentives/actor response, ownership/adoption, uncertainty controls, kill/scale criteria, signposts, counterevidence, residual-uncertainty classification, and confidence calibration. See `scripts/decision_robustness.py` for the canonical weights.

## 90+ hard rules

A decision cannot reach 90 while any of these remains decision-flipping and uncontrolled:

- unresolved critical empirical breaker;
- material quantitative error;
- material evidence conflict;
- missing decision contract;
- unsupported load-bearing factual claim;
- forecast-heavy commitment without an outside-view check when a defensible reference class exists;
- material alternative not evaluated;
- execution-heavy commitment with feasibility untested;
- surviving critical uncertainty without a falsifier, signpost, switching condition, or explicit controlled staging;
- accepted critical risk still capable of flipping the decision;
- residual uncertainty that is empirically resolvable now and still capable of changing the recommendation.

## Applicability guard

`na` is not a score-improvement tool. For a substantive decision, the scorer requires minimum applicable coverage in evidence, assumptions, alternatives, falsifiers, and residual uncertainty. If the decision is quantitatively material, all quantitative criteria remain applicable. If execution is material, all execution criteria remain applicable. A response that hides a weak area by marking it non-applicable is `INVALID`, not robust.

## Anti-gaming rule

The score evaluates the **chosen decision**, not the attractiveness of the original thesis.

If the original proposal is weak, the correct path to 90+ may be:

`FULL COMMITMENT -> STAGE -> TEST -> SCALE ONLY IF GATE PASSES`

or:

`RECOMMEND -> DO NOT RECOMMEND`.

Do not inflate dimension scores to protect the user's original position.

## Output behavior

Do not normally print a seven-row scorecard in client-facing prose. Surface the DRS when:

- the user asks for it;
- the Challenge Engine is active;
- the score is below 90;
- the release status is conditional or blocked;
- the work is explicitly a benchmark, QA, or audit.

Otherwise use the score as internal release discipline and keep the answer concise.
