# Proposal data schema

The renderer consumes JSON with `schema_version`, `meta`, optional `evidence_ledger`, and `pages`.

`meta.release_mode` may be `draft`, `consulting`, or `autonomous`; omission means `consulting` for backward compatibility.

Every page requires `type`, `section`, and `title`. Commercial pages require investment keys for included scope, assumptions, rationale, components, and total. Next-step pages require `next_step`.

## Autonomous additions

Autonomous release also requires:

- `meta.source_profile_revision` matching current configuration state;
- no unresolved markers anywhere in JSON;
- a commercial page and next-step page;
- `evidence_ids` on proof pages, pointing to valid ledger entries;
- no ledger item with `confidence: unverified`;
- structured investment `calculation` metadata.

For `calculation.status: fixed`, provide numeric `total_value`. Every component included in total must provide numeric `amount_value`; the validator reconciles the sum.

For `range`, provide numeric `range_min` and `range_max`. For `formula`, provide formula and resolved inputs. For `variable`, explain what makes total variable.

The schema stays flexible for draft and consulting work, but autonomous release deliberately trades flexibility for verifiability.
