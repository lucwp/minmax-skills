---
name: minmax-enterprise-proposal
description: Generate, revise, render, and QA high-quality B2B and enterprise proposals using the business configuration compiled into this worker by minmax-proposal-inquiry. Use when a configured MinMax proposal system needs a commercial thesis, recommendation, scope, investment structure, proposal narrative, structured proposal data, branded standalone HTML, or proposal revision. Do not perform reusable business onboarding here; if the embedded profile is template, stale, or materially incomplete, route configuration work to minmax-proposal-inquiry before generating the proposal.
---

# Minmax Enterprise Proposal

Create proposals as decision artifacts, not brochures. Optimize for a buyer who did not attend the sales call: they should understand the situation, recommended decision, business consequence, scope, investment, dependencies, and next step without needing oral explanation.

## Source of truth

Before writing a proposal:

1. Load `references/business-profile.json` and, when present, `references/configuration-state.json`.
2. Require profile status `configured`, or an explicitly accepted `draft` with material gaps surfaced. If the profile is missing, `template`, stale, or materially incomplete, stop proposal generation and route reusable configuration to `minmax-proposal-inquiry`. Do not run a parallel business-onboarding flow inside this worker.
3. Treat the embedded profile as the source of truth for business identity, offer definitions, pricing rules, proof, brand, voice, and proposal defaults.
4. Treat deal-specific facts supplied in the current conversation or files as the source of truth for the client opportunity.
5. Never infer a price, discount, client fact, testimonial, metric, legal term, or case-study claim that is not supported by those sources. Mark gaps as `[TO DEFINE]`.
6. If the user supplies a reusable business change while requesting a proposal, route that change through Inquiry first, then generate the proposal from the updated worker.

Validate configured profiles with:

```bash
python scripts/validate_profile.py references/business-profile.json
```

## Configuration boundary

This worker reads reusable business configuration but does not own its mutation. `minmax-proposal-inquiry` is responsible for changing offers, positioning, pricing policy, proof, brand assets, voice, and proposal defaults.

Deal-specific information may be used without recompiling the worker. Reusable changes must be compiled into the worker before they affect proposal generation.

Examples:

- client budget, stakeholders, timing, current pain -> deal-specific;
- provider price floor, new offer, new logo, new case study, new discount policy -> reusable configuration -> Inquiry.

## Proposal workflow

1. **Collect the deal brief.** Capture client, problem/opportunity, desired outcome, stakeholders, decision criteria, timing, budget signal, constraints, risks, current state, prior conversation, and requested next step. Do not re-ask facts already supplied.
2. **Select the commercial architecture.** Read `references/commercial-architecture.md`. Decide whether the opportunity is a custom project, comparable/recurring service, or hybrid.
3. **Map the right offers.** Use only offers defined in the business profile unless the user explicitly asks to design a new offer. Respect boundaries, prerequisites, dependencies, capacity, and pricing rules.
4. **Formulate the commercial thesis.** State the central tension/opportunity, business reading, recommendation, why this shape is appropriate, what is deliberately excluded, material assumptions, and unresolved gaps.
5. **Approval behavior.** By default, present the thesis before materializing the final proposal. If the user explicitly asks to proceed without approval, treat the thesis as an internal gate and continue in the same turn.
6. **Write the proposal.** Follow `references/proposal-blueprint.md`, `references/investment-format.md`, `references/claim-evidence-policy.md`, and the configured voice.
7. **Create structured proposal data.** Write `proposal.json` following `references/proposal-data-schema.md` and validate it with `scripts/validate_proposal.py`.
8. **Render standalone HTML.** Use `scripts/render_proposal.py --profile references/business-profile.json --proposal proposal.json --output proposal.html`.
9. **Run preflight.** Execute `scripts/preflight_proposal.py proposal.html proposal.json` and fix every FAIL.
10. **Run the content consistency pass.** Read `references/content-consistency-contract.md`. Remove redundant facts, duplicate recommendation labels, inconsistent totals, unsupported claims, and repeated briefing.
11. **Deliver.** Return the proposal text when useful, `proposal.json` for editability, and the validated standalone HTML. Generate a send email only when the user asks for one.

## Commercial thesis contract

Include:

- central problem, tension, or opportunity;
- business consequence;
- proposal type: custom project, comparable/recurring, or hybrid;
- recommended commercial shape;
- offers or workstreams included;
- why this design is more appropriate than the obvious alternatives;
- what will not be prioritized;
- assumptions and dependencies;
- unresolved items marked `[TO DEFINE]`.

Do not use generic discovery language. The thesis must make a decision easier.

## Proposal architecture

Use the smallest structure that supports the buying decision. A sensible default is:

1. Cover
2. Executive summary
3. What we understood
4. Recommendation and rationale
5. Scope / workstreams / offers
6. Delivery approach or operating model, only when it clarifies execution
7. Investment
8. Conditions for success / dependencies
9. Evolution or optional extensions, only when relevant
10. Next steps

Do not add an “About us” page by default. Use proof selectively where it reduces risk or strengthens a decision.

## Executive summary test

A decision maker should be able to answer, from the executive summary alone:

- What are you recommending?
- Why now?
- What business outcome or risk does this address?
- What is included?
- What will it cost or how will it be priced?
- What remains variable or `[TO DEFINE]`?
- What should happen next?

If those answers are not visible, rewrite the summary.

## Scope pages

For each offer, phase, or workstream, use this information hierarchy unless the deal requires a better one:

**[Offer / phase / workstream name]**  
[Short contextual subtitle]

**Business value**  
One concise paragraph connecting the work to the client's situation.

**How it works**
- practical operating detail;
- cadence, coverage, participation, or mechanism;
- relevant prerequisite or boundary.

**What it delivers**
- concrete deliverable or capability;
- concrete deliverable or capability;
- concrete deliverable or capability.

Avoid burying commercial terms in scope prose. Keep pricing and payment terms in Investment.

## Investment rules

Read `references/investment-format.md` before writing pricing.

- Use a **single recommended investment** for custom projects unless options materially improve the decision.
- Use **A/B/C or tiered options** only when the alternatives genuinely differ in scope, capacity, coverage, intensity, term, risk, or outcome potential.
- Never create cosmetic options.
- Identify one option as recommended only when the profile or deal logic supports a recommendation.
- Preserve units: fixed fee, monthly retainer, per seat, per unit, usage, milestone, variable fee, or hybrid.
- Separate fixed, recurring, and variable components.
- Make the consolidated total explicit only when it can be calculated from known inputs.
- If a total depends on volume or an unresolved variable, show a formula, range, or `[TO DEFINE]`; do not fake precision.
- Apply only discount rules explicitly allowed by the business profile.

## Evidence and claims

Read `references/claim-evidence-policy.md`.

- Prefer verified proof linked to the relevant offer or buyer concern.
- Distinguish company facts, client-specific facts, internal estimates, third-party evidence, and assumptions.
- Do not turn correlation into causation.
- Do not promise outcomes the provider does not control.
- If proof permission is unknown, do not place a customer logo or quote in the final proposal as an approved endorsement.

## Visual and brand behavior

Read `references/design-system.md`.

- Apply the configured brand tokens from the business profile.
- Use the provider logo and optional cover imagery only when a valid local asset path exists.
- Client logo is deal-specific. Use only an asset supplied by the user or an official version retrieved with permission from an available source.
- Do not create a white rectangle behind transparent logos unless the brand profile explicitly requires it.
- Do not bundle proprietary font binaries. Use configured CSS family names with safe fallbacks.
- Keep decoration subordinate to information. Shapes, gradients, photography, or illustration must support hierarchy rather than fill space.
- Preserve page-safe layout. Never fix overflow by shrinking text below readable sizes.

## Semantic page planning

Before rendering a complex proposal, map each page to one of these semantic families:

- `cover`
- `executive`
- `narrative`
- `decision`
- `scope`
- `sequence`
- `comparison`
- `commercial`
- `proof`
- `next-step`

Use `references/page-manifest-schema.md` when a proposal needs explicit page planning. Do not create a visual sequence unless the underlying work is actually sequential.

## Content consistency

A page should have one visual carrier for each important fact, state, metric, date, recommendation, or total. If a badge says `RECOMMENDED`, the option title should not repeat “Recommended.” If a total is shown in a summary card and detailed investment page, the numbers must match exactly.

## Quality gates

Before considering a proposal complete, verify `references/quality-gates.md` and run the scripts. Hard failures include:

- invented pricing or proof;
- unsupported guarantee or outcome claim;
- contradictory totals;
- unclear contracted scope versus optional future work;
- repeated recommendation state within the same page;
- placeholders presented as facts;
- invalid or missing business profile;
- HTML overflow, clipped content, or missing essential assets;
- generic copy that could be sent to any company without changing meaning.

## Editing behavior

When the user asks to revise a proposal:

1. Preserve verified deal facts and configured business rules.
2. Change only the requested content or design dimensions unless a dependency forces a broader correction.
3. Re-run validation and preflight after any structural, pricing, or HTML change.
4. If a requested change conflicts with the business profile, identify the conflict explicitly rather than silently overriding the source of truth.
