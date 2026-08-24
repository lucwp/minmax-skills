# Business profile contract

`references/business-profile.json` is the reusable source of truth compiled into this worker by `minmax-proposal-inquiry`.

## Ownership
This enterprise worker reads the profile. It does not run full reusable business onboarding or silently rewrite the profile during ordinary proposal generation. If reusable configuration is missing, stale, contradictory, or materially incomplete, route the change to Inquiry first.

## Minimum viable profile
A profile is usable when it contains business identity/default currency/language; at least one offer with value, deliverables, boundaries and pricing state; buyer/ICP context; payment/validity rules or explicit unresolved states; brand colors/logo rule; claim policy/proof permissions; and proposal workflow defaults.

## Status behavior
- `configured` — generate normally.
- `draft` — proceed only with explicit acceptance of material gaps and keep unresolved values as `[TO DEFINE]`.
- `template` — do not generate a client proposal; route to Inquiry.

## Deal-specific exceptions
Do not recompile the worker for client-specific budget, stakeholders, timing, deal constraints, or client logo.
