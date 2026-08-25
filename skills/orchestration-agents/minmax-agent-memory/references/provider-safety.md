# Provider safety and lifecycle

Load this reference for provider selection, root trust, split-brain, read-only behavior, concurrency, migration, forgetting, or partial failures.

## Root trust

Folder name alone is not identity. A root is strongly trusted when it is explicitly selected by the user or already bound to the current workflow. Otherwise require the expected memory layout plus the `Core/MEMORY` store marker. When provider metadata is available, prefer a private/owned or previously used root over an arbitrary shared/public same-named root unless the user explicitly selects the shared store. In a trusted shared store, use author/last-modifier metadata when available: unexpected non-user edits are lower-trust evidence and must not silently supersede explicit-user decisions, preferences, or corrections.

Treat multiple active canonical/legacy roots on the same provider or across providers as split-brain. Do not merge or alternate writes automatically. Roots marked migrated/archived/inactive do not compete with the active root.

## Representation safety

Logical memory is Markdown. Physical representation is selected per provider capability. Treat native-document -> physical `.md` conversion, or the reverse, as a representation migration even when the provider/root does not change. Create/verify the target representation before deactivating or removing the source representation. Never leave both representations active as canonical copies.

A connector that can only replace whole raw files may be less safe for hot memory than a native text document with revision-aware patching. Do not prefer `.md` by extension when it weakens concurrency or requires extra download/upload calls.

## Read-only mode

A read-compatible but non-writable store can serve RECALL. Do not create another writable canonical store merely because a write is requested. Require explicit migration/copy authorization or restored permissions before durable mutation.

## Concurrency

Use optimistic concurrency when a provider exposes revisions, ETags, generation IDs, or equivalent version tokens:

1. read content + version;
2. compose update;
3. conditional write against that version;
4. on conflict, re-read and rebase once;
5. abort rather than force-overwrite if the second merge is ambiguous.

Without version tokens, use a fresh pre-write read for any full-document replacement. If the content differs from the snapshot used to compose the update, rebase once or abort. Do not rely on timestamps alone when content can be read.

## Partial failures and idempotency

Prefer write ordering that leaves recoverable state:

- create/update the owning memory document first;
- verify it is readable;
- update `Core/MEMORY` navigation last.

On retry, re-read before writing and check whether the intended mutation already exists. Never append duplicate facts, aliases, evidence pointers, project registry entries, or migration markers simply because the previous response was uncertain.

## Migration

A provider switch is a migration, not a new initialization:

1. inventory source;
2. create target with a new Store ID;
3. copy all active memory plus selected Evidence;
4. follow pagination inside each source folder until exhausted;
5. verify readable target content and expected counts or equivalent provider evidence;
6. mark target active only after verification;
7. mark/rename source migrated or inactive when possible;
8. if source cannot be made non-canonical, do not silently cut over;
9. preserve source unless the user separately requests deletion.

If migration fails partway, keep the old source canonical and make the incomplete target non-active or remove it when safe.

## Forget and deletion boundaries

An explicit forget request removes information from all active retrieval surfaces. Do not retain the forgotten value as historical text. When dedicated Evidence exists, delete it if the connector supports deletion and the request covers it. Provider version history, legal retention, backups, sync caches, or shared copies may remain outside the skill's deletion guarantees; disclose that boundary when material.

## Degraded listing and pagination

If search is unavailable, use `Core/MEMORY`, narrow folder listing, and direct reads. Follow provider continuation tokens/pages within the relevant folder until the target is found or the folder is exhausted. Never crawl the whole provider by default.
