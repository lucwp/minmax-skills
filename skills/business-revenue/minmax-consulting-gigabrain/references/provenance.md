# Provenance and inspiration ledger

Last reviewed: 2026-08-24

This file makes the skill's intellectual basis explicit. The implementation in this package is an original synthesis. Unless a row explicitly says otherwise, no source code or prose was copied; concepts were reimplemented from scratch.


## Naming provenance

`minmax-consulting-gigabrain` uses **Gigabrain** as a deliberately playful name. It is a tongue-in-cheek reference to the 2026 Brazilian internet meme around Thiago Finch’s “Mega Brain”. The reference is cultural, not architectural: no Mega Brain code, prompts, methods, branding, or proprietary material are included. There is no affiliation with, sponsorship by, or endorsement from Thiago Finch or Mega Brain.

The joke also encodes an anti-pattern: this skill must never claim that a magic phrase, “full power” instruction, hidden mode, or theatrical prompting makes an LLM more reliable. Reliability must come from scoped context, source provenance, falsification, deterministic validation, explicit uncertainty, and release gates.

## Agent-skill architecture inspirations

| ID | Source | Contribution to MinMax | License / use posture |
|---|---|---|---|
| A-001 | appautomaton/presentation, `consultant` | Client-specific intake, hypothesis lifecycle, falsification, iterative analysis/synthesis, backtracking, engagement-state thinking | No root LICENSE was observed during the 2026-08-24 audit. Conceptual inspiration only; no code copied. https://github.com/appautomaton/presentation/tree/main/consultant |
| A-002 | K-Dense-AI/scientific-agent-skills, `market-research-reports` | Source ledger, claim ledger, type separation, unit/denominator consistency, deterministic evidence checks, release discipline | Skill declares MIT in its SKILL frontmatter. Conceptual/implementation-pattern inspiration; validators here are original. https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/market-research-reports |
| A-003 | Natan-Mohart/24-strategy-skills-for-claude | Driver-based business cases, deterministic NPV/IRR/sensitivity, assumption auditing, value realization | MIT. Algorithms in this package were independently implemented. https://github.com/Natan-Mohart/24-strategy-skills-for-claude |
| A-004 | anotb/management-consulting-plugin | Full consulting lifecycle: setup, pricing, analysis, DD, implementation, change, governance, closeout | MIT. Conceptual lifecycle inspiration. https://github.com/anotb/management-consulting-plugin |
| A-005 | gcamilo/management-consulting | Fact/inference/assumption/estimate discipline, devil's-advocate and decision-contract patterns | MIT. Conceptual inspiration. https://github.com/gcamilo/management-consulting |
| A-006 | DeloitteDigitalUK/assured-engineering-superpowers | Atomic/composite boundaries, standards separation, external-call gates, independent review, validation against signed-off real work, assurance trail | MIT. Assurance philosophy adapted conceptually. https://github.com/DeloitteDigitalUK/assured-engineering-superpowers |
| A-007 | aapersh/consulting-strategy-problem-solving | Partner/associate review cadence, staged engagement artifacts, traceability between question, branch, analysis, finding and recommendation | No LICENSE found at repository root during the 2026-08-24 audit. Conceptual inspiration only. https://github.com/aapersh/consulting-strategy-problem-solving |
| A-008 | bestagentkits/agency-skills, `strategy-red-team` | Lean load-bearing-assumption attack, steelman-before-attack, falsifiable `fails if` framing, cheap tests and kill criteria | MIT. Conceptual inspiration; no prose copied. https://github.com/bestagentkits/agency-skills/tree/main/skills/pm-skills/strategy-red-team |
| A-009 | latour-ai/skills, `thesis-red-team` | Fragility ranking, explicit opposing case, falsifiability map, precommitted kill criteria and evidence-vs-logic labeling | Skill declares MIT. Conceptual inspiration; generalized beyond investment use. https://github.com/latour-ai/skills/tree/main/thesis-red-team |
| A-010 | Jeffallan/claude-skills, `the-fool` | Routing adversarial work into distinct modes such as evidence audit, premortem and adversarial challenge instead of using one universal red-team ritual | MIT. Conceptual routing inspiration; no prompt text copied. https://github.com/Jeffallan/claude-skills/tree/main/skills/the-fool |
| A-011 | projectious-work/processkit, `devils-advocate` | Explicit user opt-in, intensity calibration by stakes, alternatives comparison, constraint checks and second-order effects | MIT. Conceptual inspiration; no prose copied. https://github.com/projectious-work/processkit/tree/main/src/context/skills/product/devils-advocate |

## What is original to MinMax

- The combined consulting state model and release-gate architecture.
- The requirement that evidence truth, arithmetic correctness, unit consistency, and decision thresholds be separate validation layers.
- The `FACT / INFERENCE / ASSUMPTION / ESTIMATE / CALCULATION / FORECAST / RECOMMENDATION` decision contract as used here.
- The policy that deterministic validation outranks model self-review for mechanically testable properties.
- The integration of public practitioner frameworks into a source-ledger with explicit anti-patterns and evidence requirements.
- The release statuses `PASS / CONDITIONAL / BLOCK` and their default decision semantics.
- The bundled Python implementations.
- The Gigabrain Challenge Engine: opt-in `OFF / PULSE / CONVICTION / INDEPENDENT` modes, a one-primary-technique routing rule, finite challenge budgets, a persistent challenge ledger, a mechanical challenge gate, and explicit robustness/stop criteria.
- The policy that same-model devil's advocacy is never labeled independent review and that recursive intrinsic self-critique is not a substitute for external evidence or deterministic checks.
- The Decision Robustness Score (DRS): a 0-100 decision-quality threshold calculated from observable criterion states, with hard caps that prevent unresolved empirical breakers from reaching the 90+ stop state.
- The One-Shot Robustness Standard: target 90+ in the first substantive response, allow one bounded repair pass, and change commitment strength instead of fabricating certainty when evidence is missing.
- The benchmark release target of 95+ mean with a 90 one-shot floor, zero hard-gate misses, zero false-ROBUST outcomes, and zero wrong decision classes. Certified claims require blind scoring by an independent reviewer; same-context self-scoring is development evidence only.
- The 90/95 dual-threshold design: 90 is the robustness release/Challenge stop floor; 95 is the one-shot construction target and package benchmark mean target. A 90-94.9 answer may receive one cheap same-pass micro-repair, never a new research or red-team loop merely to gain points.

## Attribution rule for derivative versions

Keep this file or an equivalent provenance ledger in derivative versions. If code is later copied or substantially adapted from an external repository, update this ledger with the exact file, commit/tag, license, and copyright notice required by that license.

## Framework sources

The consulting frameworks themselves are sourced separately in `framework-source-ledger.md`. Those sources include trademarks and copyrighted publications. This package summarizes operational concepts and links to the authoritative sources; it does not redistribute their proprietary text, diagrams, or branded templates.
