#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
skill=(ROOT/'SKILL.md').read_text(encoding='utf-8').lower()
loop=(ROOT/'references'/'loop-mode.md').read_text(encoding='utf-8').lower()
top=(ROOT/'references'/'loop-topology.md').read_text(encoding='utf-8').lower()
state=(ROOT/'references'/'loop-state.md').read_text(encoding='utf-8').lower()
term=(ROOT/'references'/'termination-budgets.md').read_text(encoding='utf-8').lower()
safety=(ROOT/'references'/'production-safety.md').read_text(encoding='utf-8').lower()

# Simple work must stay simple; sophisticated topology cannot become default.
assert 'single_adaptive_loop' in top and 'default for open-ended loop mode work' in top
assert 'evaluator_optimizer' in top and 'use only when all are true' in top
assert 'task complexity alone is not sufficient' in top
assert 'when the gain is uncertain, choose the simpler topology' in top

# Approval and finite-budget invariants remain explicit.
assert 'loop approval is mandatory' in skill
assert 'material replan invalidates prior loop approval' in skill
assert 'fresh approval is mandatory' in loop
assert 'never use unlimited turns, recursion, or retries' in term
assert 'finite max-iteration budget' in term

# Safety / write protections remain intact.
assert 'loop mode never expands the autonomous write envelope' in loop
assert 'irreversible_high_consequence' in loop and 'human approval boundary' in loop
assert 'action manifest' in safety
assert 'ambiguous write' in loop and 'authoritative state' in loop

# No recursive orchestration and no unnecessary durable infrastructure.
assert 'child workers cannot recursively invoke the orchestrator or loop mode' in loop
assert 'ephemeral' in state and 'short, single-session' in state
assert 'checkpointed' in state and 'state-changing writes' in state

# Context and progress controls cannot degrade into transcript replay or fake work.
assert 'do not use conversation history as the only durable memory' in loop
assert 'reasoning text alone is not progress' in loop
assert 'progress fingerprint' in loop

print('PASS: Loop Mode regression gates remain protected')
