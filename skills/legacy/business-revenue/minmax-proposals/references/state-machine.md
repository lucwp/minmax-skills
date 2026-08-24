# Proposal system state machine

## States

### UNCONFIGURED

Enterprise worker missing, template, or no usable offer architecture.

Action: run Inquiry.

### DRAFT

Some reusable configuration exists but material gaps remain.

Action: run targeted Inquiry for gaps before autonomous proposal generation. A user may explicitly accept draft mode; unresolved fields remain `[TO DEFINE]`.

### CONFIGURED

Business identity, usable offers, pricing policy, buyer context, commercial defaults, evidence policy, brand minimums, and workflow defaults are materially complete.

Action: use Enterprise Proposal.

### STALE

Configured worker exists, but user has supplied newer reusable information that conflicts with or supersedes it.

Action: run targeted Inquiry update, validate, then use Enterprise Proposal.

## Reusable vs deal-specific

Reusable configuration belongs to Inquiry if it should affect more than one future proposal.

Deal-specific information belongs to Enterprise Proposal if it is unique to the current client opportunity.

Examples:

- "Our minimum retainer is now $8k" -> reusable -> Inquiry.
- "This client has a $20k budget" -> deal-specific -> Enterprise Proposal.
- "We changed our logo" -> reusable -> Inquiry.
- "Use the client's new logo on this proposal" -> deal-specific asset -> Enterprise Proposal.
