# Proposal data schema

The renderer consumes JSON with `schema_version`, `meta`, and `pages`.

```json
{
  "schema_version": "1.0",
  "meta": {"proposal_title":"Proposal","client_name":"Client","client_logo_path":"","issue_date":"2026-08-24","valid_until":"2026-09-23","prepared_for":"","prepared_by":""},
  "pages": [{"type":"cover|executive|narrative|decision|scope|sequence|comparison|commercial|proof|next-step","section":"Executive summary","title":"","subtitle":"","body":["Short paragraph"],"bullets":["Item"],"cards":[{"label":"","title":"","body":"","value":""}],"items":[{"label":"","title":"","body":""}],"investment":{"included_scope":[""],"assumptions":[""],"rationale":"","components":[{"label":"","amount":"","unit":"","note":""}],"total":"","payment_terms":""},"next_step":""}]
}
```

## Required fields
- `schema_version` must be `1.0`.
- `meta.client_name` and `meta.proposal_title` are required.
- `pages` must contain at least one page.
- Every page requires `type`, `section`, and `title`.
- `commercial` pages require investment keys for included scope, assumptions, rationale, components, and total. Values may be `[TO DEFINE]` but must not be silently omitted.
- `next-step` pages require `next_step`.

The schema is intentionally flexible: content can be edited without hand-editing HTML.
