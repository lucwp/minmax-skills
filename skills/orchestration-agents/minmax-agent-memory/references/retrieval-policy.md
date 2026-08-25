# Retrieval policy

## Progressive disclosure

Use the narrowest sufficient path.

### L0 — current conversation

First use information already present in the current conversation. Do not call persistent storage for facts already available and trustworthy in the active context.

### L1 — targeted durable memory

If the project/entity/scope is obvious, read its specific memory document directly.

Examples:

- current project design -> `Projects/<Project>/Memory`
- standing preference -> `User/Preferences`
- cross-project choice -> `User/Decisions`
- known organization/person relationship -> `Entities/*`

For recurring project/entity memories, use the compact `Retrieval aliases` section as additional lexical anchors when the user's wording differs from the canonical name.

### L2 — memory map

If scope is unclear, read logical `Core/MEMORY.md` to identify the correct durable memory surface. The map should include a compact active-scope registry with project/entity names plus short descriptors or aliases when useful.

### L3 — storage search

Use storage search when:

- the expected document is unknown;
- a paraphrase may not match a known title;
- multiple projects/entities may contain the answer;
- a targeted document does not contain the needed context.

Search with the strongest available anchors: project, entity, decision keyword, approximate date, distinctive terminology, aliases, abbreviations, or prior names. Prefer several compact searches over dumping unrelated content.

Keep searches scoped to `MinMax Agent Memory`, a known memory subfolder, or a known project/entity folder whenever the storage backend permits. Avoid unconstrained whole-storage search as a normal memory path: unrelated documents can dominate results and create unnecessary exposure and context noise. If scoped or recursive search is unavailable, use logical `Core/MEMORY.md` plus folder listing and direct reads to narrow candidate discovery before any broad search. If listing is paginated, continue within the narrow folder until the target is found or that folder is exhausted; do not page the whole provider.

Do not assume storage search is semantic retrieval. It can miss meaning-preserving paraphrases with weak lexical overlap.

### Semantic-miss fallback

If the query is plausibly about known durable context but storage search returns no useful result:

1. Do not conclude that no memory exists.
2. Identify the most likely scope from the current conversation, logical `Core/MEMORY.md`, known project/entity names, aliases, or distinctive context.
3. Search by the scope/project/entity name rather than the paraphrased concept.
4. Open that scope's `Memory` document.
5. Inspect the document semantically with the model.
6. Only report a memory miss after this scope fallback fails or no likely scope can be identified.

This fallback is the default V1 compensation for the absence of vector search.

### L4 — evidence

Open Evidence only when exact history, rationale, wording, or contradiction resolution is required.

## Retrieval aliases

Use aliases to improve lexical recall without creating a semantic backend.

For a recurring project/entity memory, keep a small section such as:

```markdown
## Retrieval aliases
account management; customer accounts; account plan; AM; success plan
```

Rules:

- prefer 3-10 high-signal aliases;
- include user wording, abbreviations, prior names, and materially different synonyms;
- do not add generic words that would create noisy matches;
- remove stale aliases when terminology changes;
- do not duplicate the full memory content as keywords.

Aliases are retrieval aids, not canonical facts.

## Ranking rule

Rank retrieved candidates qualitatively using:

1. scope/entity match;
2. active/current status;
3. explicitness and provenance;
4. specificity to the query;
5. recency where the fact is time-sensitive;
6. textual/semantic similarity.

Penalize superseded and inferred memories. Prefer canonical current memory over Evidence when both match the same query.

## Query ambiguity

Do not infer a historical fact from a vague match. If two current candidates remain plausible and the answer materially changes, surface the ambiguity or gather more evidence.

## Context budget

Normal recall should inject only the small relevant passage/document. Avoid copying whole unrelated documents into the working context.

## Vector-search boundary

This V1 does not include a vector database. Storage retrieval plus structured scopes, bounded aliases, and scope fallback are the available retrieval layer. If measured Recall@5 remains below the accepted threshold after aliasing and scope fallback are evaluated, add a semantic index later as an optional rebuildable cache; do not claim it exists before implementation.


## Serialization neutrality

Retrieval quality is governed by scope resolution, aliases, provider search/listing, and semantic inspection after a read. Treat `.md` as the canonical serialization but do not assume the `.md` extension itself improves semantic retrieval. When a provider-native document implements a logical Markdown memory file, retrieve it exactly as the corresponding `.md` logical path.
