# Contributing to public-skills

This repository is a maintained catalog of reusable agent skills developed by Lucas W. Portella.

## Where a skill belongs

Use exactly one primary category:

- `orchestration-agents`: routing, planning, delegation, agent/model/context governance
- `business-revenue`: strategy, partnerships, sales, revenue operations, account planning
- `product-growth`: product strategy, discovery, retention, experimentation, growth systems
- `marketing-content`: positioning, messaging, copywriting, content, demand generation
- `design-ux`: UX, UI, visual systems, design QA
- `operations-process`: SOPs, process design, service blueprints, operating systems
- `data-analytics`: metrics, diagnostics, dashboards, analysis, reporting
- `career`: career workflows, applications, interviews, professional positioning
- `artifact-workflows`: reusable document, presentation, spreadsheet, and output workflows

Do not duplicate one skill across categories. If classification is ambiguous, choose the category that best describes the skill's primary trigger and user outcome.

## Required structure

```text
skills/<category>/<skill-name>/
└── SKILL.md
```

Optional supporting directories:

```text
agents/       runtime metadata/configuration
references/   progressive-loading instructions
assets/       icons/static assets
scripts/      deterministic helpers
```

## Replacement and legacy policy

Distinguish an **incremental improvement** from a **complete replacement**.

- **Incremental improvement:** the skill keeps the same identity, primary trigger, responsibility, and conceptual contract. Update it in place under `skills/`. Do not create a legacy copy for every normal revision.
- **Complete replacement:** a new skill supersedes the old one as the active implementation, especially when its identity/name, architecture, primary contract, or intended runtime behavior materially changes. Move the replaced skill out of the active catalog to `legacy/<category>/<old-skill-name>/`, then publish the replacement only under `skills/<category>/<new-skill-name>/`.
- Never keep both the superseded and replacement skill active under `skills/` when the replacement is intended to be canonical.
- Legacy skills are historical snapshots. Do not update them after archival except to fix repository integrity or add clearly non-functional archival metadata.
- The active `skills/` tree is the source of truth for what should be installed or used now. The `legacy/` tree exists only for history, rollback, and comparison.

When uncertain, treat a change as a complete replacement only if keeping the previous skill active would create duplicate triggers, competing orchestration, or materially different behavior for the same user intent.

## Publishing checklist

Before pushing a new skill:

1. `SKILL.md` exists and clearly states when the skill should be used.
2. The skill has a narrow enough purpose to be reliably triggered.
3. Supporting files are referenced with relative paths and remain self-contained.
4. No credentials, tokens, `.env`, private keys, customer data, private transcripts, or proprietary company material are included.
5. Third-party material is attributed when applicable.
6. Large generated artifacts and dependency folders are excluded.
7. The skill is placed under the correct primary category.
8. If this is a complete replacement, the superseded skill has been moved to `legacy/` and removed from active `skills/`.

## README catalog

Do not manually edit content between:

```text
<!-- SKILL_CATALOG:START -->
<!-- SKILL_CATALOG:END -->
```

`scripts/update_readme.py` regenerates that section from the repository's `SKILL.md` files. The GitHub Action runs after changes reach `main`.

The generated catalog must index only active skills under `skills/`; content under `legacy/` must remain outside the active catalog.
