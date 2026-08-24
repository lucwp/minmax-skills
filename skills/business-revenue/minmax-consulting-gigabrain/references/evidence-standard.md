# Evidence and epistemic standard

This is a MinMax synthesis influenced by A-002, A-004, A-005 and assurance principles in A-006.

## Source ledger

For each material source record:
- `source_id`
- title / dataset name
- producer / owner
- source type
- publication/as-of date
- retrieval date
- geography
- population / coverage
- unit, currency, base year where relevant
- denominator / taxonomy
- method / sample where relevant
- revision status
- conflict-of-interest note
- limitations
- location / URL / internal path

## Claim ledger

For each material claim record:
- `claim_id`
- exact claim
- type: fact, estimate, calculation, forecast, qualitative_fact, opinion, recommendation
- source IDs
- calculation ID
- assumption IDs
- as-of date
- geography
- unit/currency/base year/measure type
- confidence
- limitations
- report location

## Evidence hierarchy

Prefer the source closest to the underlying event. A CRM field is not automatically stronger than an audited revenue ledger; a management deck is not automatically stronger than transaction-level data.

When two sources conflict, compare:
1. definition compatibility;
2. directness to underlying event;
3. controls/auditability;
4. recency/vintage;
5. coverage/sample;
6. incentives/conflict of interest.

Record the losing source and reason. Do not erase the conflict.

## Internal evidence is not automatically true

Check:
- grain;
- completeness;
- duplicates;
- nulls;
- impossible values;
- definition changes;
- reconciliation to controlled totals;
- selection/survivorship bias;
- whether pilot economics exclude scaled costs.

## Minimum release rules

- No load-bearing factual/quantitative claim without a source.
- No forecast without assumptions and a calculation/model reference.
- No comparison across incompatible currency, period, geography, measure, denominator or taxonomy.
- No estimate presented with fake precision.
- No benchmark applied without confirming comparability.
- No claim upgraded from correlation to causation without a credible causal basis.


## Deterministic ledger minimums

When using `validate_evidence.py`, the compact source ledger must include `source_id`, `publication_date`, and `retrieval_date`; the compact claim ledger must include `claim_id`, `claim_type`, `source_ids`, `calculation_id`, `assumption_ids`, and `confidence`. Empty ledgers, malformed IDs, duplicate claim/source IDs, duplicate citations, future retrieval dates, publication-after-retrieval dates, uncited evidence-bearing claims, malformed calculation/assumption IDs, and blank/invalid confidence fail closed.

When using `validate_consistency.py`, all required comparison fields must be populated with valid formats. Use optional `comparison_mode=time_series` only when period variance is intentional; other comparability fields must still reconcile.
