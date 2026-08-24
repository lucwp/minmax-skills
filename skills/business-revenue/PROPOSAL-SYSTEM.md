# MinMax Proposal System

The MinMax Proposal System is a three-skill architecture for configuring and operating a reusable enterprise proposal engine.

```text
minmax-proposals                  # public router / orchestrator
├── minmax-proposal-inquiry       # configures and updates the proposal worker
└── minmax-enterprise-proposal    # generates, renders, and QA-checks proposals
```

## Components

- [`minmax-proposals`](./minmax-proposals/) is the public entrypoint. It routes configuration work to Inquiry and deal/proposal work to the Enterprise Proposal worker.
- [`minmax-proposal-inquiry`](./minmax-proposal-inquiry/) performs first-run onboarding and targeted configuration updates. It compiles reusable business context into the enterprise worker.
- [`minmax-enterprise-proposal`](./minmax-enterprise-proposal/) is the configured runtime that creates commercial theses, proposals, structured proposal data, standalone HTML, and QA outputs.

## First run

1. Invoke `minmax-proposals` for proposal setup.
2. The orchestrator routes to `minmax-proposal-inquiry`.
3. Inquiry harvests existing business context and asks only material gaps.
4. Inquiry validates the business profile and compiles it into `minmax-enterprise-proposal`.
5. In a writable workspace the worker is patched in place. In an installed/read-only environment Inquiry builds a replacement worker package for installation.
6. Future proposal requests route directly to the configured enterprise worker.

## Updating configuration

Reusable changes such as a new offer, price floor, logo, case study, positioning rule, or commercial policy route through Inquiry. The updated configuration is compiled into the enterprise worker before subsequent proposals are generated.

Deal-specific facts such as client budget, stakeholders, timing, and opportunity constraints stay inside the proposal workflow and do not rewrite the reusable worker.

## Persistence model

The configured enterprise worker is the persistent system of record for reusable proposal context. Its embedded configuration includes the business profile, approved brand assets, and configuration state.

The Inquiry owns mutations to that configuration. The Enterprise Proposal worker reads it but does not silently rewrite reusable business rules during normal proposal generation.

## Installation

Each component is an independently valid ChatGPT Skill and should be installed as its own skill directory. Do not package the three `SKILL.md` entrypoints into one ChatGPT skill ZIP: the repository represents a system composed of multiple installable skills.

For a complete deployment, install all three components for the same business/workspace.
