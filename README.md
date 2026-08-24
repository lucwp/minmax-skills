# MinMax Skills

**Tryhard agent skills for people who care about the last 20%.**

I'm a tech-savvy autistic business nerd with a tendency to hyperfocus on systems, edge cases, and the uncomfortable distance between **“this basically works”** and **“I would trust this with a client.”**

MinMax is what comes out of that.

This is a public collection of high-effort agent skills for **consulting-grade business work** across SMBs, scale-ups, and enterprise organizations.

Strategy. Revenue. Product. Growth. Partnerships. Operations. Design. Analytics. Executive artifacts. The kind of work where a confident hallucination is not a quirky model behavior. It is a problem.

> **LLMs hallucinate. MinMax skills are designed assuming they will.**

The goal is not to make AI sound like a consultant.

The goal is to make agentic workflows **reliable enough to use in consulting without having to trust the model blindly**.

## Why “MinMax”?

In games, min-maxing means being unreasonably deliberate about a build: understand the system, cut what does not matter, stack what does, exploit the interactions, and keep tuning until the result performs the way you want.

That is pretty close to how I approach business systems.

I like finding the weak link. I like turning fuzzy judgment into explicit rules without making the rules stupid. I like automating repeatable work without automating away the part that actually requires judgment.

And I care disproportionately about the last 20%.

The first 80% gets you a convincing demo.

The last 20% is where you discover whether the workflow survives contradictory context, missing information, pricing exceptions, bad inputs, multiple sources of truth, edge cases, client scrutiny, and the simple question:

**“Where did this fact come from?”**

That is the part MinMax is built for.

## Consulting-grade, not hallucination-free

No skill can honestly guarantee that an LLM will never hallucinate.

So I do not try to solve hallucination with another sentence saying **“do not hallucinate.”**

MinMax skills are designed to make hallucinations **harder to introduce, easier to detect, and less likely to survive into the final output**.

Depending on the workflow, that means things like:

- **Explicit sources of truth.** Define which file, dataset, business profile, source, or user-provided fact wins when context conflicts.
- **Evidence before claims.** Important claims should be traceable to supplied evidence, approved business context, or a clearly identified external source.
- **No silent gap-filling.** If a price, metric, client fact, legal term, testimonial, or assumption is unknown, mark the gap instead of inventing a plausible answer.
- **Fact / assumption separation.** Keep verified facts, estimates, hypotheses, and recommendations from quietly blending into one confident paragraph.
- **Fail closed when needed.** If a critical input is missing or inconsistent, stop the downstream workflow instead of fabricating enough information to continue.
- **Deterministic validation.** Use scripts, schemas, calculators, preflights, and regression checks for things a model should not be trusted to validate by vibes.
- **Consistency checks.** Totals, statuses, recommendations, dates, and repeated claims should agree across the artifact.
- **Human-readable uncertainty.** A consultant should be able to see what is known, what is inferred, and what still needs validation.

The point is not zero-risk AI.

The point is **AI you can supervise like a serious piece of consulting infrastructure rather than a very articulate intern with no fear of being wrong.**

## Business nerd first, AI nerd second

MinMax is not a general collection of developer utilities.

The center of gravity is **high-level business activity** where an agent needs to reason across messy context and still produce something you would be comfortable putting in front of a founder, executive, client, or investment committee.

Typical use cases include:

- structuring enterprise proposals and commercial recommendations;
- planning accounts, partnerships, and revenue motions;
- turning business context into reusable operating systems;
- diagnosing product, growth, retention, and KPI problems;
- designing executive-ready reports, plans, and decision artifacts;
- orchestrating multi-step agent workflows without wasting model capability or context;
- encoding the way a good operator or consultant approaches recurring high-level work.

I care less about making an agent **sound like an expert** and more about making it **operate like someone competent already thought through the workflow, the failure modes, and the review process**.

## What makes a MinMax skill different

These are not prompt snippets, “act as a world-class consultant” wrappers, or giant markdown files that look sophisticated until the task stops following the happy path.

A MinMax skill can include the operating system around the prompt.

- **Opinionated by design.** Decision rules, defaults, boundaries, escalation logic, and stop conditions are explicit when they matter.
- **Source-grounded.** Business facts and reusable context should have identifiable sources of truth instead of living in model improvisation.
- **Built for consequential work.** The target is something usable: a proposal, strategy, analysis, operating model, recommendation, decision, or production-ready artifact.
- **Agent-native.** Skills are designed around tools, files, references, scripts, other skills, and multi-step execution rather than a single giant prompt.
- **Quality-gated.** If something can fail deterministically, I would rather test it than ask the model to “double-check.”
- **Context-rich.** Offers, positioning, pricing rules, proof, templates, design systems, operating constraints, and governance can live with the workflow instead of being rediscovered every run.
- **Complex when complexity earns its keep.** I am not optimizing for the shortest `SKILL.md`. I am optimizing for the simplest system I would actually trust with the task.

## Start here

### [MinMax Orchestrator GPT](skills/orchestration-agents/minmax-orchestrator-gpt/)

The skill behind the name.

A lightweight control plane for planning, delegation, model selection, context management, verification, and cost-aware agent execution.

It exists for the moment when the question stops being **“can the model answer this?”** and becomes **“what is the safest and most efficient way to get this done without turning the workflow into agent spaghetti?”**

### [MinMax Proposals](skills/business-revenue/minmax-proposals/)

A reusable proposal system for SMB and enterprise commercial work.

It combines business onboarding, offer and pricing configuration, positioning, claim governance, brand rules, proposal strategy, HTML rendering, and QA into one workflow.

The business is configured once. Facts, prices, proof, and commercial rules come from explicit sources of truth. Missing information stays missing until it is resolved. The final proposal passes validation before it is treated as client-ready.

It is intentionally overbuilt compared with **“write me a proposal.”**

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

A lot of AI tooling is optimized around getting to a plausible first answer quickly.

That is useful. It is also not what this repository is primarily about.

MinMax starts where the happy path ends.

If a workflow only needs three good instructions, it should stay three instructions. But when the work has real state, reusable business context, multiple sources of truth, fragile calculations, branching logic, external evidence, visual output, or meaningful failure modes, those things should be designed explicitly.

That can mean going beyond prose:

```text
SKILL.md      routing and execution contract
agents/       runtime metadata and agent configuration
references/   business rules, evidence policies, and reusable context
assets/       templates, icons, and production assets
scripts/      validators, calculators, renderers, and deterministic helpers
```

The objective is not complexity.

The objective is reaching the point where the workflow becomes **boringly dependable**.

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

If you adapt a MinMax skill to another runtime, preserve the **workflow contract, source-of-truth rules, and quality gates** rather than copying only the top-level prompt.

## Authorship and attribution

Unless a specific skill explicitly states otherwise, the work in this repository was authored by **Lucas W. Portella**.

If a skill is adapted from third-party work, its source and attribution should be documented inside that skill. Public does not mean provenance-free.

## Contributing and maintenance

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for folder taxonomy, replacement/legacy policy, and the publishing checklist. The active catalog indexes only canonical skills and ignores `skills/legacy/`.
