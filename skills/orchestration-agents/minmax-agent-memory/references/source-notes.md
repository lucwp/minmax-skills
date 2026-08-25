# Architectural sources and caveats

Use primary/official sources first. These notes explain which ideas are borrowed and which claims must not be overstated.

## Agent Skills open standard

Authoritative specification:
https://agentskills.io/specification

Relevant points:

- The portable core is a directory containing `SKILL.md` with required `name` and `description` frontmatter.
- `scripts/`, `references/`, `assets/`, and additional files/directories are optional.
- Agents should load metadata first, `SKILL.md` on activation, and supporting resources only as needed.
- Runtime/tool support can differ; vendor-specific metadata must not become a core prerequisite.

OpenAI separately documents that its Skills follow the Agent Skills open standard and are supported across ChatGPT, Codex, and API surfaces. Treat that as one implementation of the open format, not the definition of the format itself.

## OpenAI Skills

Source: OpenAI Help Center, “Skills in ChatGPT”
https://help.openai.com/en/articles/20001066-skills-in-chatgpt

Relevant points:

- Skills are reusable workflows with instructions, examples, and optional code.
- After installation, ChatGPT can automatically use one or more Skills when helpful.
- This supports making memory an independent Skill rather than coupling it to the orchestrator, while the open standard keeps the core portable across compatible runtimes.
- OpenAI does not publish a trigger-recall SLA; do not claim automatic invocation is guaranteed.

## OpenAI skill-authoring guidance

Source: bundled OpenAI `skill-creator` guidance in the current runtime.

Relevant points:

- Skill metadata is used for discovery; full instructions load only after selection.
- Keep `SKILL.md` compact and use progressive loading for references.
- Supporting resources should exist only when they materially improve reliability.

This is why the memory Skill keeps routing instructions compact and moves retrieval/write/evaluation detail into references.

## OpenAI Agents SDK — Agent memory

Source:
https://openai.github.io/openai-agents-python/sandbox/memory/

Relevant points:

- Durable Memory is separate from conversational Session history.
- The Sandbox Memory feature is beta; treat it as design guidance, not a stable universal runtime contract.
- Memory generation uses two phases: conversation extraction followed by consolidation.
- Default memory uses `memory_summary.md`, `MEMORY.md`, raw memories, and rollout summaries with progressive disclosure.
- Internal agents can be configured read-only (`generate=None`).

This Skill adopts the conceptual separation, selective consolidation, progressive disclosure, and read-only-worker principle without pretending any cloud-drive connector is the SDK Sandbox Memory implementation.

## OpenAI Agents SDK — Sessions and compaction

Sources:
https://openai.github.io/openai-agents-python/ref/memory/session/
https://openai.github.io/openai-agents-python/ref/memory/openai_responses_compaction_session/

Relevant points:

- Sessions maintain conversational history.
- Compaction reduces stored conversation history when it grows.
- Compaction and durable memory solve different problems.

Therefore this Skill does not archive every session turn as long-term memory.

## MemPalace

Official repository:
https://github.com/MemPalace/mempalace

Official concepts:
https://mempalaceofficial.com/concepts/the-palace
https://mempalaceofficial.com/concepts/memory-stack

Useful ideas adopted:

- keep original evidence available instead of relying exclusively on lossy summaries;
- structure memory by person/project and topic;
- progressive layers from small startup context to deeper retrieval;
- isolate retrieval scope before searching a flat corpus.

Ideas deliberately not copied into V1:

- mandatory Wings/Rooms/Halls/Drawers physical ontology;
- ChromaDB/vector backend;
- temporal SQLite knowledge graph;
- graph traversal/tunnels;
- always-verbatim conversation archival.

### Benchmark caveat

The MemPalace README currently reports 96.6% R@5 on LongMemEval for raw semantic search. That is a retrieval-recall metric, not end-to-end QA accuracy. Public GitHub issue #875 documents methodology/attribution concerns and notes that the raw benchmark path relies on ChromaDB default embeddings without the palace-structure path. Treat the number as a reported retrieval baseline, not evidence that a provider-neutral cloud-drive implementation will achieve similar results.

Issue:
https://github.com/MemPalace/mempalace/issues/875

Never compare MemPalace R@5 directly with another system's QA accuracy.

## Cloud-drive retrieval boundary

Observed V1 behavior on Google Drive: its connector search is useful for titles, metadata, exact terms, and queries with meaningful lexical overlap, but it can miss distant meaning-preserving paraphrases. Treat this as one provider observation, not a universal property of every storage connector. Do not describe connector search as equivalent to a vector/embedding semantic index.

V1 mitigation:

- use structured project/entity scopes;
- keep bounded retrieval aliases for recurring scopes;
- when a semantic query misses, fall back to the likely scope/project/entity name and inspect that memory document semantically;
- add a semantic backend only if measured full-policy retrieval remains below the accepted threshold.

Whole-connector search is not a memory index. Prefer `MinMax Agent Memory`-scoped routing because unrelated Drive content can outrank memory documents for generic lexical queries.


## Markdown-first serialization note

MinMax Agent Memory treats Markdown as its canonical logical serialization because it is portable, human-readable, diff-friendly, and easy for models to parse. This does not imply that a physical `.md` file is always the fastest or safest representation on every connector. Provider-native text documents are permitted when they offer better incremental editing or version/concurrency controls, provided their content remains Markdown-compatible and maps to one logical Markdown document.
