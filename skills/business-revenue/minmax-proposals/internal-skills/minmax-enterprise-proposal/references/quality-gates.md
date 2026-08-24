# Quality gates

A proposal is ready only when all material gates for its release mode pass.

## Commercial

Recommendation is explicit; scope maps to configured offers or clearly identified custom work; contracted and optional work are unambiguous; pricing units and totals reconcile; discounts comply; next step is concrete.

For autonomous fixed-price release, component `amount_value` fields must reconcile exactly with `calculation.total_value` within validator tolerance. Do not rely on model arithmetic.

## Evidence

No unsupported guarantees; no invented metrics, logos, testimonials, or client facts; estimates and assumptions are labelled; case-study proof is not generalized beyond evidence.

Autonomous proof pages must reference the proposal evidence ledger. Evidence cannot be `unverified`, and the proposal must remain bound to the configured profile revision and SHA-256 recorded in `configuration-state.json`.

## Narrative

Executive summary passes the decision memo test; What-we-understood is client-specific; recommendation explains tradeoffs; pages do not repeat the same idea in multiple containers; filler and internal jargon are removed.

## Visual

No clipping or overflow; no microscopic type workaround; brand tokens are consistent; logos preserve aspect ratio and contrast; commercial totals are legible.

Static HTML checks are not proof of visual correctness. Autonomous release requires a separate browser, PDF, or screenshot-based QA report with `PASS`, `overflow=false`, `clipping=false`, and no missing assets.

## Technical

Profile validates; proposal JSON validates; profile revision and hash binding pass when autonomous; HTML static preflight passes; visual QA passes when autonomous; required files are present and paths resolve when used.

## Release decision

- `draft`: unresolved items may remain visible.
- `consulting`: a human reviews the artifact before client delivery.
- `autonomous`: every strict gate passes with no unresolved markers.

External sending or publishing is not authorized by this skill. It requires a separate external-write safety envelope.
