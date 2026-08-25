# Write and consolidation policy

## Promotion test

Promote an observation to durable memory only when all three are reasonably true:

1. **Future utility** — it can materially improve a later task.
2. **Durability** — it is expected to remain relevant beyond the current turn/session.
3. **Evidence quality** — it is explicit or strongly grounded, not merely guessed.

High-risk or sensitive information requires explicit user intent to remember it, a clear future-utility case, and data minimization. Never infer sensitive traits into durable memory.

Explicit correction of existing durable memory is a separate **REPAIR** path: when the target memory is unambiguous, fix known stale state even if the replacement fact would not independently pass the normal promotion threshold.

## Provenance labels

Use compact labels when they improve reliability:

- `explicit-user` — directly stated by the user;
- `approved-artifact` — established in a user-approved deliverable;
- `observed-state` — confirmed by a connected tool/system;
- `agent-inference` — inferred by the agent; never silently promote as fact.

## Markdown serialization

Write durable memory in Markdown-compatible text regardless of physical provider representation. Prefer stable headings and compact entries; avoid provider-only rich formatting as semantic state. A provider-native text document may be used as the physical container when it gives safer patch/version behavior, but its body must remain portable Markdown-compatible content.

Do not dual-write a `.md` file and a native document as mirrors. Format conversion is a migration of representation and requires verification before cutover.

## Compact durable entry

Prefer readable prose over database ceremony. When metadata matters, use a compact pattern:

```markdown
### Primary model preference
Current: Sol; Sol Max is generally unnecessary.
Status: active
Updated: 2026-08-23
Source: explicit-user
```

## Retrieval aliases

For recurring project/entity documents, add a compact alias section only when it materially improves lexical recall:

```markdown
## Retrieval aliases
account management; customer accounts; AM; success plan
```

Use at most 10 high-signal aliases; fewer is fine. Prefer terms the user actually uses, abbreviations, prior names, and materially different synonyms. Do not create keyword dumps or treat aliases as facts.

## Supersession pattern

When a single-valued durable choice changes:

```markdown
### Primary model preference
Current: Sol.
Updated: 2026-08-23
Source: explicit-user

Historical:
- Luna Max — superseded 2026-08-23.
```

Do not keep both as active preferences.

## Scoped differences

Do not supersede when two values can coexist under different scopes. Record scope explicitly instead.

Example:

```markdown
- Coding model: X
- High-consequence review model: Y
```

## Open loops

Persist only loops likely to be resumed. Remove or mark completed loops when the project memory is next updated.

## Evidence promotion

Store high-value evidence separately when exact source context matters. In the durable memory document, point to it with a short human-readable reference rather than duplicating the full source.

## Memory repair

Treat explicit corrections, retractions, or supersessions of stored durable memory as high-priority repair events.

When current user input contradicts stale memory and the target scope is clear:

1. follow the current user input immediately;
2. identify the owning memory document;
3. repair the stale current value without requiring the normal promotion test;
4. preserve the previous value as historical only when future reconstruction has value;
5. update source/date when useful;
6. remove or update aliases that would keep retrieving the stale terminology as current.

If the user correction is explicitly temporary, scoped only to the current task, or ambiguous about what it replaces, do not rewrite durable memory silently.

## Forgetting

Separate retention cleanup from an explicit user request to forget.

For ordinary cleanup, archive or delete information that is incorrect, duplicated, no longer relevant, or retained only because it once appeared.

For an explicit **FORGET** request:

- remove the value from active memory rather than superseding it;
- remove aliases, summaries, pointers, and open loops that would reintroduce it;
- do not copy the forgotten content into Historical or a content-bearing tombstone;
- delete dedicated evidence when the request covers it and the connector supports delete; otherwise remove it from retrieval and state physical-erasure limits if material;
- verify that normal recall no longer returns it.

Provider revisions/backups may retain historical bytes outside the active memory surface. Never promise physical erasure beyond connector capabilities.

## Concurrency and idempotency

Never blind-overwrite from a stale snapshot. Prefer optimistic version checks. Without version checks, perform a fresh pre-write read for full-document replacements; if content changed, rebase once or abort on ambiguity. Make retryable writes idempotent so an uncertain retry cannot duplicate facts, aliases, evidence pointers, or topology entries.

## Scope retirement

When a recurring project is retired, mark the project memory inactive/archived and remove it from the active registry. Preserve it for explicit historical recall unless the user asks to forget/delete it. Archived project memory must not rank as active current context.
