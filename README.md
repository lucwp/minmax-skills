# MinMax Skills

**Tryhard agent skills for people who care about the last 20%.**

I'm a tech-savvy autistic business nerd. I tend to hyperfocus on systems, edge cases, and the uncomfortable gap between **“this basically works”** and **“I would trust this with a client or leave it running in production.”**

MinMax is what comes out of that.

This is a public collection of high-effort agent skills for serious business work across SMBs, scale-ups, consultancies, and enterprise teams.

Strategy. Revenue. Product. Growth. Partnerships. Operations. Design. Analytics. Executive artifacts. The kind of work where a confident hallucination is not a funny model quirk. It is a real problem.

> **LLMs hallucinate. MinMax skills are designed assuming they will.**

I am not trying to make AI sound like a consultant.

I am trying to build workflows I can trust in two very different situations: when the output is going in front of a client, and when the workflow is bounded enough that I want the agent to keep running without someone watching every step.

That second bar is much higher.

## Why “MinMax”?

In games, min-maxing means getting unreasonably deliberate about a build. You learn the system, cut what does not matter, stack what does, and keep tuning until the whole thing behaves the way you want.

That is pretty close to how my brain approaches business systems.

I like finding the weak link. I like turning fuzzy judgment into explicit rules without making the rules stupid. I like automating repeatable work without automating away the part that actually needs judgment.

And I care disproportionately about the last 20%.

The first 80% gets you a convincing demo.

The last 20% is where you find out whether the workflow survives contradictory context, missing information, pricing exceptions, bad inputs, multiple sources of truth, weird edge cases, client scrutiny, and unattended runs at 2 a.m.

It is also where someone eventually asks:

**“Where did this fact come from?”**

That is the part MinMax is built for.

## Consulting-grade, production-minded

No skill can honestly guarantee that an LLM will never hallucinate. I do not pretend otherwise.

What I can do is design the workflow so hallucinations are harder to introduce, easier to catch, and less likely to make it into the final output or the next automated step.

That matters when a consultant is reviewing the work. It matters even more when no one is there to catch the mistake in real time.

Depending on the workflow, a MinMax skill may use:

- explicit sources of truth for business facts and configuration;
- evidence requirements before important claims are allowed through;
- visible gaps instead of plausible filler when information is missing;
- clear separation between facts, estimates, assumptions, and recommendations;
- hard stops when a critical input is missing or contradictory;
- schemas, calculators, validators, preflights, and regression checks for things that should not be left to model judgment;
- consistency checks across totals, dates, statuses, recommendations, and repeated claims;
- escalation rules for cases that genuinely need a human decision.

For client work, the goal is straightforward: I want to know what the output is based on before I put my name on it.

For autonomous production use, the standard is stricter. The workflow needs enough boundaries, validation, and failure handling that I am comfortable with the agent doing real work without being babysat turn by turn.

Some tasks will never meet that bar, and that is fine. A good MinMax skill should know when it can continue, when it should ask, and when it should stop.

## Business nerd first, AI nerd second

MinMax is not a general collection of developer utilities.

The center of gravity is high-level business work where the agent has to reason across messy context and still produce something useful: a recommendation, a proposal, a plan, an operating model, an analysis, a decision artifact, or a workflow that keeps running after the chat window closes.

Typical use cases include structuring enterprise proposals, planning accounts and partnerships, diagnosing product or revenue problems, turning business context into reusable operating systems, creating executive-ready artifacts, and orchestrating multi-step agent workflows without wasting model capability or context.

I care less about making an agent sound like an expert and more about making it operate like someone competent has already thought through the workflow, the failure modes, the sources of truth, and what happens when things go wrong.

## What makes a MinMax skill different

These are not prompt snippets or “act as a world-class consultant” wrappers.

A MinMax skill can include the operating system around the prompt.

That may mean decision rules, defaults, source-of-truth contracts, escalation logic, stop conditions, reusable business context, deterministic scripts, validators, renderers, or internal workers that handle different parts of the job.

If something can be checked deterministically, I would rather check it than ask the model to “double-check.” If a fact is missing, I would rather leave it missing than invent a polished answer. If a workflow should stop, it should stop.

I am not optimizing for the shortest `SKILL.md`. I am optimizing for the simplest system I would actually trust with the task.

## Start here

### [MinMax Orchestrator GPT](skills/orchestration-agents/minmax-orchestrator-gpt/)

The skill behind the name.

A lightweight control plane for planning, delegation, model selection, context management, verification, and cost-aware agent execution.

It exists for the moment when the question stops being “can the model answer this?” and becomes “what is the safest and most efficient way to get this done without turning the workflow into agent spaghetti?”

### [MinMax Proposals](skills/business-revenue/minmax-proposals/)

A reusable proposal system for SMB and enterprise commercial work.

It combines business onboarding, offer and pricing configuration, positioning, claim governance, brand rules, proposal strategy, HTML rendering, and QA in one workflow.

The business is configured once. Facts, prices, proof, and commercial rules come from explicit sources of truth. Missing information stays missing until it is resolved. The proposal is validated before it is treated as client-ready.

It is intentionally overbuilt compared with “write me a proposal.”

That is the point.

## What you will find here

| Area | Examples |
| --- | --- |
| **Orchestration & agents** | Planning, delegation, model/context governance, verification, multi-agent execution |
| **Business & revenue** | Strategy, enterprise proposals, partnerships, sales systems, account planning, RevOps |
| **Product & growth** | Product strategy, discovery, retention, experimentation, prioritization, growth systems |
| **Marketing & GTM** | Positioning, messaging, demand generation, GTM planning, commercial narratives |
| **Design & UX** | Product design, UI/UX systems, design governance, client-facing artifacts |
| **Operations & process** | SOPs, service blueprints, operating systems, process design, management cadence |
| **Data & analytics** | KPI design, business diagnostics, dashboards, evidence-backed decision support |
| **Executive artifacts** | Proposals, reports, presentations, memos, plans, spreadsheets, decision documents |

## The last 20%

A lot of AI tooling is optimized around getting to a plausible first answer quickly. That is useful. It is just not what this repository is primarily about.

MinMax starts where the happy path ends.

If a workflow only needs three good instructions, it should stay three instructions. But when the work has real state, reusable business context, multiple sources of truth, fragile calculations, branching logic, external evidence, visual output, unattended execution, or meaningful failure modes, those things should be designed explicitly.

That can mean going beyond prose:

```text
SKILL.md      routing and execution contract
agents/       runtime metadata and agent configuration
references/   business rules, evidence policies, and reusable context
assets/       templates, icons, and production assets
scripts/      validators, calculators, renderers, and deterministic helpers
```

The objective is not complexity.

The objective is getting the workflow to the point where it becomes boringly dependable.

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

**3 public skills** across **3 categories**.

### Orchestration & Agents

| Skill | What it does |
| --- | --- |
| [MinMax Orchestrator GPT](skills/orchestration-agents/minmax-orchestrator-gpt/) | Workspace-level manager/orchestrator for cost-effective, production-minded planning and delegation. Apply on every input as a lightweight routing control plane: keep trivial wor... |

### Business & Revenue

| Skill | What it does |
| --- | --- |
| [MinMax Proposals](skills/business-revenue/minmax-proposals/) | Orchestrate a complete enterprise proposal system inside one MinMax skill package. Use when a user wants to configure a business for reusable proposal generation, update offers/... |

### Artifact Workflows

| Skill | What it does |
| --- | --- |
| [MinMax PT-BR Output](skills/artifact-workflows/minmax-ptbr-output/) | Production-grade PT-BR output standard for writing, rewriting, translating, editing, or reviewing prose with native Brazilian syntax, natural register, semantic fidelity, factua... |

<!-- SKILL_CATALOG:END -->

## Using a skill

Copy the complete active skill directory into the skills directory used by your agent runtime, then follow the runtime-specific installation rules. Keep the full folder together: `SKILL.md` may progressively load supporting references, assets, or scripts during execution.

If you adapt a MinMax skill to another runtime, preserve the workflow contract, source-of-truth rules, and quality gates rather than copying only the top-level prompt.

## Authorship and attribution

Unless a specific skill explicitly states otherwise, the work in this repository was authored by **Lucas W. Portella**.

If a skill is adapted from third-party work, its source and attribution should be documented inside that skill. Public does not mean provenance-free.

## Contributing and maintenance

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for folder taxonomy, replacement/legacy policy, and the publishing checklist. The active catalog indexes only canonical skills and ignores `skills/legacy/`.
