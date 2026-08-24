# Model Routing

## Principle

Allocate model capability to the narrowest node where its marginal value exceeds its marginal cost.

Model names and pricing can change; treat this file as a policy layer, not a pricing source of truth.

## Default Policy

### Root / trivial / mechanical
Use the current root model or Luna medium/high when model selection is available and the work is deterministic or cheaply verified.

### Normal substantive worker
Default to **Luna high**.

Use for:
- bounded research;
- routine implementation;
- transformations;
- structured analysis;
- normal tool workflows;
- first-pass verification.

### Complex planner / hard bounded reasoning
Use **Luna xhigh** only when the planning/node complexity plausibly benefits from extra reasoning and the run is externally bounded when possible.

Do not use xhigh merely because the overall user request is large.

### Capability / coordination escalation
Use **Terra xhigh** only after:
1. missing context was repaired;
2. scope was narrowed/clarified;
3. validation still shows a genuine capability/coupling failure.

Escalate the node, not the project.

### High-consequence judgment
Use **Sol high/xhigh** only for narrow decisions/criticism where error cost is materially high and evidence remains ambiguous.

Prefer high before xhigh unless the unresolved ambiguity is central.

## Prohibited

Never request `max` reasoning effort.

Never use a premium model for:
- deterministic arithmetic;
- raw source collection;
- simple summarization;
- routine formatting;
- prestige/status signaling.

## Failure Diagnosis Before Escalation

- **Context failure:** retrieve the missing facts.
- **Assignment failure:** rewrite/narrow the worker contract.
- **Tool failure:** use/fix the correct tool.
- **Validation failure:** improve the check.
- **Reasoning ceiling:** increase reasoning or model family for that node.
- **Judgment risk:** use a narrow senior critic.

## Runtime Truthfulness

If runtime does not expose model-specific delegation or reasoning controls, do not claim these models/efforts ran. Apply the routing logic conceptually with available capabilities and disclose the limitation only when material.
