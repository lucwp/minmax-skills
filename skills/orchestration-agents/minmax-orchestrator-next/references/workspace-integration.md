# Workspace Integration

For true all-input routing, configure the workspace to apply `minmax-orchestrator-next` before substantive work while preserving specific domain skills as authorities.

Recommended workspace rule:

```md
For every user input, apply `minmax-orchestrator-next` as the lightweight routing control plane before substantive work. Keep simple work direct. Use a central manager: root owns intent, approvals, global plan, integration, and final claims; specialist workers are bounded. Delegate only when parallelism, context isolation, specialist capability, rework prevention, or risk reduction justify overhead. Prefer deterministic/authoritative verification and finite budgets. Never use recursive orchestration.

If the user explicitly asks to execute the current task "with a loop", "in Loop Mode", as an autonomous loop, or equivalent, activate MinMax Orchestrator NEXT Loop Mode. Before substantive execution, create the plan, compile a bounded loop using loop-engineering principles, preflight it, present the full plan/loop contract, and STOP. Execute no task cycle until the user explicitly approves that exact contract. A material replan invalidates approval and must be presented for fresh approval before execution resumes. Loop approval never waives domain-specific or high-consequence action approvals.
```

Runtime mappings, when available:
- manager -> bounded specialist agents/tools;
- worker packet -> structured/custom input;
- worker budget -> finite turns/timeouts;
- cancellation -> runtime abort/cancel;
- parallel ready nodes -> runtime concurrency;
- final synthesis -> root manager.

If runtime lacks a primitive, preserve the architecture conceptually and never claim unsupported controls executed.
