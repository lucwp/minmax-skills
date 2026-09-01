#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
loop=(ROOT/'references'/'loop-mode.md').read_text(encoding='utf-8').lower()
validator=(ROOT/'scripts'/'validate_loop_contract.py').read_text(encoding='utf-8')
checkpoint=(ROOT/'scripts'/'validate_loop_checkpoint.py').read_text(encoding='utf-8')
workspace=(ROOT/'references'/'workspace-integration.md').read_text(encoding='utf-8').lower()
planning=(ROOT/'references'/'planning-engine.md').read_text(encoding='utf-8').lower()
# Contract schema/approval binding are untouched.
assert 'LATEST_SCHEMA = "1.4"' in validator
assert 'external approved digest does not match contract_digest' in validator
# decision_pause is additive control-plane semantics, not schema churn.
assert '`decision_pause`' in loop and 'preserve the approved contract/digest' in loop
assert 'status=blocked' in loop
assert 'STATUS = {"active", "blocked", "success", "failure", "budget_exit", "paused_replan"}' in checkpoint
# Decision ownership does not become ask-everything behavior.
assert 'do not pre-ask implementation choices the agent owns' in planning
assert 'keep local technical/evidence-dominated choices autonomous' in workspace
# Material replan still requires fresh approval.
assert 'fresh approval is mandatory' in loop
# Runtime limitation is explicit.
assert 'blocking host cannot accept assistant output' in workspace
print('PASS: interaction hardening preserves schema 1.4, approval binding, local autonomy, checkpoint compatibility, and runtime honesty')
