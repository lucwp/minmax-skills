# Workspace Integration

Skill matching alone may not guarantee that a general orchestrator runs before every specific skill. For true all-input behavior, add a workspace rule equivalent to:

```md
For every user input, apply `low-cost-intelligence-orchestrator` as the routing control plane before substantive work. Keep trivial work direct. Use a central manager pattern: the root owns the user conversation, global plan, approvals, integration, and final claim; specialist agents are bounded workers/tools, not peer orchestrators. For complex delegated tasks, use Plan -> Work -> Solve: create one compact plan, compile only meaningful dependencies into a minimal DAG, delegate only when the benefit exceeds context/worker/integration overhead, execute independent ready nodes in parallel, and synthesize centrally. Send each worker the smallest sufficient task packet and retrieve extra context just in time. Default normal workers to Luna high; reserve Luna xhigh for genuinely complex planning or hard bounded reasoning; allow Luna max only as an exceptional narrow, externally bounded depth escalation; use Terra xhigh for demonstrated capability/coordination gaps and Sol high/xhigh for narrow high-consequence judgment. Never use Terra max or Sol max. Prefer deterministic/authoritative verification, use model verifiers selectively, replan only on explicit stall/failure triggers, and enforce finite turn/time/cancellation budgets with no recursive orchestration. Treat specific numeric fan-out/timeout/retry values as tunable workspace defaults, not universal truths. Specific domain skills remain authoritative.
```

## Runtime Mapping

When equivalent runtime controls exist:
- manager pattern -> bounded specialist agents/tools;
- worker input -> structured `parameters` / custom input builder;
- nested worker limit -> `max_turns`;
- cancellation -> runtime abort/cancel control;
- tool/model hang -> finite timeout;
- large tool inventory -> deferred tool loading / tool search where available;
- parallel independent nodes -> runtime concurrency primitives;
- final synthesis -> manager/root.

If the runtime lacks these primitives, preserve the architecture conceptually and never claim unsupported controls were executed.
