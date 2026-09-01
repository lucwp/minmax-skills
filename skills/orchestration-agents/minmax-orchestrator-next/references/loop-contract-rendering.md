# Loop Contract Rendering

## Purpose

Keep the Internal Loop Contract complete and machine-readable while presenting the user with the shortest approval view that preserves:

1. a clear name for the loop;
2. a mental model of what will happen, in what order, and why;
3. every approval-relevant boundary.

Use a two-pass process:

1. compile and preflight the Internal Contract;
2. render a Human Contract from that validated source.

Do not let the human rendering become the source of truth. Do not let compression make the execution logic opaque.

## Hard clarity gates

A Human Contract is not ready for approval unless all are true:

- its first line is always the document's largest Markdown header (`H1`): exactly `# Contrato de Loop - <o que é>` in pt-BR or `# Loop Contract - <what it is>` in English, with a short task-specific suffix; never render this title as plain text, `##`, `###`, or any smaller heading;
- a capable user can predict the execution path after one read;
- every material execution step states **what happens**, **why it happens**, **what it produces**, and **what that output enables next**;
- abstract orchestration terminology is omitted unless it changes approval, risk, cost, or method;
- labels such as `research`, `analyze`, `improve`, `validate`, or `iterate` are not accepted as standalone steps;
- technical terms remain precise, but unexplained jargon does not carry the logic of the contract;
- the contract distinguishes the plan from the convergence logic: the user can see both the path and the rule that decides whether another cycle is useful;
- brevity never wins over comprehension.

Use this final readability question:

> Can the user explain back what the loop will do first, what each step is for, what comes out of it, and how the loop decides to continue or stop?

If not, repair the rendering before asking for approval.

## Language standard

The Human Contract should be written in the user's language unless the user requests another language. The Internal Contract may remain technical and machine-oriented.

### Brazilian Portuguese

Embed the relevant principles of **MinMax PT-BR Output** directly in the renderer. Do not require that skill to be available at runtime.

- write in natural contemporary Brazilian Portuguese;
- preserve objective, scope, certainty, constraints, agency, and causal/logical relations exactly;
- prefer ordinary verbs, direct clause relations, and stable terminology;
- keep established technical English terms when they are more precise, but integrate them naturally into Portuguese syntax;
- avoid literal English sentence molds, generic metadiscourse, mechanical cadence, artificial synonym cycling, and compressed phrases that force the user to reconstruct the logic;
- do not add claims, implications, or certainty merely to make the contract sound smoother;
- clarity and semantic fidelity outrank elegance.

If `minmax-ptbr-output` is installed and already in scope, it may be used as an editorial specialist. Its absence must not degrade the embedded standard above.

### English

Embed the relevant principles of **Humanizer** directly in the renderer. Do not require that skill to be available at runtime.

- use natural, idiomatic, professional English rather than model-like prose;
- prefer concrete nouns and verbs, explicit agency, and direct transitions;
- remove canned AI transitions, inflated significance, vague abstractions, promotional puffery, repetitive sentence molds, and unnecessary restatement;
- vary rhythm naturally without making technical content chatty or theatrical;
- preserve technical precision, modality, scope, and all approval boundaries;
- do not add opinions, jokes, emotional framing, or personality merely to appear human;
- a cleaner sentence is a regression if it changes the contract's meaning.

If `humanizer` is installed and already in scope, it may be used as an editorial specialist. Its absence must not degrade the embedded standard above.

### Other languages

Use clear, idiomatic professional language and preserve the same semantic and structural gates. Do not silently apply Portuguese or English idioms to another language. The bundled reference renderer has explicit label maps only for `pt-BR` and `en`; for another language, render deliberately rather than falling back to English.

## Human Contract structure

The first line is mandatory, localized, and must always be a Markdown `H1` (the largest heading level):

```text
pt-BR: # Contrato de Loop - <o que é>
en:    # Loop Contract - <what it is>
```

Then use fully localized section labels. Do not mix the English canonical labels into a pt-BR contract.

### pt-BR label map

```text
Resumo para aprovação
Resultado
Entregável
PASS
Autonomia
Orçamento
Escopo e evidências
Plano de execução
Verificação e convergência
Limites e saídas
Pode
Não pode
SUCCESS
FAILURE
BUDGET
REPLAN
Aprovação
```

### English label map

```text
Approval snapshot
Outcome
Deliverable
PASS
Autonomy
Budget
Scope and evidence
Execution plan
Verification and convergence
Boundaries and exits
Can
Cannot
SUCCESS
FAILURE
BUDGET
REPLAN
Approval
```

## Loop name

The name is mandatory. It should describe the job of the loop, not the architecture. The renderer prepends the localized H1 contract label automatically: `# Contrato de Loop -` in pt-BR and `# Loop Contract -` in English. Do not duplicate `Loop` inside the task-specific suffix unless it is part of a proper name.

Good task-specific suffixes:

- `Stress Test de Posicionamento do Hero`
- `Clareza e Conversão do Hero`
- `Candidate Research Evidence`

Bad:

- `Loop 1234`
- `Optimization Loop`
- `Evaluator-Optimizer #1`
- `Loop Mode Execution`

Keep it short enough to scan. Prefer approximately 3-8 words when natural; this is a heuristic, not a validator rule.

## Approval Snapshot

Always show:

- **Outcome**: intended result;
- **Deliverable**: concrete terminal artifact/action/result;
- **PASS**: primary terminal gate;
- **Autonomy**: side-effect class and material human boundary;
- **Budget**: compact cycle/retry/no-progress budget.

Show topology only when it materially changes how the user should understand execution, risk, or cost. If shown, explain it in one plain-language sentence before or after the technical class.

## Scope & Evidence

When non-trivial, show authoritative inputs, universe, constraints, exclusions, and material evidence gaps.

Omit trivial scope detail.

## Execution Plan

Normally render 3-7 material steps. Very small loops may use 2. Do not add steps merely to satisfy a preferred count.

Render each step so its logic is explicit:

```text
### 1. <Concrete step name>
What happens: <observable action>
Why: <purpose / decision this resolves>
Produces: <evidence, artifact, decision, or state>
Then: <how this output constrains or enables the next step>
```

Equivalent natural prose or a table is allowed when it is equally clear. The four relations must remain recoverable.

Prefer operational actions. For example, replace:

`Research -> Analyze -> Validate`

with:

1. collect the named evidence required to test the current hypothesis;
2. compare it against the frozen decision criteria and identify the load-bearing gap;
3. change only the part responsible for that gap;
4. run the independent verifier and decide whether to stop, repair locally, or start another approved cycle.

Do not expose low-level implementation choices that correctness depends on future observations. Explain the material path, not a speculative script.

Mention tools/skills only when they change method, capability, risk, or approval meaning.

## Verification & Convergence

Show:

- detailed PASS criteria;
- terminal verifier/evidence;
- what counts as material progress;
- local repair rule;
- no-progress rule;
- the convergence decision: why another cycle would or would not be useful.

Do not expose internal proxy-hardening detail unless it materially affects approval.

## Boundaries & Exits

Always make explicit:

```text
Pode
Não pode
SUCCESS
FAILURE
BUDGET
REPLAN
```

A material replan requires a new approval.

## Approval

State that approval authorizes only the presented contract and that a material replan invalidates it.

Then stop. Never execute the first cycle in the same turn as the contract.

## Density heuristic

Use the shortest contract that preserves operational clarity and approval boundaries.

Typical ranges are guidance, not hard limits:

- Lite: 180-320 words;
- Standard: 300-520 words;
- Complex: 500-750 words.

These ranges may be exceeded when needed to make the execution path unambiguous. Additional words must add operational information, not architecture theory.
