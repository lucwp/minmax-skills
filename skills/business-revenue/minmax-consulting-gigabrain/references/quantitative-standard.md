# Quantitative and business-case standard

Architecture inspiration: A-003 and A-002. Implementation in `scripts/business_case.py` is original.

## Model architecture

Separate:
- sourced historical inputs;
- management estimates;
- assumptions;
- formulas/calculations;
- scenarios;
- decision thresholds.

Do not hard-code assumptions invisibly into formulas.

## Driver-based economics

Prefer operational drivers such as:

`customers x price x retention`

`volume x price`

`capacity x utilization x yield`

`headcount x productivity x conversion`

Then connect to variable cost, fixed cost, working capital, capex and one-time investment.

A top-line CAGR is an output or shorthand, not a sufficient operating model.

## Scenario design

At minimum include a base and a credible adverse case when uncertainty is material. A scenario changes coherent drivers, not just revenue by +/- 10%.

For each scenario state:
- assumptions changed;
- reason/evidence;
- NPV/IRR/payback or relevant economics;
- operational constraints;
- threshold at which recommendation changes.

## Input truth vs arithmetic truth

A deterministic calculator validates arithmetic only. It does not validate whether:
- the market exists;
- CAC scales;
- retention is measurable;
- capacity supports sales;
- the implementation is feasible.

Validate those premises through the evidence and logic layers before trusting the result.

## Decision thresholds

Define thresholds before seeing the preferred answer where possible. Examples:
- minimum NPV or IRR;
- maximum downside loss;
- payback limit;
- minimum contribution margin;
- capacity or adoption milestone;
- regulatory/technical blocker.

If the base case passes but a plausible downside violates a board-approved hard threshold, prefer staged commitment, option value, or additional evidence over an unconditional rollout.

## Sensitivity

Identify the 2-4 inputs with the greatest ability to flip the decision. Show switching values, not merely +/- ranges.


## Calculator failure behavior

`business_case.py` rejects non-finite numbers, discount rates at or below -100%, negative initial investment, empty scenarios, and empty year arrays. It suppresses IRR when cash flows change sign more than once because multiple IRRs may exist. Treat warnings as model-review prompts, not as automatic proof that the economics are invalid.
