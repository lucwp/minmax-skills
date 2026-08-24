# Lucas W. Portella — Public Skills

A public collection of agent skills developed and maintained by **Lucas W. Portella**.

This repository is where I publish reusable skills I build for AI agents, ChatGPT, Codex, and compatible agentic runtimes. The focus is practical: orchestration, business systems, product and growth, revenue, operations, design, analytics, and artifact workflows that can be reused across projects.

Unless a specific skill explicitly states otherwise, the skills in this repository were authored by me. If a future skill is adapted from third-party work, its source and attribution should be documented inside that skill.

## Repository structure

Skills are organized by **type first**, then by skill name:

```text
public-skills/
├── skills/
│   ├── orchestration-agents/
│   │   └── <skill-name>/
│   ├── business-revenue/
│   │   └── <skill-name>/
│   ├── product-growth/
│   │   └── <skill-name>/
│   ├── marketing-content/
│   │   └── <skill-name>/
│   ├── design-ux/
│   │   └── <skill-name>/
│   ├── operations-process/
│   │   └── <skill-name>/
│   ├── data-analytics/
│   │   └── <skill-name>/
│   ├── career/
│   │   └── <skill-name>/
│   └── artifact-workflows/
│       └── <skill-name>/
├── scripts/
│   └── update_readme.py
└── .github/workflows/
    └── update-skill-catalog.yml
```

### Category guide

| Folder | Use for |
| --- | --- |
| `orchestration-agents` | Routing, planning, delegation, multi-agent coordination, model/context governance |
| `business-revenue` | Strategy, partnerships, sales, revenue operations, account planning |
| `product-growth` | Product strategy, discovery, retention, experimentation, growth systems |
| `marketing-content` | Positioning, messaging, copywriting, content and demand generation |
| `design-ux` | Product design, UX, UI, visual systems and design QA |
| `operations-process` | SOPs, process design, service blueprints and operating systems |
| `data-analytics` | KPI design, analysis, diagnostics, dashboards and reporting |
| `career` | Career operations, applications, interviews and professional positioning |
| `artifact-workflows` | Reusable document, presentation, spreadsheet and output workflows |

A new category should only be created when an existing one would materially misclassify the skill.

## Skill contract

Each skill should be self-contained under:

```text
skills/<category>/<skill-name>/
```

The only required file is `SKILL.md`. A skill may also include:

```text
agents/       runtime metadata and agent configuration
references/   deeper instructions loaded only when needed
assets/       icons and static assets
scripts/      deterministic helpers used by the skill
```

Do not place credentials, `.env` files, private keys, customer data, or proprietary internal material in this public repository.

## Automatic catalog

The catalog below is generated automatically from every `SKILL.md` under `skills/`.

When a skill is added, removed, renamed, or updated on `main`, GitHub Actions runs `scripts/update_readme.py` and commits an updated catalog when necessary. **Do not manually edit the generated section.**

<!-- SKILL_CATALOG:START -->
## Skill catalog

**1 public skill** across **1 category**.

### Orchestration & Agents

| Skill | What it does |
| --- | --- |
| [Low-Cost Intelligence Orchestrator](skills/orchestration-agents/low-cost-intelligence-orchestrator/) | Manager-style routing, planning and delegation optimized for verified task success per total expected cost. |

<!-- SKILL_CATALOG:END -->

## Using a skill

Copy the complete skill directory into the skills directory used by your agent runtime, then follow the runtime-specific installation rules. Keep the full folder together because `SKILL.md` may progressively load files from `references/`, `assets/`, or `scripts/`.

## Contributing and maintenance

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the folder taxonomy and publishing checklist. The repository is intentionally structured so adding a skill requires minimal repository maintenance: place it in the correct category and push it; the catalog is maintained automatically.
