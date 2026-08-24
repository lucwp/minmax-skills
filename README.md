## Public Skills

A public collection of agent skills developed and maintained by **me**.

This repository is where I publish reusable skills I build for AI agents, ChatGPT, Codex, and compatible agentic runtimes. The focus is practical: orchestration, business systems, product and growth, revenue, operations, design, analytics, and artifact workflows that can be reused across projects.

Unless a specific skill explicitly states otherwise, the skills in this repository were authored by me. If a future skill is adapted from third-party work, its source and attribution should be documented inside that skill.

## Repository structure

Active skills are organized by **type first**, then by skill name. Superseded skills that were fully replaced live outside the active catalog under `legacy/`.

```text
public-skills/
├── skills/
│   ├── orchestration-agents/
│   │   └── <active-skill-name>/
│   ├── business-revenue/
│   │   └── <active-skill-name>/
│   ├── product-growth/
│   │   └── <active-skill-name>/
│   ├── marketing-content/
│   │   └── <active-skill-name>/
│   ├── design-ux/
│   │   └── <active-skill-name>/
│   ├── operations-process/
│   │   └── <active-skill-name>/
│   ├── data-analytics/
│   │   └── <active-skill-name>/
│   ├── career/
│   │   └── <active-skill-name>/
│   └── artifact-workflows/
│       └── <active-skill-name>/
├── legacy/
│   └── <category>/
│       └── <superseded-skill-name>/
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

Each active skill should be self-contained under:

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

## Replacements and legacy

Normal improvements update the existing active skill in place. When one skill is a **complete replacement** for another, the replacement becomes the only active version under `skills/` and the superseded skill is archived under `legacy/<category>/<old-skill-name>/`.

`legacy/` is historical only: it is excluded from the active skill catalog and should not be treated as the version to install. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the replacement criteria and maintenance rules.

## Automatic catalog

The catalog below is generated automatically from every `SKILL.md` under `skills/`.

When a skill is added, removed, renamed, or updated on `main`, GitHub Actions runs `scripts/update_readme.py` and commits an updated catalog when necessary. **Do not manually edit the generated section.**

<!-- SKILL_CATALOG:START -->
## Skill catalog

**4 public skills** across **2 categories**.

### Orchestration & Agents

| Skill | What it does |
| --- | --- |
| [MinMax Orchestrator GPT](skills/orchestration-agents/minmax-orchestrator-gpt/) | Workspace-level manager/orchestrator for cost-effective planning and delegation. Apply on every input as a lightweight routing control plane: keep trivial work direct; plan boun... |

### Business & Revenue

| Skill | What it does |
| --- | --- |
| [Minmax Enterprise Proposal](skills/business-revenue/minmax-enterprise-proposal/) | Generate, revise, render, and QA high-quality B2B and enterprise proposals using the business configuration compiled into this worker by minmax-proposal-inquiry. Use when a conf... |
| [MinMax Proposal Inquiry](skills/business-revenue/minmax-proposal-inquiry/) | Configure and update the MinMax enterprise proposal worker for a specific business. Use for first-time setup or whenever reusable proposal context changes, including offers, pos... |
| [MinMax Proposals](skills/business-revenue/minmax-proposals/) | Orchestrate the MinMax proposal system across business onboarding/configuration and enterprise proposal generation. Use when a user wants to set up MinMax proposals for a busine... |

<!-- SKILL_CATALOG:END -->

## Using a skill

Copy the complete skill directory into the skills directory used by your agent runtime, then follow the runtime-specific installation rules. Keep the full folder together because `SKILL.md` may progressively load files from `references/`, `assets/`, or `scripts/`.

## Contributing and maintenance

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the folder taxonomy, replacement/legacy policy, and publishing checklist. The active catalog is maintained automatically from `skills/` only.
