#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
skill=(ROOT/'SKILL.md').read_text(encoding='utf-8').lower()
p=(ROOT/'references'/'user-interaction-protocol.md').read_text(encoding='utf-8').lower()
a=(ROOT/'references'/'assignment-contracts.md').read_text(encoding='utf-8').lower()
t=(ROOT/'references'/'token-economy.md').read_text(encoding='utf-8').lower()
assert 'substantive execution must be visibly observable' in skill
assert 'decision rights are explicit' in skill
assert 'root owns the public voice' in skill
for event in ['`start`','`progress`','`finding`','`recovery`','`decision`','`final`']: assert event in p
assert 'roughly 2-3 substantive operations' in p
assert 'do not narrate every tool call' in t
assert 'retrieve before asking' in p
assert 'reasonable users could prefer different viable outcomes' in p
assert '`decision_pause` is a control-plane transition, not a new loop contract schema field' in p
assert 'status=blocked' in p and 'preserve the current contract and approval digest' in p
assert 'workers/planners/verifiers return distilled state' in p
assert 'decision_request' in a and 'independently address the user' in a
assert 'chain-of-thought' in p and 'never claim unsupported live streaming' in p
print('PASS: user interaction protocol enforces visible progress, decision rights, root ownership, token economy, and runtime honesty')
