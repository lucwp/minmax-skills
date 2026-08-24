# Claim and evidence policy

Treat claims as verified provider facts, verified client facts, approved proof, third-party evidence, internal estimates, or assumptions.

- Never upgrade an assumption to a fact because it sounds plausible.
- Never turn a historical case-study result into a guaranteed future outcome.
- Never claim causality from correlational evidence.
- Never use customer logos or testimonials as endorsements when permission is unknown.
- Prefer proof that addresses the buyer's actual risk.
- Use fewer stronger proof points rather than a logo wall with no decision value.

## Evidence ledger

For proposals that use explicit proof, maintain `evidence_ledger` entries in `proposal.json` with a stable ID, evidence class, exact claim, source reference, and confidence. Pages reference those entries through `evidence_ids`.

Autonomous release forbids `confidence: unverified`. Internal estimates may be used only with an explicit `display_label` that makes the estimate status visible to the reader.

The ledger improves traceability; it does not give the model permission to manufacture sources. `source_ref` must point to an actual supplied, configured, or retrieved source.
