from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

from .common import iter_files, tree_manifest

TEXT_EXTS = {'.md', '.txt', '.py', '.sh', '.bash', '.zsh', '.ps1', '.js', '.ts', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'}
SCRIPT_EXTS = {'.py', '.sh', '.bash', '.zsh', '.ps1', '.js', '.ts', '.rb', '.pl'}

PATTERNS = {
    'shell': [r'\bsubprocess\b', r'os\.system\s*\(', r'shell\s*=\s*True', r'\bcurl\b', r'\bwget\b', r'\bpowershell\b', r'\bchmod\b'],
    'network': [r'https?://', r'\brequests\.', r'urllib\.request', r'\bcurl\b', r'\bwget\b', r'\bsocket\.'],
    'filesystem_write': [r'open\s*\([^\n]{0,120}["\'](?:w|a|x)[+b]?["\']', r'write_text\s*\(', r'write_bytes\s*\(', r'shutil\.(?:copy|move|rmtree)', r'\bunlink\s*\(', r'\brm\s+-'],
    'credentials': [r'api[_ -]?key', r'access[_ -]?token', r'password', r'credential', r'client[_ -]?secret', r'\bsecret\b', r'\.env\b'],
    'persistence': [r'crontab', r'systemctl\s+enable', r'launchctl', r'schtasks', r'startup folder', r'auto[- ]?start'],
    'package_installation': [r'pip\s+install', r'npm\s+install', r'pnpm\s+add', r'yarn\s+add', r'apt(?:-get)?\s+install', r'brew\s+install'],
    'child_agents': [r'\bsubagent\b', r'child agent', r'spawn\s+(?:an?\s+)?agent', r'delegate\s+to\s+(?:an?\s+)?agent'],
}

CRITICAL_PATTERNS = {
    'credential_harvesting': [r'(?:send|upload|post).{0,80}(?:password|token|credential|secret)', r'(?:password|token|credential|secret).{0,80}(?:send|upload|post)'],
    'hidden_remote_execution': [r'(?:base64|b64decode).{0,120}(?:exec|eval)', r'(?:exec|eval).{0,120}(?:urlopen|requests\.|curl|wget)'],
    'privilege_escalation': [r'\bsudo\b', r'SeDebugPrivilege', r'runas\s+/user:administrator'],
}


def _read_text(path: Path) -> str:
    try:
        if path.stat().st_size > 1024 * 1024:
            return ''
        return path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


def detect_entrypoints(root: Path) -> List[str]:
    result = []
    for candidate in ('SKILL.md', 'skill.md'):
        if (root / candidate).is_file():
            result.append(candidate)
    return result


def find_skill_roots(root: Path) -> List[str]:
    roots: Set[str] = set()
    for path in root.rglob('*'):
        if not path.is_file() or path.name not in {'SKILL.md', 'skill.md'}:
            continue
        if '.git' in path.parts:
            continue
        roots.add(path.parent.relative_to(root).as_posix() or '.')
    return sorted(roots)


def inspect(root: Path) -> Dict[str, Any]:
    manifest = tree_manifest(root)
    capabilities: Set[str] = set()
    evidence: Dict[str, List[str]] = {}
    critical: Set[str] = set()
    scripts: List[str] = []
    external_requirements: Set[str] = set()

    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() in SCRIPT_EXTS or '/scripts/' in '/' + rel:
            scripts.append(rel)
        if path.suffix.lower() not in TEXT_EXTS and path.name not in {'SKILL.md', 'skill.md'}:
            continue
        text = _read_text(path)
        lower = text.lower()
        for cap, patterns in PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, flags=re.I | re.S):
                    capabilities.add(cap)
                    evidence.setdefault(cap, []).append(rel)
                    break
        for signal, patterns in CRITICAL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, flags=re.I | re.S):
                    critical.add(signal)
                    evidence.setdefault(signal, []).append(rel)
                    break
        if path.name in {'SKILL.md', 'skill.md'}:
            for match in re.finditer(r'(?:requires?|depends on|dependency)\s*[:=-]?\s*[`"\']?([a-z0-9][a-z0-9-]{2,})', lower):
                value = match.group(1)
                if value not in {'python', 'node', 'github', 'google'}:
                    external_requirements.add(value)

    risk = 'LOW'
    reasons: List[str] = []
    if critical:
        risk = 'CRITICAL'
        reasons.extend(sorted(critical))
    elif capabilities.intersection({'shell', 'network', 'filesystem_write', 'credentials', 'persistence', 'package_installation'}):
        risk = 'HIGH'
        reasons.extend('capability:' + cap for cap in sorted(capabilities.intersection({'shell', 'network', 'filesystem_write', 'credentials', 'persistence', 'package_installation'})))
    elif scripts or capabilities:
        risk = 'MEDIUM'
        if scripts:
            reasons.append('contains executable/script files')
        reasons.extend('capability:' + cap for cap in sorted(capabilities))

    return {
        'files': manifest,
        'file_count': len(manifest),
        'entrypoints': detect_entrypoints(root),
        'skill_roots': find_skill_roots(root),
        'scripts': sorted(set(scripts)),
        'capabilities': sorted(capabilities),
        'critical_signals': sorted(critical),
        'evidence': {k: sorted(set(v)) for k, v in sorted(evidence.items())},
        'external_skill_requirements': sorted(external_requirements),
        'risk': risk,
        'risk_reasons': reasons,
    }


def diff_inspections(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    old_files = old.get('files', {})
    new_files = new.get('files', {})
    old_keys = set(old_files)
    new_keys = set(new_files)
    changed = sorted(path for path in old_keys & new_keys if old_files[path] != new_files[path])
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    old_caps = set(old.get('capabilities', []))
    new_caps = set(new.get('capabilities', []))
    script_changes = sorted(path for path in set(changed + added + removed) if Path(path).suffix.lower() in SCRIPT_EXTS or '/scripts/' in '/' + path)
    skill_changes = sorted(path for path in set(changed + added + removed) if Path(path).name in {'SKILL.md', 'skill.md'})
    return {
        'added': added,
        'removed': removed,
        'changed': changed,
        'script_changes': script_changes,
        'skill_entrypoint_changes': skill_changes,
        'capabilities_added': sorted(new_caps - old_caps),
        'capabilities_removed': sorted(old_caps - new_caps),
        'external_requirements_added': sorted(set(new.get('external_skill_requirements', [])) - set(old.get('external_skill_requirements', []))),
        'external_requirements_removed': sorted(set(old.get('external_skill_requirements', [])) - set(new.get('external_skill_requirements', []))),
    }


def classify_update_risk(new_inspection: Dict[str, Any], diff: Dict[str, Any]) -> Dict[str, Any]:
    level = new_inspection.get('risk', 'LOW')
    reasons = list(new_inspection.get('risk_reasons', []))
    order = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'CRITICAL': 3}

    def raise_to(candidate: str, reason: str) -> None:
        nonlocal level
        if order[candidate] > order[level]:
            level = candidate
        if reason not in reasons:
            reasons.append(reason)

    if diff.get('skill_entrypoint_changes'):
        raise_to('MEDIUM', 'behavioral skill entrypoint changed')
    if diff.get('external_requirements_added'):
        raise_to('MEDIUM', 'external skill requirement added')
    if diff.get('script_changes'):
        raise_to('HIGH', 'executable/script content changed')
    if diff.get('capabilities_added'):
        raise_to('HIGH', 'capability escalation: ' + ', '.join(diff['capabilities_added']))
    if new_inspection.get('critical_signals'):
        raise_to('CRITICAL', 'critical structural signal detected')
    return {'level': level, 'reasons': reasons}
