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

## Publishing checklist

Before pushing a new skill:

1. `SKILL.md` exists and clearly states when the skill should be used.
2. The skill has a narrow enough purpose to be reliably triggered.
3. Supporting files are referenced with relative paths and remain self-contained.
4. No credentials, tokens, `.env`, private keys, customer data, private transcripts, or proprietary company material are included.
5. Third-party material is attributed when applicable.
6. Large generated artifacts and dependency folders are excluded.
7. The skill is placed under the correct primary category.

## README catalog

Do not manually edit content between:

```text
<!-- SKILL_CATALOG:START -->
<!-- SKILL_CATALOG:END -->
```

`scripts/update_readme.py` regenerates that section from the repository's `SKILL.md` files. The GitHub Action runs after changes reach `main`.
