# Generic proposal design system

The runtime is brand-configurable. The provider profile, not this file, determines the final visual identity.

## Hierarchy
- Use large, concise titles and restrained supporting copy.
- Favor a clear reading path over dense grids.
- Use whitespace as structure, not decoration.
- Keep commercial numbers optically prominent and easy to compare.
- Use visual grouping to distinguish contracted scope, variables, optional work, and conditions.

## Brand tokens
Read primary, accent, background, surface, text, muted colors; display/body font names; border radius; provider logo; optional cover image; footer/confidentiality from `business-profile.json`. If missing, use neutral defaults. Do not invent a new brand personality.

## Typography
Do not package proprietary font files. Use CSS family names and system fallbacks. Keep body text readable in print and browser rendering.

## Images and logos
Prefer transparent SVG/PNG logos; keep surfaces transparent unless contrast requires otherwise; use client logos only from authorized assets; use imagery only when meaningful and crop safely; never distort logos.

## Components
Use semantic components for executive callouts, decision cards, scope cards, sequence steps, comparisons, proof blocks, investment blocks, conditions, and next-step callouts.

## Page safety
Prefer splitting content over reducing type; avoid fixed-height boxes for unpredictable copy; keep print backgrounds intentional; use page breaks and break-inside avoidance on critical groups.
