# MinMax Skills

**Tryhard agent skills for high-level business work.**

A public collection of high-effort agent skills for **SMBs and enterprise teams**, built and maintained by **Lucas W. Portella**.

MinMax is where I turn senior-level business workflows into reusable systems for AI agents. The primary target is **OpenAI / ChatGPT / Codex**, with the underlying patterns designed to remain portable to compatible agentic runtimes.

These skills are built for work where quality, context, and judgment matter: **strategy, revenue, product, growth, partnerships, operations, design, analytics, executive communication, and high-stakes business artifacts**.

They are not prompt snippets, generic “act as an expert” wrappers, or automation for automation’s sake. A MinMax skill is meant to encode the parts that usually get lost between conversations: operating logic, decision rules, business context, references, assets, deterministic scripts, quality gates, stop conditions, and the criteria for what “good” actually looks like.

> **The idea:** turn complex business judgment into reusable agent infrastructure.

## Who this is for

MinMax is designed primarily for people doing high-leverage work inside **SMBs, scale-ups, consultancies, and enterprise organizations**.

Think founders, executives, revenue leaders, product leaders, operators, consultants, strategists, and cross-functional teams using AI for work that normally requires context, judgment, and iteration.

Typical use cases include:

- structuring enterprise proposals and commercial recommendations;
- planning complex accounts, partnerships, and revenue motions;
- turning business context into repeatable operating systems;
- diagnosing product, growth, retention, and KPI problems;
- designing executive-ready reports, plans, and decision artifacts;
- orchestrating multi-step agent workflows without wasting model capability or context;
- standardizing how teams approach recurring high-level work.

## Why MinMax

Most agent workflows fail in boring ways: vague instructions, missing context, inconsistent quality, duplicated work, invented assumptions, or no clear definition of “done.” Those failures matter much more when the output informs a client, an executive decision, a commercial negotiation, or a strategic bet.

MinMax skills are built to reduce those failure modes.

- **Business judgment over generic prompting.** The workflow should understand the decision being made, not merely produce well-formatted text.
- **Opinionated by design.** Good workflows require choices. Skills include decision rules, boundaries, escalation logic, and defaults instead of pushing every decision back to the user.
- **Built for consequential work.** The target output is something usable: a proposal, strategy, analysis, plan, operating system, recommendation, decision, or production-ready artifact.
- **Agent-native.** Skills are designed to work with tools, files, references, scripts, other skills, and multi-step execution rather than as isolated prompts.
- **Quality-gated.** When a workflow is fragile, the skill should validate it. Deterministic checks, preflights, regression tests, and explicit PASS/FAIL criteria are preferred over “looks good to me.”
- **Reusable business context.** Offers, positioning, pricing rules, evidence, templates, design systems, and operating constraints can live with the workflow rather than being rediscovered every run.
- **Complex when complexity earns its keep.** I am not optimizing for the shortest `SKILL.md`. I am optimizing for reliable outcomes without unnecessary machinery.

## Start here

### [MinMax Orchestrator GPT](skills/orchestration-agents/minmax-orchestrator-gpt/)

A lightweight control plane for planning, delegation, model selection, context management, verification, and cost-aware agent execution. Use it when the problem is not “can the model answer this?” but **“what is the best way to get this business task done?”**

### [MinMax Proposals](skills/business-revenue/minmax-proposals/)

A reusable proposal system for SMB and enterprise commercial work. It combines business onboarding, offer and pricing configuration, positioning, brand rules, proposal strategy, HTML rendering, and QA into one reusable workflow.

Configure the business once, then generate decision-oriented proposals without rebuilding the commercial context from scratch every time.

## What you will find here

The repository focuses on high-level business activities rather than general-purpose developer utilities.

| Area | Examples |
| --- | --- |
| **Orchestration & agents** | Planning, delegation, model/context governance, verification, multi-agent execution |
| **Business & revenue** | Strategy, enterprise proposals, partnerships, sales systems, account planning, RevOps |
| **Product & growth** | Product strategy, discovery, retention, experimentation, prioritization, growth systems |
| **Marketing & GTM** | Positioning, messaging, demand generation, GTM planning, commercial narratives |
| **Design & UX** | Product design, UI/UX systems, design governance, high-quality business-facing artifacts |
| **Operations & process** | SOPs, service blueprints, operating systems, process design, management cadence |
| **Data & analytics** | KPI design, business diagnostics, dashboards, analytical decision support |
| **Executive artifacts** | Proposals, reports, presentations, memos, plans, spreadsheets, decision documents |

## Philosophy

A useful business skill should make an agent **more consistent, more context-aware, more commercially useful, and harder to derail**.

The goal is not to make AI imitate a job title. It is to encode a better operating model for completing the work.

That often means going beyond prose instructions. Depending on the problem, a skill may include:

```text
SKILL.md      routing and execution contract
agents/       runtime metadata and agent configuration
references/   deeper domain rules and reusable business context
assets/       templates, icons, and static production assets
scripts/      deterministic helpers, validators, and renderers
```

Not every skill needs all of that. Complexity is only justified when it improves the reliability, repeatability, or quality of the business result.

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

If you are adapting a MinMax skill to another runtime, preserve the **workflow contract, business logic, and quality gates** rather than copying only the top-level prompt.

## Authorship and attribution

Unless a specific skill explicitly states otherwise, the work in this repository was authored by **Lucas W. Portella**.

If a skill is adapted from third-party work, its source and attribution should be documented inside that skill. Public does not mean provenance-free.

## Contributing and maintenance

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for folder taxonomy, replacement/legacy policy, and the publishing checklist. The active catalog indexes only canonical skills and ignores `skills/legacy/`.
