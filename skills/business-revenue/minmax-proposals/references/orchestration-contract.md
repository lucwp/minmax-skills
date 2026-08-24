# Orchestration contract

## Public entrypoint

`minmax-proposals` is the only public and installable skill.

It contains two private internal skills:

- `internal-skills/minmax-proposal-inquiry/`
- `internal-skills/minmax-enterprise-proposal/`

The user must not install or invoke them separately.

## Internal Skill A — minmax-proposal-inquiry

Own reusable configuration:

- business identity;
- offer architecture;
- positioning and buyer logic;
- pricing and commercial rules;
- evidence and claim permissions;
- brand assets and visual tokens;
- voice and proposal workflow defaults.

Its successful terminal state is an updated and validated internal Enterprise Proposal configuration.

## Internal Skill B — minmax-enterprise-proposal

Own deal execution:

- deal brief;
- commercial thesis;
- recommendation;
- proposal narrative;
- scope architecture;
- investment presentation;
- structured proposal data;
- HTML rendering and QA.

It must not redefine reusable business configuration during ordinary proposal work.

## Configuration ownership

The internal Enterprise Proposal folder is the system of record for reusable configuration. Inquiry may create temporary working files while interviewing, but after compilation the source of truth is:

- `internal-skills/minmax-enterprise-proposal/references/business-profile.json`;
- `internal-skills/minmax-enterprise-proposal/references/configuration-state.json`;
- `internal-skills/minmax-enterprise-proposal/assets/brand/`;
- `internal-skills/minmax-enterprise-proposal/CONFIGURATION.md`.

## Compile rule

Whenever Inquiry changes reusable configuration, it must:

1. validate the working profile;
2. update the internal Enterprise Proposal profile and approved brand assets;
3. increment configuration metadata;
4. run the Enterprise Proposal profile validator;
5. validate the one-package bundle;
6. if persistence is immutable, package a replacement **root `minmax-proposals/skill.zip`**, never a standalone worker ZIP.

## Staleness rule

Any proposal generated after a reusable configuration change must use the updated internal worker. Do not generate from a pre-update profile.
