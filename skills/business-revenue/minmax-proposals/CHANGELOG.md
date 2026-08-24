# Changelog

## 2.1.0 - 2026-08-24

- Added the MinMax reliability contract and scoped autonomous release modes.
- Added profile revision and SHA-256 binding for autonomous proposals.
- Fixed readiness scoring so missing critical domains cannot be hidden by a high aggregate score.
- Hardened configured-profile validation for pricing, dependencies, commercial rules, brand minimums, voice, and proposal defaults.
- Added evidence-ledger validation and strict autonomous evidence rules.
- Added deterministic fixed-price reconciliation from numeric component values.
- Added strict static preflight plus mandatory external visual QA evidence for autonomous release.
- Hardened asset handling and CSS/font/path safety in compilation and rendering.
- Added regression tests and repository reliability certification metadata.

## 2.0.0 - 2026-08-24

- Consolidated the system into one installable `minmax-proposals` skill.
- Embedded `minmax-proposal-inquiry` and `minmax-enterprise-proposal` as two private internal skills.
- Removed the requirement to install or replace three separate skills.
- Changed persistence so Inquiry compiles configuration into the internal Enterprise Proposal worker.
- Added whole-orchestrator replacement packaging for immutable installed environments.
- Preserved targeted incremental updates, configuration revisioning, proposal validation, HTML rendering, and QA.
