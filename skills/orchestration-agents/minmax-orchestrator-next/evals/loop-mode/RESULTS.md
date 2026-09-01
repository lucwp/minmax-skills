# Loop Mode Hardening Results

## Evidence class

These results are deterministic / adversarial / rendering-level evidence. They are **not** a stochastic model-runtime benchmark. The current environment does not expose isolated execution of the modified skill as a separate model policy, so no runtime trial result is fabricated.

## Hardening target

This release closes the independent QA findings from the prior candidate:

1. approval replay after material contract mutation;
2. schema downgrade bypass;
3. generic execution steps passing as a clear plan;
4. complex topology justified only by importance/complexity;
5. read-only envelopes containing obvious state-changing actions;
6. executor self-report as terminal verification;
7. decorative proxy-hardening text;
8. reasoning-only activity counted as progress;
9. prose no-progress limits contradicting the structured budget;
10. opaque loop names;
11. checkpoint identity/budget drift;
12. behavioral fixture placeholders passing validation;
13. no grader for actual behavioral observations;
14. no rendered PT-BR/English golden contracts;
15. PT-BR localization leakage and missing required contract prefix;
16. alternative external-write verbs/targets hidden inside `read_only`;
17. irreversible steps without a per-step human gate;
18. executor-fabricated external-write preauthorization references;
19. behavioral full-suite PASS with zero/missing observations;
20. silent English fallback for unsupported Human Contract languages;
21. no-progress prose false positives when unrelated numeric budgets/retries are mentioned.

## Deterministic gates

PASS:

- latest-schema default (`1.4`) with explicit legacy resume/migration path only;
- canonical contract digest self-integrity;
- approved-contract validation against an externally supplied root-captured digest;
- checkpoint validation against contract identity, approval digest, boundaries, side-effect class, and remaining budgets;
- structured Complexity Gate benefit types for complex topologies;
- execution-step side-effect envelopes, expanded external-mutation contradiction checks, and mandatory per-step human gates for irreversible actions;
- structured progress evidence types and no-progress budget consistency;
- terminal actor/evidence-source requirements that exclude executor self-report;
- structured proxy hardening with attack path, protected elements, frozen thresholds, and protected verifier ownership;
- strengthened behavioral specification validation that rejects placeholder semantics;
- behavioral observation grader that first validates each captured contract, requires complete case coverage for full-suite PASS, and exposes partial coverage only through explicit diagnostic mode;
- six golden Human Contract snapshots: Lite/Standard/Complex in pt-BR and English;
- approved autonomous external writes require a root-supplied preauthorization reference matching executor-visible approval metadata and checkpoint state;
- unsupported Human Contract languages fail explicitly in the bundled reference renderer instead of silently falling back to English;
- no-progress prose is checked against the contextual no-progress threshold rather than every unrelated number in the sentence;
- localized first-line contract convention: `Contrato de Loop - <o que é>` and `Loop Contract - <what it is>`;
- existing action-manifest, topology, safety, finite-budget, recursion, context, and regression gates;
- Python syntax compilation.

## Independent red-team mutations

The external mutation harness rejects:

- unstamped contract mutations;
- generic loop names;
- obvious external writes hidden inside `read_only`;
- executor terminal actors;
- mutable verifier thresholds;
- parallel-independent-review without risk-reduction benefit;
- no-progress prose that contradicts the frozen budget;
- decorative structured proxy hardening;
- approval replay even after rewriting all digest fields inside the contract;
- schema downgrade through the normal validation path;
- calendar/Drive/GitHub/CRM mutation synonyms hidden under `read_only`;
- irreversible actions with missing, false, or non-boolean human gates;
- `mixed` side-effect envelopes used as a single-class bypass;
- fabricated internal external-write preauthorization that disagrees with the root-captured reference;
- empty behavioral observation suites reporting PASS;
- multiline loop-name title injection;
- silent unsupported-language renderer fallback.

## Remaining limitation

A deterministic validator can prove structural consistency and reject known semantic contradictions. It cannot prove that a claimed real-world benefit such as “true parallelism exists” is factually true for an arbitrary task. The root semantic preflight therefore remains authoritative for task-truth judgments, while the validator ensures that such judgments are explicit, structured, and cannot bypass approval/safety invariants.

Runtime behavioral confidence should be upgraded only after isolated multi-trial execution is available.
