# Changelog

## 2.0.0 — 2026-08-24

- Consolidated the system into one installable `minmax-proposals` skill.
- Embedded `minmax-proposal-inquiry` and `minmax-enterprise-proposal` as two private internal skills.
- Removed the requirement to install or replace three separate skills.
- Changed persistence so Inquiry compiles configuration into the internal Enterprise Proposal worker.
- Added whole-orchestrator replacement packaging for immutable installed environments.
- Preserved targeted incremental updates, configuration revisioning, proposal validation, HTML rendering, and QA.
