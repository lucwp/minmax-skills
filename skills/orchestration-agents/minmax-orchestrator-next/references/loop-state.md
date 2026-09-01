# Loop State Policy

## Purpose

Choose the lightest state strategy that can recover verified work without relying on conversation history as the only memory.

## ephemeral

Use when the loop is short, single-session, cheap to reconstruct, read-only, and has no material intermediate human interruption.

Keep only the minimum current-cycle state required for verification and transition.

## checkpointed

Use when any of the following materially applies:

- long-running work;
- multiple sessions;
- HITL interruption;
- completed work is expensive to repeat;
- state-changing writes;
- parallel work;
- context-compaction/reset risk;
- external state requires receipts or read-back.

Persist compact state after initial approval when needed, after material progress, before human interruption, after verified writes, and before a known context reset/compaction.

## Minimum checkpoint schema

Runtime checkpoint state is a separate artifact from the immutable Loop Contract. Store only fields that help reconstruct truth:

```text
schema_version
run_id
contract_id
contract_version
contract_digest
approval_reference
approved_contract_digest
external_write_preauthorization_ref  # when autonomous external_write is approved
topology
side_effect_class
approved_boundaries
done
active
blocked
invalidated
evidence
verification_status
remaining_budgets
write_receipts
next_ready
status
```

Validate checkpoints with `scripts/validate_loop_checkpoint.py --contract <contract> --approved-digest <root-captured-digest>` and add `--external-write-preauthorization-ref <root-captured-ref>` when an approved external write may run without a per-step human gate. Remaining budgets may decrease but must never exceed the approved contract budgets. The checkpoint cannot create a new approval identity by rewriting its own digest fields.

Do not persist chain-of-thought, full transcripts, or copied conversation history.

## Resume protocol

On resume:

1. load the latest checkpoint;
2. validate contract/version compatibility;
3. read authoritative external state when the world may have changed;
4. reconstruct only high-signal context for incomplete work;
5. verify ambiguous writes before retrying;
6. continue only unfinished work inside the approved envelope.

If the checkpoint conflicts with authoritative state, authoritative state wins and the discrepancy becomes a recovery signal.
