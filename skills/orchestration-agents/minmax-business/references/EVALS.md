# Routing Evaluation Set

Use these cases to regression-test the router. The objective is not merely to find a relevant skill; it is to choose the smallest sufficient set with the correct primary owner.

## Core cases

| User request | Expected primary | Possible support | Failure to avoid |
|---|---|---|---|
| Our pipeline fell 30%. Find out why. | Revenue Operations | Sales, Marketing only if evidence points there | Route immediately to Sales because of the word pipeline |
| How should we price the new enterprise plan? | Commercial | Market Intelligence | Let Marketing own price authority |
| We want to enter Brazilian enterprise accounts. | Strategy | Market Intelligence, Commercial, Marketing, Sales | Launch tactics before strategic choices |
| Build a LinkedIn campaign for this ICP. | Marketing | Market Intelligence if ICP evidence is missing | Invoke Strategy/GTM unnecessarily |
| Should I give this deal a 20% discount? | Commercial | Sales for deal context | Let Sales approve its own exception |
| Increase win rate. | Revenue Operations for diagnosis | Sales, Commercial, Marketing according to driver | Assume coaching is the answer before diagnosis |
| Create a partner program. | Partnerships | Commercial for economics, RevOps for infrastructure | Put the whole program under Commercial |
| Customers cancel around month six. Diagnose it. | Customer | RevOps for cohort/data analysis | Treat churn as only a Marketing problem |
| Which feature should we build next? | Product | Market Intelligence | Route to Strategy solely because prioritization is strategic |
| Improve our internal employee onboarding process. | Business Operations | Management if people-leadership issues dominate | Route to Customer onboarding |
| Build our complete GTM plan. | Strategy | Market Intelligence, Product, Commercial, Marketing, Sales, RevOps as needed | Treat GTM as one monolithic specialist |
| Write a cold email to this account. | Sales | Account research only if needed | Trigger a full orchestration plan |
| Create an SEO content plan. | Marketing | Market Intelligence for demand evidence | Route to Market Intelligence as final owner |
| Size this market before we invest. | Market Intelligence | Strategy after sizing if decision requested | Let Strategy invent market data |
| Should we acquire this adjacent product line? | Strategy | Market Intelligence, Product, Commercial/Finance | Route to Product as final owner |
| Our reps keep skipping CRM stages. Fix the system. | Revenue Operations | Sales, Business Operations | Treat it only as rep coaching |
| Our handoff from sales to implementation is broken. | Customer if post-sale outcome dominates | Sales, RevOps, BizOps | Pick one domain without mapping the boundary |
| Build a mutual action plan for this opportunity. | Sales | Commercial only for commercial milestones | Route to Customer success plan |
| Model partner-channel economics. | Commercial | Partnerships | Duplicate economics logic inside Partnerships |
| Design our QBR process for strategic accounts. | Customer | RevOps for data infrastructure | Route to Business Operations only |

## Adversarial ambiguity cases

### “We need a growth strategy.”
Expected behavior: clarify the decision only if needed. If company-level growth choices are requested, Strategy owns. If channel/campaign growth is clearly intended, Marketing owns. If expansion inside existing accounts dominates, Customer owns.

### “Fix our GTM.”
Expected behavior: diagnose before routing. GTM is not a functional owner.

### “Our pricing page is not converting.”
Expected behavior: Marketing/CRO owns page conversion diagnosis; Commercial owns any actual change to pricing or packaging economics.

### “Our sales forecast is wrong.”
Expected behavior: Revenue Operations owns forecast governance/accuracy. Sales supports opportunity evidence. Commercial owns separate commercial forecasting decisions when applicable.

### “Research this account and tell me how to win it.”
Expected behavior: Sales owns the outcome; account research is supporting work, not a separate end state.

### “Create a customer scorecard.”
Expected behavior: Customer owns the success/health concept; RevOps supports data model and system implementation.

### “We should launch a referral partnership with this company.”
Expected behavior: Partnerships owns the partnership decision. Commercial owns economics/terms. Marketing may support co-marketing execution.

### “Create the board plan for next year.”
Expected behavior: Strategy owns overall choices. Pull functional specialists only for decision-critical inputs.

## Minimum-sufficient orchestration tests

The router should resist calling extra specialists for:
- rewriting one sales email;
- calculating one commercial scenario when inputs are complete;
- summarizing one customer interview;
- creating one marketing CTA;
- reviewing one simple SOP;
- answering a conceptual business-framework question.

## Failure tests

Fail the router if it:
- routes primarily by keyword;
- selects more than one primary owner without a reason;
- uses GTM, Growth, Revenue, or Business Development as catch-all ownership categories;
- allows a supporting domain to override the decision owner;
- upgrades uncertain evidence states silently;
- delegates recursively through generic orchestrators;
- invokes reviewers on low-risk work by default;
- asks clarification when a reversible assumption would suffice;
- keeps delegating after the answer is already decision-sufficient.
