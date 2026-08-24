# Proposal system state machine

## UNCONFIGURED

The internal Enterprise Proposal profile is missing, `template`, or has no usable offer architecture.

Action: route to internal Inquiry.

## DRAFT

Some reusable configuration exists but material gaps remain.

Action: run targeted Inquiry for the gaps before autonomous proposal generation. The user may explicitly accept draft mode for reviewed consulting work; unresolved fields remain visible.

A draft profile cannot produce an `autonomous` release.

## CONFIGURED

Business identity, usable offers, pricing policy, buyer context, commercial defaults, evidence policy, brand minimums, and proposal workflow defaults are materially complete and pass deterministic profile validation.

Action: route to internal Enterprise Proposal. Autonomous release is allowed only when the proposal also binds to the current configuration revision and profile SHA-256 and passes every strict release gate.

## STALE

A configured profile exists, but newer reusable information supplied by the user conflicts with or supersedes it, or the current profile hash no longer matches its recorded configuration state.

Action: route the change through Inquiry, compile into the internal Enterprise Proposal skill, validate, then continue.

## Reusable versus deal-specific

Reusable configuration should affect more than one future proposal and belongs to Inquiry.

Deal-specific information is unique to the current client opportunity and belongs to Enterprise Proposal.

Examples:

- `Our minimum retainer is now $8k` -> reusable -> Inquiry.
- `This client has a $20k budget` -> deal-specific -> Enterprise Proposal.
- `We changed our provider logo` -> reusable -> Inquiry.
- `Use this client's logo in the proposal` -> deal-specific -> Enterprise Proposal.

## Release state

Proposal release state is separate from configuration state:

- `draft`: unfinished artifact;
- `consulting`: reviewed by a human before client delivery;
- `autonomous`: strict profile, evidence, calculation, static HTML, and visual QA gates all pass.

External sending is not part of the proposal release state and requires a separate external-write policy.
