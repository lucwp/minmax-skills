# Gigabrain Challenge Engine

Last reviewed: 2026-08-24

Purpose: provide opt-in adversarial review for material consulting decisions without turning every engagement into a slow recursive debate. The engine challenges a decision only when the user asks for it or explicitly accepts the option at a decision boundary.

## Design principle

Challenge is not ordinary consulting hygiene. The core workflow must already test assumptions, seek disconfirming evidence, reconcile sources, and run deterministic checks. The Challenge Engine is an additional adversarial layer for a user who wants a belief, recommendation, or plan attacked more aggressively.

Do not run it by default. Do not use it to manufacture doubt. Do not loop until the model feels satisfied.

## Activation

Activate when the user explicitly asks to:

- red-team or stress-test a recommendation;
- attack their convictions or prove them wrong;
- argue the strongest opposing case;
- run a premortem;
- pressure-test a business case or forecast;
- challenge consensus before a commitment.

At a material decision boundary, it is acceptable to offer one concise option such as: `Challenge available: Pulse | Conviction | Independent.` Do not execute it without opt-in.

Natural-language requests override mode names. Map the request to the cheapest mode that satisfies it.

## Modes and processing budgets

### OFF

Default. Run no additional adversarial pass. Normal evidence validation and falsification remain mandatory because they are part of the consulting workflow, not red teaming.

### PULSE

Use for a quick sanity check.

Budget:
- one challenge pass;
- one primary technique;
- top 1-3 decision-flipping issues only;
- no recursive self-critique;
- no new external research unless the user asks for verification or the missing fact is necessary to avoid a misleading claim.

Return the strongest objection, strongest credible alternative when applicable, one falsifier or switching condition, and the conviction delta.

### CONVICTION

Use when the user explicitly wants their position challenged until it is decision-robust.

Budget:
- maximum three rounds per decision cycle;
- normally one round per user turn so new evidence or rebuttal can enter the state;
- one primary technique and at most one secondary technique per round;
- only attack unresolved load-bearing issues from prior rounds;
- never repeat an objection that was resolved unless new evidence reopens it.

After each round, update the challenge ledger and return the open breaker(s). Stop as soon as the robustness criteria are met. If the third round still contains a decision-flipping unknown, stop with `STOP_BUDGET` or `UNRESOLVED`; do not invent closure.

A user may start a new bounded cycle only when there is new evidence, a changed decision, or an explicit request to reopen a resolved issue.

### INDEPENDENT

Use only on explicit request for a genuinely independent challenge or when the user explicitly chooses the strongest review mode.

Budget:
- one independent challenge pass;
- at most one rebuttal/response pass;
- no council, voting swarm, or open-ended debate.

When runtime capabilities allow, give the challenger the decision contract, raw evidence ledger, claim ledger, quantitative outputs, constraints, and alternatives, but do not preload the persuasive narrative of the original recommendation. This reduces anchoring on the authoring agent's framing.

Prefer an isolated context or different model family when available. Do not claim independence, cross-model review, or a second agent unless the runtime actually executed it. If isolation is unavailable, disclose that and fall back to `CONVICTION` rather than mislabeling self-critique as independent review.

## Technique router

Use the smallest technique that matches the failure mode. Do not run every technique.

| Signal | Primary technique | What it tests |
|---|---|---|
| Conclusion depends on hidden or fragile premises | Key Assumptions Check | What must be true, why, and what breaks it |
| Evidence appears selective, causal, or overconfident | Evidence Audit / consider-the-opposite | Source quality, disconfirming evidence, alternative explanations |
| Strong preference or consensus around one option | Devil's Advocacy / dialectical countercase | Strongest credible opposing case and missing alternative |
| Plan is execution-heavy or coordination-heavy | Premortem | Concrete failure paths, warning signs, second-order effects |
| Forecast, timeline, adoption, ROI, or market case is load-bearing | Outside View / reference class | Whether the inside forecast is plausible against comparable outcomes |
| Competitor, regulator, customer, partner, or incentive response matters | Adversary simulation | How another actor can respond, exploit, block, or game the plan |

Select one primary technique. Add one secondary technique only when the first pass reveals a distinct decision-flipping risk category.

## Core challenge protocol

1. **Freeze the decision claim.** State the recommendation or user conviction in one falsifiable sentence. Do not let the target move during the attack.
2. **Steelman before attacking.** Restate the strongest defensible version of the position and its best evidence. If the user would reject the restatement, the challenge target is wrong.
3. **Extract load-bearing premises.** Separate premises that can flip the decision from supporting detail. Prioritize weak support plus high decision impact.
4. **Attack with a matched technique.** Generate a small number of specific attacks. Every attack must say what fails and why it matters to the decision.
5. **Separate evidence from reasoning.** Label each attack as `VERIFIED`, `REASONING-ONLY`, or `UNKNOWN`. Never invent data to make the attack stronger.
6. **Define the falsifier.** State the evidence, threshold, event, or test that would resolve the challenge. If the issue is not falsifiable, say so and lower confidence rather than pretending it can be settled.
7. **Evaluate the strongest alternative.** Compare it using the same decision criteria. Do not merely criticize the current option in isolation.
8. **Update conviction, not rhetoric.** Record whether the decision is `UNCHANGED`, `NARROWED`, `REVISED`, `REVERSED`, or `UNDECIDED`.
9. **Stop deliberately.** Run `challenge_gate.py` when a ledger exists. Do not continue because another objection can always be invented.

## Key Assumptions Check

Use early when a recommendation rests on premises that may be implicit, and again when a long-standing judgment is being challenged.

For each candidate assumption:

1. Why must this be true for the recommendation to hold?
2. What evidence supports it directly?
3. What circumstance would make it false?
4. If it fails, does the decision reverse, narrow, or merely become less confident?
5. What is the cheapest evidence that can resolve it?

Keep only assumptions that are truly load-bearing.

## Devil's Advocacy and dialectical countercase

Use when one view is strongly held, consensus is suspiciously clean, or an alternative has not received a fair hearing.

Build the best credible case for the alternative or opposite conclusion. The countercase must answer the original position's strongest argument, not a weak caricature.

Caution: assigned devil's advocacy is not equivalent to authentic independent dissent. Empirical work by Nemeth, Brown, and Rogers found authentic dissent generated more divergent/original thinking than role-played devil's advocacy. Treat a same-model countercase as a useful structured technique, not as proof of independence. For high-stakes review, prefer `INDEPENDENT` when the runtime genuinely supports isolation.

## Evidence Audit

Use when the conviction is mostly data-driven.

For each decision-flipping claim:

- identify claim type: causal, predictive, comparative, quantitative, or existential;
- identify exact supporting evidence;
- ask what would disprove it;
- search for contradictory evidence or competing explanations when research is allowed;
- test source independence, population fit, denominator, recency, and measurement definition;
- downgrade confidence when the source is indirect, promotional, stale, or mismatched.

The evidence validator and consistency validator remain higher-authority than rhetorical critique for mechanically testable issues.

## Premortem

Use when the main uncertainty is whether the plan can be executed.

Assume the initiative has clearly failed at a plausible future date. Generate only the most credible failure paths. Each path should contain:

- trigger;
- first-order consequence;
- second-order consequence;
- early warning signal;
- mitigation or contingency;
- decision implication.

A premortem is not a substitute for assumption testing. It explores how a plan fails after the decision; a Key Assumptions Check tests whether the decision's premises are sound now.

## Outside View / reference class

Use for material forecasts when a reasonable reference class can be defined.

1. Define the forecasted outcome precisely.
2. Select a reference class based on causal/operational similarity, not superficial analogy.
3. Establish the distribution or base rate when credible data exists.
4. Compare the inside-view forecast with the reference class.
5. Explain material deviations rather than averaging them away.
6. If no defensible reference class exists, mark `outside_view_status = unavailable` and preserve that uncertainty.

Do not force a reference class if comparability is too weak. A bad analogy is not debiasing.

## Adversary simulation

Use only where another actor can materially respond to the strategy.

Define the actor's:

- objective;
- incentives;
- capabilities;
- constraints;
- information/access;
- cheapest countermove.

Then ask how that countermove changes economics, timing, differentiation, regulatory feasibility, or implementation.

## Decision Robustness Score and stopping threshold

Use the same Decision Robustness Score (DRS) as the core one-shot workflow. Read `references/one-shot-standard.md` for the full scoring model.

The score measures how robust the **decision** is to remaining uncertainty. It is not a probability that the thesis is correct. A revised, staged, conditional, `DO NOT RECOMMEND`, or `INSUFFICIENT EVIDENCE` decision can score higher than the user's original conviction.

Nominal weights:

- evidence & provenance: 20;
- assumption resilience: 20;
- economics / quant / sensitivity: 15;
- alternatives / countercase: 15;
- execution / incentives / actor response: 15;
- falsifiers / signposts / reversibility: 10;
- residual dissent quality: 5.

**Automatic stop rule:** stop the Challenge Engine when DRS is **90+** and no applicable critical empirical breaker remains. Do not run another round merely because another objection can be invented.

A decision cannot reach the 90+ stop state while any decision-flipping issue remains empirically resolvable and uncontrolled. Convert uncertainty into a falsifier, signpost, switching condition, staged test, or explicit `INSUFFICIENT EVIDENCE` decision before treating the decision as robust.

The target is not `no objections`. At 90+, the remaining disagreement should be mostly:

- risk appetite;
- relative preference among empirically close alternatives;
- strategic taste or weighting of objectives;
- genuinely future uncertainty already controlled by signposts or switching rules.

If another round has low expected information gain, stop even below 90 as `UNRESOLVED` or `STOP_BUDGET`. Never spend more tokens pretending uncertainty can be reasoned away.

## Challenge ledger

Create `06a-challenge-ledger` only when the engine is active. Suggested JSON shape:

```json
{
  "mode": "conviction",
  "round": 1,
  "max_rounds": 3,
  "forecast_heavy": true,
  "outside_view_status": "done",
  "outside_view_note": "Reference class and source IDs recorded in evidence ledger",
  "strongest_alternative_evaluated": true,
  "independent_challenger_used": false,
  "isolation_note": "",
  "decision_state": "narrowed",
  "challenges": [
    {
      "id": "CH-001",
      "severity": "critical",
      "load_bearing": true,
      "status": "open",
      "evidence_basis": "verified",
      "falsifier": "Retention below 85% in two consecutive cohorts",
      "decision_flip_condition": "Downside NPV falls below the board threshold",
      "resolution": ""
    }
  ]
}
```

Run:

```bash
python scripts/decision_robustness.py robustness-input.json --output robustness-report.json
python scripts/challenge_gate.py challenge.json --robustness robustness-report.json
```

The gate validates budget, mechanical completeness, and the 90+ DRS stopping rule. Resolved, accepted-risk, and non-decision-relevant challenges require a `resolution` note; real independent review requires an `isolation_note`; an unavailable outside view requires an `outside_view_note`. Accepted critical risk is preserved as `UNRESOLVED`, never upgraded to `ROBUST`. The gate does not decide whether the argument is true.

## Output contract

Keep challenge output short unless the user asks for the full ledger.

```text
CHALLENGE MODE: PULSE | CONVICTION | INDEPENDENT
TARGET: <frozen decision claim>

STRONGEST ATTACK
<the single most decision-relevant challenge>

WHY IT CAN FLIP THE DECISION
<causal link>

BEST COUNTERCASE / ALTERNATIVE
<strongest credible opposing option>

WHAT WOULD SETTLE IT
<falsifier, evidence, threshold, or cheapest test>

CONVICTION DELTA
UNCHANGED | NARROWED | REVISED | REVERSED | UNDECIDED

DECISION ROBUSTNESS
<score>/100 | ROBUST if >=90 and no critical empirical breaker remains

RESIDUAL DISSENT
<what remains unresolved>

STOP STATE
ROBUST | CONTINUE | STOP_BUDGET | UNRESOLVED
```

## Anti-patterns

- Do not run challenge automatically just because the decision is important.
- Do not generate 20 generic risks when three can flip the decision.
- Do not use recursive self-critique as a substitute for new evidence.
- Do not equate same-model role play with independent dissent.
- Do not reward the challenger for disagreeing. A strong position may survive unchanged.
- Do not soften a real blocker to preserve the original recommendation.
- Do not keep debating after the decision is made unless new evidence crosses a pre-agreed trigger.
- Do not run every adversarial technique in sequence.

## Research basis

See `framework-source-ledger.md`, especially F-018 through F-027. The design draws on CIA Structured Analytic Techniques, U.S. Army red teaming, Gary Klein's premortem, decision-challenger practices, outside-view/reference-class forecasting, empirical research on authentic dissent versus assigned devil's advocacy, and empirical reviews of LLM self-correction.
