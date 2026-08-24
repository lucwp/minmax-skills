# Internal Skill: minmax-proposal-inquiry

Configure or update reusable business context for the MinMax proposal system. Never present this internal skill as separately installable.

## Goal

End with the internal `minmax-enterprise-proposal` configuration updated, validated, and ready for future proposals. Treat any standalone working profile as an intermediate artifact only.

## Source and target paths

Working inquiry resources live under:

- `internal-skills/minmax-proposal-inquiry/`

Compile the final reusable configuration into:

- `internal-skills/minmax-enterprise-proposal/references/business-profile.json`
- `internal-skills/minmax-enterprise-proposal/references/configuration-state.json`
- `internal-skills/minmax-enterprise-proposal/assets/brand/`
- `internal-skills/minmax-enterprise-proposal/CONFIGURATION.md`

Read before operating:

- `references/profile-schema.md`
- `references/question-bank.md`
- `references/completeness-rubric.md`
- `references/handoff-contract.md`

Resolve those paths relative to this internal skill directory.

## Workflow

1. **Harvest existing context first.** Use supplied files, websites, decks, pricing sheets, brand guides, case studies, prior approved answers, and the currently compiled enterprise profile. Do not re-ask known facts.
2. **Inspect current configuration.** Read the internal Enterprise Proposal profile and configuration state. Treat an existing profile as an update baseline.
3. **Create a working profile.** Start from current compiled values when present. Use `assets/business-profile.example.json` only as a schema example, never as factual content.
4. **Ask only material questions.** Use waves of 3–6 coherent questions. Prioritize offer architecture, pricing, buyer logic, boundaries, and proof before decorative preferences.
5. **Cover all seven domains.** Business basics; offers; positioning/buyers; commercial rules; evidence/claims; brand/visual system; proposal workflow/defaults.
6. **Challenge weak inputs.** Do not normalize vague positioning, unsupported differentiation, arbitrary discounts, unlimited scope, contradictory pricing, or unverified claims into false certainty.
7. **Validate.** Run `scripts/validate_profile.py` on the working profile.
8. **Score completeness.** Run `scripts/profile_report.py`. Use `configured` only when the completeness gate is materially satisfied; otherwise use `draft`.
9. **Review material changes.** Surface reusable facts changed, critical gaps, and assumptions. Do not ask approval for trivial formatting normalization.
10. **Compile into Enterprise Proposal.** Run `scripts/compile_orchestrator.py` from this internal skill.
11. **Validate the compiled enterprise profile.** Run `internal-skills/minmax-enterprise-proposal/scripts/validate_profile.py` against the compiled profile.
12. **Return control to the root orchestrator.** If the current request also needs a proposal, continue through the internal Enterprise Proposal skill using the new configuration.

## Inquiry domains

### Business basics

Capture business name, display/legal naming rules, website, category, one-line description, markets, languages, currencies, issuer defaults, and relevant brand architecture.

### Offer architecture

For each offer that may appear in proposals, capture:

- official name and optional descriptor;
- type: project, recurring, usage, hybrid, or custom;
- best-fit problems and use cases;
- buyer value;
- delivery mechanism and cadence;
- deliverables;
- boundaries and exclusions;
- prerequisites and client dependencies;
- duration/cadence;
- pricing model, units, ranges, floors, variables, and discount authority;
- evidence supporting the offer.

Do not accept an offer definition that is only marketing copy.

### Positioning and buyer logic

Capture ICP, poor-fit customers, economic buyers, champions, users, procurement/legal stakeholders, trigger events, competitive alternatives, demonstrable differentiators, value proposition, objections, decision criteria, preferred framing, and framing to avoid.

### Commercial rules

Capture currency, tax treatment, payment terms, proposal validity, pricing authority, discount policy, fixed/variable components, minimum term or volume, setup fees, capacity limits, scope-change policy, negotiability boundaries, and scenario policy.

Do not infer legal terms.

### Evidence and claims

Capture verified metrics, case studies, testimonials, customer-logo permissions, third-party evidence, claim permissions, forbidden claims, guarantees, SLAs, and authorized commitments. Preserve source and confidence.

### Brand and visual system

Capture approved logo assets/variants, colors, font family names, visual adjectives and anti-adjectives, image direction, radius/density/layout preferences, cover treatment, footer/confidentiality language, client-logo behavior, and design references.

Never bundle proprietary font binaries.

### Proposal workflow and defaults

Capture output language, page format/orientation, section defaults, About-us behavior, thesis approval behavior, default CTA, email behavior, preferred outputs, and confidentiality/legal footer requirements.

## Incremental update behavior

When only one reusable dimension changes, update only the affected fields and dependencies.

Examples:

- pricing change -> affected offer pricing + commercial rules;
- new logo -> brand asset + path + configuration revision;
- new case study -> proof library + offer linkage if applicable;
- new offer -> offer architecture + pricing + boundaries + relevant proof;
- new positioning -> buyer logic + framing + differentiators.

Never rerun the full onboarding merely because one reusable field changed.

## Compile and persistence behavior

Use:

```bash
python internal-skills/minmax-proposal-inquiry/scripts/compile_orchestrator.py \
  --orchestrator-dir <minmax-proposals-root> \
  --profile <working-business-profile.json> \
  --in-place
```

when the source package is writable.

When it is not persistently writable, use:

```bash
python internal-skills/minmax-proposal-inquiry/scripts/compile_orchestrator.py \
  --orchestrator-dir <minmax-proposals-root> \
  --profile <working-business-profile.json> \
  --output-dir <destination>
```

This must build one replacement `minmax-proposals/` package and one `skill.zip` containing the whole orchestrator with both internal skills. Never emit a standalone Enterprise Proposal worker as the normal persistence artifact.

## Hard rules

- Never invent missing business facts.
- Never mark a profile `configured` merely to avoid more inquiry.
- Never overwrite methodology files while compiling business configuration.
- Never make deal-specific client facts part of reusable provider configuration unless the user explicitly wants that.
- Never route the user to a separately installed Inquiry or Enterprise skill.
