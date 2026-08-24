# Proposal system state machine

## UNCONFIGURED

The internal Enterprise Proposal profile is missing, `template`, or has no usable offer architecture.

Action: route to internal Inquiry.

## DRAFT

Some reusable configuration exists but material gaps remain.

Action: run targeted Inquiry for the gaps before autonomous proposal generation. The user may explicitly accept draft mode; unresolved fields remain `[TO DEFINE]`.

## CONFIGURED

Business identity, usable offers, pricing policy, buyer context, commercial defaults, evidence policy, brand minimums, and proposal workflow defaults are materially complete.

Action: route to internal Enterprise Proposal.

## STALE

A configured profile exists, but newer reusable information supplied by the user conflicts with or supersedes it.

Action: route the change through Inquiry, compile into the internal Enterprise Proposal skill, validate, then continue.

## Reusable versus deal-specific

Reusable configuration should affect more than one future proposal and belongs to Inquiry.

Deal-specific information is unique to the current client opportunity and belongs to Enterprise Proposal.

Examples:

- `Our minimum retainer is now $8k` -> reusable -> Inquiry.
- `This client has a $20k budget` -> deal-specific -> Enterprise Proposal.
- `We changed our provider logo` -> reusable -> Inquiry.
- `Use this client's logo in the proposal` -> deal-specific -> Enterprise Proposal.
