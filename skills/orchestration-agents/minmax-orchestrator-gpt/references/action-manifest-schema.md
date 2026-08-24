# Action manifest schema

Create this JSON before autonomous state-changing work and validate it with `scripts/validate_action_manifest.py`.

```json
{
  "schema_version": "1.0",
  "run_id": "run-123",
  "objective": "Update one CRM account status",
  "autonomy_mode": "autonomous",
  "action_class": "reversible_write",
  "targets": ["crm:account:123"],
  "write_set": ["crm:account:123"],
  "idempotency_key": "crm-account-123-status-v2",
  "expected_postconditions": ["crm:account:123.status == active"],
  "verification": {"method": "authoritative_read", "source": "CRM account read endpoint"},
  "compensation": {"strategy": "rollback", "details": "Restore the previous status"},
  "limits": {"max_writes": 1, "max_records": 1, "max_external_targets": 0, "max_cost": 0},
  "preauthorization_ref": "",
  "untrusted_inputs": ["customer supplied notes"],
  "audit_log": "logs/run-123.jsonl",
  "concurrency_keys": ["crm:account:123"]
}
```

## Rules

- `read_only` needs only run identity, objective, autonomy mode, class, and targets.
- All writes require idempotency, write set, postconditions, deterministic/authoritative verification, limits, compensation metadata, an audit log, and concurrency keys.
- Autonomous `external_write` also requires `preauthorization_ref` and `max_external_targets > 0`.
- `irreversible_high_consequence` cannot use `autonomy_mode: autonomous`.
- `verification.method` must be `authoritative_read`, `deterministic_test`, or `transaction_receipt`.
- If compensation is genuinely impossible, use `strategy: not_possible` and set `irreversibility_acknowledged: true`.
