# Synthetic red-team benchmark cases

Purpose: red-team reasoning fixtures for MinMax Consulting Giga Brain. These cases are synthetic and intentionally contain seductive but wrong management narratives, evidence conflicts, denominator traps, causal leaps, or challenge-engine failure modes.

Use these only for QA or skill maintenance. Do not load them for normal client work.

## Scoring rule

A case passes only if the workflow:
1. reaches the expected decision class;
2. identifies the load-bearing trap;
3. does not invent missing facts;
4. applies the smallest appropriate technique;
5. respects release/challenge stop rules.

## Cases

### Q01 Market entry: attractive headline, broken scalable economics
Management requests a full Mexico rollout. The pilot reports 12 logos, but only 10 are paying. Pilot CAC is USD 18k but excludes partner fees and founder time; comparable scaled CAC is USD 25k. Management forecasts 600 active customers in year 3, but ramp-adjusted sales capacity supports 24/60/84 new logos in years 1-3. Base NPV remains positive; downside NPV is below the board's -USD 1m hard threshold.

Expected: do not approve full rollout; recommend staged entry with explicit scale gates. Trap: pilot economics and commercial capacity invalidate the headline case.

### Q02 Pricing: average uplift hides a segment hard constraint
SMB price pilot raises price 25% but causes 15% immediate logo churn. Enterprise price pilot raises price 10% with 2% churn. Board rule: no segment-level price action may create more than 5% churn. Management proposes one blanket increase because aggregate ARPU rises.

Expected: reject blanket increase; segment pricing, with enterprise action potentially viable and SMB requiring redesign/testing. Trap: aggregation hides a segment-level hard constraint.

### Q03 M&A: double-counted synergy
Target EBITDA is USD 10m; purchase price is USD 90m. Management claims USD 8m annual synergies. USD 5m is already captured in current EBITDA/procurement run-rate. True incremental synergy is USD 3m/year for five years. Integration cost of USD 15m was omitted. At 10% discount rate, net incremental synergy NPV is about -USD 3.63m. Board requires net synergy NPV >= USD 10m.

Expected: do not support the deal on current terms; renegotiate or pass. Trap: synergy double counting plus omitted integration cost.

### Q04 Cost transformation: savings lower than induced penalty
Support cut removes 30 FTE and saves USD 2.4m annually. Capacity model shows response time rises above contractual threshold, producing expected SLA penalties of USD 3m annually. Management calls the cut "pure efficiency."

Expected: reject blunt cut; redesign capacity/automation before headcount removal. Trap: local cost saving destroys more value downstream.

### Q05 Operating model: reorg targets the wrong bottleneck
Sales cycle is 120 days. Process data shows 45 days waiting for CFO pricing approval, 20 days legal queue, and 5 days actual account-team processing. Management proposes a USD 1m Sales-CS reorganization to speed the cycle.

Expected: prioritize decision-rights/approval-threshold and legal-flow changes before reorganization. Trap: structural solution does not address measured wait-state bottleneck.

### Q06 Market sizing: denominator inflation
External source lists 50,000 businesses. 30,000 are sole proprietors and 12,000 are below eligibility requirements. Internal ICP leaves 2,400 reachable enterprises. Management uses 50,000 x USD 10k ARR = USD 500m TAM. Board enters only if defensible serviceable market >= USD 100m.

Expected: no entry under current ICP or re-segment/redefine the offer. Defensible serviceable revenue is USD 24m. Trap: universe count is used as serviceable denominator.

### Q07 Pilot selection bias
A partner-recruited pilot has 12 accounts and 10 renewals. A broader inbound cohort has 100 accounts, 45 activate, and 20 retain at day 90. Management extrapolates the partner pilot retention to full launch.

Expected: staged validation, not scale. Trap: selected pilot is not representative of the deployment population.

### Q08 Portfolio: highest single NPV is not highest portfolio value
Project A: NPV USD 8m, 10 engineers. Project B: NPV USD 6m, 5 engineers. Project C: NPV USD 5m, 4 engineers. Engineering capacity is 10. Management chooses A because it has the highest project NPV.

Expected: B + C, total NPV USD 11m using 9 engineers. Trap: optimizing project rank instead of constrained portfolio value.

### Q09 Turnaround: layoffs worsen the immediate cash problem
Company loses USD 1m EBITDA/month and has two months of cash runway. USD 12m receivables are >90 days overdue; 70% is collectible within 60 days with a USD 0.3m collection effort. Layoffs save USD 0.8m/month but require USD 4m severance immediately.

Expected: prioritize collections/working-capital action and liquidity bridge; layoffs alone worsen 60-day cash by USD 2.4m before other effects. Trap: EBITDA action is confused with near-term liquidity action.

### Q10 Transformation launch: benefits case is ahead of readiness
New platform promises USD 5m annual savings. Only 30% of managers are trained, two divisions have no executive sponsor, and migration tests cover 60% of critical data. Board launch criterion is >=80% readiness on all critical dimensions.

Expected: delay or staged rollout until readiness gates are met. Trap: positive value case does not override implementation blockers.

### Q11 Due diligence: management EBITDA is not normalized EBITDA
Management EBITDA is USD 15m and purchase price USD 120m. EBITDA includes a USD 4m one-off grant and USD 2m of recurring operating expense capitalized away. Normalized EBITDA is USD 9m, so entry multiple is 13.33x. Board maximum is 10x.

Expected: renegotiate valuation or pass. Trap: QoE normalization changes the deal threshold.

### Q12 Healthy thesis: red team must know when to stop
Manual invoice processing handles 100k invoices/year with audited annual labor cost USD 800k. Automation costs USD 300k one-time plus USD 250k/year. A representative 20k-invoice pilot has lower error rate than manual processing, rollback is available, and no material regulatory blocker is known. Simple payback is about 0.55 years; board hurdle is <2 years.

Expected: recommendation survives challenge; do not manufacture a critical objection. Conviction delta can remain UNCHANGED and challenge can become ROBUST after genuine concerns are resolved. Trap: contrarian theater.

### Q13 Weak conviction: hiring more SDRs attacks the wrong constraint
User conviction: hire 20 SDRs because pipeline is low. Current 5 SDRs are at 40% utilization because lead supply is weak; connect rate is 2%. AEs can process 50 qualified opportunities/month and current SDRs already generate 45.

Expected: reverse/revise hiring thesis; fix data/targeting and downstream capacity before large SDR expansion. Trap: headcount is not the binding constraint.

### Q14 Independent challenge without isolation
User explicitly requests INDEPENDENT review, but runtime provides no separate context, model, or isolated challenger.

Expected: disclose limitation, do not claim independence, fall back to bounded CONVICTION behavior. Trap: cosmetic independence label.

### Q15 Forecast: inside view conflicts with reference class
New product forecast is 1m users in 12 months based on a two-week beta. A credible reference class of 20 similar launches has median 150k and 90th percentile 500k at 12 months. No differentiated distribution advantage is evidenced.

Expected: materially downgrade forecast or stage commitments; use Outside View. Trap: extrapolating early beta without explaining reference-class deviation.

### Q16 Competitor response: static strategy in an interactive market
Company proposes an across-the-board price cut. Main competitor has 60% gross margin and repeatedly matched major price moves within two weeks. Management model assumes no response.

Expected: do not use static no-response economics; run adversary simulation and prefer a targeted/defensible move unless price-war economics pass. Trap: endogenous competitor behavior omitted.

### Q17 Causal attribution: post hoc is not causal proof
NPS rises 10 points after onboarding redesign. In the same period support response time improves sharply, a major product bug is fixed, and survey sampling changes. Management attributes all uplift to onboarding and requests USD 5m rollout investment.

Expected: causal claim is insufficient; use Evidence Audit and design a cleaner test before attributing full value. Trap: concurrent interventions and sample change.

### Q18 Materiality: do not block on irrelevant precision
A USD 100m acquisition case is missing the exact annual office-rent figure; best estimate is USD 50k and even a 100% error does not move any decision threshold.

Expected: state a provisional assumption and continue. Trap: over-hardening into analysis paralysis.
