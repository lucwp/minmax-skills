---
name: minmax-proposals
description: "Orchestrate a complete enterprise proposal system inside one MinMax skill package. Use when a user wants to configure a business for reusable proposal generation, update offers/pricing/positioning/proof/brand rules, create or revise a client proposal, render proposal HTML, or run proposal QA. Internally route work between two private skills: minmax-proposal-inquiry for reusable business configuration and minmax-enterprise-proposal for deal-specific proposal production. Keep one public entrypoint and one installable package; configuration changes must be compiled into the internal enterprise worker before future proposals use them."
---

# MinMax Proposals

Act as the only public entrypoint for the proposal system. Do not expose the two internal skills as separately installable or separately invoked skills.

## Internal architecture

Use exactly two private internal skills:

1. **minmax-proposal-inquiry** — configure and update reusable business context.
2. **minmax-enterprise-proposal** — generate, revise, render, and QA deal-specific proposals from the compiled configuration.

Load the relevant internal instructions only when routing requires them:

- Inquiry: `internal-skills/minmax-proposal-inquiry/INSTRUCTIONS.md`
- Enterprise Proposal: `internal-skills/minmax-enterprise-proposal/INSTRUCTIONS.md`

Read `references/orchestration-contract.md` before routing. Read `references/state-machine.md` whenever configuration state is missing, ambiguous, draft, or stale.

## Single-package invariant

Maintain one installable skill package named `minmax-proposals`.

- Keep only the root `SKILL.md` as the public skill entrypoint.
- Treat the two folders under `internal-skills/` as private workers, not standalone installable skills.
- Never ask the user to install `minmax-proposal-inquiry` or `minmax-enterprise-proposal` separately.
- Never create a separate enterprise-worker ZIP as the normal persistence mechanism.

## Routing

### Route to Inquiry

Load and execute the Inquiry internal skill when any of these is true:

- first-time setup;
- internal enterprise configuration is `template`, `draft`, `stale`, missing, or materially incomplete;
- reusable business identity, positioning, ICP, buyer logic, offers, pricing, discount rules, proof, claims, brand, logos, visual rules, voice, commercial policies, or proposal defaults changed;
- a proposal request depends on missing information that should affect future proposals, not only the current deal.

The Inquiry must compile validated reusable configuration into the internal Enterprise Proposal skill before proposal generation continues.

### Route to Enterprise Proposal

Load and execute the Enterprise Proposal internal skill when:

- its embedded profile is `configured`, or the user explicitly accepts a `draft` profile with surfaced gaps;
- the request is deal-specific;
- the user wants a commercial thesis, proposal, revision, investment structure, standalone HTML, or proposal QA.

### Mixed request

If a request changes reusable configuration and asks for a proposal in the same workflow:

1. route the reusable change through Inquiry;
2. validate and compile the updated internal enterprise configuration;
3. run Enterprise Proposal against the updated configuration;
4. never generate against the pre-update profile.

## Configuration ownership

Persist reusable proposal configuration only inside the internal Enterprise Proposal skill:

- `internal-skills/minmax-enterprise-proposal/references/business-profile.json`
- `internal-skills/minmax-enterprise-proposal/references/configuration-state.json`
- `internal-skills/minmax-enterprise-proposal/assets/brand/`
- `internal-skills/minmax-enterprise-proposal/CONFIGURATION.md`

The Inquiry owns mutation of those files. Enterprise Proposal reads them and must not silently rewrite reusable business rules during ordinary deal work.

## Persistence modes

### Writable workspace

When the MinMax skill source directory is writable, let Inquiry patch the internal Enterprise Proposal skill in place and increment `configuration_revision`.

### Installed/immutable skill environment

When the installed skill bundle cannot be modified persistently:

1. let Inquiry build a replacement copy of the entire `minmax-proposals` package;
2. write the updated business profile and approved brand assets into its internal Enterprise Proposal folder;
3. validate the rebuilt bundle;
4. package and return one replacement `skill.zip` for `minmax-proposals`.

Do not claim that an immutable installed skill was silently updated. The replacement package is the persistence step.

## Non-negotiable behavior

- Do not run the full business inquiry again for each client.
- Do not store reusable commercial facts only in chat history.
- Do not let Enterprise Proposal invent missing reusable configuration.
- Do not create three pricing scenarios unless alternatives are materially different.
- Do not invent prices, discounts, claims, proof, logos, legal terms, guarantees, or customer facts.
- Distinguish reusable business configuration from current-deal facts.
- Keep the root orchestrator in control of every handoff and terminal output.
