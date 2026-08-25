# Runtime portability

Use this reference when installing or adapting MinMax Agent Memory outside its current host runtime. The normative core is `SKILL.md` plus the files under `references/`. Runtime metadata and tool names are adapters, not memory semantics.

## Portability target

The package follows the Agent Skills open format: a skill directory with `SKILL.md` containing `name` and `description`, plus optional supporting resources. Keep the core valid under that standard and avoid mandatory vendor-specific frontmatter.

Authoritative format reference:
https://agentskills.io/specification

OpenAI also documents that its Skills follow the Agent Skills open standard and can be moved between supported products:
https://help.openai.com/en/articles/20001066-skills-in-chatgpt

## Runtime profiles

### 1. Native Agent Skills runtime

Install the directory unchanged in the runtime's supported skills location or package mechanism. The runtime should use `name` and `description` for discovery, load `SKILL.md` on activation, and resolve referenced files on demand. Unknown optional metadata such as `agents/openai.yaml` must not become part of the core contract.

### 2. Instruction-loading runtime

If the runtime has no native Agent Skills discovery but supports persistent instructions, configure a small bootstrap that says, in substance:

```text
When a task requires durable cross-session memory, load <skill-root>/SKILL.md and follow it. Resolve its relative references only when the active path requires them. Treat runtime-specific tool names as adapters for the logical storage operations defined by the skill.
```

Do not paste or maintain a second full copy of the skill body in `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, workspace rules, system prompts, or equivalent instruction files. A duplicated core will drift.

### 3. MCP/plugin/tool runtime

The skill does not require a particular connector system. Bind logical storage operations to whatever the runtime exposes:

- local or sandbox filesystem;
- MCP filesystem/cloud-storage server;
- plugin/app/connector file service;
- Git/repository API or CLI;
- object storage or document store with text access;
- SDK/tool calls that expose equivalent persistent file operations.

The minimum for RECALL is `LIST/LOCATE + READ`. The minimum for durable writes is `CREATE + UPDATE` in addition. `SEARCH`, `DELETE`, `RENAME/MOVE`, and `VERSION_CHECK` improve quality but are optional.

### 4. Stateless runtime

If the runtime cannot access persistent storage across sessions, the skill cannot provide durable memory. Do not emulate persistence by claiming the model will remember. Use current session context only.

## Runtime-neutral invariants

- Never depend on a particular tool namespace, function name, CLI syntax, filesystem path convention, or provider MIME type in canonical memory logic.
- Keep logical paths relative to the `MinMax Agent Memory` root. An adapter translates those paths to folders, directories, prefixes, repository paths, or collections.
- Keep memory content Markdown-compatible even when the physical representation is a native document.
- Preserve one canonical active store and one canonical physical representation per logical memory document.
- Use runtime-native version/CAS semantics when available; otherwise apply the skill's re-read/rebase safeguards.
- Do not make a cloud connector mandatory when a local filesystem, repository, MCP server, or another persistent file tool already satisfies the contract.
- Do not make local filesystem access mandatory when the runtime only exposes cloud/document tools.

## Runtime metadata

`agents/openai.yaml` is optional metadata for OpenAI runtimes. It must not be referenced as a prerequisite by `SKILL.md`. Other runtimes may add their own metadata outside the normative core as long as it does not duplicate or override the skill's behavior.

If a runtime requires generated adapter files, generate the smallest adapter that points back to `SKILL.md`; do not fork the memory policy into separate vendor-specific versions.

## Compatibility test

Before claiming full support for a runtime, verify:

1. discovery or bootstrap can load `SKILL.md`;
2. relative references are reachable;
3. the runtime exposes at least read-compatible persistent storage;
4. write workflows map cleanly when durable mutation is expected;
5. one ordinary RECALL completes without vendor-specific assumptions in the core;
6. one WRITE/REPAIR/FORGET path behaves correctly for the backend's concurrency capabilities;
7. unsupported optional metadata is ignored rather than treated as required.

A runtime can be **format-compatible** while still lacking the storage capabilities needed for full durable-memory behavior. Report those as separate dimensions.
