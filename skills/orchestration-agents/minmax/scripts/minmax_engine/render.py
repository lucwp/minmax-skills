from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

RESET = '\033[0m'
GREEN = '\033[32m'
RED = '\033[31m'
YELLOW = '\033[33m'
GRAY = '\033[90m'
BOLD = '\033[1m'


def _text(path: Path) -> List[str]:
    try:
        return path.read_text(encoding='utf-8', errors='replace').splitlines()
    except OSError:
        return []


def build_visual_diff(old_root: Path, new_root: Path, diff: Dict[str, Any], max_lines: int = 24) -> List[str]:
    lines: List[str] = []
    for path in diff.get('removed', []):
        lines.append(f'- [removed] {path}')
    for path in diff.get('added', []):
        lines.append(f'+ [added] {path}')
    for path in diff.get('changed', []):
        lines.append(f'! [changed] {path}')
        if Path(path).name in {'SKILL.md', 'skill.md'}:
            before = _text(old_root / path)
            after = _text(new_root / path)
            for raw in difflib.unified_diff(before, after, lineterm='', n=1):
                if raw.startswith(('---', '+++', '@@')):
                    continue
                if raw.startswith(('+', '-', ' ')):
                    lines.append(raw)
                if len(lines) >= max_lines:
                    lines.append('! [truncated] use --format json for full detail')
                    return lines[:max_lines]
    for cap in diff.get('capabilities_added', []):
        lines.append(f'! [capability added] {cap}')
    for cap in diff.get('capabilities_removed', []):
        lines.append(f'- [capability removed] {cap}')
    for req in diff.get('external_requirements_added', []):
        lines.append(f'! [requirement added] {req}')
    if not lines:
        lines.append('  [context] no deterministic content changes')
    if len(lines) > max_lines:
        return [*lines[: max_lines - 1], '! [truncated] use --format json for full detail']
    return lines


def colorize(line: str) -> str:
    if line.startswith('+'):
        return GREEN + line + RESET
    if line.startswith('-'):
        return RED + line + RESET
    if line.startswith('!'):
        return YELLOW + line + RESET
    return GRAY + line + RESET


def render_update_plan(plan: Dict[str, Any], ansi: bool = True) -> str:
    current = plan.get('current', {})
    candidate = plan.get('candidate', {})
    risk = plan.get('risk', {})
    name = current.get('name') or candidate.get('name') or plan.get('package_id', 'package')
    header = f"{name}  risk={risk.get('level', 'UNKNOWN')}  plan={plan.get('id', '')}"
    output = [BOLD + header + RESET if ansi else header]
    for line in plan.get('visual_diff', []):
        output.append(colorize(line) if ansi else line)
    overlay = plan.get('overlay', {})
    if overlay and not overlay.get('clean', True):
        warning = '! [overlay conflict] ' + ', '.join(overlay.get('conflicts', []))
        output.append(colorize(warning) if ansi else warning)
    return '\n'.join(output)


def render_install_plan(plan: Dict[str, Any], ansi: bool = True) -> str:
    pkg = plan.get('package', {})
    risk = plan.get('risk', {})
    targets = ','.join(pkg.get('targets', [])) or 'none'
    lines = [f"{pkg.get('name', 'package')}  risk={risk.get('level', 'UNKNOWN')}  plan={plan.get('id', '')}"]
    lines.append(f"source={pkg.get('source', {}).get('canonical_url') or 'unknown'}")
    if pkg.get('targets'):
        lines.append(f"install -> {targets}")
    if plan.get('delivery_output'):
        lines.append(f"deliver -> {plan['delivery_output']}")
    return '\n'.join(BOLD + x + RESET if ansi and i == 0 else x for i, x in enumerate(lines))


def render_global_update(payload: Dict[str, Any], ansi: bool = True) -> str:
    summary = payload.get('summary', {})
    title = (
        f"MinMax update: {summary.get('plans', 0)} update(s), "
        f"{summary.get('up_to_date', 0)} current, {summary.get('unresolved', 0)} unresolved, "
        f"{summary.get('failures', 0)} failed"
    )
    out = [BOLD + title + RESET if ansi else title]
    for plan in payload.get('plans', []):
        out.append(render_update_plan(plan, ansi=ansi))
    for item in payload.get('unresolved_sources', []):
        line = f"! [unresolved] {item.get('name')}"
        out.append(colorize(line) if ansi else line)
    for item in payload.get('failures', []):
        line = f"! [{item.get('status', 'failed')}] {item.get('name')}"
        out.append(colorize(line) if ansi else line)
    if payload.get('unmanaged'):
        out.append(f"! [unmanaged] {len(payload['unmanaged'])} skill(s); run scan/resolve when needed")
    return '\n'.join(out)


def render_compact(payload: Any, ansi: bool = False) -> str:
    if not isinstance(payload, dict):
        return str(payload)
    if payload.get('action') == 'review_required' and isinstance(payload.get('plan'), dict):
        plan = payload['plan']
        if plan.get('type') == 'install':
            return render_install_plan(plan, ansi=ansi)
        if plan.get('type') == 'update':
            return render_update_plan(plan, ansi=ansi)
        return f"{plan.get('type', 'plan')}  plan={plan.get('id', '')}"
    if payload.get('action') == 'global_update_review':
        return render_global_update(payload, ansi=ansi)
    if payload.get('status') == 'up_to_date':
        return f"{payload.get('name', payload.get('package_id', 'package'))}: up to date"
    if payload.get('plan_id'):
        state = payload.get('install_state') or payload.get('state', 'done')
        extra = ''
        if payload.get('delivery_output'):
            extra = f"  output={payload['delivery_output']}"
        if payload.get('installed_targets'):
            extra += f"  targets={','.join(payload['installed_targets'])}"
        return f"{payload.get('type', 'apply')}  {state}  plan={payload['plan_id']}{extra}"
    if 'managed_packages' in payload:
        return (
            f"managed={payload.get('managed_packages', 0)}  installed={payload.get('installed', 0)}  "
            f"registered_only={payload.get('registered_only', 0)}  pinned={payload.get('pinned', 0)}"
        )
    if 'updates_available' in payload:
        return (
            f"updates={payload.get('updates_available', 0)}  unresolved={len(payload.get('unresolved_sources', []))}  "
            f"unmanaged={len(payload.get('unmanaged', []))}"
        )
    if 'managed' in payload and 'unmanaged' in payload:
        return (
            f"managed={len(payload.get('managed', []))}  unresolved={len(payload.get('unresolved_sources', []))}  "
            f"unmanaged={len(payload.get('unmanaged', []))}"
        )
    if 'error' in payload:
        detail = payload.get('message') or payload.get('package') or payload.get('name') or ''
        return f"error={payload['error']} {detail}".strip()
    if 'count' in payload and len(payload) <= 3:
        return '  '.join(f'{k}={v}' for k, v in payload.items() if k != 'recovered')
    return json.dumps(payload, separators=(',', ':'), sort_keys=True)


def should_use_ansi(mode: str) -> bool:
    if mode == 'ansi':
        return True
    if mode in {'json', 'compact'}:
        return False
    return sys.stdout.isatty()
