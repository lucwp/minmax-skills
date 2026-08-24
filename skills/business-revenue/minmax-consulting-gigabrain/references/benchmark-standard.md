# Gigabrain Benchmark Standard

Last reviewed: 2026-08-24

Purpose: prevent the Challenge Engine from optimizing for a few showcase examples while regressing on adversarial decision review.

## Release target

A candidate version should target all of the following on the approved benchmark set:

- **mean Decision Robustness >= 95**;
- **every one-shot case >= 90**;
- **10th percentile one-shot score >= 90**;
- **zero hard-gate misses**;
- **zero false-ROBUST outcomes**;
- **zero wrong decision-class outcomes**;
- at least **20 materially different cases** before treating the score as release evidence.

Run:

```bash
python scripts/benchmark_gate.py benchmark-results.json
```

The benchmark gate consumes scored case results. It does not generate scores itself. In `certification_mode=true` (default), every case must be blind-scored and reviewed independently from the answer-producing context. Use `certification_mode=false` only for development calibration; never cite that as a certified 95+ result.

## Why mean 95 and floor 90

The floor protects consistency. The mean target creates headroom so ordinary variance does not push production answers below the 90 robustness threshold.

A system averaging exactly 90 is too close to the release boundary. A 95 target means strong cases should usually land in the mid/high 90s, while unusually ambiguous cases can still remain above 90 by choosing a conditional or insufficient-evidence decision class.

## Benchmark composition

Use materially different red-team cases, not near-identical strategy prompts. The benchmark set should cover at least:

1. hidden load-bearing assumptions;
2. evidence conflict or selection bias;
3. denominator or quantitative traps that flip the decision;
4. strongest-alternative comparison;
5. forecast outside-view failure;
6. execution or readiness blockers;
7. competitor or third-party response;
8. causal attribution error;
9. materiality judgment so challenge does not become analysis paralysis;
10. a healthy thesis where the correct action is to stop challenging;
11. a weak thesis where the correct action is to reverse;
12. a case where staging is better than yes/no commitment;
13. accepted critical risk that must remain unresolved;
14. cosmetic independent review that must not be called independent;
15. bounded PULSE behavior;
16. bounded CONVICTION behavior;
17. genuine INDEPENDENT review with isolation;
18. a case that reaches 90+ before the round budget and therefore must stop.

Use the 18 synthetic red-team fixtures plus real historical business decisions. For real cases, freeze the evidence set at the decision date when possible and reveal the later outcome only after the red-team result is scored. This reduces hindsight leakage.

## Scoring discipline

The benchmark score is not self-certified by the authoring response.

Preferred order:

1. run the case with the outcome hidden;
2. capture the first answer before red teaming;
3. have a separate reviewer/context score the DRS dimensions and decision class;
4. record hard-gate misses and false robustness separately;
5. only then reveal the historical/synthetic ground truth;
6. run `benchmark_gate.py` over the collected results.

Same-model self-scoring is useful for development but is not sufficient evidence for a public 95+ benchmark claim.

## Benchmark assets in this package

- `references/red-team-benchmark-cases.md`: 18 synthetic adversarial decision cases with predeclared ground truth.
- `references/real-world-benchmark-cases.md`: historical business decisions with decision-date evidence separated from later outcomes to reduce hindsight leakage.
- `scripts/red_team_test.py`: focused mechanical regression/fuzzing for Challenge Engine, DRS, stop logic, independence, and release coupling.
- `scripts/benchmark_gate.py`: release aggregator for independently scored benchmark results.

## Required benchmark result schema

```json
{
  "target_mean": 95,
  "target_min": 90,
  "target_p10": 90,
  "min_cases": 20,
  "certification_mode": true,
  "cases": [
    {
      "case_id": "Q01",
      "one_shot": true,
      "score": 96,
      "hard_gate_miss": false,
      "false_robust": false,
      "wrong_decision": false,
      "blind_scored": true,
      "independent_reviewer": true
    }
  ]
}
```

## Anti-benchmark-gaming

Do not:

- tune against only the published answers;
- use historical outcome information during the answer phase;
- award points for verbosity or framework count;
- penalize a robust `INSUFFICIENT EVIDENCE` decision merely for refusing to guess;
- allow an average score to hide a sub-90 one-shot case;
- count a deterministic script regression suite as proof of LLM consulting judgment.

The focused red-team regression suite and the red-team benchmark are complementary. The former catches mechanical Challenge Engine failure. The latter measures adversarial judgment and stopping quality.
