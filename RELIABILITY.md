# MinMax reliability contract

MinMax skills are built for business work where a plausible answer is not enough. This contract defines what the repository means by `consulting-ready` and `production-ready`.

No certification means an LLM cannot hallucinate. The point is to design as if it will, then make unsupported state changes, silent gap filling, and false certainty harder to survive the workflow.

## Reliability levels

### Experimental

Useful for exploration. Do not treat it as client-ready or autonomous by default.

### Consulting-ready

Safe enough for professional client work when a human reviews material before delivery or an external side effect. Important assumptions must be visible, source-of-truth boundaries preserved, and material validation failures must fail visibly.

### Production-ready

Safe to run autonomously only inside the skill's declared `autonomous_envelope`.

Production-ready does not mean unlimited autonomy. Every production-ready skill must state what it can do unattended, what remains supervised, and which runtime controls it depends on. Irreversible or high-consequence actions can remain outside the autonomous envelope.

## Required controls

Every active skill has a `reliability.json` manifest. A production-ready skill must account for source of truth, uncertainty handling, fail-closed behavior, deterministic validation, side-effect safety, idempotency, postcondition verification, rollback/compensation, untrusted-input boundaries, concurrency control, auditability, termination budgets, and regression tests.

A control may be marked `not_applicable` only when genuinely outside the declared autonomous envelope, with a written reason.

## Certification is scoped

The unit of trust is the autonomous envelope, not the skill name. A proposal generator can be production-ready for generating and validating an artifact while still requiring a separate external-write policy before sending it. An orchestrator can autonomously update bounded CRM state while refusing an irreversible financial action.

## Enforcement

`scripts/validate_reliability.py` checks active skills, ignores `skills/legacy/`, validates each `reliability.json`, confirms declared evidence paths exist, and can run regression tests.

CI runs the validator on changes to active skills or reliability policy. A production-ready label should fail CI if declared controls or tests disappear.

Legacy skills are historical snapshots and are not certified under this contract.
