# Source-backed problem solving

Primary source: F-001 in `framework-source-ledger.md`.

## Operating sequence

1. Define the decision problem narrowly enough to be answered.
2. Separate context, complication, decision question, constraints, success criteria and out-of-scope.
3. Disaggregate the question using a logic tree. Use multiple cuts when a different decomposition could expose a different answer.
4. Convert high-priority branches into testable hypotheses.
5. Prioritize by decision impact and tractability. Do not boil the ocean.
6. Build an analysis plan whose outputs can support or kill hypotheses.
7. Synthesize findings into an answer, then iterate if evidence changes the structure.

## Hypothesis record

For each material hypothesis record:

- `hypothesis_id`
- statement
- branch
- current confidence
- evidence required
- disconfirming evidence
- fastest credible test
- source/data owner
- decision implication if supported
- decision implication if refuted
- status: `open / supported / weakened / refuted / unresolved`

If neither support nor refutation would change the recommendation, the hypothesis is probably not worth a major workstream.

## Issue-tree quality tests

- Siblings use the same basis of decomposition.
- Material overlap is identified and removed.
- Major causal or economic branch is not missing.
- Leaf nodes can be investigated with evidence.
- The tree is tailored to the client's actual business model.
- The tree distinguishes causes, outcomes and interventions rather than mixing them.

## Falsification discipline

For every high-confidence early hypothesis, write the strongest evidence that would prove it wrong. Seek that evidence before spending heavily on confirmation.

Do not preserve a favored hypothesis after load-bearing contradictory evidence appears. Revise the tree, analysis plan and storyline together.

## 80/20 is not permission for weak evidence

Prioritize the few analyses most likely to change the decision. Do not use 80/20 as an excuse to skip a material risk, denominator check, or sensitivity that could reverse the recommendation.
