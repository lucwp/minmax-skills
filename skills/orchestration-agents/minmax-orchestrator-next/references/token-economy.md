# Token and Context Economy

Optimize utility of every token entering agent context. A cheap model can still create an expensive workflow through repeated large context or redundant workers.

Worker packet should contain only:
1. outcome;
2. scope/ownership;
3. direct prerequisites;
4. evidence or retrievable references;
5. constraints/domain rules;
6. required tools;
7. completion test;
8. concise return schema;
9. runtime budget.

Prefer stable file paths, document/record IDs, line/page ranges, URLs, and query terms over copied history.

Do not send full conversation history, whole DAG, unrelated sibling results/files/tool schemas, or planner rationale unless indispensable.

Workers return distilled state: result, evidence/change, completion-test status, blocker/residual risk, and an optional `decision_request`. Workers do not emit user-facing narration; root aggregates state.

Prefer verification in this order: deterministic test -> authoritative state -> cheap bounded semantic check -> strong independent critic only when expected failure cost warrants it.

## User-visible output economy

Progress updates are part of token economy, not an exception to it. For substantive execution, prefer 1-2 sentences (usually about 15-35 words) at material boundaries or after roughly 2-3 substantive operations without visible state when the runtime permits. Each update must add new evidence/state, a completed action, a changed next step, a blocker/recovery, a decision request, or terminal verification. Do not narrate every tool call, duplicate the previous status, replay the plan, or expose chain-of-thought. Trivial/direct work should stay quiet until its normal answer unless a real blocker/decision appears.
