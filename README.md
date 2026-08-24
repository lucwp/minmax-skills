# MinMax Skills

**Tryhard agent skills for people who care about the last 20%.**

A public collection of high-effort, business-first agent skills built and maintained by **Lucas W. Portella**.

MinMax is where I turn workflows I actually use into reusable systems for AI agents. The primary target is **OpenAI / ChatGPT / Codex**, with the underlying patterns designed to remain portable to compatible agentic runtimes.

These are not prompt snippets, generic “act as an expert” wrappers, or a pile of best practices. A MinMax skill is meant to encode the parts that usually get lost between conversations: operating logic, decision rules, references, assets, deterministic scripts, quality gates, stop conditions, and the context required to do the work well more than once.

The focus is practical and business-oriented: **orchestration, business systems, product and growth, revenue, operations, design, analytics, and artifact workflows**.

> **The idea:** configure the thinking once, then reuse the system instead of rebuilding the workflow from scratch every time.

## Why MinMax

Most agent workflows fail in boring ways: vague instructions, missing context, inconsistent quality, duplicated work, invented assumptions, or no clear definition of “done.” MinMax skills are built to reduce those failure modes.

- **Opinionated by design.** Good workflows require choices. Skills include decision rules, boundaries, escalation logic, and defaults instead of pushing every decision back to the user.
- **Built for real work.** The goal is a usable business outcome, not an impressive demo: a proposal, an analysis, a plan, a decision, a system, or a production-ready artifact.
- **Agent-native.** Skills are designed to work with tools, files, references, scripts, other skills, and multi-step execution rather than as isolated prompts.
- **Quality-gated.** When a workflow is fragile, the skill should validate it. Deterministic checks, preflights, regression tests, and explicit PASS/FAIL criteria are preferred over “looks good to me.”
- **Reusable context.** Business rules, positioning, templates, design systems, or operating constraints can live with the skill so they do not need to be rediscovered every run.
- **Complex when complexity earns its keep.** I am not optimizing for the shortest `SKILL.md`. I am optimizing for reliable outcomes without unnecessary machinery.

## Start here

### [MinMax Orchestrator GPT](skills/orchestration-agents/minmax-orchestrator-gpt/)

A lightweight control plane for planning, delegation, model selection, context management, verification, and cost-aware agent execution. Use it when the problem is not “can the model answer this?” but **“what is the best way to get this done?”**

### [MinMax Proposals](skills/business-revenue/minmax-proposals/)

A reusable enterprise proposal system with an internal inquiry/configuration worker and an enterprise-proposal worker. Configure the business once, then generate decision-oriented proposals with consistent offers, positioning, pricing logic, brand rules, HTML rendering, and QA.

## What you will find here

The repository is intentionally broader than developer tooling. Skills may cover:

| Area | Examples |
| --- | --- |
| **Orchestration & agents** | Routing, planning, delegation, model/context governance, verification |
| **Business & revenue** | Strategy, partnerships, proposals, sales systems, account planning, RevOps |
| **Product & growth** | Discovery, retention, experimentation, prioritization, growth systems |
| **Marketing & content** | Positioning, messaging, copy, content systems, demand generation |
| **Design & UX** | Product design, UI/UX systems, visual QA, design governance |
| **Operations & process** | SOPs, service blueprints, operating systems, process design |
| **Data & analytics** | KPI design, diagnostics, dashboards, analytical workflows |
| **Career** | Career operations, applications, interviews, professional positioning |
| **Artifact workflows** | Documents, presentations, spreadsheets, reports, reusable output systems |

## Philosophy

A useful skill should make an agent **more consistent, more context-aware, and harder to derail**.

That usually means going beyond prose instructions. Depending on the problem, a skill may include:

```text
SKILL.md      routing and execution contract
agents/       runtime metadata and agent configuration
references/   deeper domain rules and reusable context
assets/       templates, icons, and static production assets
scripts/      deterministic helpers, validators, and renderers
```

Not every skill needs all of that. Complexity is only justified when it improves the reliability, repeatability, or quality of the result.

## Repository structure

Active skills are organized by **type first**, then by skill name. Superseded skills that were fully replaced are kept under `skills/legacy/` rather than deleted.

```text
minmax-skills/
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
│   ├── artifact-workflows/
│   │   └── <active-skill-name>/
│   └── legacy/
│       └── <category>/
│           └── <superseded-skill-name>/
├── scripts/
│   └── update_readme.py
└── .github/workflows/
    └── update-skill-catalog.yml
```

## Skill contract

Each active skill is self-contained under:

```text
skills/<category>/<skill-name>/
```

The only required entrypoint is `SKILL.md`. Supporting resources stay with the skill so it can be moved, inspected, versioned, and improved as one unit.

Do not place credentials, `.env` files, private keys, customer data, or proprietary internal material in this public repository.

## Replacements and legacy

Normal improvements update the existing active skill in place. When one skill is a **complete replacement** for another, the replacement becomes the canonical active version and the superseded implementation moves to:

```text
skills/legacy/<category>/<old-skill-name>/
```

`skills/legacy/` is historical only. It is excluded from the active catalog and should not be treated as the version to install.

## Skill catalog

The catalog below is generated automatically from active skill paths shaped as `skills/<category>/<skill-name>/SKILL.md`.

When a skill is added, removed, renamed, or updated on `main`, GitHub Actions runs `scripts/update_readme.py` and commits an updated catalog when necessary. **Do not manually edit the generated section.**

<!-- SKILL_CATALOG:START -->
## Skill catalog

**2 public skills** across **2 categories**.

### Orchestration & Agents

| Skill | What it does |
| --- | --- |
| [MinMax Orchestrator GPT](skills/orchestration-agents/minmax-orchestrator-gpt/) | Workspace-level manager/orchestrator for cost-effective planning and delegation. Apply on every input as a lightweight routing control plane: keep trivial work direct; plan boun... |

### Business & Revenue

| Skill | What it does |
| --- | --- |
| [MinMax Proposals](skills/business-revenue/minmax-proposals/) | Orchestrate a complete enterprise proposal system inside one MinMax skill package. Use when a user wants to configure a business for reusable proposal generation, update offers/... |

<!-- SKILL_CATALOG:END -->

## Using a skill

Copy the complete active skill directory into the skills directory used by your agent runtime, then follow the runtime-specific installation rules. Keep the full folder together: `SKILL.md` may progressively load supporting references, assets, or scripts during execution.

If you are adapting a MinMax skill to another runtime, preserve the **workflow contract and quality gates** rather than copying only the top-level prompt.

## Authorship and attribution

Unless a specific skill explicitly states otherwise, the work in this repository was authored by **Lucas W. Portella**.

If a skill is adapted from third-party work, its source and attribution should be documented inside that skill. Public does not mean provenance-free.

## Contributing and maintenance

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for folder taxonomy, replacement/legacy policy, and the publishing checklist. The active catalog indexes only canonical skills and ignores `skills/legacy/`.
