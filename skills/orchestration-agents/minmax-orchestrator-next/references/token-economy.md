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

Workers return distilled state: result, evidence/change, completion-test status, blocker/residual risk.

Prefer verification in this order: deterministic test -> authoritative state -> cheap bounded semantic check -> strong independent critic only when expected failure cost warrants it.
