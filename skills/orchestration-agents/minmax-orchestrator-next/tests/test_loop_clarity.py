#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
skill=(ROOT/'SKILL.md').read_text(encoding='utf-8').lower()
render=(ROOT/'references'/'loop-contract-rendering.md').read_text(encoding='utf-8').lower()
loop=(ROOT/'references'/'loop-mode.md').read_text(encoding='utf-8').lower()
plan=(ROOT/'references'/'planning-engine.md').read_text(encoding='utf-8').lower()

for needle in [
    'every human loop contract must have a short descriptive loop name',
    'contrato de loop - <o que é>',
    'loop contract - <what it is>',
    'minmax pt-br output',
    'humanizer',
    'clarity is a preflight gate',
]:
    assert needle in skill, needle

for needle in [
    'hard clarity gates','loop name','contrato de loop - <o que é>','loop contract - <what it is>','what happens','why','produces','then',
    'brazilian portuguese','minmax pt-br output','english','humanizer',
    'brevity never wins over comprehension','can the user explain back what the loop will do first',
]:
    assert needle in render, needle

for needle in [
    'human clarity','loop name','action, purpose, output, and handoff/next logic',
    'embedded minmax pt-br output','embedded humanizer',
]:
    assert needle in loop, needle

assert 'action -> purpose -> output -> what the output enables next' in plan
print('PASS: named-loop, language, and execution-clarity hard gates')
