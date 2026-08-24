---
name: minmax-proposal-inquiry
description: Configure and update the MinMax enterprise proposal worker for a specific business. Use for first-time setup or whenever reusable proposal context changes, including offers, positioning, ICP, buyers, pricing, discount rules, proof, claims, brand identity, visual direction, logos, voice, commercial policies, and proposal defaults. Run an adaptive inquiry, validate the resulting business profile, then compile it into minmax-enterprise-proposal by updating that worker's embedded profile, approved brand assets, and configuration state; package a replacement worker when direct in-place updates are unavailable.
---

# MinMax Proposal Inquiry

Configure the proposal engine itself. The final deliverable is an updated `minmax-enterprise-proposal` worker, not a loose questionnaire result.

## Ownership

Use this worker only for reusable business configuration that should affect future proposals.

The enterprise proposal worker owns the persisted configuration after compilation:

- `references/business-profile.json`;
- `assets/brand/`;
- `CONFIGURATION.md`;
- `references/configuration-state.json`.

Temporary inquiry files may be created during setup, but do not treat them as the final system of record.

Read `references/handoff-contract.md`, `references/profile-schema.md`, `references/question-bank.md`, and `references/completeness-rubric.md`.

## Workflow

1. Harvest existing context first from conversation, files, websites, decks, pricing sheets, brand guides, case studies, or approved sources. Do not re-ask known facts.
2. Inspect the current proposal worker. If configured, read its embedded profile and configuration state and treat this as an update.
3. Create a working profile from the current embedded profile or the example schema.
4. Ask only material questions in waves of 3–6 coherent questions.
5. Cover business basics, offer architecture, positioning/buyers, commercial rules, evidence/claims, brand/visual system, and proposal workflow/defaults.
6. Challenge vague positioning, unsupported differentiation, arbitrary discounts, unbounded scope, unverified claims, and conflicting sources.
7. Normalize and validate a temporary `business-profile.json` with `scripts/validate_profile.py`.
8. Score completeness and keep `status: draft` while material gaps remain.
9. Review material reusable changes with the user.
10. Compile into the proposal worker using `scripts/update_enterprise_worker.py`.
11. Validate the updated worker using its profile validator.
12. Persist in place when writable; otherwise build a replacement `minmax-enterprise-proposal/skill.zip`.

## Inquiry domains

### 1. Business basics
Capture business name, legal/display naming rules, website, category, one-line description, markets, languages, currencies, proposal issuer defaults, and brand architecture.

### 2. Offer architecture
For every offer capture official name/descriptor, type, best-fit use cases, business value, delivery mechanism/cadence, deliverables, boundaries/exclusions, prerequisites, client dependencies, duration, pricing model/units/ranges/floors/variables/discount authority, and supporting proof. Do not accept an offer definition that is only marketing copy.

### 3. Positioning and buyer logic
Capture ICP, poor-fit customers, economic buyers, champions, users, procurement/legal stakeholders, trigger events, competitive alternatives, demonstrable differentiators, value proposition, objections, decision criteria, preferred framing, and framing to avoid.

### 4. Commercial rules
Capture currency, tax treatment, payment terms, proposal validity, pricing authority, discount policy, fixed/variable components, minimum term/volume, setup fees, capacity limits, scope-change policy, negotiability boundaries, and scenario policy. Do not infer legal terms.

### 5. Evidence and claims
Capture verified metrics, case studies, testimonials, customer logos, third-party evidence, claim permissions, forbidden claims, guarantees, SLAs, and authorized commitments. Store source and confidence.

### 6. Brand and visual system
Capture approved logo assets/variants, colors, font family names, visual adjectives and anti-adjectives, photography/illustration direction, radius/density/layout preferences, cover treatment, footer/confidentiality language, client-logo behavior, and design references. Never bundle proprietary font binaries.

### 7. Proposal workflow and defaults
Capture output language, page format/orientation, section defaults, About-us behavior, thesis approval behavior, default CTA, email behavior, preferred file outputs, and confidentiality/legal footer requirements.

## Update behavior

When the user changes only one reusable dimension, run a targeted update rather than the full inquiry. Pricing changes update affected offer pricing + commercial rules; new logos update brand assets; new offers collect the complete offer contract; positioning changes update ICP/buyer/value-proposition fields; new case studies update proof and permissions.

After every material update, compile the new profile into the enterprise worker before generating another proposal.

## Completeness gate

Autonomous proposal generation requires materially complete business identity, at least one usable offer, offer boundaries, pricing model or explicit `[TO DEFINE]` policy, buyer/ICP context, commercial defaults, brand minimums, evidence/claim policy, and proposal language/workflow defaults.

If material gaps remain, keep `status: "draft"`. Never fabricate fields to earn a configured status.

## Compilation

Writable workspace:

```bash
python scripts/update_enterprise_worker.py --runtime-skill-dir ../minmax-enterprise-proposal --profile business-profile.json --brand-assets brand-assets --in-place
```

Replacement build:

```bash
python scripts/update_enterprise_worker.py --runtime-skill-dir /path/to/minmax-enterprise-proposal --profile business-profile.json --brand-assets brand-assets --output-dir configured-worker
```

The updater must preserve the enterprise worker's core proposal methodology. Inquiry modifies configuration, not commercial safety rules or QA logic.

## Final handoff

Finish with either **Updated in place** or **Replacement package required**. Do not present `business-profile.json` as the main final deliverable unless the user explicitly asks to inspect or export it.
