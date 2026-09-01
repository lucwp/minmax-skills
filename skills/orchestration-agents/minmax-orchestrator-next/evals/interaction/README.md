# User Interaction Eval Suite

This suite validates the behavioral envelope for user-visible progress and decision rights. Structural validation is not proof of runtime stochastic behavior.

1. Run `python scripts/validate_interaction_evals.py evals/interaction/cases.json`.
2. Capture runtime observations as `observed_checks` per case when isolated trials are available.
3. Grade them with `python scripts/grade_interaction_observations.py evals/interaction/cases.json observations.json`.
4. Do not fabricate runtime observations. PASS for this implementation requires deterministic/static gates at 100/100; runtime stochastic compliance must be measured separately when the host supports trials.
