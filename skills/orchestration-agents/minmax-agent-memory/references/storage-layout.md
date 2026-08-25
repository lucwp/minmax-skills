# Provider-neutral Markdown storage model

Use the same shallow logical Markdown structure on any compatible file/cloud-storage provider. Markdown is the canonical serialization. Physical storage may be a real `.md` file or a provider-native text document when the native representation has materially better edit/version semantics.

```text
MinMax Agent Memory/
├── Core/
│   └── MEMORY.md
├── User/
│   ├── Preferences.md
│   ├── Decisions.md
│   └── Context.md
├── Projects/
│   └── <Project>/
│       └── Memory.md
├── Entities/
│   ├── People.md
│   └── Organizations.md
└── Evidence/
    └── <selected high-value evidence>.md
```

## Logical serialization vs physical representation

The names above are logical Markdown paths. An adapter may map them to provider-native text documents when that is the safer/faster representation. Example: a native Google Doc titled `MEMORY` may implement logical `Core/MEMORY.md`; a filesystem or object-storage connector should normally use the literal `MEMORY.md`.

Selection rules:

- use physical `.md` when the connector can read/update text efficiently and provides adequate concurrency protection;
- use native text documents when they provide materially better patching or version/CAS behavior than raw-file replacement;
- if capability is equivalent, prefer `.md` for portability;
- never keep `.md` and native mirrors as co-equal canonical copies;
- do not convert an existing healthy representation without explicit user intent or measured benefit.

Memory bodies must stay Markdown-compatible even in native documents. Avoid rich-layout-only semantics that would be lost on export. Prefer headings, bullets, compact metadata lines, and plain links.

## Root naming and migration

Canonical root: `MinMax Agent Memory`.

Legacy alias: `AI Memory`. If a legacy root already exists, reuse it as the same store and rename it to the canonical name when safe. Never initialize both names without an explicit migration decision.

If more than one active memory root exists on the same provider or across connected providers, treat that as split-brain. Do not automatically merge histories or alternate writes. A root explicitly marked migrated/archived/inactive is not an active competitor.

## Store marker

At creation or the next safe write, keep a compact identity block near the top of logical `Core/MEMORY.md`:

```text
Memory system: minmax-agent-memory
Schema: 1
Store ID: <stable random identifier>
Status: active
```

Use it to distinguish the real store from unrelated same-named folders. When a provider exposes ownership/sharing metadata, combine marker/layout validation with provider trust signals; do not adopt an arbitrary shared/public root solely by name.

## Capability mapping

The logical layout assumes folder/file listing and content reads for recall. Writes additionally require file/folder creation and updates. Search improves deep recall but is not mandatory. Delete, revision/version checks, and atomic rename/move are optional safety capabilities. Use native docs, plain text, Markdown, or equivalent provider formats as long as the content stays readable and editable. A read-only active store may serve recall but must not cause automatic creation of a second writable truth store.

## Core/MEMORY.md

Keep this as a small navigation map, not a knowledge dump. Include only:

- active persistent scopes/projects;
- a short descriptor and optional high-signal aliases for each active project/entity when that improves routing;
- where durable user memory lives;
- where entity memory lives;
- short notes on which document owns which kind of context.

Recommended compact registry:

```markdown
## Active scopes
- aTip CRM — internal CRM; aliases: accounts, account management, pipeline
- GoDo — local experience discovery product; aliases: experiences, organizers
- MinMax Skills — agent-skill ecosystem; aliases: skills repo, MinMax
```

Do not copy project facts into this registry. Its purpose is routing. Do not update logical `Core/MEMORY.md` for every new fact; update it only when navigation changes, a recurring scope is created/retired, or aliases materially change.

## User

- `Preferences.md`: durable user preferences and standing choices.
- `Decisions.md`: cross-project decisions that materially affect future work.
- `Context.md`: durable user context that is useful across domains but is neither a preference nor a decision.

Keep sensitive or unnecessary personal information out of memory.

## Projects

Create one folder only for a project that is likely to recur. Default to one logical `Memory.md` document per project. Split into topic documents only after the project memory becomes materially hard to retrieve or edit.

Recommended project memory sections:

```markdown
# <Project>

## Retrieval aliases
<up to 10 high-signal synonyms, abbreviations, user terms, or prior names>

## Current state
## Active decisions
## Constraints
## Open loops
## Superseded / historical
## Evidence pointers
```

Aliases improve lexical retrieval but are not canonical facts. Keep them bounded and remove stale ones.

## Entities

Start with aggregate logical `People.md` and `Organizations.md` documents. Split into per-entity documents only when density or ambiguity makes the aggregate file inefficient. Use a bounded `Retrieval aliases` section for alternate names, company abbreviations, or prior names when materially useful.

## Evidence

Evidence is selective. Prefer descriptive titles containing date, scope, and topic, for example:

`2026-08-24 - aTip CRM - account-management rationale`

Do not make Evidence the normal recall path.
