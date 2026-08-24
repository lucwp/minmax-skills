---
name: minmax-proposals
description: Orchestrate the MinMax proposal system across business onboarding/configuration and enterprise proposal generation. Use when a user wants to set up MinMax proposals for a business, update offer/pricing/brand/positioning information used by proposals, create a new client proposal, revise an existing proposal, or decide whether proposal configuration must be refreshed first. Route configuration work to minmax-proposal-inquiry and proposal production to minmax-enterprise-proposal, enforcing the shared worker state contract.
---

# MinMax Proposals

Act as the single public entrypoint for the MinMax proposal system. Keep business configuration and deal execution separate.

## Architecture

Use two workers:

1. `minmax-proposal-inquiry` — configure or update the business-specific proposal engine.
2. `minmax-enterprise-proposal` — generate, revise, render, and QA proposals using the configuration compiled into that worker.

Read `references/orchestration-contract.md` before routing. Read `references/state-machine.md` when configuration state is ambiguous.

## Routing

### Route to Inquiry

Use `minmax-proposal-inquiry` when any of these is true:

- first-time setup;
- proposal worker is missing, template, draft, stale, or materially incomplete;
- user wants to change business identity, positioning, ICP, buyer logic, offers, pricing, discount rules, proof, claims, brand, logos, visual rules, voice, commercial policies, or proposal defaults;
- a proposal request depends on information the configured worker does not contain and the missing information is reusable business context rather than deal-specific context.

The Inquiry must update the enterprise worker. A standalone profile is an intermediate build artifact, not the final system of record.

### Route to Enterprise Proposal

Use `minmax-enterprise-proposal` when:

- its embedded profile is `configured` or an explicitly accepted `draft`;
- requested changes are deal-specific rather than reusable business configuration;
- the user wants a commercial thesis, proposal, proposal revision, investment structure, proposal HTML, or proposal QA.

### Mixed requests

If a request contains both configuration changes and a proposal request:

1. update the enterprise worker through Inquiry first;
2. validate the updated worker;
3. generate the proposal against the new configuration in the same workflow when possible.

Never let proposal generation continue against stale configuration after the user changes a reusable commercial rule.

## State contract

The proposal worker owns the persistent business configuration in:

- `references/business-profile.json`;
- `assets/brand/`;
- `CONFIGURATION.md`;
- `references/configuration-state.json` when present.

The Inquiry owns the process that modifies those files. The Enterprise Proposal worker reads them but does not rewrite business configuration during ordinary proposal generation.

## Runtime constraints

In a writable local/Codex workspace, let Inquiry patch the sibling `minmax-enterprise-proposal` skill directly.

In environments where installed skills cannot be overwritten in place, let Inquiry build and package a replacement `minmax-enterprise-proposal/skill.zip`. Treat installing/replacing that worker as the persistence step. Do not pretend an installed package was silently mutated when it was not.

## Non-negotiable behavior

- Do not ask the full business inquiry again for each deal.
- Do not store reusable business facts only in conversation history.
- Do not let the Enterprise Proposal worker invent missing reusable configuration.
- Do not create a new configured worker per client; one configured worker represents the proposal system for one business/brand context.
- If a business operates materially different brands or commercial systems, create separate configured proposal workers or explicit profiles only when the distinction is operationally necessary.
