# MinMax Proposal System

The MinMax Proposal System is now a **single installable skill** with two private internal workers.

```text
minmax-proposals                  # only public/installable skill
└── internal-skills/
    ├── minmax-proposal-inquiry   # configures reusable business context
    └── minmax-enterprise-proposal# generates, renders, and QA-checks proposals
```

## Public entrypoint

[`minmax-proposals`](./minmax-proposals/) is the only active skill to install or invoke. It owns routing, state, handoffs, and terminal output.

## Internal workers

- **minmax-proposal-inquiry** performs first-run onboarding and targeted updates to reusable proposal context: offers, positioning, pricing, commercial rules, proof, brand, voice, and proposal defaults.
- **minmax-enterprise-proposal** creates commercial theses, proposals, structured proposal data, standalone HTML, and QA outputs from the compiled reusable configuration plus current-deal facts.

The workers are intentionally private and do not contain public `SKILL.md` entrypoints.

## First run

1. Invoke `minmax-proposals`.
2. The orchestrator inspects configuration state.
3. If setup is missing or stale, it runs the internal Inquiry worker.
4. Inquiry harvests existing context, asks only material gaps, validates the profile, and compiles it into the internal Enterprise Proposal worker.
5. The orchestrator then routes deal-specific proposal work to Enterprise Proposal.

## Updating configuration

Reusable changes such as a new offer, pricing floor, logo, case study, positioning rule, discount policy, or proposal default route through Inquiry. Inquiry updates the internal Enterprise Proposal configuration before any subsequent proposal is generated.

Deal-specific facts such as client budget, stakeholders, timing, current pain, and opportunity constraints stay inside the proposal workflow and do not rewrite reusable business configuration.

## Persistence

In a writable workspace, Inquiry patches the internal Enterprise Proposal configuration in place and increments `configuration_revision`.

In an immutable installed environment, Inquiry rebuilds and returns one replacement package for the **entire `minmax-proposals` skill**. It never emits a standalone worker as the normal persistence mechanism.

## Legacy

The former three-skill architecture is preserved under:

```text
skills/legacy/business-revenue/
├── minmax-proposals/
├── minmax-proposal-inquiry/
└── minmax-enterprise-proposal/
```

Those directories are historical only and are not part of the active catalog.
