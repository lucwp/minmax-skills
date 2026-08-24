# Proposal release modes

Every proposal has `meta.release_mode` set to `draft`, `consulting`, or `autonomous`. If omitted for backward compatibility, treat it as `consulting`.

## Draft

Use while facts, scope, pricing, evidence, or design are still being assembled. `[TO DEFINE]` is allowed when it is visibly unresolved. Draft output is not client-ready.

## Consulting

Use for professional client work with a human review before delivery. The proposal may use an explicitly accepted draft business profile, but unresolved items must remain visible and no unsupported fact may be upgraded into certainty.

## Autonomous

Use only when the proposal can be generated and validated without turn-by-turn human review.

Autonomous release requires:

- `business-profile.json` status `configured`;
- the proposal's `source_profile_revision` to match `configuration-state.json`;
- the current profile SHA-256 to match the state file;
- no `[TO DEFINE]` or `[A DEFINIR]` anywhere in the proposal;
- evidence ledger entries for proof pages and referenced claims;
- no unverified evidence;
- structured commercial calculation metadata;
- fixed totals to reconcile deterministically from component values;
- proposal JSON validation to pass;
- HTML static preflight to pass;
- a separate visual QA report with `PASS`, `overflow=false`, `clipping=false`, and no missing assets.

If a runtime cannot produce the visual QA evidence, stop at consulting release. Do not silently downgrade the gate.

Autonomous proposal generation does not authorize autonomous sending. Email, publishing, CRM mutation, or any other external write must pass the surrounding orchestrator's external-write guardrails.
