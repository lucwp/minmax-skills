# Business Proposal Profile schema

The profile is a portable JSON source of truth. Unknown values should be empty, `null`, or explicitly `[TO DEFINE]`; never fabricate them to make the file look complete.

## Top-level fields

### `schema_version`
Required. Current value: `1.0`.

### `status`
One of `draft`, `configured`, or `template`.

### `business`
Required fields: `name`, `legal_name`, `website`, `category`, `one_liner`, `markets[]`, `languages[]`, `default_currency`, `proposal_issuer` with `name`, `title`, `email`.

### `positioning`
`ideal_customers[]`, `poor_fit_customers[]`, `buyer_roles[]`, `trigger_events[]`, `core_problems[]`, `value_proposition`, `competitive_alternatives[]`, `differentiators[]`, `objections[]`, `decision_criteria[]`, `preferred_framing[]`, `avoid_framing[]`.

### `offers[]`
Each offer should contain `id`, `name`, `descriptor`, `type`, `summary`, `best_for[]`, `business_value`, `delivery`, `deliverables[]`, `boundaries[]`, `prerequisites[]`, `client_dependencies[]`, `pricing`, and `proof_ids[]`.
Offer types: `project`, `recurring`, `usage`, `hybrid`, `custom`.
Pricing models: `fixed`, `retainer`, `per_unit`, `tiered`, `usage`, `milestone`, `hybrid`, `custom`.

### `commercial`
`default_payment_terms`, `proposal_validity_days`, `tax_notes`, `discount_policy`, `scope_change_policy`, `scenario_policy`.

### `proof`
Metrics include `id`, `claim`, `value`, `source`, `confidence`, `allowed_contexts[]`. Confidence: `verified`, `internal_estimate`, `unverified`.
Case studies include `id`, `client`, `situation`, `work`, `outcome`, `source`, `permission`. Permission: `approved`, `restricted`, `unknown`.
Testimonials include `id`, `quote`, `attribution`, `source`, `permission`. Customer logos include `name`, `asset_path`, `permission`.

### `brand`
`logo_path`, `primary_color`, `accent_color`, `background_color`, `surface_color`, `text_color`, `muted_color`, `font_display`, `font_body`, `border_radius_px`, `visual_style[]`, `anti_style[]`, `image_style`, `cover_image_path`, `footer_text`, `confidentiality_label`.
Do not store proprietary font binaries in the skill profile. Store CSS family names only.

### `voice`
`default_language`, `tone[]`, `preferred_terms[]`, `banned_terms[]`, `claim_policy`.

### `proposal_defaults`
`page_size`, `include_about_us`, `approval_mode`, `generate_email`, `default_next_step`.
