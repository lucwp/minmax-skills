# Loop Contract - Hero Clarity

## Approval snapshot

**Outcome:** improve the hero without changing the approved offer
**Deliverable:** final hero with verification evidence
**PASS:** the frozen criteria pass with no hard failure
**Autonomy:** read_only
**Budget:** 4 cycles; 1 retries; 2 no-progress cycles.

## Scope and evidence

current hero; approved offer

## Execution plan

### 1. Freeze the baseline
**What happens:** capture the current state and available evidence
**Why:** establish a reliable reference before changing anything
**Produces:** a verifiable baseline
**Then:** use only demonstrated gaps in the next step

### 2. Test the main hypothesis
**What happens:** compare the baseline with the frozen decision criteria
**Why:** identify the highest-value gap blocking PASS
**Produces:** a prioritized gap with supporting evidence
**Then:** change only the component responsible for that gap

### 3. Repair the verified gap
**What happens:** apply the smallest change that can resolve the prioritized gap
**Why:** avoid scope drift or unsupported optimization
**Produces:** a revised candidate and diff
**Then:** verify whether the change had the intended effect

## Verification and convergence

**PASS:** global PASS confirmed
Verifier: independent reviewer against the frozen rubric
Progress: verified change or verifier movement
No-progress: stop after 2 cycles without material progress

## Boundaries and exits

**Can:** scope: hero only; side_effect: read_only
**Cannot:** objective, scope, or boundary change
**SUCCESS:** global PASS confirmed
**FAILURE:** unrecoverable blocker inside scope
**BUDGET:** budget exhausted
**REPLAN:** objective, scope, or boundary change

## Approval

Approval authorizes only this contract. Any material replan requires a new approval.
