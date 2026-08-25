# MinMax Skill Package Manager — Architecture Design

**Date:** 2026-08-25  
**Status:** Approved architecture, pre-implementation  
**Repository:** `lucwp/minmax-skills`

## 1. Purpose

MinMax is a package manager for AI skills with a conversational control plane and a deterministic package engine. It is intended to manage skills across heterogeneous sources and heterogeneous agent clients with the reliability expectations of a Linux package manager: explicit package identity, immutable artifacts, review-before-apply updates, pinning, rollback, reproducible installs, transaction safety, and recovery from partial failure.

The product is not a Git updater. GitHub is one source among several. SkillsMP is a discovery/source adapter, and generic Git, GitLab, direct URLs, downloadable archives, and future providers are first-class architectural concerns.

The primary UX is conversational through `@minmax`, while the underlying engine remains deterministic and independently callable.

## 2. Design principles

1. **Deterministic core, agentic control plane.** The model may interpret intent, summarize changes, explain risk, and recommend actions. It must not be the authority for hashes, installed versions, transaction state, identity, rollback success, or whether files differ.
2. **Preview and apply are separate operations.** Every mutation is represented by an immutable transaction plan that must be approved before execution under the default policy.
3. **Content is addressed by hash.** Installed artifacts, snapshots, overlays, and transaction plans refer to immutable content identities.
4. **Package state is not agent memory.** Persistent state belongs in the package registry, lockfile, artifact store, and transaction journal. Agent memory may retain user preferences only.
5. **Local-first, cloud-synchronized.** Devices operate from a fast local canonical store; cloud storage carries reproducible state and artifacts rather than acting as a directly executed shared folder.
6. **Source provenance is separate from behavioral risk.** A verified GitHub source can still contain high-risk behavior.
7. **Existing skills are adopted, not forcibly reinstalled.** Setup scans and classifies the current environment without destructive normalization.
8. **Bundled subskills stay within their package.** External skill dependencies are warned about rather than solved transitively in the MVP.
9. **Branch tracking is an explicit override.** Default tracking prefers stable releases and falls back to the source repository's default branch when releases do not exist.
10. **No silent source switching.** Forks, repository identity changes, and skill moves require explicit or verifiable migration evidence.

## 3. Scope

### 3.1 MVP 1.0

The MVP includes:

- `@minmax setup`
- import/adoption of existing skills
- package registry
- portable lockfile
- content-addressable artifact store
- transaction journal
- GitHub source adapter
- SkillsMP source/discovery adapter
- generic Git adapter
- direct URL/archive adapter
- package identity and alias resolution
- monorepo support
- bundled subskills
- stable release to default-branch fallback
- explicit branch override
- `install`, `check`, `update`, `status`, `sync`, `pin`, `unpin`, `rollback`
- selective updates
- deterministic diff
- AI semantic changelog layered on deterministic facts
- local overlays and overlay reconciliation
- immutable transaction plans
- atomic activation and rollback
- source trust classification
- capability inspection and risk rules
- local canonical store
- Google Drive storage adapter
- generic filesystem storage adapter
- initial target adapters for supported skill directories
- crash recovery
- drift detection

### 3.2 Deferred to 1.x or later

Not required for the first release:

- public MinMax registry
- MinMax signing authority
- Sigstore publishing flow
- full dependency solver
- internet-wide automatic discovery
- enterprise policy engine
- RBAC / organization management
- telemetry
- marketplace UI
- broad auto-update mode
- advanced automatic merge resolution
- GUI
- permanent daemon
- background polling
- OneDrive/Dropbox-specific adapters unless implementation cost is negligible

## 4. High-level architecture

```text
                    @minmax
                       |
                Agent Control Plane
                       |
               +-------+--------+
               |                |
        Semantic Layer     Package Engine
               |                |
   intent / summaries /      deterministic
   explanation / risk        resolve / hash
   recommendation            diff / stage
                             install / rollback
                             sync / verify
                                |
              +-----------------+------------------+
              |                 |                  |
        Source Adapters    Storage Adapters   Target Adapters
              |                 |                  |
       GitHub / SkillsMP    Local / GDrive     Codex / Claude
       GitLab / Generic    Filesystem / ...   Cursor / ...
       Git / URL / Archive
```

The control plane creates or requests deterministic operations. The engine emits structured facts and transaction plans. The control plane converts those facts into human-readable explanations but cannot mutate their meaning.

## 5. Core components

### 5.1 Source Resolver

Accepts heterogeneous references and normalizes them into a common source descriptor.

Supported classes:

- GitHub repository or repository path
- SkillsMP listing
- GitLab repository or path
- generic Git URL
- direct HTTP(S) archive/download
- generic filesystem source where explicitly supported

Normalized descriptor example:

```yaml
source:
  provider: github
  repository_id: 123456789
  canonical_url: https://github.com/example/repo
  package_path: skills/foo
  tracking:
    mode: stable
    ref: null
```

The rest of the engine consumes the normalized descriptor, not provider-specific URL syntax.

### 5.2 Package Inspector

Inspects candidate package contents without executing them. It identifies:

- `SKILL.md` / `skill.md`
- package root and entrypoint
- bundled subskills
- scripts and executable files
- references and assets
- external skill requirements
- external connectors/tools mentioned
- filesystem/network/shell behavior indicators
- package-structure anomalies
- files escaping expected package boundaries

It computes package and file hashes and emits structured findings.

### 5.3 Version Resolver

Default policy:

```text
stable release/tag
    -> if absent
repository default branch HEAD
    -> if non-Git
content hash
```

A user may explicitly track a branch. Branches are update channels, not installed versions. The installed version is always pinned to an immutable commit/hash in the lockfile.

### 5.4 Package Registry

The operational registry records logical package state and aliases. SQLite is preferred for local operational state because it supports safe querying, transactions, and migration better than a single mutable JSON file.

Representative fields:

- internal package ID
- display name
- canonical package identity
- canonical source identity
- source aliases
- tracking policy
- installed artifact hash
- installed release/tag/commit when available
- overlay hash
- configured targets
- pin state
- trust/provenance metadata
- external requirements
- last successful transaction

### 5.5 Lockfile

The lockfile is portable, deterministic, human-inspectable, and sufficient to reconstruct the package set when paired with the artifact store or original sources.

It records only stable reconstruction state, including:

- package identity
- source identity
- canonical/resolved source
- release/tag where applicable
- exact commit where applicable
- content hash
- overlay hash
- tracking configuration
- target configuration necessary for reproducibility

Transient cache state, logs, or transaction-internal fields do not belong in the lockfile.

### 5.6 Artifact Store

The artifact store is content-addressable using SHA-256 (or a future stronger/default algorithm through a versioned abstraction).

```text
objects/
  sha256/
    ab/
      abcd.../
```

The same object is never duplicated because it is referenced by digest. Installed versions, rollback candidates, snapshots, and cloud synchronization all refer to these immutable objects.

### 5.7 Overlay Manager

Local customization is modeled as an overlay over an immutable upstream base:

```text
base package + user overlay = effective package
```

The base artifact is never modified. During update, the system reconciles:

- old base
- new base
- local overlay

If the overlay applies cleanly, the candidate can proceed to review. If it conflicts, the update is blocked from activation and the package enters `CONFLICT` until resolution.

### 5.8 Transaction Manager

All package mutation occurs through transactions.

Canonical update pipeline:

```text
resolve
-> download/fetch immutable candidate
-> verify source identity
-> hash
-> inspect
-> deterministic diff
-> semantic analysis
-> apply overlay in staging
-> validate
-> create immutable transaction plan
-> user approval
-> atomic activate
-> verify targets
-> commit registry/lock state
-> sync cloud state
```

The apply step never downloads `latest` again. It activates the exact artifact hash reviewed in the plan. If upstream changes between preview and apply, the previous plan becomes invalid.

### 5.9 Sync Engine

Sync has two distinct domains:

1. **Package-state sync:** registry reconstruction data, lockfiles, overlays, artifact objects, snapshots, and device metadata.
2. **Target sync:** ensures configured agent clients expose the effective package versions from the canonical store.

The engine must not conflate cloud state with target materialization.

## 6. Storage model

### 6.1 Local canonical store

Conceptual layout:

```text
~/.minmax/
├── config.toml
├── minmax.lock
├── registry.db
├── journal/
├── objects/
├── overlays/
├── snapshots/
├── staging/
├── cache/
└── devices/
```

### 6.2 Cloud storage

Cloud is a synchronized reproducibility layer, not the directly executed filesystem.

MVP adapters:

- Google Drive
- generic filesystem path

Cloud carries:

- lockfiles/manifests
- overlays
- immutable artifact objects needed for restore/rollback
- snapshots
- device metadata
- revision metadata

### 6.3 Device synchronization

Each device has a local store and a device identity. Cloud state uses revision ancestry rather than last-write-wins timestamps.

If two devices independently modify the same overlay from the same parent revision, the state is a real conflict. The system does not select the newest file by clock time.

## 7. Target model

Target adapters materialize canonical packages into environments such as Codex, Claude Code, Cursor, OpenCode, or a generic skill directory.

An update modifies one canonical package and then reconciles all configured targets. Target-specific layout adaptation must not alter the logical package identity or installed artifact hash.

Drift is detected by comparing the expected materialized state with the actual target state.

On drift, the user may:

1. restore the canonical version;
2. adopt the local modification as an overlay;
3. temporarily ignore that target.

The system never silently overwrites drifted local changes.

## 8. Package identity

Four identities are distinct:

1. **Display name:** human-facing and mutable.
2. **Package identity:** logical package being managed.
3. **Source identity:** authoritative upstream source and package path.
4. **Artifact identity:** immutable content hash.

For Git-based sources without an explicit package ID, derived package identity is based on stable repository identity plus normalized package path, not repository name alone.

```text
<provider>/<stable-repository-id>/<normalized-package-path>
```

Repository renames/transfers that preserve provider repository identity can update aliases without creating a duplicate package.

### 8.1 Aliases

Multiple discovery references may map to one package identity:

- SkillsMP listing
- GitHub tree URL
- generic Git URL
- canonical repository URL plus path

The registry stores aliases to prevent duplicate installation.

### 8.2 SkillsMP

SkillsMP is treated primarily as a discovery/source adapter. When a SkillsMP listing resolves to a canonical Git source, the Git source identity becomes the canonical package source and the SkillsMP reference remains an alias/discovery reference.

If SkillsMP or a future provider hosts an independent immutable artifact, that provider may become the canonical source for that artifact.

### 8.3 Forks

Forks are separate source identities even if they share history. The system may record the fork relationship but never silently switches upstream.

Source switching is explicit, e.g. `switch-source` in a future or advanced command surface.

### 8.4 Package IDs declared by publishers

An optional manifest may define a stable package ID (for example reverse-DNS or UUID). Explicit IDs may become preferred if ecosystem adoption grows, but are not required in the MVP.

## 9. Monorepos, bundles, and subskills

A repository may contain many independently installable skills. A package may also contain bundled internal subskills.

These are distinct concepts.

### Monorepo

Each installable package root receives its own package identity.

### Bundle

Bundled subskills/components belong to the parent package lifecycle:

- installed together
- updated together
- rolled back together
- share parent package version/artifact transaction
- are not external dependencies

An optional `minmax.toml` may explicitly identify entrypoints, bundled paths, declared package ID, and external skill requirements.

The manifest is optional so existing skill packages containing only `SKILL.md`, references, and scripts remain compatible.

## 10. External dependencies

The MVP does not implement a full dependency solver.

External skill requirements are detected or declared and surfaced in the install/update plan. The package manager warns when a required external skill is absent but does not silently install it transitively.

Bundled subskills are not treated as external dependencies.

Runtime/tool requirements may also be surfaced as warnings or requirements but are not automatically solved unless a specific target adapter already provides a safe deterministic mechanism.

## 11. User experience and commands

Primary conversational verbs:

```text
@minmax setup
@minmax install <source>
@minmax check
@minmax update
@minmax update <skill>
@minmax status
@minmax sync
@minmax pin <skill>
@minmax unpin <skill>
@minmax rollback <skill>
```

Natural-language variants are supported by the control plane and compiled into explicit deterministic operations.

### 11.1 `@minmax setup`

Setup is environment adoption.

Flow:

```text
detect environment/targets
-> detect existing MinMax state
-> optionally connect personal cloud storage
-> scan installed skills
-> identify exact/modified/unknown origins
-> calculate hashes
-> convert local modifications to overlays where origin is known
-> create proposed registry/lock state
-> show adoption plan
-> user approval
-> activate management state
```

Unknown origins are registered as local packages and remain usable but are not remotely updateable until a source is explicitly linked.

### 11.2 `install`

Flow:

```text
resolve source
-> inspect
-> determine package boundaries
-> identify version
-> calculate hashes
-> provenance/security inspection
-> detect existing package/alias
-> detect external requirements
-> build plan
-> approval
-> transactional install
-> target sync
-> cloud sync
```

### 11.3 `check`

Equivalent in spirit to `apt update`: refreshes package metadata and discovers candidate updates without mutating installed packages.

Semantic deep analysis should be lazy to keep `check` efficient. Deterministic update metadata is fetched first; deeper AI analysis is generated when a candidate needs review or when explicitly requested.

### 11.4 `update`

By default, `@minmax update` means **build an update plan**, not **mutate everything immediately**.

The user may approve:

- all safe candidates
- selected packages
- all candidates including high-risk ones
- none

Natural-language filters such as "update everything except X" or "only low-risk updates" are compiled to an explicit selection before apply.

### 11.5 Pin and branch tracking

`pin` freezes exact installed content.

Branch tracking is separate:

- default: stable release, else default branch
- branch tracking: explicit user override
- pin: exact content freeze

A pinned package may still report newer versions during `check`, but it is not selected for update automatically.

### 11.6 Rollback

Rollback uses locally/cloud-stored immutable artifacts and therefore does not depend on the upstream source still existing.

The rollback itself is transactional and re-applies/reconciles the relevant overlay before activation.

### 11.7 Status

Status summarizes:

- managed package count
- updates available
- pinned packages
- local overlays
- conflicts
- unknown sources
- canonical storage mode
- target synchronization state
- last metadata check
- incomplete/recovery-required transactions

## 12. Changelog and semantic diff

The update review contains two layers.

### 12.1 Deterministic facts

Derived from actual old/new package state:

- files added/removed/changed
- `SKILL.md` changes
- trigger changes where parseable
- scripts/executables changed
- bundled component changes
- external requirement changes
- capability changes
- overlay impact
- exact old/new source refs and hashes

### 12.2 Semantic explanation

The model may summarize:

- intended behavioral changes
- likely breaking changes
- why risk increased/decreased
- what the user should pay attention to

The semantic layer must distinguish:

- upstream-authored changelog/release notes
- deterministic engine findings
- model inference

The model may not invent changes or suppress material capability escalation.

## 13. Security model

### 13.1 Source trust levels

Provenance/trust is represented categorically rather than with a single pseudo-precise score:

- `TRUSTED`
- `VERIFIED`
- `KNOWN`
- `UNVERIFIED`
- `BLOCKED`

These levels describe source/provenance confidence, not whether package behavior is safe.

### 13.2 Provenance chain

Where available, the registry records:

```text
package
-> source URL
-> provider
-> repository/project stable ID
-> publisher identity
-> release/ref
-> commit
-> downloaded artifact
-> content hash
```

Signatures/attestations are optional in the MVP but the data model is prepared for Git signatures, Sigstore/Cosign, provider attestations, or future MinMax signatures.

### 13.3 Capability inspection

The inspector emits capabilities such as:

- filesystem read/write
- network access
- code execution
- shell execution
- credential access indicators
- external connectors
- system configuration
- persistence
- child-agent execution
- package installation
- remote-content retrieval
- external write operations

Capability escalation between installed and candidate versions is a first-class risk signal.

### 13.4 Risk levels

Risk classification is rule-driven first.

**LOW:** documentation/reference changes, no new executable behavior, no capability escalation, clean overlay.

**MEDIUM:** behavioral instruction changes, trigger changes, new files, bundled subskill changes, requirement changes.

**HIGH:** executable/script changes, new shell/network/filesystem-write behavior, credential-related instructions, installer changes, major package-structure changes.

**CRITICAL:** clear structural violations such as credential-harvesting patterns, hidden remote execution, unexpected persistence, privilege escalation, self-modifying installer behavior, path escape, or attempts to bypass MinMax approval.

The model may explain the deterministic classification but may not silently downgrade it.

### 13.5 Prompt-injection boundary

Package contents are untrusted data during inspection. `SKILL.md`, scripts, comments, README text, or other package content must never be interpreted as instructions to the control plane while the package is being inspected.

The allowed flow is:

```text
untrusted package content
-> isolated inspector
-> structured findings
-> control plane
```

Never:

```text
package instructions -> agent execution
```

### 13.6 Block versus warning

Capabilities such as shell or network are not inherently malicious. They raise review requirements.

Hard blocking is reserved for deterministic integrity or policy failures such as:

- hash mismatch
- artifact changed after approval
- source identity mismatch
- path traversal/package escape
- corrupt archive
- target write outside allowed scope
- explicit configured policy violation

## 14. Update approval policy

Default policy: `review-all`.

Potential future modes:

- `review-all`
- `safe-auto`
- `manual`

The MVP defaults to explicit review before mutation. `safe-auto`, if later enabled, may only apply when deterministic guardrails are satisfied (for example verified source, clean overlay, no executable/capability change, low-risk patch-class change).

No unrestricted silent auto-update mode is required.

## 15. Failure model and recovery

Transaction states:

- `PLANNED`
- `STAGED`
- `APPROVED`
- `APPLYING`
- `ACTIVE`
- `FAILED`
- `ROLLED_BACK`
- `CONFLICT`

An append-only transaction journal records enough state to recover after crash or process interruption.

On startup/status, an incomplete transaction is reconciled by journal evidence and content hashes:

- discard untouched staging;
- restore previous active state if activation was incomplete;
- reconcile target state if target materialization succeeded but registry commit did not;
- block further mutation and require repair if a safe state cannot be proven.

The invariant is: a failed transaction must leave the previous known-good environment usable or produce a clearly blocked recovery state, never silently partial success.

## 16. Rollback retention and garbage collection

Default retention target: last three activated versions per package, plus any artifact referenced by:

- a pin
- another device
- a snapshot
- an open/incomplete transaction
- an overlay base still needed for reconciliation

Unreferenced artifact objects may be garbage-collected.

## 17. Snapshots

The data model supports environment snapshots from the MVP even if the dedicated UX arrives slightly later.

A snapshot records the complete logical environment:

- package identities
- exact artifact hashes
- overlays
- tracking policies
- target configuration

Because artifacts are content-addressed, snapshots are metadata-heavy rather than duplicate-heavy.

## 18. Test strategy

### 18.1 Unit tests

Required for:

- source normalization
- package identity
- version resolution
- hashing
- manifest parsing
- risk rules
- lockfile generation
- overlay reconciliation
- journal state transitions

### 18.2 Adapter contract tests

Every adapter family has a common contract suite.

Source adapters must implement equivalent behavior for operations such as:

- resolve
- fetch metadata
- fetch immutable artifact
- enumerate versions/refs when supported
- obtain default ref
- verify source identity

Storage and target adapters receive analogous contract suites.

### 18.3 Fixture repositories/packages

Test fixtures cover:

- single skill
- monorepo
- bundle with subskills
- repository with releases
- repository without releases
- renamed repository
- fork
- moved package
- malformed package
- direct archive
- malicious/path-traversal archive

### 18.4 Transaction failure injection

Failure must be injected at every meaningful boundary:

- remote fetch failure
- hash mismatch
- staging failure
- overlay conflict
- target write failure
- registry/lock commit failure
- cloud sync failure
- process crash

The required assertion is that the previous environment remains usable or recovery state is explicit and safe.

### 18.5 Semantic-diff golden tests

Fixtures contain before/after package states plus expected deterministic findings. Model output is checked for:

- no omitted capability escalation
- no invented change
- correct distinction between fact and inference
- breaking-behavior visibility
- prompt-injection resistance

## 19. MVP acceptance criteria

The MVP is not considered reliable until all of the following scenarios pass:

1. Install a GitHub skill and reproduce the exact artifact hash on another device.
2. Install through SkillsMP and recognize the equivalent canonical GitHub package without duplication when applicable.
3. Update a no-release skill using the repository default branch.
4. Track a custom branch only after explicit configuration.
5. Detect a local modification and preserve it as an overlay.
6. Update upstream while preserving a clean overlay.
7. Block activation when overlay reconciliation conflicts.
8. Show deterministic and semantic changelog before update.
9. Update only selected packages from a multi-package plan.
10. Recover safely from process interruption during update.
11. Roll back without contacting upstream.
12. Detect target drift.
13. Restore the environment from the configured cloud store.
14. Recognize different source aliases as one package identity when deterministically provable.
15. Inspect malicious package content without executing or following its embedded instructions.

## 20. Setup default behavior

`@minmax setup` should default to:

- local canonical store
- optional Google Drive sync
- automatic target detection
- review-all update policy
- stable-release tracking with default-branch fallback
- no custom branch unless explicitly requested
- scan/adopt existing skills
- unknown sources preserved as local packages
- no destructive file changes before adoption plan approval

Cloud configuration is optional. A user may stay local-only or point the generic filesystem adapter at a personally synchronized drive directory, but direct multi-device execution from a shared cloud directory is not the canonical architecture.

## 21. Non-goals and explicit constraints

- MinMax does not guarantee that a package is safe; it reports what it can verify, detects capabilities/risk signals, and makes uncertainty explicit.
- MinMax does not treat semantic version numbers as security/risk classification.
- MinMax does not use package names as globally unique identifiers.
- MinMax does not automatically infer source identity from fuzzy name/content similarity.
- MinMax does not silently install external skill dependencies.
- MinMax does not silently change a package's upstream source.
- MinMax does not let the language model become the source of truth for package state.

## 22. Final architectural invariant

Every mutating operation follows this pattern:

```text
user intent
-> deterministic resolution
-> immutable candidate
-> verification + inspection
-> deterministic facts
-> semantic explanation
-> immutable transaction plan
-> explicit approval under default policy
-> atomic activation
-> verification
-> durable state commit
-> optional cloud synchronization
```

The package manager is therefore a reproducible multi-source, multi-target package system with an agentic interface, rather than an agent that happens to edit skill folders.