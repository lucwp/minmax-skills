# Handoff contract to internal minmax-enterprise-proposal

The Inquiry internal skill is the only component responsible for changing reusable business configuration.

## Final system of record

After compilation, the internal Enterprise Proposal skill must contain:

- `references/business-profile.json` — configured reusable commercial and brand context;
- `assets/brand/` — approved provider brand assets only;
- `CONFIGURATION.md` — human-readable configuration metadata;
- `references/configuration-state.json` — machine-readable update metadata.

A temporary inquiry profile is not authoritative after compilation.

## Status behavior

- `configured` — Enterprise Proposal may generate proposals without rerunning business onboarding.
- `draft` — Enterprise Proposal may proceed only with explicit acceptance of unresolved gaps and must keep unknowns as `[TO DEFINE]`.
- `template` — Enterprise Proposal must not generate a client proposal; return control to the orchestrator and run Inquiry.

## Update boundary

Inquiry may change business identity, offers, commercial rules, positioning, buyer logic, proof, claim permissions, brand tokens/assets, voice rules, and proposal defaults.

Inquiry must not rewrite the Enterprise Proposal methodology, claim safeguards, pricing integrity rules, rendering safety checks, or QA gates merely to satisfy a business preference.

## Persistence modes

### Writable workspace

Patch `internal-skills/minmax-enterprise-proposal/` inside the current `minmax-proposals` package and validate the bundle.

### Installed/read-only environment

Build a replacement copy of the entire `minmax-proposals` package with the updated Enterprise Proposal configuration compiled inside it, then package one replacement `skill.zip`. Do not create or ask the user to install a standalone worker.
