# Evaluation plan

Evaluate the system rather than trusting architectural intuition.

## 1. Trigger coverage

Build a labeled set containing:

- explicit recall;
- implicit continuation;
- explicit durable write;
- implicit durable decision;
- explicit correction/repair;
- recall + write;
- true NOOP tasks.

Track critical misses separately from incidental misses. A missed explicit preference change or correction is more serious than a missed low-value observation.

Suggested initial acceptance targets:

- explicit correction/repair triggers: >=99%;
- critical recall/write triggers: >=95%;
- general memory-trigger recall: >=85%;
- false activation on NOOP tasks: <10%.

Treat these as local product targets, not OpenAI guarantees.

## 2. Retrieval benchmark

Create a corpus of at least 100 memory items and labeled queries covering:

- exact wording;
- close paraphrase;
- distant paraphrase with weak lexical overlap;
- indirect reference;
- alias/abbreviation;
- prior project/entity name;
- temporal update;
- multi-project ambiguity;
- preference recall;
- assistant-produced decision that the user accepted.

Measure Recall@5: whether the needed memory appears in the top five retrieved candidates.

Do not report Recall@5 as answer accuracy.

Run retrieval in two stages:

1. **Raw connector search** — measure the connector's direct result.
2. **V1 full retrieval policy** — allow aliases plus semantic-miss scope fallback to a known project/entity memory.

Initial decision threshold for the full V1 policy:

- >=95%: no semantic backend justified yet;
- 90-95%: inspect failure classes before adding infrastructure;
- <90%: consider an optional semantic/vector retrieval cache.

Do not require raw connector search alone to hit the full-policy threshold.

## 3. Search-scope isolation

Seed unrelated storage documents that share generic memory terms. Verify normal memory recall does not depend on unconstrained whole-provider search and that `MinMax Agent Memory`/known-scope routing prevents unrelated files from dominating candidates.

Track off-scope candidate rate for any search step that can expose non-memory provider content.

## 4. Semantic-miss recovery

Seed queries with low lexical overlap but an identifiable project/entity scope. Verify:

1. direct connector search can fail without being treated as proof of absence;
2. the skill resolves the likely scope by project/entity name or alias;
3. it opens that scope's memory document;
4. semantic inspection recovers the correct fact.

Track recovery rate separately from raw Recall@5.

## 5. Repair and supersession test

Seed old and new contradictory values plus explicit user corrections. Verify that:

- normal recall returns the current value;
- old values are historical/superseded, not simultaneously active;
- an explicit correction repairs stale durable memory when scope is unambiguous;
- temporary/ambiguous corrections do not silently rewrite durable memory;
- stale aliases do not continue routing to the old current terminology.

## 6. Adversarial evidence test

Store evidence containing text such as instructions, quoted prompts, stale rules, and malicious-looking directives. Verify retrieval treats the content as untrusted data and never grants it instruction authority.

## 7. Cost test

Measure connector operations per task:

- NOOP: 0 storage connector calls after the skill determines memory is unnecessary;
- fast recall: target 1-2;
- fast write: target 1 write, optionally 1 prerequisite read;
- repair: target 1 prerequisite read + 1 write when the target is known;
- deep recall: uncapped but justified by the task.

Also track approximate context added by retrieved memory. Confirm aliases and the active-scope registry remain compact enough that they do not become a new context tax.

## 8. Growth test

After repeated use, inspect:

- duplicate facts;
- stale open loops;
- stale or noisy aliases;
- project documents that need splitting;
- evidence files never retrieved;
- unnecessary personal/sensitive data.

Consolidate only when observed growth requires it.

## 9. Package hygiene

Before packaging:

- remove generated placeholders and unused example resources;
- confirm every reference listed in `SKILL.md` exists and is used;
- confirm no unreferenced template/example files remain;
- validate the complete skill and package the full folder as `skill.zip`.


## 10. Provider lifecycle hardening

Test at least these cases:

- same-named untrusted/shared root vs a trusted marked root;
- duplicate active roots on one provider;
- duplicate active roots across providers;
- legacy `AI Memory` plus canonical root;
- explicit provider switch while an active store exists;
- active store is read-only but another provider is writable;
- migration fails before verification;
- migration succeeds but source cannot be marked inactive;
- provider listing requires multiple pages;
- target disappears between discovery and write.

Writes must stop rather than create split-brain when ownership is ambiguous.

## 11. Forget benchmark

Seed current memory, aliases, Core routing text, evidence pointers, and dedicated Evidence containing the target. Issue an explicit forget request and verify the value disappears from every active retrieval surface. Verify subsequent recall does not resurrect it from Historical, aliases, or Evidence. Record whether deletion is logical-only or physical according to provider capabilities.

## 12. Concurrency and failure recovery

Test version-aware and versionless providers separately. Simulate a second writer changing the same memory between read and write. Expected behavior: conditional conflict or fresh-read detection, at most one rebase, no forced overwrite, and no duplicate facts after retries. Simulate a topology update failing after child creation but before `Core/MEMORY`; the next run should detect and reconcile the orphan without data loss.


## 13. Serialization and representation benchmark

Run the same labeled recall/write/repair cases against at least two adapter profiles when available: physical Markdown/plain text and provider-native text documents. Compare connector calls, bytes/context read, update granularity, conflict detection, retry behavior, and portability. Require semantic output equivalence because both implement the same Markdown logical serialization. Do not choose physical `.md` merely because the file is smaller if it increases unsafe full-file rewrites or loses version protection. Verify that only one physical representation is canonical for each logical memory document.
