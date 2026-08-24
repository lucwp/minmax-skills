# Orchestration contract

## Public entrypoint

`minmax-proposals` is the user-facing router. The two workers have narrow responsibilities.

## Worker A — minmax-proposal-inquiry

Owns reusable configuration:

- business identity;
- offer architecture;
- positioning and buyer logic;
- pricing and commercial rules;
- evidence and claim permissions;
- brand assets and visual tokens;
- voice and proposal workflow defaults.

Its successful terminal state is an updated, validated `minmax-enterprise-proposal` worker.

## Worker B — minmax-enterprise-proposal

Owns deal execution:

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

The configured enterprise worker is the system of record. The Inquiry may use temporary profile files while interviewing, but the final configuration must be compiled into the enterprise worker.

## Update rule

When Inquiry changes reusable configuration, it must:

1. validate the new profile;
2. update the enterprise worker profile and approved assets;
3. write configuration metadata;
4. run the enterprise worker profile validator;
5. package the replacement worker when direct in-place persistence is unavailable.

## Staleness rule

Any proposal generated after a reusable configuration change must use the updated worker. Do not generate from the pre-update profile.
