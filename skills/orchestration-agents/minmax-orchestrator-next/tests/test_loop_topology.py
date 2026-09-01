#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
top=(ROOT/'references'/'loop-topology.md').read_text(encoding='utf-8').lower()
render=(ROOT/'references'/'loop-contract-rendering.md').read_text(encoding='utf-8').lower()
state=(ROOT/'references'/'loop-state.md').read_text(encoding='utf-8').lower()
plan=(ROOT/'references'/'planning-engine.md').read_text(encoding='utf-8').lower()

classes=[
    'deterministic_prompt_chain','router','single_adaptive_loop','parallel_sectioning',
    'parallel_independent_review','orchestrator_workers','evaluator_optimizer',
]
for cls in classes:
    assert cls in top, cls

assert 'when the gain is uncertain, choose the simpler topology' in top
assert 'task complexity alone is not sufficient' in top
assert 'do not use merely to "think more"' in top
assert 'this is the default for open-ended loop mode work' in top
assert 'plan deliverables and material dependencies upfront' in plan
assert 'implementation details whose correctness depends on evidence' in plan
assert 'internal work-unit contracts' in plan

for heading in ['approval snapshot','scope & evidence','execution','verification & convergence','boundaries & exits','approval']:
    assert heading in render, heading
for field in ['outcome','deliverable','pass','autonomy','budget']:
    assert field in render, field
for field in ['loop name','what happens','why','produces','then','minmax pt-br output','humanizer']:
    assert field in render, field
for exit_name in ['success','failure','budget','replan']:
    assert exit_name in render, exit_name

assert 'ephemeral' in state
assert 'checkpointed' in state
assert 'do not persist chain-of-thought' in state
assert 'authoritative state wins' in state

print('PASS: topology, adaptive planning, rendering, and state policy tests')
