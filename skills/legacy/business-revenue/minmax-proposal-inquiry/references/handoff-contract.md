# Handoff contract to minmax-enterprise-proposal

The Inquiry is the only worker responsible for changing reusable business configuration.

## Final system of record

After compilation, the enterprise worker must contain:

- `references/business-profile.json` — configured reusable commercial/brand context;
- `assets/brand/` — approved provider brand assets only;
- `CONFIGURATION.md` — human-readable configuration metadata;
- `references/configuration-state.json` — machine-readable update metadata.

A temporary inquiry profile is not authoritative after compilation.

## Status behavior

- `configured` — enterprise worker may generate proposals without rerunning business onboarding.
- `draft` — enterprise worker may proceed only with explicit acceptance of unresolved gaps and must keep unknowns as `[TO DEFINE]`.
- `template` — enterprise worker must not generate a client proposal; route to Inquiry.

## Update boundary

Inquiry may change business identity, offers and commercial rules, positioning and buyer logic, proof and claim permissions, brand tokens and approved assets, voice rules, and proposal defaults.

Inquiry must not rewrite the enterprise worker's core proposal methodology, claim safeguards, pricing integrity rules, rendering safety checks, or QA gates merely to satisfy a business preference.

## Persistence modes

### Writable workspace

Patch the sibling enterprise worker directly and validate it.

### Installed/read-only environment

Build a replacement enterprise worker and package it. The user's installation/replacement of that worker is the persistence action. Do not claim a silent in-place update occurred.
