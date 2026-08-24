# Token and Context Economy

## Core Rule

Optimize the utility of every token entering an agent context.

Treat context as a finite attention and cost budget. Prefer the smallest set of high-signal tokens that preserves task correctness.

## Cost Model

Track qualitatively:

`total = planner + repeated system/tool schemas + duplicated user/history context + worker execution + worker output + integration + verification + retries + recovery`

A cheap model can still produce an expensive workflow if it repeatedly ingests large context or spawns redundant workers.

## Minimal Sufficient Task Packet

A worker receives only:
1. outcome;
2. exact scope/ownership;
3. direct prerequisite outputs;
4. relevant evidence or retrievable references;
5. constraints / mandatory domain rules;
6. available tools needed for this node;
7. completion test;
8. concise return schema;
9. runtime budget.

Do not send:
- full conversation history unless indispensable;
- the entire DAG;
- sibling results that are not dependencies;
- unrelated files;
- unrelated tool schemas;
- verbose planner rationale.

## Just-in-Time Retrieval

Prefer passing stable identifiers that let the worker retrieve only what it needs:
- file paths;
- document IDs;
- line/page ranges;
- URLs;
- record IDs;
- query terms.

Preload content only when retrieval overhead would be worse or runtime access is unavailable.

## Tool Surface Economy

When runtime supports tool search/deferred loading:
- expose tool namespaces, not every tool globally;
- load only the relevant namespace for the node;
- keep overlapping tools out of the same surface where possible.

Tool outputs should prefer filtering, pagination, range selection, and truncation over giant raw payloads.

## Multi-Agent Cost Warning

Multi-agent workflows can multiply context transfer, model calls, integration work, and verification. Therefore:
- do not treat multi-agent as a quality default;
- require parallelism, context isolation, specialist value, rework prevention, or risk reduction;
- scale agent count and reasoning effort to task complexity.

## Worker Return Economy

Workers return distilled state, not transcripts:
- result;
- evidence/change;
- completion test;
- blocker/residual risk.

The root should not receive the worker's chronological tool log unless debugging requires it.

## Verification Economy

Prefer:
1. deterministic test;
2. authoritative state read;
3. cheap bounded model check;
4. independent strong critic only when expected failure cost warrants it.

## Caching and Reuse

When runtime supports prompt/tool caching or shared immutable context:
- reuse stable system/domain context;
- avoid retransmitting unchanged large prefixes;
- still keep worker task packets narrow because cached tokens can remain an attention burden.

## Economic Eval Metrics

Track at least:
- task success / acceptance;
- total input tokens;
- total output/reasoning tokens if available;
- agent count;
- tool calls;
- duplicated context estimate;
- wall-clock time;
- retries/replans;
- model tier usage;
- human rework required.

Tune local defaults against these metrics.
