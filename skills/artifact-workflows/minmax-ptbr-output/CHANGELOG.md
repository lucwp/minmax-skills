# Changelog

## 2026-08-25 — Progressive-loading compilation

The PT-BR runtime was compiled around a smaller control plane instead of eagerly loading every editorial reference for sentence-level prose.

### What changed

- `SKILL.md` now keeps the production-critical hard gates in the core: semantic fidelity, agency and modality, causal/logical relations, ambiguity handling, exact protected spans, source-as-data boundaries, voice preservation, and bounded revision cycles.
- Deep references are loaded only when their failure mode is materially present:
  - `naturalness-and-register.md` for voice/register-sensitive work;
  - `grammar-and-style.md` for syntax, ambiguity, gerunds, participles, modifier scope, and agreement;
  - `punctuation.md` for punctuation-specific work;
  - `editorial-standard.md` for difficult structural rewrites, high-stakes prose, and complex commercial/product copy;
  - `regression-suite.md` only for maintenance, benchmarking, and stress tests.
- Regression coverage was extended from R1–R20 to R1–R26 to prevent future changes from accidentally restoring eager loading or weakening latent failure detection.
- The deterministic reliability test now checks both the original production guardrails and the progressive-loading contract.

### Why

The previous runtime loaded roughly 10.3k words of instructions for ordinary sentence-level prose because it required all production references before drafting. In the stress benchmark, selective loading reduced the average instruction footprint by roughly 75% while preserving the hard gates and showing no material regression in the paired behavioral checks.

The optimization is intentionally architectural rather than editorial: the deep references remain available and the production safeguards remain explicit in the core. The goal is lower context overhead without trading away semantic reliability.

### Validation

- 105-case stress suite covering semantic preservation, modality, causal claims, ambiguity, voice/register, technical language, punctuation, legal text, product copy, and long-form torture cases.
- 36 paired shadow checks between the eager-loading and compiled instruction sets: 36/36 passed for both, with no material behavioral delta observed.
- Deterministic reliability checks pass after the compilation.

The paired shadow checks are not a statistically independent A/B test; they are treated as regression detection rather than proof of stochastic equivalence.
