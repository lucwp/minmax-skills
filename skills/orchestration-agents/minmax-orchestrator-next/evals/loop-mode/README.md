# Loop Mode Eval Suite

This eval package has three evidence layers. Keep them separate so structural checks are never reported as runtime behavior.

## 1. Behavioral spec validation

`cases.json` defines the acceptable behavioral envelope for each scenario: topology, verifier properties, state policy, side effects, approval expectations, and terminal behavior.

Run:

```bash
python scripts/validate_behavioral_evals.py evals/loop-mode/cases.json
```

This validates the **quality and completeness of the eval specification**. It is not evidence that a model executed the skill correctly.

## 2. Behavioral observation grading

When a runtime produces actual Loop Contract observations, store them in a JSON object keyed by case id and grade them with:

```bash
python scripts/grade_behavioral_observations.py \
  evals/loop-mode/cases.json observations.json
```

This checks observable decisions such as topology, side-effect class, state mode, schema, approval state, name, and execution-plan presence against the case envelope. It grades supplied observations; it does not itself invoke a model.

## 3. Runtime stochastic trials

When the runtime can execute the candidate skill in isolated trials:

1. run at least 3 trials for ambiguous/non-deterministic cases;
2. capture the generated Internal Contract before approval;
3. grade outcome and reasonable process, not exact wording or step order;
4. record topology, worker/tool count, verification evidence, state mode, approval behavior, exit behavior, and cost/latency proxies;
5. compare candidate against the frozen baseline using the same prompts and grader;
6. treat a regression as real only when repeatable evidence supports it.

If isolated execution is unavailable, do **not** fabricate runtime trial results. Report deterministic validation, golden rendering, adversarial mutation tests, and observation-grader capability separately.

## Scoring dimensions

- Topology fit: 25
- Verification quality: 25
- Complexity/efficiency: 20
- Safety/boundaries: 20
- Human Contract usability: 10

PASS requires >=95/100 **and** every hard gate. A high score cannot override a safety, approval, finite-budget, topology, or regression failure.
