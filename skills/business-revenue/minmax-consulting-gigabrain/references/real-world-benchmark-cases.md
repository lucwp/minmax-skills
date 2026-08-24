# Real-world consulting benchmark cases

Last reviewed: 2026-08-24

Purpose: historical business decisions for blind one-shot consulting evaluation. These cases are not framework references and must not be loaded into ordinary client work.

## Benchmark protocol

For each case:

1. expose only the **decision-date packet** to the answering model;
2. hide the later outcome;
3. capture the first substantive answer before any Challenge Engine pass;
4. score Decision Robustness with a separate reviewer/context;
5. record hard-gate misses, false-ROBUST outcomes, and wrong decision class;
6. reveal the outcome packet only after scoring.

Historical outcome is a calibration signal, not proof that the hindsight-optimal decision was knowable ex ante. Score the quality of reasoning and decision architecture, not whether the model predicts history perfectly.

## RW01 Adobe Creative Cloud transition

**Decision question:** Should Adobe continue shifting the Creative Suite business from perpetual licensing toward Creative Cloud subscriptions despite near-term revenue/cash-flow disruption and adoption risk?

**Decision-date packet:**
- Adobe FY2011 10-K: https://www.sec.gov/Archives/edgar/data/796343/000079634312000003/adbe10kfy11.htm
- Adobe FY2013 10-K for contemporaneous transition risks and discontinuation of future Creative Suite perpetual releases: https://www.sec.gov/Archives/edgar/data/796343/000079634314000004/adbe10kfy13.htm

**Outcome packet, reveal after scoring:**
- Adobe FY2015 10-K: https://www.sec.gov/Archives/edgar/data/796343/000079634316000224/adbe10kfy15.htm

**Reference decision class:** continue the transition, but govern adoption, renewal, pricing, cash-flow, and customer-friction gates rather than treating subscription adoption as guaranteed.

## RW02 Disney acquisition of Pixar

**Decision question:** Should Disney acquire Pixar for roughly USD 7.4bn, and if so, how should the integration be structured to protect the creative asset being purchased?

**Decision-date packet:**
- Disney/Pixar acquisition announcement: https://thewaltdisneycompany.com/press-releases/disney-to-acquire-pixar/
- SEC transaction presentation preserving separate facilities/cultures and leadership structure: https://www.sec.gov/Archives/edgar/data/1002114/000119312506011004/d425.htm

**Outcome packet:**
- Disney completion announcement: https://thewaltdisneycompany.com/press-releases/disney-completes-pixar-acquisition/

**Reference decision class:** approve with explicit cultural/creative-governance protections and integration boundaries.

## RW03 Microsoft Office 365 / cloud transition

**Decision question:** Should Microsoft accelerate Office into a cloud subscription model or protect the traditional on-premise/perpetual model?

**Decision-date packet:**
- Office 365 global launch, June 2011: https://news.microsoft.com/source/2011/06/28/microsoft-launches-office-365-globally/
- Microsoft 2011 annual-report shareholder letter describing cloud as a staged/hybrid journey: https://msftar.azurewebsites.net/investor/reports/ar11/shareholder_letter/index.html

**Outcome packet:**
- Later Microsoft annual reports/earnings should be used only after scoring.

**Reference decision class:** continue transition with migration, adoption, retention, service reliability, and hybrid-path gates rather than assuming immediate full conversion.

## RW04 WeWork 2019 IPO

**Decision question:** Should WeWork proceed with the 2019 IPO on the proposed narrative/valuation and governance structure?

**Decision-date packet:**
- 2019 Form S-1/A showing losses and inability to predict profitability: https://www.sec.gov/Archives/edgar/data/1533523/000119312519236798/d781982ds1a.htm

**Outcome packet:**
- Use contemporaneous withdrawal/recapitalization records only after scoring.

**Reference decision class:** do not proceed on the existing terms; address governance, economics, cash burn, lease-duration mismatch, and valuation before reconsidering a public offering.

## RW05 Zillow Offers scaling decision

**Decision question:** Should Zillow continue rapidly scaling Zillow Offers in 2021?

**Decision-date packet:**
- Q2 2021 results and acceleration narrative: https://investors.zillowgroup.com/news-and-events/news/news-details/2021/Zillow-Group-Reports-Second-Quarter-2021-Financial-Results/default.aspx
- October 2021 operational-capacity pause: https://investors.zillowgroup.com/investors/news-and-events/news/news-details/2021/At-Operational-Capacity-Zillow-Offers-to-Focus-on-Signed-Customer-Contracts-and-Current-Inventory-Suspends-Signing-of-New-Contracts-Through-2021/default.aspx

**Outcome packet:**
- Q3 wind-down announcement: https://investors.zillowgroup.com/news-and-events/news/news-details/2021/Zillow-Group-Reports-Third-Quarter-2021-Financial-Results--Shares-Plan-to-Wind-Down-Zillow-Offers-Operations/default.aspx

**Reference decision class:** stop or sharply constrain scaling until pricing-model error, renovation/resale capacity, and balance-sheet exposure are proven within gates.

## RW06 Target Canada rollout

**Decision question:** Should Target continue a large, rapid Canadian rollout before supply chain, inventory availability, merchandising, and unit economics are demonstrably stable?

**Decision-date packet:**
- FY2013 10-K describing 124 stores and Canadian segment risks/results: https://www.sec.gov/Archives/edgar/data/27419/000002741914000014/tgt-20140201x10k.htm

**Outcome packet:**
- FY2014/2015 exit and USD 5.1bn pretax charges: https://www.sec.gov/Archives/edgar/data/27419/000002741915000012/tgt-20150131x10k.htm

**Reference decision class:** replace big-bang rollout with staged expansion gated by supply-chain, in-stock, inventory, customer acceptance, and store economics.

## RW07 Netflix Qwikster separation

**Decision question:** After separating DVD and streaming pricing, should Netflix also separate the DVD business into the Qwikster brand/site?

**Decision-date packet:**
- Netflix September 2011 shareholder communication on splitting services: https://www.sec.gov/Archives/edgar/data/1065280/000119312511248698/d231910dex991.htm

**Outcome packet:**
- Q3 2011 shareholder letter acknowledging cancelled rebranding, reputation damage, cancellations, and stalled domestic growth: https://www.sec.gov/Archives/edgar/data/1065280/000119312511278716/d246709dex991.htm
- Q3 2011 10-Q: https://www.sec.gov/Archives/edgar/data/1065280/000119312511284366/d222257d10q.htm

**Reference decision class:** separate economics/operations as needed, but do not add brand/site fragmentation without evidence that the incremental strategic benefit exceeds customer friction.

## RW08 Microsoft acquisition of Nokia Devices & Services

**Decision question:** Should Microsoft buy substantially all of Nokia Devices & Services to accelerate Windows Phone share/profitability, or preserve partnership/optionality instead?

**Decision-date packet:**
- Microsoft acquisition announcement and deal terms: https://news.microsoft.com/source/2013/09/03/microsoft-to-acquire-nokias-devices-services-business-license-nokias-patents-and-mapping-services/
- Microsoft investor rationale including expected EPS accretion: https://news.microsoft.com/source/2013/09/03/media-alert-microsoft-to-acquire-nokias-devices-services-business-license-nokias-patents-and-mapping-services/

**Outcome packet:**
- 2015 restructuring and approximately USD 7.6bn impairment: https://www.sec.gov/Archives/edgar/data/789019/000119312515247530/d54167dex991.htm

**Reference decision class:** require a much stronger proof that vertical integration solves the ecosystem/share problem; prefer staged partnership/optionality if that causal link is not demonstrated.

## Required failure patterns across these cases

The benchmark reviewer should penalize the answering system for:

- hindsight language before outcome reveal;
- generic framework recitation instead of a decision;
- ignoring an explicit hard threshold or balance-sheet exposure;
- treating a strategic thesis as equivalent to its implementation architecture;
- failing to distinguish reversible staging from irreversible commitment;
- inventing unavailable numbers;
- continuing to manufacture objections after a healthy decision reaches 90+ DRS.
