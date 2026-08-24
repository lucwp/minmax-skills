# Contributing to MinMax Skills

This repository is a maintained catalog of reusable agent skills developed by Lucas W. Portella.

## Where a skill belongs

Use exactly one primary category: `orchestration-agents`, `business-revenue`, `product-growth`, `marketing-content`, `design-ux`, `operations-process`, `data-analytics`, `career`, or `artifact-workflows`.

Do not duplicate one skill across categories. If classification is ambiguous, choose the category that best describes the skill's primary trigger and user outcome.

## Required structure

Active skill:

```text
skills/<category>/<skill-name>/
├── SKILL.md
└── reliability.json
```

Superseded skill:

```text
skills/legacy/<category>/<skill-name>/
└── SKILL.md
```

Optional supporting directories include `agents/`, `references/`, `assets/`, `scripts/`, and `tests/`.

## Reliability contract

Read `RELIABILITY.md` before publishing or materially changing an active skill.

Every active skill must declare one reliability level in `reliability.json`: `experimental`, `consulting-ready`, or `production-ready`.

`production-ready` is scoped to the declared `autonomous_envelope`; it is not a claim of unlimited autonomy. The manifest must account for source of truth, uncertainty handling, fail-closed behavior, deterministic validation, side-effect safety, idempotency, postcondition verification, rollback/compensation, untrusted-input boundaries, concurrency control, auditability, termination budgets, and regression tests. Use `not_applicable` only with a real reason tied to the autonomous envelope.

Run before publishing:

```bash
python scripts/validate_reliability.py --repo-root . --run-tests
```

CI runs the same gate. Do not weaken a validator, delete a regression test, or broaden an autonomous envelope merely to make CI pass.

## Replacement and legacy policy

Distinguish an incremental improvement from a complete replacement.

- Incremental improvement: keep the same active skill and update it in place.
- Complete replacement: move the superseded implementation to `skills/legacy/<category>/<old-skill-name>/`, then publish only the replacement as active.
- Never keep both replacement and superseded skill active when they serve the same canonical intent.
- Legacy skills are historical snapshots. Do not update them except for repository integrity or archival metadata.
- Legacy skills are not certified by the current reliability contract.

## Publishing checklist

Before pushing a new or materially changed active skill:

1. `SKILL.md` exists and clearly states the trigger and responsibility.
2. `reliability.json` exists and accurately scopes the reliability level and autonomous envelope.
3. Every implemented reliability control points to real evidence files.
4. Production-ready skills have executable regression tests for load-bearing guardrails.
5. Deterministic rules are enforced in scripts when model judgment would be fragile.
6. Autonomous writes, if any, have explicit side-effect, idempotency, postcondition, compensation, concurrency, audit, and blast-radius controls.
7. Critical missing or contradictory state fails closed.
8. Supporting files are self-contained and referenced with safe relative paths.
9. No credentials, tokens, `.env`, private keys, customer data, private transcripts, or proprietary company material are included.
10. Third-party material is attributed when applicable.
11. Large generated artifacts and dependency folders are excluded.
12. The skill is placed under the correct category.
13. If this is a complete replacement, the superseded skill has moved to `skills/legacy/`.
14. `python scripts/validate_reliability.py --repo-root . --run-tests` passes.

## README catalog

Do not manually edit content between `<!-- SKILL_CATALOG:START -->` and `<!-- SKILL_CATALOG:END -->`. `scripts/update_readme.py` regenerates that section from active skill paths. Legacy skills are excluded from the active catalog.
